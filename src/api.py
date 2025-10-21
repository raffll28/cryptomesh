from flask import Flask, jsonify, request, render_template
from blockchain import Blockchain
from wallet import Wallet
import json
from argparse import ArgumentParser
import requests

# Instancia o nosso nó
app = Flask(__name__, template_folder='templates')

# A instância da Blockchain será criada no main, com o arquivo de storage correto
blockchain = None
# A carteira do nó será criada no main, com o ID do nó (porta)
node_wallet = None
node_identifier = None

@app.route('/mine', methods=['GET'])
def mine():
    # Executamos o algoritmo de prova de trabalho para obter a próxima prova...
    last_block = blockchain.last_block
    proof = blockchain.proof_of_work(last_block)

    # Calcula o total de taxas das transações no mempool
    total_fees = sum(blockchain.get_transaction_fee(tx) for tx in blockchain.mempool)

    # Adiciona a transação de recompensa (coinbase), incluindo as taxas
    blockchain.new_coinbase_transaction(node_identifier, total_fees)

    # Forja o novo Bloco, adicionando-o à cadeia
    previous_hash = blockchain.hash(last_block)
    block = blockchain.new_block(proof, previous_hash)

    # Transmite o novo bloco para todos os nós da rede
    for node in blockchain.nodes:
        try:
            requests.post(f'http://{node}/blocks/receive', json=block)
        except requests.exceptions.ConnectionError:
            # Ignora nós que não estão respondendo
            pass

    response = {
        'message': "Novo bloco forjado e transmitido",
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
    }
    return jsonify(response), 200

@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = request.get_json()

    # Verifica se os campos obrigatórios estão nos dados postados
    required = ['recipient_address', 'amount']
    if not all(k in values for k in required):
        return 'Valores faltando: recipient_address, amount', 400

    fee = values.get('fee', 0.0)

    try:
        # Cria uma nova transação UTXO usando a carteira do nó
        tx = blockchain.new_utxo_transaction(node_wallet, values['recipient_address'], values['amount'], fee)
    except ValueError as e:
        return str(e), 400

    if tx is None:
        return 'Saldo insuficiente para a transação', 400

    # Transmite a nova transação para todos os nós da rede
    for node in blockchain.nodes:
        try:
            requests.post(f'http://{node}/transactions/receive', json=tx.to_dict())
        except requests.exceptions.ConnectionError:
            # Ignora nós que não estão respondendo
            pass

    response = {'message': f'Transação criada e transmitida.'}
    return jsonify(response), 201

@app.route('/transactions/receive', methods=['POST'])
def receive_transaction():
    tx_data = request.get_json()
    # TODO: Adicionar validação completa da transação recebida
    required = ['inputs', 'outputs', 'id']
    if not all(k in tx_data for k in required):
        return 'Valores faltando na transação recebida', 400

    if not blockchain.verify_transaction(tx_data):
        return 'Transação recebida inválida', 400

    blockchain.mempool.append(tx_data)
    
    response = {'message': f'Transação recebida e adicionada ao mempool.'}
    return jsonify(response), 201

@app.route('/blocks/receive', methods=['POST'])
def receive_block():
    block = request.get_json()
    if not block:
        return 'Bloco faltando', 400

    if blockchain.add_block(block):
        return jsonify({'message': 'Bloco recebido e adicionado à cadeia'}), 201
    
    return 'Bloco recebido inválido', 400

@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200

@app.route('/explorer', methods=['GET'])
def explorer():
    return render_template('explorer.html', chain=blockchain.chain)

@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    values = request.get_json()

    nodes = values.get('nodes')
    if nodes is None:
        return "Erro: Forneça uma lista de nós", 400

    for node in nodes:
        blockchain.register_node(node)

    response = {
        'message': 'Novos nós foram adicionados',
        'total_nodes': list(blockchain.nodes),
    }
    return jsonify(response), 201

@app.route('/nodes/resolve', methods=['GET'])
def consensus():
    replaced = blockchain.resolve_conflicts()

    if replaced:
        response = {
            'message': 'Nossa cadeia foi substituída',
            'new_chain': blockchain.chain
        }
    else:
        response = {
            'message': 'Nossa cadeia é autoritativa',
            'chain': blockchain.chain
        }

    return jsonify(response), 200

@app.route('/balance/<address>', methods=['GET'])
def get_balance(address):
    balance = blockchain.get_balance(address)
    response = {
        'address': address,
        'balance': balance,
    }
    return jsonify(response), 200

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
    parser.add_argument('--difficulty-interval', default=10, type=int, help='Intervalo de ajuste de dificuldade')
    parser.add_argument('--block-time', default=10, type=int, help='Tempo de geração de bloco em segundos')
    args = parser.parse_args()
    port = args.port

    # Instancia a blockchain com um arquivo de storage específico para esta porta
    storage_file = f'blockchain-{port}.json'
    blockchain = Blockchain(
        storage_path=storage_file,
        difficulty_adjustment_interval=args.difficulty_interval,
        block_generation_interval=args.block_time
    )

    # Cria a carteira para este nó, usando a porta como identificador
    node_wallet = Wallet(node_id=port)
    node_identifier = node_wallet.public_key

    print(f"Carteira do nó: {node_identifier}")

    app.run(host='0.0.0.0', port=port)
