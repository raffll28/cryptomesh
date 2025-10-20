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

### `send <destinatário> <quantia>`

Cria e propaga uma transação a partir da carteira do nó para o endereço de um destinatário.

```bash
python src/main.py send <chave_publica_destinatario> <quantia>
```

### `balance <endereço>`

Consulta o saldo de uma carteira específica.

```bash
python src/main.py balance <chave_publica>
```

### `mine`

Minera um novo bloco, incluindo as transações do mempool.

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

Minera um novo bloco e o adiciona à cadeia.

### `POST /transactions/new`

Adiciona uma nova transação ao mempool.

*   **Body (JSON):**
    ```json
    {
     "recipient_address": "...",
     "amount": 0.5
    }
    ```

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

---

## Plano de Evolução para o Modelo Bitcoin (Concluído)

Esta seção documenta as melhorias que foram implementadas para alinhar o projeto com a arquitetura de criptomoedas como o Bitcoin.

### 1. Implementar um Mempool de Transações [Concluído]

*   **Objetivo:** Criar uma "área de espera" para transações que foram recebidas mas ainda não foram incluídas em um bloco.

### 2. Mudar do Modelo "Pull" para "Push" (Broadcast) [Concluído]

*   **Objetivo:** Fazer com que transações e blocos recém-criados sejam ativamente propagados pela rede.

### 3. Implementar Ajuste de Dificuldade Dinâmico [Concluído]

*   **Objetivo:** Substituir a dificuldade fixa por uma que se ajuste periodicamente.

### 4. (Avançado) Introduzir o Modelo UTXO [Concluído]

*   **Objetivo:** Refatorar o sistema de transações para que ele se baseie em entradas (inputs) que consomem UTXOs e saídas (outputs) que criam novos UTXOs.