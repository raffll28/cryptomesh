from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
import binascii

class Wallet:
    def __init__(self):
        """
        Cria uma nova carteira com um par de chaves RSA.
        """
        self._private_key = RSA.generate(1024)
        self._public_key = self._private_key.publickey()

    @property
    def public_key(self):
        """
        Retorna a chave pública em formato hexadecimal.
        """
        return binascii.hexlify(self._public_key.export_key(format='DER')).decode('ascii')

    @property
    def private_key(self):
        """
        Retorna a chave privada em formato hexadecimal (apenas para fins de demonstração).
        EM UM SISTEMA REAL, NUNCA EXPONHA A CHAVE PRIVADA.
        """
        return binascii.hexlify(self._private_key.export_key(format='DER')).decode('ascii')

    def sign(self, data):
        """
        Assina os dados fornecidos com a chave privada.
        """
        h = SHA256.new(str(data).encode('utf8'))
        signer = pkcs1_15.new(self._private_key)
        signature = signer.sign(h)
        return binascii.hexlify(signature).decode('ascii')

    @staticmethod
    def verify(public_key_hex, data, signature_hex):
        """
        Verifica a assinatura com a chave pública.
        """
        try:
            public_key = RSA.import_key(binascii.unhexlify(public_key_hex))
            h = SHA256.new(str(data).encode('utf8'))
            verifier = pkcs1_15.new(public_key)
            verifier.verify(h, binascii.unhexlify(signature_hex))
            return True
        except (ValueError, TypeError):
            return False



w = Wallet()
print(w.private_key)
print()
print(w.public_key)


