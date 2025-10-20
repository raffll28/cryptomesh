# CryptoMesh

Uma implementação de uma blockchain simples para fins educacionais.

---

## Plano de Melhorias da CLI e API

### 1. Corrigir o comando `send` na CLI [Concluído]

*   **Objetivo:** Alinhar o comando `send` da CLI com a lógica de transações UTXO da API.
*   **Passos:**
    *   Refatorar a função `send` em `src/main.py` para enviar apenas o endereço do destinatário e a quantia.
    *   Remover a necessidade de fornecer uma chave privada no lado do cliente para essa operação.
    *   Corrigir a função `create-wallet` que não estava gerando chaves.

### 2. Adicionar endpoint de saldo na API [Concluído]

*   **Objetivo:** Permitir a consulta de saldo de qualquer endereço.
*   **Passos:**
    *   Criar um endpoint `GET /balance/<address>` em `src/api.py`.
    *   A lógica deverá varrer o conjunto de UTXOs (`self.utxo`) para somar os valores pertencentes ao endereço.

### 3. Implementar comando de saldo na CLI [Concluído]

*   **Objetivo:** Expor a funcionalidade de consulta de saldo na CLI.
*   **Passos:**
    *   Adicionar um novo comando `balance <address>` em `src/main.py`.
    *   O comando deverá fazer uma requisição ao novo endpoint `/balance/<address>` da API.

### 4. Atualizar a documentação

*   **Objetivo:** Manter o `README.md` atualizado com as novas funcionalidades.
*   **Passos:**
    *   Detalhar os novos comandos da CLI.
    *   Documentar os novos endpoints da API.

---

## Plano de Evolução para o Modelo Bitcoin (Concluído)

Para tornar este projeto mais alinhado com a arquitetura de criptomoedas reais como o Bitcoin, propomos as seguintes melhorias, em ordem de implementação:

### 1. Implementar um Mempool de Transações [Concluído]

*   **Objetivo:** Criar uma "área de espera" para transações que foram recebidas mas ainda não foram incluídas em um bloco.

### 2. Mudar do Modelo "Pull" para "Push" (Broadcast) [Concluído]

*   **Objetivo:** Fazer com que transações e blocos recém-criados sejam ativamente propagados pela rede.

### 3. Implementar Ajuste de Dificuldade Dinâmico [Concluído]

*   **Objetivo:** Substituir a dificuldade fixa por uma que se ajuste periodicamente.

### 4. (Avançado) Introduzir o Modelo UTXO [Concluído]

*   **Objetivo:** Refatorar o sistema de transações para que ele se baseie em entradas (inputs) que consomem UTXOs e saídas (outputs) que criam novos UTXOs.