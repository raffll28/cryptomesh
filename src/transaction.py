import json
import hashlib
from dataclasses import dataclass, asdict
from typing import List

@dataclass(frozen=True)
class TxOutput:
    recipient_address: str
    amount: float

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, data):
        return cls(data['recipient_address'], data['amount'])

@dataclass(frozen=True)
class TxInput:
    transaction_id: str
    output_index: int
    signature: str = ""

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, data):
        return cls(data['transaction_id'], data['output_index'], data.get('signature', ''))

@dataclass(frozen=True)
class Transaction:
    inputs: List[TxInput]
    outputs: List[TxOutput]
    id: str

    def __init__(self, inputs: List[TxInput], outputs: List[TxOutput]):
        object.__setattr__(self, 'inputs', inputs)
        object.__setattr__(self, 'outputs', outputs)
        object.__setattr__(self, 'id', self.calculate_hash())

    def to_dict(self):
        return {
            'inputs': [i.to_dict() for i in self.inputs],
            'outputs': [o.to_dict() for o in self.outputs],
            'id': self.id
        }

    def calculate_hash(self):
        """
        Calcula o hash (ID) da transação.
        O hash é calculado sobre as entradas (sem assinatura) e saídas.
        """
        tx_data = {
            'inputs': [{k: v for k, v in i.to_dict().items() if k != 'signature'} for i in self.inputs],
            'outputs': [o.to_dict() for o in self.outputs],
        }
        tx_string = json.dumps(tx_data, sort_keys=True).encode()
        return hashlib.sha256(tx_string).hexdigest()