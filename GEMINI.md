# GEMINI.md

## Visão Geral do Projeto

Este projeto é uma implementação de uma blockchain simples em Python para fins educacionais. Ele demonstra os conceitos fundamentais de uma criptomoeda, incluindo blocos, cadeias, transações, prova de trabalho (Proof of Work) e consenso.

O projeto utiliza as seguintes tecnologias:

*   **Python:** Linguagem de programação principal.
*   **Flask:** Para expor a blockchain como uma API RESTful.
*   **PyCryptodome:** Para a geração de carteiras e assinaturas digitais.

## Ambiente de Desenvolvimento

Para configurar o ambiente de desenvolvimento, siga os passos abaixo. Estas instruções são baseadas em um ambiente WSL2 (Windows Subsystem for Linux) e o uso de um ambiente virtual (`venv`).

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

A arquitetura consiste em:

*   `blockchain.py`: A classe principal que implementa a lógica da blockchain.
*   `api.py`: Uma API Flask que permite a interação com a blockchain (mineração, novas transações, etc.).
*   `wallet.py`: Uma classe que gerencia carteiras com chaves pública e privada.
*   `main.py`: Uma interface de linha de comando (CLI) para interagir com a blockchain.

## Construindo e Executando

### Dependências

O projeto utiliza um arquivo `requirements.txt` para gerenciar suas dependências. Para instalar as dependências, execute:

```bash
pip install -r requirements.txt
```

As principais dependências são:

*   `flask`: Para a API RESTful.
*   `requests`: Para comunicação entre os nós.
*   `pycryptodome`: Para criptografia.

### Executando a API

Para iniciar o nó da blockchain e a API, execute o seguinte comando:

```bash
python3 src/api.py
```

Por padrão, a API será executada em `http://localhost:5000`. Você pode especificar uma porta diferente usando o argumento `--port` ou `-p`:

```bash
python3 src/api.py -p 5001
```

### Endpoints da API

*   `GET /mine`: Minera um novo bloco.
*   `POST /transactions/new`: Adiciona uma nova transação.
*   `GET /chain`: Retorna a blockchain completa.
*   `POST /nodes/register`: Registra um novo nó na rede.
*   `GET /nodes/resolve`: Executa o algoritmo de consenso para resolver conflitos.
*   `GET /balance/<address>`: Retorna o saldo de um endereço.

### Utilizando a CLI (`main.py`)

O arquivo `main.py` é uma interface de linha de comando que permite interagir com um nó da blockchain.

**Comandos disponíveis:**

*   `create-wallet`: Cria uma nova carteira com um par de chaves pública/privada.
    ```bash
    python3 src/main.py create-wallet
    ```

*   `send`: Envia moedas da carteira do nó para outro endereço.
    ```bash
    python3 src/main.py send <ENDEREÇO_DESTINATÁRIO> <QUANTIA> --fee <TAXA>
    ```

*   `mine`: Solicita ao nó que minere um novo bloco.
    ```bash
    python3 src/main.py mine
    ```

*   `print-chain`: Exibe a cadeia de blocos completa do nó.
    ```bash
    python3 src/main.py print-chain
    ```

*   `balance`: Consulta o saldo de um endereço específico.
    ```bash
    python3 src/main.py balance <ENDEREÇO>
    ```

Você pode especificar o host e a porta do nó para cada comando (o padrão é `localhost:5000`), por exemplo:

```bash
python3 src/main.py mine --host localhost --port 5001
```

## Convenções de Desenvolvimento

*   **Estilo de Código:** O código segue as convenções do PEP 8 para formatação de código Python.
*   **Estrutura do Projeto:** O código-fonte está localizado no diretório `src`.
*   **Persistência:** A blockchain de cada nó é persistida em um arquivo JSON (ex: `blockchain-5000.json`), nomeado de acordo com a porta em que o nó está sendo executado.

## Regras de Workflow

*   Ao final de cada passo do plano, devo ajustar o README.md para marcar o passo como concluído e depois fazer o commit das mudanças.
*   Antes de fazer o commit, devo executar os testes unitários para verificar as mudanças.