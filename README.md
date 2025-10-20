# CryptoMesh

Uma implementação de uma blockchain simples em Python para fins educacionais, demonstrando conceitos como Prova de Trabalho (Proof of Work), transações, consenso e uma API RESTful para interação.

---

## Funcionalidades

*   **Prova de Trabalho (Proof of Work):** Algoritmo de consenso para proteger a rede.
*   **Transações UTXO:** Modelo de transações não gastas (Unspent Transaction Output).
*   **API RESTful com Flask:** Permite a interação com a blockchain via HTTP.
*   **CLI Interativa:** Uma interface de linha de comando amigável para interagir com a blockchain.
*   **Blockchain Explorer:** Uma interface web simples para visualizar a cadeia de blocos.
*   **Gerenciamento de Carteira:** Criação e armazenamento de carteiras com pares de chaves pública/privada.
*   **Rede Descentralizada:** Suporte para múltiplos nós e resolução de conflitos.

---

## Como Executar

### Pré-requisitos

*   Python 3.8+
*   Ambiente virtual (`venv`)

### Configuração do Ambiente

1.  **Clone o repositório:**
    ```bash
    git clone <URL_DO_REPOSITORIO>
    cd cryptomesh
    ```

2.  **Crie e ative um ambiente virtual:**
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```

3.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```

### Executando um Nó da Blockchain

Para iniciar um nó da API, execute o seguinte comando:

```bash
python3 src/api.py -p 5000
```

*   O argumento `-p` ou `--port` define a porta em que o nó será executado.
*   Você pode iniciar múltiplos nós em portas diferentes para simular uma rede.

---

## CLI Interativa

A maneira mais fácil de interagir com a blockchain é através da CLI interativa. Para iniciá-la, execute:

```bash
python3 src/main.py
```

Você verá um menu com as seguintes opções:

*   **Criar/Carregar uma carteira:** Cria um novo par de chaves (pública e privada) e o salva em um arquivo `wallet-<nome>.json`.
*   **Consultar saldo:** Verifica o saldo de um endereço específico.
*   **Enviar moedas:** Cria e propaga uma transação para outro endereço.
*   **Minerar um bloco:** Inicia o processo de mineração de um novo bloco.
*   **Imprimir a blockchain:** Exibe a cadeia de blocos completa do nó conectado.
*   **Sair:** Encerra a CLI.

---

## Blockchain Explorer

Cada nó possui um explorador de blockchain integrado. Para acessá-lo, abra o seu navegador e vá para:

```
http://<HOST_DO_NO>:<PORTA_DO_NO>/explorer
```

Por exemplo: `http://localhost:5000/explorer`.

---

## Endpoints da API

A API RESTful fornece os seguintes endpoints para interação programática:

*   `GET /mine`: Minera um novo bloco.
*   `POST /transactions/new`: Adiciona uma nova transação.
*   `GET /chain`: Retorna a cadeia de blocos completa.
*   `GET /balance/<address>`: Retorna o saldo de um endereço.
*   `POST /nodes/register`: Registra um ou mais nós na rede.
*   `GET /nodes/resolve`: Executa o algoritmo de consenso.

Para mais detalhes sobre cada endpoint, consulte o arquivo `GEMINI.md`.
