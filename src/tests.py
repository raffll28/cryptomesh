import unittest
import requests
import subprocess
import time
import os
import sys
from wallet import Wallet

api_process_1 = None
api_process_2 = None

def setUpModule():
    global api_process_1, api_process_2
    # Inicia duas instâncias da API em portas diferentes
    # Usamos sys.executable para portabilidade e preexec_fn para rodar em um novo grupo de processos
    api_process_1 = subprocess.Popen([sys.executable, "src/api.py", "-p", "5001", "--wallet-password", "test_password"], preexec_fn=os.setsid)
    api_process_2 = subprocess.Popen([sys.executable, "src/api.py", "-p", "5002", "--wallet-password", "test_password"], preexec_fn=os.setsid)
    time.sleep(5) # Dá mais tempo para as APIs iniciarem

def tearDownModule():
    # Termina os processos da API
    if api_process_1 and api_process_1.poll() is None:
        os.killpg(os.getpgid(api_process_1.pid), 15) # SIGTERM
        api_process_1.wait()
    if api_process_2 and api_process_2.poll() is None:
        os.killpg(os.getpgid(api_process_2.pid), 15) # SIGTERM
        api_process_2.wait()

    # Limpa os arquivos de teste
    for port in [5001, 5002]:
        if os.path.exists(f"blockchain-{port}.json"):
            os.remove(f"blockchain-{port}.json")
        if os.path.exists(f"wallet-{port}.json"):
            os.remove(f"wallet-{port}.json")
    if os.path.exists("wallet-user_wallet.json"):
        os.remove("wallet-user_wallet.json")

class TestBlockchain(unittest.TestCase):

    def setUp(self):
        self.base_url_1 = "http://localhost:5001"
        self.base_url_2 = "http://localhost:5002"

    def test_01_api_is_running(self):
        """Verifica se ambas as APIs estão respondendo."""
        try:
            response1 = requests.get(f"{self.base_url_1}/chain")
            self.assertEqual(response1.status_code, 200)
            response2 = requests.get(f"{self.base_url_2}/chain")
            self.assertEqual(response2.status_code, 200)
        except requests.exceptions.ConnectionError as e:
            self.fail(f"API não está respondendo: {e}")

    def test_02_create_wallet(self):
        """Testa a criação de uma carteira de usuário."""
        w = Wallet(node_id="user_wallet", password="test_password")
        self.assertTrue(os.path.exists("wallet-user_wallet.json"))
        # Verifica se a chave pública foi carregada corretamente
        self.assertIsNotNone(w.public_key)

    def test_03_mine_block(self):
        """Testa a mineração de um bloco no nó 1."""
        response = requests.get(f"{self.base_url_1}/mine")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['index'], 2)

    def test_04_send_transaction(self):
        """Testa o envio de uma transação do nó 1 para um usuário."""
        with open("wallet-user_wallet.json", 'r') as f:
            # A chave pública é a primeira linha do arquivo
            user_pub_key = f.readline().strip()

        payload = {"recipient_address": user_pub_key, "amount": 0.5}
        response = requests.post(f"{self.base_url_1}/transactions/new", json=payload)
        self.assertEqual(response.status_code, 201)

        mine_response = requests.get(f"{self.base_url_1}/mine")
        self.assertEqual(mine_response.status_code, 200)
        self.assertEqual(mine_response.json()['index'], 3)

    def test_05_check_balance(self):
        """Testa a consulta de saldo do usuário no nó 1."""
        with open("wallet-user_wallet.json", 'r') as f:
            user_pub_key = f.readline().strip()

        response = requests.get(f"{self.base_url_1}/balance/{user_pub_key}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['balance'], 0.5)

    def test_06_resolve_conflicts(self):
        """Testa o algoritmo de consenso para resolver conflitos."""
        # 1. Registra o nó 2 no nó 1
        payload = {"nodes": [self.base_url_2]}
        response = requests.post(f"{self.base_url_1}/nodes/register", json=payload)
        self.assertEqual(response.status_code, 201)

        # 2. Minera 3 blocos no nó 2 para torná-lo a cadeia mais longa
        for i in range(3):
            requests.get(f"{self.base_url_2}/mine")

        # 3. Executa o consenso no nó 1
        resolve_response = requests.get(f"{self.base_url_1}/nodes/resolve")
        self.assertEqual(resolve_response.status_code, 200)
        self.assertEqual(resolve_response.json()['message'], 'Nossa cadeia foi substituída')

        # 4. Verifica se a cadeia do nó 1 foi atualizada
        chain_response = requests.get(f"{self.base_url_1}/chain")
        self.assertEqual(len(chain_response.json()['chain']), 4) # 1 genesis + 3 minerados no nó 2

    def test_07_insufficient_balance(self):
        """Testa o envio de uma transação com saldo insuficiente."""
        with open("wallet-user_wallet.json", 'r') as f:
            user_pub_key = f.readline().strip()

        payload = {"recipient_address": user_pub_key, "amount": 9999}
        response = requests.post(f"{self.base_url_1}/transactions/new", json=payload)
        self.assertEqual(response.status_code, 400)
        self.assertIn("Saldo insuficiente", response.text)

    def test_08_invalid_address(self):
        """Testa o envio de uma transação para um endereço inválido."""
        payload = {"recipient_address": "invalid_address", "amount": 0.1}
        response = requests.post(f"{self.base_url_1}/transactions/new", json=payload)
        self.assertEqual(response.status_code, 400)
        self.assertIn("Endereço do destinatário inválido", response.text)

if __name__ == '__main__':
    unittest.main()