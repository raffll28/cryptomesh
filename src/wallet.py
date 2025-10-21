from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
from Crypto.Cipher import AES
from Crypto import Random
import Crypto.Random
import binascii
import os
from getpass import getpass
from Crypto.Protocol.KDF import PBKDF2
from base64 import b64encode, b64decode

class Wallet:
    def __init__(self, node_id, password=None):
        self.private_key = None
        self.public_key = None
        self.wallet_file = f'wallet-{node_id}.json'
        self.password = password

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
            if not self.password:
                self.password = getpass("Digite uma senha para sua carteira: ")
                if not self.password:
                    print("Erro: Senha não pode ser vazia.")
                    return False

            try:
                salt = Random.get_random_bytes(16)
                key = PBKDF2(self.password.encode('utf-8'), salt, dkLen=32)
                cipher = AES.new(key, AES.MODE_EAX)
                nonce = cipher.nonce
                ciphertext, tag = cipher.encrypt_and_digest(self.private_key.encode('ascii'))

                with open(self.wallet_file, 'w') as f:
                    f.write(f'{self.public_key}\n')
                    f.write(f'{b64encode(salt).decode('utf-8')}\n')
                    f.write(f'{b64encode(nonce).decode('utf-8')}\n')
                    f.write(f'{b64encode(ciphertext).decode('utf-8')}\n')
                    f.write(f'{b64encode(tag).decode('utf-8')}')
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
                    lines = f.readlines()
                    self.public_key = lines[0].strip()
                    salt = b64decode(lines[1].strip())
                    nonce = b64decode(lines[2].strip())
                    ciphertext = b64decode(lines[3].strip())
                    tag = b64decode(lines[4].strip())

                if not self.password:
                    self.password = getpass("Digite a senha da sua carteira: ")

                key = PBKDF2(self.password.encode('utf-8'), salt, dkLen=32)
                cipher = AES.new(key, AES.MODE_EAX, nonce=nonce)
                private_key_bytes = cipher.decrypt_and_verify(ciphertext, tag)
                self.private_key = private_key_bytes.decode('ascii')
                return True
            except ValueError:
                print("Erro: Senha incorreta ou arquivo de carteira corrompido.")
                return False
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

    @staticmethod
    def is_valid_address(address):
        """Verifica se um endereço (chave pública) é válido."""
        try:
            RSA.import_key(binascii.unhexlify(address))
            return True
        except (ValueError, TypeError, binascii.Error):
            return False