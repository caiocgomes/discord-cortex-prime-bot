## ADDED Requirements

### Requirement: Botões contextuais em toda resposta do bot

Toda resposta de sucesso do bot SHALL incluir uma View com botões representando as ações mais prováveis como próximo passo, determinadas pelo contexto da ação que acabou de ser executada. Respostas de erro SHALL NOT incluir botões.

#### Scenario: Botões após scene start

- **WHEN** GM executa scene start com sucesso
- **THEN** resposta inclui botões: Roll, Stress Add, Asset Add, Complication Add
- **AND** se doom_pool habilitado, inclui botão Doom Add

#### Scenario: Botões após scene end

- **WHEN** GM encerra uma cena com sucesso
- **THEN** resposta inclui botões: Scene Start, Campaign Info

#### Scenario: Botões após rolagem

- **WHEN** jogador ou GM executa roll ou gmroll com sucesso
- **THEN** resposta inclui botões: Roll, Undo

#### Scenario: Botões após ação de state (stress/asset/complication)

- **WHEN** GM executa stress add, asset add, ou complication add com sucesso
- **THEN** resposta inclui botão Undo e botão para repetir a mesma categoria de ação

#### Scenario: Botões após campaign setup

- **WHEN** GM cria campanha com sucesso
- **THEN** resposta inclui botão Scene Start

#### Scenario: Botões após campaign/scene info

- **WHEN** usuário consulta campaign info ou scene info
- **THEN** se há cena ativa, resposta inclui botão Roll
- **AND** se não há cena ativa, resposta inclui botão Scene Start

#### Scenario: Sem botões em respostas de erro

- **WHEN** bot envia mensagem de erro (campanha não encontrada, permissão negada, etc.)
- **THEN** resposta SHALL NOT incluir View com botões

### Requirement: Select menu chains para comandos multi-parâmetro

Comandos que exigem múltiplos parâmetros (stress add, complication add, asset add) SHALL usar sequência de select menus onde cada seleção leva ao próximo parâmetro, até completar a ação. Opções dos selects SHALL ser populadas a partir do estado atual da campanha no banco de dados.

#### Scenario: Chain de stress add completa

- **WHEN** GM clica botão "Stress Add"
- **THEN** bot apresenta select menu com jogadores da campanha (excluindo GM)
- **WHEN** GM seleciona jogador
- **THEN** bot apresenta select menu com tipos de stress da campanha
- **WHEN** GM seleciona tipo de stress
- **THEN** bot apresenta select menu com tamanhos de dado (d4, d6, d8, d10, d12)
- **WHEN** GM seleciona dado
- **THEN** bot executa stress add e exibe resultado com botões contextuais

#### Scenario: Chain de asset add completa

- **WHEN** GM clica botão "Asset Add"
- **THEN** bot apresenta select menu com jogadores da campanha mais opção "Asset de Cena"
- **WHEN** GM seleciona jogador ou cena
- **THEN** bot apresenta select menu solicitando nome do asset (opções: assets comuns pré-definidos + "Outro")
- **WHEN** GM seleciona ou digita nome
- **THEN** bot apresenta select menu com tamanhos de dado
- **WHEN** GM seleciona dado
- **THEN** bot executa asset add e exibe resultado com botões contextuais

#### Scenario: Chain de complication add completa

- **WHEN** GM clica botão "Complication Add"
- **THEN** bot apresenta select menu com jogadores da campanha mais opção "Complicação de Cena"
- **WHEN** GM seleciona alvo
- **THEN** bot solicita nome da complication via select ou input
- **WHEN** GM fornece nome
- **THEN** bot apresenta select com tamanhos de dado
- **WHEN** GM seleciona dado
- **THEN** bot executa complication add e exibe resultado com botões contextuais

#### Scenario: Mensagens intermediárias são efêmeras

- **WHEN** bot envia select menu intermediário durante uma chain
- **THEN** mensagem SHALL ser efêmera (visível apenas para quem clicou)

