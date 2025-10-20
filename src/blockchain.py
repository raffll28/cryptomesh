import time
import json
import hashlib
from urllib.parse import urlparse
import requests
from wallet import Wallet
from transaction import Transaction, TxInput, TxOutput

class Blockchain:
    def __init__(self, storage_path='blockchain.json'):
        self.storage_path = storage_path
        self.chain = []
        self.mempool = []
        self.nodes = set()
        self.difficulty = 4
        self.DIFFICULTY_ADJUSTMENT_INTERVAL = 10
        self.BLOCK_GENERATION_INTERVAL = 10 # in seconds
        self.utxo = {}

        self.load_chain()

    def load_chain(self):
        try:
            with open(self.storage_path, 'r') as f:
                self.chain = json.load(f)
            if not self.chain:
                # Se o arquivo estiver vazio, cria o bloco gênese
                coinbase_tx = self.new_coinbase_transaction("genesis_address")
                self.new_block(previous_hash='1', proof=100)
        except (FileNotFoundError, json.JSONDecodeError):
            # Se o arquivo não existir ou for inválido, cria o bloco gênese
            coinbase_tx = self.new_coinbase_transaction("genesis_address")
            self.new_block(previous_hash='1', proof=100)
        
        self._rebuild_utxo_set()

    def _rebuild_utxo_set(self):
        self.utxo = {}
        for block in self.chain:
            self._update_utxo_set(block)

    def get_balance(self, address):
        """Calcula e retorna o saldo de um endereço."""
        balance = 0
        for utxo_output in self.utxo.values():
            if utxo_output['recipient_address'] == address:
                balance += utxo_output['amount']
        return balance

    def _update_utxo_set(self, block):
        for tx in block['transactions']:
            # Adiciona as novas saídas
            for i, output in enumerate(tx['outputs']):
                self.utxo[f"{tx['id']}:{i}"] = output
            # Remove as entradas gastas (ignorando transações coinbase)
            if tx['inputs'] and tx['inputs'][0]['transaction_id'] != '0':
                for input_tx in tx['inputs']:
                    spent_utxo_key = f"{input_tx['transaction_id']}:{input_tx['output_index']}"
                    if spent_utxo_key in self.utxo:
                        del self.utxo[spent_utxo_key]

    def save_chain(self):
        with open(self.storage_path, 'w') as f:
            json.dump(self.chain, f, indent=2)

    def register_node(self, address):
        """
        Adiciona um novo nó à lista de nós
        """
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)

    def valid_chain(self, chain):
        """
        Determina se uma dada blockchain é válida
        """
        last_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]
            # Verifica se o hash do bloco está correto
            if block['previous_hash'] != self.hash(last_block):
                return False

            # Verifica se a Prova de Trabalho é correta
            last_block_hash = self.hash(last_block)
            if not self.valid_proof(last_block['proof'], block['proof'], last_block_hash):
                return False

            last_block = block
            current_index += 1

        return True

    def resolve_conflicts(self):
        """
        Este é o nosso algoritmo de consenso, ele resolve conflitos
        substituindo nossa cadeia pela mais longa da rede.
        """
        neighbours = self.nodes
        new_chain = None

        # Estamos apenas procurando por cadeias mais longas que a nossa
        max_length = len(self.chain)

        # Pega e verifica as cadeias de todos os nós da nossa rede
        for node in neighbours:
            try:
                response = requests.get(f'http://{node}/chain')
                if response.status_code == 200:
                    length = response.json()['length']
                    chain = response.json()['chain']

                    # Verifica se o comprimento é maior e se a cadeia é válida
                    if length > max_length and self.valid_chain(chain):
                        max_length = length
                        new_chain = chain
            except requests.exceptions.ConnectionError:
                # Ignora nós que não estão respondendo
                pass

        # Substitui nossa cadeia se descobrirmos uma nova cadeia válida mais longa
        if new_chain:
            self.chain = new_chain
            self.save_chain()
            self._rebuild_utxo_set()
            return True

        return False

    def new_block(self, proof, previous_hash=None):
        """
        Cria um novo bloco e o adiciona à blockchain
        """
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time.time(),
            'transactions': self.mempool,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
        }

        self.chain.append(block)
        self._update_utxo_set(block)
        self._adjust_difficulty()
        self.save_chain() # Salva a cadeia após adicionar um novo bloco
        
        # Reseta a lista de transações atuais
        self.mempool = []
        return block

    def add_block(self, block):
        """
        Adiciona um bloco recebido de outro nó à cadeia, após validação.
        """
        previous_block = self.last_block

        # Verifica se o previous_hash do bloco recebido é o hash do último bloco da nossa cadeia
        if block['previous_hash'] != self.hash(previous_block):
            return False

        # Verifica se a prova de trabalho é válida
        if not self.valid_proof(previous_block['proof'], block['proof'], self.hash(previous_block)):
            return False

        # Verifica todas as transações no bloco
        for tx in block['transactions']:
            if not self.verify_transaction(tx):
                return False

        self.chain.append(block)
        self._update_utxo_set(block)
        self._adjust_difficulty()
        self.save_chain()

        # Limpa o mempool de transações que já estão no bloco recebido
        self.mempool = [tx for tx in self.mempool if tx not in block['transactions']]
        return True

    def _adjust_difficulty(self):
        """
        Ajusta a dificuldade da mineração a cada DIFFICULTY_ADJUSTMENT_INTERVAL blocos.
        """
        # O bloco gênese não conta para o ajuste
        if len(self.chain) % self.DIFFICULTY_ADJUSTMENT_INTERVAL != 0 or len(self.chain) == 0:
            return

        last_adjustment_block = self.chain[-self.DIFFICULTY_ADJUSTMENT_INTERVAL]
        current_block = self.last_block

        actual_time = current_block['timestamp'] - last_adjustment_block['timestamp']
        expected_time = self.DIFFICULTY_ADJUSTMENT_INTERVAL * self.BLOCK_GENERATION_INTERVAL

        if actual_time < expected_time / 2:
            self.difficulty += 1
        elif actual_time > expected_time * 2:
            self.difficulty = max(1, self.difficulty - 1)

    def _find_spendable_outputs(self, owner_address, amount_needed):
        spendable_outputs = []
        accumulated_amount = 0
        for utxo_key, utxo_output in self.utxo.items():
            if utxo_output['recipient_address'] == owner_address:
                accumulated_amount += utxo_output['amount']
                spendable_outputs.append(utxo_key)
                if accumulated_amount >= amount_needed:
                    break
        return accumulated_amount, spendable_outputs

    def new_utxo_transaction(self, wallet, recipient_address, amount):
        accumulated, spendable_utxo_keys = self._find_spendable_outputs(wallet.public_key, amount)

        if accumulated < amount:
            return None # Saldo insuficiente

        inputs = []
        for utxo_key in spendable_utxo_keys:
            tx_id, output_index = utxo_key.split(':')
            inputs.append(TxInput(tx_id, int(output_index)))

        outputs = [TxOutput(recipient_address, amount)]
        if accumulated > amount:
            # Troco
            outputs.append(TxOutput(wallet.public_key, accumulated - amount))

        tx = Transaction(inputs, outputs)
        self.sign_transaction(wallet, tx)

        self.mempool.append(tx.to_dict())
        return tx

    def new_coinbase_transaction(self, recipient_address):
        """Cria a transação de mineração (coinbase)."""
        # A entrada da transação coinbase é especial
        coinbase_input = TxInput(transaction_id='0', output_index=-1)
        # A recompensa de mineração é 1
        coinbase_output = TxOutput(recipient_address, 1)
        
        tx = Transaction(inputs=[coinbase_input], outputs=[coinbase_output])
        self.mempool.append(tx.to_dict())
        return tx

    def sign_transaction(self, wallet, tx):
        tx_hash = tx.calculate_hash()
        signature = wallet.sign(wallet.private_key, tx_hash)
        for input_tx in tx.inputs:
            input_tx.signature = signature

    def verify_transaction(self, tx_dict):
        # Ignora a verificação para transações coinbase
        if not tx_dict['inputs'] or tx_dict['inputs'][0]['transaction_id'] == '0':
            return True

        tx_for_hash = Transaction([TxInput.from_dict(i) for i in tx_dict['inputs']], [TxOutput.from_dict(o) for o in tx_dict['outputs']])
        tx_hash = tx_for_hash.calculate_hash()
        
        total_input_value = 0
        for i, input_tx_dict in enumerate(tx_dict['inputs']):
            utxo_key = f"{input_tx_dict['transaction_id']}:{input_tx_dict['output_index']}"
            if utxo_key not in self.utxo:
                return False # Entrada não encontrada no conjunto UTXO

            utxo = self.utxo[utxo_key]
            total_input_value += utxo['amount']
            
            # A chave pública do dono da UTXO é o recipient_address da saída original
            public_key = utxo['recipient_address']
            signature = input_tx_dict['signature']
            if not Wallet.verify_signature(public_key, signature, tx_hash):
                return False

        total_output_value = sum(output['amount'] for output in tx_dict['outputs'])

        if total_input_value < total_output_value:
            return False # Valor de entrada insuficiente

        return True

    @staticmethod
    def hash(block):
        """
        Cria um hash SHA-256 de um bloco
        """
        # Precisamos garantir que o dicionário esteja ordenado ou teremos hashes inconsistentes
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    @property
    def last_block(self):
        return self.chain[-1]

    def proof_of_work(self, last_block):
        """
        Prova de Trabalho simples:
         - Encontre um número 'p' tal que o hash(pp') contenha 4 uns à esquerda
         - Onde p é a prova anterior, e p' é a nova prova
        """
        last_proof = last_block['proof']
        last_hash = self.hash(last_block)
        proof = 0
        while self.valid_proof(last_proof, proof, last_hash) is False:
            proof += 1

        return proof

    def valid_proof(self, last_proof, proof, last_hash):
        """
        Valida a prova: O hash(last_proof, proof, last_hash) contém a quantidade de uns à esquerda definida pela dificuldade?
        """
        guess = f'{last_proof}{proof}{last_hash}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:self.difficulty] == '1' * self.difficulty