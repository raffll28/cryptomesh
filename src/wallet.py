from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
import Crypto.Random
import binascii

class Wallet:
    def __init__(self):
        """
        Initializes a new wallet with a private and public key pair.
        """
        self.private_key = None
        self.public_key = None

    def create_keys(self):
        """
        Generates a new private and public key pair.
        """
        private_key = RSA.generate(1024, Crypto.Random.new().read)
        public_key = private_key.publickey()
        self.private_key = binascii.hexlify(private_key.exportKey(format='DER')).decode('ascii')
        self.public_key = binascii.hexlify(public_key.exportKey(format='DER')).decode('ascii')

    def load_keys(self, private_key, public_key):
        """
        Loads a private and public key pair from strings.
        """
        self.private_key = private_key
        self.public_key = public_key

    def sign(self, private_key_hex, transaction_hash):
        """
        Signs a transaction hash with the private key.
        """
        private_key = RSA.importKey(binascii.unhexlify(private_key_hex))
        signer = pkcs1_15.new(private_key)
        h = SHA256.new(transaction_hash.encode('utf8'))
        return binascii.hexlify(signer.sign(h)).decode('ascii')

    @staticmethod
    def verify_signature(public_key_hex, signature, transaction_hash):
        """
        Verifies the signature of a transaction hash.
        """
        public_key = RSA.import_key(binascii.unhexlify(public_key_hex))
        verifier = pkcs1_15.new(public_key)
        h = SHA256.new(transaction_hash.encode('utf8'))
        try:
            verifier.verify(h, binascii.unhexlify(signature))
            return True
        except (ValueError, TypeError):
            return False

