# CryptoMesh

Uma implementação de uma blockchain simples para fins educacionais.

---

## Comandos da CLI

A interação com a blockchain pode ser feita através do `src/main.py`.

### `create-wallet`

Cria um novo par de chaves (privada e pública).

```bash
python src/main.py create-wallet
```

### `send <destinatário> <quantia> [--fee <taxa>]`

Cria e propaga uma transação a partir da carteira do nó para o endereço de um destinatário.

*   `--fee`: Define uma taxa opcional para a transação, incentivando os mineradores.

```bash
python src/main.py send <chave_publica_destinatario> <quantia> --fee 0.1
```

### `balance <endereço>`

Consulta o saldo de uma carteira específica.

```bash
python src/main.py balance <chave_publica>
```

### `mine`

Minera um novo bloco, incluindo as transações do mempool e coletando as taxas.

```bash
python src/main.py mine
```

### `print-chain`

Exibe a cadeia de blocos completa.

```bash
python src/main.py print-chain
```

---

## Endpoints da API

A API é executada com `python src/api.py` e fornece os seguintes endpoints:

### `GET /mine`

Minera um novo bloco, coleta as taxas de transação do mempool e o adiciona à cadeia.

### `POST /transactions/new`

Adiciona uma nova transação ao mempool.

*   **Body (JSON):**
    ```json
    {
     "recipient_address": "...",
     "amount": 0.5,
     "fee": 0.1
    }
    ```
    O campo `fee` é opcional.

### `GET /chain`

Retorna a cadeia de blocos completa.

### `GET /balance/<address>`

Retorna o saldo de um endereço específico.

### `POST /nodes/register`

Registra um ou mais nós na rede.

*   **Body (JSON):**
    ```json
    {
     "nodes": ["http://localhost:5001", "http://localhost:5002"]
    }
    ```

### `GET /nodes/resolve`

Executa o algoritmo de consenso para resolver conflitos na cadeia.

### `POST /transactions/receive`

Endpoint interno para receber transações de outros nós.

### `POST /blocks/receive`

Endpoint interno para receber blocos de outros nós.