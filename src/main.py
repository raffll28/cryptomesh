import argparse
import json
import requests
from wallet import Wallet

def create_wallet():
    """Cria uma nova carteira e imprime as chaves pública e privada."""
    w = Wallet()
    w.create_keys()
    print("Carteira criada com sucesso!")
    print(f"Chave Privada: {w.private_key}")
    print(f"Chave Pública (Endereço): {w.public_key}")

def send(args):
    """Envia moedas para outro endereço a partir da carteira do nó."""
    payload = {
        'recipient_address': args.pubkey,
        'amount': args.amount,
    }

    try:
        # Envia a transação para o nó da blockchain
        response = requests.post(f"http://{args.host}:{args.port}/transactions/new", json=payload)
        response.raise_for_status()  # Lança uma exceção para respostas de erro (4xx ou 5xx)
        
        print("Requisição de transação enviada com sucesso!")
        print(json.dumps(response.json(), indent=2))

    except requests.exceptions.RequestException as e:
        print(f"Erro ao enviar a requisição de transação: {e}")

def mine(args):
    """Minera um novo bloco na blockchain."""
    try:
        response = requests.get(f"http://{args.host}:{args.port}/mine")
        response.raise_for_status()
        print("Bloco minerado com sucesso!")
        print(json.dumps(response.json(), indent=2))
    except requests.exceptions.RequestException as e:
        print(f"Erro ao minerar o bloco: {e}")

def print_chain(args):
    """Imprime a blockchain completa."""
    try:
        response = requests.get(f"http://{args.host}:{args.port}/chain")
        response.raise_for_status()
        print("Blockchain atual:")
        print(json.dumps(response.json(), indent=2))
    except requests.exceptions.RequestException as e:
        print(f"Erro ao obter a blockchain: {e}")

def balance(args):
    """Consulta o saldo de um endereço."""
    try:
        response = requests.get(f"http://{args.host}:{args.port}/balance/{args.address}")
        response.raise_for_status()
        print("Saldo consultado com sucesso!")
        print(json.dumps(response.json(), indent=2))
    except requests.exceptions.RequestException as e:
        print(f"Erro ao consultar o saldo: {e}")


def main():
    parser = argparse.ArgumentParser(description="CryptoMesh: uma CLI para interagir com a blockchain.")
    subparsers = parser.add_subparsers(dest='command', help='Comandos disponíveis')

    # Comando para criar uma carteira
    parser_create_wallet = subparsers.add_parser('create-wallet', help='Cria uma nova carteira.')
    parser_create_wallet.set_defaults(func=lambda args: create_wallet())

    # Comando para enviar moedas
    parser_send = subparsers.add_parser('send', help='Envia moedas para outro endereço a partir da carteira do nó.')
    parser_send.add_argument('pubkey', help='A chave pública (endereço) do destinatário.')
    parser_send.add_argument('amount', type=float, help='A quantidade de moedas a serem enviadas.')
    parser_send.add_argument('--host', default='localhost', help='O host do nó da blockchain.')
    parser_send.add_argument('--port', default=5000, type=int, help='A porta do nó da blockchain.')
    parser_send.set_defaults(func=send)

    # Comando para minerar um bloco
    parser_mine = subparsers.add_parser('mine', help='Minera um novo bloco.')
    parser_mine.add_argument('--host', default='localhost', help='O host do nó da blockchain.')
    parser_mine.add_argument('--port', default=5000, type=int, help='A porta do nó da blockchain.')
    parser_mine.set_defaults(func=mine)

    # Comando para imprimir a blockchain
    parser_print_chain = subparsers.add_parser('print-chain', help='Imprime a blockchain completa.')
    parser_print_chain.add_argument('--host', default='localhost', help='O host do nó da blockchain.')
    parser_print_chain.add_argument('--port', default=5000, type=int, help='A porta do nó da blockchain.')
    parser_print_chain.set_defaults(func=print_chain)

    # Comando para consultar o saldo
    parser_balance = subparsers.add_parser('balance', help='Consulta o saldo de um endereço.')
    parser_balance.add_argument('address', help='O endereço da carteira a ser consultado.')
    parser_balance.add_argument('--host', default='localhost', help='O host do nó da blockchain.')
    parser_balance.add_argument('--port', default=5000, type=int, help='A porta do nó da blockchain.')
    parser_balance.set_defaults(func=balance)

    args = parser.parse_args()

    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
