# GEMINI.md

## Visão Geral do Projeto

Este projeto é uma implementação de uma blockchain simples em Python para fins educacionais. Ele demonstra os conceitos fundamentais de uma criptomoeda, incluindo blocos, cadeias, transações, prova de trabalho (Proof of Work) e consenso.

O projeto utiliza as seguintes tecnologias:

*   **Python:** Linguagem de programação principal.
*   **Flask:** Para expor a blockchain como uma API RESTful.
*   **PyCryptodome:** Para a geração de carteiras e assinaturas digitais.

A arquitetura consiste em:

*   `blockchain.py`: A classe principal que implementa a lógica da blockchain.
*   `api.py`: Uma API Flask que permite a interação com a blockchain (mineração, novas transações, etc.).
*   `wallet.py`: Uma classe que gerencia carteiras com chaves pública e privada.
*   `main.py`: Um script de exemplo para mineração de um bloco.

## Construindo e Executando

### Dependências

O projeto não possui um arquivo `requirements.txt`, mas as seguintes dependências podem ser inferidas do código-fonte:

*   `flask`
*   `requests`
*   `pycryptodome`

Você pode instalá-las usando `pip`:

```bash
pip install flask requests pycryptodome
```

### Executando a API

Para iniciar o nó da blockchain e a API, execute o seguinte comando:

```bash
python src/api.py
```

Por padrão, a API será executada em `http://localhost:5000`. Você pode especificar uma porta diferente usando o argumento `--port` ou `-p`:

```bash
python src/api.py -p 5001
```

### Endpoints da API

*   `GET /mine`: Minera um novo bloco.
*   `POST /transactions/new`: Adiciona uma nova transação.
*   `GET /chain`: Retorna a blockchain completa.
*   `POST /nodes/register`: Registra um novo nó na rede.
*   `GET /nodes/resolve`: Executa o algoritmo de consenso para resolver conflitos.

### Executando o script de mineração de exemplo

O arquivo `main.py` é um script simples que minera um bloco e o imprime no console. Para executá-lo:

```bash
python src/main.py
```

## Convenções de Desenvolvimento

*   **Estilo de Código:** O código segue as convenções do PEP 8 para formatação de código Python.
*   **Estrutura do Projeto:** O código-fonte está localizado no diretório `src`.
*   **Persistência:** A blockchain de cada nó é persistida em um arquivo JSON (ex: `blockchain-5000.json`), nomeado de acordo com a porta em que o nó está sendo executado.

## Regras de Workflow

*   Ao final de cada passo do plano, devo ajustar o README.md para marcar o passo como concluído e depois fazer o commit das mudanças.