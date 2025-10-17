from blockchain import Blockchain
import json

# Cria uma instância da nossa blockchain
bc = Blockchain()

print("Iniciando a mineração...")

# Pega a prova do último bloco
last_proof = bc.last_block['proof']

# Encontra a nova prova
proof = bc.proof_of_work(last_proof)

# Minera um novo bloco
# (Estamos passando um sender '0' para significar que este nó minerou uma nova moeda)
bc.new_transaction(
    sender="0",
    recipient="node-minerador-id", # Em um sistema real, seria o nosso ID
    amount=1,
)

# Cria o novo bloco
previous_hash = bc.hash(bc.last_block)
block = bc.new_block(proof, previous_hash)

print("Novo bloco minerado!")
print(json.dumps(bc.chain, indent=2))