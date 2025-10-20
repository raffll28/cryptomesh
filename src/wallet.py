from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
import Crypto.Random
import binascii
import os

class Wallet:
    def __init__(self, node_id):
        self.private_key = None
        self.public_key = None
        self.wallet_file = f'wallet-{node_id}.json'

        # Tenta carregar as chaves, se não conseguir, cria novas e salva
        if not self.load_keys():
            self.create_keys()
            self.save_keys()

    def create_keys(self):
        """
        Gera um novo par de chaves pública e privada de 2048 bits.
        """
        private_key = RSA.generate(2048, Crypto.Random.new().read)
        public_key = private_key.publickey()
        self.private_key = binascii.hexlify(private_key.exportKey(format='DER')).decode('ascii')
        self.public_key = binascii.hexlify(public_key.exportKey(format='DER')).decode('ascii')

    def save_keys(self):
        """
        Salva as chaves da carteira em um arquivo JSON.
        """
        if self.public_key and self.private_key:
            try:
                with open(self.wallet_file, 'w') as f:
                    f.write(f'{self.public_key}\n{self.private_key}')
                return True
            except Exception as e:
                print(f"Erro ao salvar a carteira: {e}")
                return False

    def load_keys(self):
        """
        Carrega as chaves da carteira de um arquivo.
        """
        if os.path.exists(self.wallet_file):
            try:
                with open(self.wallet_file, 'r') as f:
                    keys = f.readlines()
                    self.public_key = keys[0].strip()
                    self.private_key = keys[1].strip()
                return True
            except Exception as e:
                print(f"Erro ao carregar a carteira: {e}")
                return False
        return False

    def sign(self, private_key_hex, transaction_hash):
        """
        Assina um hash de transação com a chave privada.
        """
        private_key = RSA.importKey(binascii.unhexlify(private_key_hex))
        signer = pkcs1_15.new(private_key)
        h = SHA256.new(transaction_hash.encode('utf8'))
        return binascii.hexlify(signer.sign(h)).decode('ascii')

    @staticmethod
    def verify_signature(public_key_hex, signature, transaction_hash):
        """
        Verifica a assinatura de um hash de transação.
        """
        public_key = RSA.import_key(binascii.unhexlify(public_key_hex))
        verifier = pkcs1_15.new(public_key)
        h = SHA256.new(transaction_hash.encode('utf8'))
        try:
            verifier.verify(h, binascii.unhexlify(signature))
            return True
        except (ValueError, TypeError):
            return False