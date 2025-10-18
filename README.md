# CryptoMesh

Uma implementação de uma blockchain simples para fins educacionais.

---

## Plano de Evolução para o Modelo Bitcoin

Para tornar este projeto mais alinhado com a arquitetura de criptomoedas reais como o Bitcoin, propomos as seguintes melhorias, em ordem de implementação:

### 1. Implementar um Mempool de Transações [Concluído]

Atualmente, as transações são adicionadas diretamente à lista `current_transactions` e incluídas no próximo bloco minerado por um nó. Vamos mudar isso para um modelo de "mempool" (memory pool).

*   **Objetivo:** Criar uma "área de espera" para transações que foram recebidas mas ainda não foram incluídas em um bloco.
*   **Passos:**
    *   Substituir a lista `self.current_transactions` por `self.mempool`.
    *   O endpoint `/transactions/new` adicionará novas transações ao `mempool`.
    *   Quando o endpoint `/mine` for chamado, o nó selecionará um conjunto de transações do `mempool` para incluir no novo bloco.

### 2. Mudar do Modelo "Pull" para "Push" (Broadcast) [Concluído]

O consenso no Bitcoin não acontece com um nó pedindo a cadeia dos outros (`/nodes/resolve`), mas sim com nós "empurrando" (transmitindo) informações novas para a rede.

*   **Objetivo:** Fazer com que transações e blocos recém-criados sejam ativamente propagados pela rede.
*   **Passos:**
    *   **Propagação de Transações:** Quando um nó recebe uma nova transação válida, além de adicioná-la ao seu mempool, ele a transmitirá para todos os outros nós que conhece (`/nodes`).
    *   **Propagação de Blocos:** Quando um nó minera um novo bloco com sucesso, ele o transmitirá para todos os seus pares.
    *   **Novos Endpoints:** Precisaremos criar endpoints para receber essas informações:
        *   `POST /blocks/receive`: Para um nó receber um bloco minerado por um par, validá-lo e adicioná-lo à sua própria cadeia.
        *   `POST /transactions/receive`: Para um nó receber uma transação de um par, validá-la e adicioná-la ao seu mempool.

### 3. Implementar Ajuste de Dificuldade Dinâmico [Concluído]

A dificuldade de mineração no Bitcoin se ajusta para manter o tempo médio de geração de blocos constante. Vamos implementar uma versão simplificada disso.

*   **Objetivo:** Substituir a dificuldade fixa (`"0000"`) por uma que se ajuste periodicamente.
*   **Passos:**
    *   Definir uma regra de ajuste (ex: a cada 10 blocos).
    *   Criar uma função que calcule a nova dificuldade com base no tempo que levou para minerar os últimos 10 blocos.
    *   Modificar a função `valid_proof` para usar a dificuldade atual da rede em vez de um valor fixo.

### 4. (Avançado) Introduzir o Modelo UTXO

Esta é a mudança mais complexa e fundamental. Em vez de simplesmente ter um "saldo", o Bitcoin rastreia "Unspent Transaction Outputs" (UTXOs).

*   **Objetivo:** Refatorar o sistema de transações para que ele se baseie em entradas (inputs) que consomem UTXOs e saídas (outputs) que criam novos UTXOs.
*   **Passos:**
    *   Alterar a estrutura de uma transação para conter uma lista de `inputs` e `outputs`.
    *   Implementar uma lógica para rastrear todos os UTXOs na blockchain.
    *   Mudar a validação de transações para verificar se os `inputs` se referem a UTXOs válidos e não gastos que pertencem ao remetente.