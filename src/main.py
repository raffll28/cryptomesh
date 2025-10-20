import json
import requests
import inquirer
from wallet import Wallet

# --- Funções de Interação com a API ---

def get_balance(host, port, address):
    try:
        response = requests.get(f"http://{host}:{port}/balance/{address}")
        response.raise_for_status()
        data = response.json()
        print(f"\nSaldo do endereço {data['address']}: {data['balance']}\n")
    except requests.exceptions.RequestException as e:
        print(f"\nErro ao consultar o saldo: {e}\n")

def send_transaction(host, port, pubkey, amount, fee):
    payload = {
        'recipient_address': pubkey,
        'amount': amount,
        'fee': fee,
    }
    try:
        response = requests.post(f"http://{host}:{port}/transactions/new", json=payload)
        response.raise_for_status()
        print("\nRequisição de transação enviada com sucesso!")
        print(json.dumps(response.json(), indent=2) + '\n')
    except requests.exceptions.RequestException as e:
        print(f"\nErro ao enviar a requisição de transação: {e}\n")

def mine_block(host, port):
    try:
        response = requests.get(f"http://{host}:{port}/mine")
        response.raise_for_status()
        print("\nBloco minerado com sucesso!")
        print(json.dumps(response.json(), indent=2) + '\n')
    except requests.exceptions.RequestException as e:
        print(f"\nErro ao minerar o bloco: {e}\n")

def print_chain(host, port):
    try:
        response = requests.get(f"http://{host}:{port}/chain")
        response.raise_for_status()
        print("\nBlockchain atual:")
        print(json.dumps(response.json(), indent=2) + '\n')
    except requests.exceptions.RequestException as e:
        print(f"\nErro ao obter a blockchain: {e}\n")

# --- Funções da CLI Interativa ---

def create_wallet_cli():
    questions = [
        inquirer.Text('node_id', message="Digite um nome para a carteira (deixe em branco para 'user_wallet')"),
    ]
    answers = inquirer.prompt(questions)
    node_id = answers['node_id'] if answers['node_id'] else 'user_wallet'
    w = Wallet(node_id=node_id)
    print(f"\nCarteira '{w.wallet_file}' criada/carregada com sucesso!")
    print(f"Chave Pública (Endereço): {w.public_key}\n")

def get_balance_cli(default_host, default_port):
    questions = [
        inquirer.Text('address', message="Endereço da carteira a ser consultado"),
        inquirer.Text('host', message="Host do nó", default=default_host),
        inquirer.Text('port', message="Porta do nó", default=str(default_port)),
    ]
    answers = inquirer.prompt(questions)
    get_balance(answers['host'], int(answers['port']), answers['address'])

def send_cli(default_host, default_port):
    questions = [
        inquirer.Text('pubkey', message="Chave pública (endereço) do destinatário"),
        inquirer.Text('amount', message="Quantidade a ser enviada"),
        inquirer.Text('fee', message="Taxa de transação", default='0.0'),
        inquirer.Text('host', message="Host do nó", default=default_host),
        inquirer.Text('port', message="Porta do nó", default=str(default_port)),
    ]
    answers = inquirer.prompt(questions)
    send_transaction(answers['host'], int(answers['port']), answers['pubkey'], float(answers['amount']), float(answers['fee']))

def mine_cli(default_host, default_port):
    questions = [
        inquirer.Text('host', message="Host do nó", default=default_host),
        inquirer.Text('port', message="Porta do nó", default=str(default_port)),
    ]
    answers = inquirer.prompt(questions)
    mine_block(answers['host'], int(answers['port']))

def print_chain_cli(default_host, default_port):
    questions = [
        inquirer.Text('host', message="Host do nó", default=default_host),
        inquirer.Text('port', message="Porta do nó", default=str(default_port)),
    ]
    answers = inquirer.prompt(questions)
    print_chain(answers['host'], int(answers['port']))

def main():
    default_host = 'localhost'
    default_port = 5000

    while True:
        questions = [
            inquirer.List('command',
                          message="O que você gostaria de fazer?",
                          choices=[
                              'Criar/Carregar uma carteira',
                              'Consultar saldo',
                              'Enviar moedas',
                              'Minerar um bloco',
                              'Imprimir a blockchain',
                              'Sair'
                          ]),
        ]
        answers = inquirer.prompt(questions)

        command = answers['command']

        if command == 'Criar/Carregar uma carteira':
            create_wallet_cli()
        elif command == 'Consultar saldo':
            get_balance_cli(default_host, default_port)
        elif command == 'Enviar moedas':
            send_cli(default_host, default_port)
        elif command == 'Minerar um bloco':
            mine_cli(default_host, default_port)
        elif command == 'Imprimir a blockchain':
            print_chain_cli(default_host, default_port)
        elif command == 'Sair':
            break

if __name__ == '__main__':
    main()