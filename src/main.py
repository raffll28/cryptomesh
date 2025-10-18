import argparse
import json
import requests
from wallet import Wallet

def create_wallet():
    """Cria uma nova carteira e imprime as chaves pública e privada."""
    w = Wallet()
    print("Carteira criada com sucesso!")
    print(f"Chave Privada: {w.private_key}")
    print(f"Chave Pública (Endereço): {w.public_key}")

def send(args):
    """Envia moedas de uma carteira para outra."""
    try:
        # Carrega a carteira do remetente a partir da chave privada
        sender_wallet = Wallet(private_key_hex=args.privkey)
    except (ValueError, TypeError):
        print("Erro: Chave privada inválida.")
        return

    transaction_data = {
        'sender': sender_wallet.public_key,
        'recipient': args.pubkey,
        'amount': args.amount,
    }

    # Assina a transação
    signature = sender_wallet.sign(transaction_data)

    # Prepara o payload para a API
    payload = {
        'sender': sender_wallet.public_key,
        'recipient': args.pubkey,
        'amount': args.amount,
        'signature': signature,
    }

    try:
        # Envia a transação para o nó da blockchain
        response = requests.post(f"http://{args.host}:{args.port}/transactions/new", json=payload)
        response.raise_for_status()  # Lança uma exceção para respostas de erro (4xx ou 5xx)
        
        print("Transação enviada com sucesso!")
        print(response.json())

    except requests.exceptions.RequestException as e:
        print(f"Erro ao enviar a transação: {e}")

def main():
    parser = argparse.ArgumentParser(description="CryptoMesh: uma CLI para interagir com a blockchain.")
    subparsers = parser.add_subparsers(dest='command', help='Comandos disponíveis')

    # Comando para criar uma carteira
    parser_create_wallet = subparsers.add_parser('create-wallet', help='Cria uma nova carteira.')
    parser_create_wallet.set_defaults(func=lambda args: create_wallet())

    # Comando para enviar moedas
    parser_send = subparsers.add_parser('send', help='Envia moedas para outro endereço.')
    parser_send.add_argument('--privkey', required=True, help='A chave privada da carteira do remetente.')
    parser_send.add_argument('--pubkey', required=True, help='A chave pública (endereço) do destinatário.')
    parser_send.add_argument('--amount', required=True, type=float, help='A quantidade de moedas a serem enviadas.')
    parser_send.add_argument('--host', default='localhost', help='O host do nó da blockchain.')
    parser_send.add_argument('--port', default=5000, type=int, help='A porta do nó da blockchain.')
    parser_send.set_defaults(func=send)

    # TODO: Adicionar outros comandos (mine, print-chain)

    args = parser.parse_args()

    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()