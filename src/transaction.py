import json
import hashlib

class TxOutput:
    def __init__(self, recipient_address, amount):
        self.recipient_address = recipient_address
        self.amount = amount

    def to_dict(self):
        return {
            'recipient_address': self.recipient_address,
            'amount': self.amount,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(data['recipient_address'], data['amount'])

class TxInput:
    def __init__(self, transaction_id, output_index):
        self.transaction_id = transaction_id
        self.output_index = output_index
        self.signature = ""

    def to_dict(self):
        return {
            'transaction_id': self.transaction_id,
            'output_index': self.output_index,
            'signature': self.signature,
        }

    @classmethod
    def from_dict(cls, data):
        instance = cls(data['transaction_id'], data['output_index'])
        instance.signature = data.get('signature', '')
        return instance

class Transaction:
    def __init__(self, inputs, outputs):
        # inputs is a list of TxInput objects
        self.inputs = inputs
        # outputs is a list of TxOutput objects
        self.outputs = outputs
        self.id = self.calculate_hash()

    def to_dict(self):
        """
        Serializes the transaction to a dictionary.
        """
        return {
            'inputs': [i.to_dict() for i in self.inputs],
            'outputs': [o.to_dict() for o in self.outputs],
            'id': self.id
        }

    def calculate_hash(self):
        """
        Calculates the hash (ID) of the transaction.
        The hash is calculated over the inputs and outputs, without signatures.
        """
        tx_data_for_hashing = {
            'inputs': [
                {
                    'transaction_id': i.transaction_id,
                    'output_index': i.output_index,
                    'signature': ''
                } for i in self.inputs
            ],
            'outputs': [o.to_dict() for o in self.outputs],
        }
        tx_string = json.dumps(tx_data_for_hashing, sort_keys=True).encode()
        return hashlib.sha256(tx_string).hexdigest()