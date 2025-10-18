from flask import Flask, jsonify, request
from blockchain import Blockchain
import json
from uuid import uuid4
from argparse import ArgumentParser
import requests

# Instancia o nosso nó
app = Flask(__name__)

# Gera um endereço globalmente único para este nó
node_identifier = str(uuid4()).replace('-', '')

# A instância da Blockchain será criada no main, com o arquivo de storage correto
blockchain = None

@app.route('/mine', methods=['GET'])
def mine():
    # Executamos o algoritmo de prova de trabalho para obter a próxima prova...
    last_block = blockchain.last_block
    last_proof = last_block['proof']
    proof = blockchain.proof_of_work(last_proof)

    # Somos recompensados por encontrar a prova, adicionando uma transação.
    # O remetente é "0" para significar que esta é uma nova moeda.
    blockchain.new_transaction(
        sender="0",
        recipient=node_identifier,
        amount=1,
        signature=""
    )

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
    required = ['sender', 'recipient', 'amount', 'signature']
    if not all(k in values for k in required):
        return 'Valores faltando', 400

    # Cria uma nova transação
    index = blockchain.new_transaction(values['sender'], values['recipient'], values['amount'], values['signature'])

    if not index:
        return 'Assinatura da transação é inválida', 400

    # Transmite a nova transação para todos os nós da rede
    for node in blockchain.nodes:
        try:
            requests.post(f'http://{node}/transactions/receive', json=values)
        except requests.exceptions.ConnectionError:
            # Ignora nós que não estão respondendo
            pass

    response = {'message': f'Transação adicionada e transmitida. Será incluída no Bloco {index}'}
    return jsonify(response), 201

@app.route('/transactions/receive', methods=['POST'])
def receive_transaction():
    values = request.get_json()
    # Verifica se os campos obrigatórios estão nos dados postados
    required = ['sender', 'recipient', 'amount', 'signature']
    if not all(k in values for k in required):
        return 'Valores faltando na transação recebida', 400

    # Adiciona a transação recebida ao mempool
    index = blockchain.new_transaction(values['sender'], values['recipient'], values['amount'], values['signature'])

    if not index:
        return 'Transação recebida inválida', 400

    response = {'message': f'Transação recebida e adicionada ao Bloco {index}'}
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

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port

    # Instancia a blockchain com um arquivo de storage específico para esta porta
    storage_file = f'blockchain-{port}.json'
    blockchain = Blockchain(storage_path=storage_file)

    app.run(host='0.0.0.0', port=port)
