import unittest
import requests
import subprocess
import time
import os

class TestAPI(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.api_process = subprocess.Popen(["/home/racaz/gits/cryptomesh/.venv/bin/python", "src/api.py", "-p", "5001"])
        time.sleep(2) # Dá tempo para a API iniciar

    @classmethod
    def tearDownClass(cls):
        cls.api_process.terminate()
        cls.api_process.wait()
        # Limpa os arquivos de teste
        if os.path.exists("blockchain-5001.json"):
            os.remove("blockchain-5001.json")
        if os.path.exists("wallet-5001.json"):
            os.remove("wallet-5001.json")
        if os.path.exists("wallet-user_wallet.json"):
            os.remove("wallet-user_wallet.json")

    def setUp(self):
        self.base_url = "http://localhost:5001"

    def test_01_api_is_running(self):
        try:
            response = requests.get(f"{self.base_url}/chain")
            self.assertEqual(response.status_code, 200)
        except requests.exceptions.ConnectionError:
            self.fail("API is not running.")

    def test_02_create_wallet(self):
        """Testa a criação de uma carteira de usuário."""
        command = ["/home/racaz/gits/cryptomesh/.venv/bin/python", "src/main.py", "create-wallet"]
        result = subprocess.run(command, capture_output=True, text=True)
        self.assertIn("criada/carregada com sucesso", result.stdout)
        self.assertTrue(os.path.exists("wallet-user_wallet.json"))

    def test_03_mine_block(self):
        """Testa a mineração de um bloco."""
        response = requests.get(f"{self.base_url}/mine")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['index'], 2) # O segundo bloco (o primeiro é o genesis)

    def test_04_send_transaction(self):
        """Testa o envio de uma transação."""
        # Pega o endereço da carteira do usuário
        with open("wallet-user_wallet.json", 'r') as f:
            user_pub_key = f.readline().strip()

        payload = {
            "recipient_address": user_pub_key,
            "amount": 0.5,
        }
        response = requests.post(f"{self.base_url}/transactions/new", json=payload)
        self.assertEqual(response.status_code, 201)

        # Minera um bloco para confirmar a transação
        mine_response = requests.get(f"{self.base_url}/mine")
        self.assertEqual(mine_response.status_code, 200)
        self.assertEqual(mine_response.json()['index'], 3)

    def test_05_check_balance(self):
        """Testa a consulta de saldo."""
        # Pega o endereço da carteira do usuário
        with open("wallet-user_wallet.json", 'r') as f:
            user_pub_key = f.readline().strip()

        response = requests.get(f"{self.base_url}/balance/{user_pub_key}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['balance'], 0.5)

    def test_06_print_chain(self):
        """Testa a impressão da blockchain."""
        response = requests.get(f"{self.base_url}/chain")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()['chain']), 3)

if __name__ == '__main__':
    unittest.main()