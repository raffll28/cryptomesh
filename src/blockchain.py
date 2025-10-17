import time
import json
import hashlib
from urllib.parse import urlparse
import requests

class Blockchain:
    def __init__(self, storage_path='blockchain.json'):
        self.storage_path = storage_path
        self.chain = []
        self.current_transactions = []
        self.nodes = set()

        self.load_chain()

    def load_chain(self):
        try:
            with open(self.storage_path, 'r') as f:
                self.chain = json.load(f)
            if not self.chain:
                # Se o arquivo estiver vazio, cria o bloco gênese
                self.new_block(previous_hash='1', proof=100)
        except (FileNotFoundError, json.JSONDecodeError):
            # Se o arquivo não existir ou for inválido, cria o bloco gênese
            self.new_block(previous_hash='1', proof=100)

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
            if not self.valid_proof(last_block['proof'], block['proof']):
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
            return True

        return False

    def new_block(self, proof, previous_hash=None):
        """
        Cria um novo bloco e o adiciona à blockchain
        """
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time.time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
        }

        # Reseta a lista de transações atuais
        self.current_transactions = []

        self.chain.append(block)
        self.save_chain() # Salva a cadeia após adicionar um novo bloco
        return block

    def new_transaction(self, sender, recipient, amount):
        """
        Adiciona uma nova transação à lista de transações
        """
        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
        })

        return self.last_block['index'] + 1

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

    def proof_of_work(self, last_proof):
        """
        Prova de Trabalho simples:
         - Encontre um número 'p' tal que o hash(pp') contenha 4 zeros à esquerda
         - Onde p é a prova anterior, e p' é a nova prova
        """
        proof = 0
        while self.valid_proof(last_proof, proof) is False:
            proof += 1

        return proof

    @staticmethod
    def valid_proof(last_proof, proof):
        """
        Valida a prova: O hash(last_proof, proof) contém o prefixo '101'?
        """
        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:3] == "101"