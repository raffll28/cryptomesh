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

### **Plano de Implementação: Taxas de Transação**

Para introduzir um sistema de taxas de transação (transaction fees) similar ao do Bitcoin, seguiremos os seguintes passos:

#### **Passo 1: Modificar a Lógica de Transação para Incluir Taxas [Concluído]**

*   **Objetivo:** Permitir que uma transação tenha uma "sobra" de valor que não é gasta nem volta como troco, representando a taxa.
*   **Ações:**
    1.  **Atualizar a CLI:** Modificar o comando `send` em `src/main.py` para aceitar um novo argumento opcional, `--fee`.
    2.  **Atualizar a API:** O endpoint `/transactions/new` em `src/api.py` precisará aceitar um campo `fee` no corpo da requisição.
    3.  **Ajustar o Core:** O método `new_utxo_transaction` em `src/blockchain.py` será o principal afetado. Ele precisará garantir que `valor_total_dos_inputs >= valor_a_enviar + taxa`. O valor do troco será `valor_total_dos_inputs - valor_a_enviar - taxa`.

#### **Passo 2: Coletar as Taxas durante a Mineração [Concluído]**

*   **Objetivo:** Recompensar o minerador com a soma das taxas de todas as transações que ele incluir em um novo bloco.
*   **Ações:**
    1.  **Atualizar a Mineração:** No endpoint `/mine` em `src/api.py`, antes de criar a transação de recompensa (*coinbase*), o código precisará varrer todas as transações do `mempool` que serão adicionadas ao bloco.
    2.  **Calcular Taxa Total:** Para cada transação, o método calculará a taxa (soma dos inputs - soma dos outputs). A soma de todas essas taxas será o prêmio do minerador.
    3.  **Atualizar Recompensa:** O valor total das taxas será somado à recompensa fixa do bloco (que hoje é 1) na transação de *coinbase*.

#### **Passo 3: Atualizar a Validação e a Documentação**

*   **Objetivo:** Garantir que a rede valide corretamente as transações com taxas e que a nova funcionalidade esteja documentada.
*   **Ações:**
    1.  **Revisar Validação:** O método `verify_transaction` já deve, implicitamente, suportar taxas (ele já checa se `input >= output`), mas vamos revisar para ter certeza.
    2.  **Atualizar `README.md`:** Documentar o novo argumento `--fee` no comando `send` e o novo campo na API.