### Requirement: Persistent views sobrevivem restart

Todas as Views SHALL usar `timeout=None` e custom_ids estáveis parseáveis por regex. O bot SHALL registrar todas as persistent views e DynamicItems no `setup_hook`, antes de carregar cogs. Após um restart, botões em mensagens anteriores SHALL continuar funcionais.

#### Scenario: Botão funciona após restart do bot

- **WHEN** bot reinicia
- **AND** GM clica um botão em mensagem anterior ao restart
- **THEN** bot processa a interação normalmente e executa a ação

#### Scenario: Custom ID codifica contexto da ação

- **WHEN** bot cria um botão ou select menu
- **THEN** custom_id SHALL seguir formato `cortex:{action}:{params}` com parâmetros suficientes para executar a ação sem estado em memória

### Requirement: Verificação de permissão em callbacks de botões

Callbacks de botões e selects que executam ações GM-only SHALL verificar `has_gm_permission()` antes de executar. Se o usuário não tem permissão, o bot SHALL responder com mensagem efêmera informando a restrição.

#### Scenario: Jogador clica botão GM-only

- **WHEN** jogador sem permissão de GM clica botão "Stress Add"
- **THEN** bot responde com mensagem efêmera "Apenas o GM pode usar este comando."
- **AND** nenhuma ação é executada

#### Scenario: GM clica botão GM-only

- **WHEN** GM ou delegate clica botão "Stress Add"
- **THEN** bot inicia a select chain normalmente

### Requirement: Botão Roll executa rolagem direta

O botão Roll SHALL abrir uma select chain onde o GM/jogador monta o dice pool via selects: quantidade e tipo de dados, assets para incluir, dificuldade opcional. Para rolagens simples, o botão SHALL oferecer opção de rolagem rápida com o último pool usado.

#### Scenario: Roll via botões com pool novo

- **WHEN** jogador clica botão "Roll"
- **THEN** bot apresenta select para compor dice pool (selects de dados, com opção de adicionar mais)
- **WHEN** jogador confirma pool
- **THEN** bot executa rolagem e exibe resultado com botões contextuais

#### Scenario: Assets disponíveis aparecem no select de roll

- **WHEN** jogador inicia roll via botão e tem assets ativos
- **THEN** select de include oferece assets do jogador como opções selecionáveis

### Requirement: Botão Undo executa desfazer imediato

O botão Undo SHALL executar a operação de undo diretamente, sem confirmação intermediária. O resultado SHALL incluir novos botões contextuais. A verificação de permissão (GM pode desfazer qualquer ação, jogador só as próprias) SHALL ser aplicada.

#### Scenario: GM clica undo via botão

- **WHEN** GM clica botão "Undo"
- **THEN** bot desfaz a última ação não-desfeita
- **AND** exibe resultado com botão para outro Undo e Campaign Info

#### Scenario: Jogador clica undo via botão

- **WHEN** jogador clica botão "Undo"
- **AND** a última ação não-desfeita é de outro jogador
- **THEN** bot responde com mensagem efêmera informando que só pode desfazer ações próprias

### Requirement: Doom pool via botões

Botões de doom (add, remove, step up, step down, roll, spend) SHALL estar disponíveis apenas quando o módulo doom_pool está habilitado na campanha. Doom add via botão SHALL apresentar select com tamanhos de dado. Doom roll SHALL executar diretamente e exibir resultado.

#### Scenario: Doom add via botão

- **WHEN** GM clica botão "Doom Add"
- **THEN** bot apresenta select com tamanhos de dado (d4 a d12)
- **WHEN** GM seleciona dado
- **THEN** bot adiciona ao doom pool e exibe resultado com botões de doom

#### Scenario: Botões de doom não aparecem sem módulo

- **WHEN** campanha não tem doom_pool habilitado
- **THEN** nenhuma resposta SHALL incluir botões relacionados a doom
