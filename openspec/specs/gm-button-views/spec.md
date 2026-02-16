## Requirements

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

### Requirement: Chains de botoes para comandos multi-parametro

Comandos que exigem multiplos parametros (stress add, complication add, asset add) SHALL usar sequencia de botoes e/ou selects dinamicos para coletar cada parametro. Selecao de dado (d4-d12) SHALL usar 5 botoes individuais em 1 ActionRow. Selecao de jogador SHALL usar botoes quando <= 5 jogadores, ou select quando > 5. Selecao de tipo de stress SHALL usar botoes (maximo 4 tipos). Listas longas (nomes de assets/complications comuns) SHALL manter select. Cada etapa intermediaria SHALL ser efemera.

#### Scenario: Chain de stress add completa com botoes

- **WHEN** GM clica botao "Stress Add"
- **AND** campanha tem 4 jogadores (excluindo GM)
- **THEN** bot apresenta 4 botoes com nomes dos jogadores (1 por botao)
- **WHEN** GM clica botao do jogador
- **THEN** bot apresenta botoes com tipos de stress da campanha (ex: Physical, Mental)
- **WHEN** GM clica botao do tipo
- **THEN** bot apresenta 5 botoes de dado: d4, d6, d8, d10, d12
- **WHEN** GM clica botao do dado
- **THEN** bot executa stress add e exibe resultado com botoes contextuais

#### Scenario: Chain de stress add com > 5 jogadores usa select

- **WHEN** GM clica botao "Stress Add"
- **AND** campanha tem 7 jogadores (excluindo GM)
- **THEN** bot apresenta select menu com 7 jogadores como opcoes
- **WHEN** GM seleciona jogador
- **THEN** chain continua com botoes para tipo e dado

#### Scenario: Chain de asset add completa

- **WHEN** GM clica botao "Asset Add"
- **THEN** bot apresenta botoes de jogadores (ou select se > 5) mais botao "Asset de Cena"
- **WHEN** GM seleciona jogador ou cena
- **THEN** bot apresenta select menu com nomes de assets comuns pre-definidos
- **WHEN** GM seleciona nome
- **THEN** bot apresenta 5 botoes de dado: d4, d6, d8, d10, d12
- **WHEN** GM seleciona dado
- **THEN** bot executa asset add e exibe resultado com botoes contextuais

#### Scenario: Chain de complication add completa

- **WHEN** GM clica botao "Complication Add"
- **THEN** bot apresenta botoes de jogadores (ou select se > 5) mais botao "Complicacao de Cena"
- **WHEN** GM seleciona alvo
- **THEN** bot apresenta select com nomes de complication comuns
- **WHEN** GM seleciona nome
- **THEN** bot apresenta 5 botoes de dado: d4, d6, d8, d10, d12
- **WHEN** GM seleciona dado
- **THEN** bot executa complication add e exibe resultado com botoes contextuais

#### Scenario: Mensagens intermediarias sao efemeras

- **WHEN** bot envia botoes ou select intermediario durante uma chain
- **THEN** mensagem SHALL ser efemera (visivel apenas para quem clicou)

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

### Requirement: Botao Roll abre pool builder

O botao Roll SHALL abrir o pool builder interativo (conforme spec pool-builder) com conteudo diferenciado por papel. O botao SHALL NOT usar select menus para composicao de pool.

#### Scenario: Roll via botao abre pool builder

- **WHEN** jogador clica botao "Roll"
- **THEN** bot abre pool builder com botoes de dado, botoes de toggles, e controles
- **AND** bot SHALL NOT apresentar select menus para composicao de pool

#### Scenario: Assets disponiveis aparecem como botoes no pool builder

- **WHEN** jogador inicia roll via botao e tem assets ativos
- **THEN** pool builder mostra assets como botoes toggle individuais

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

### Requirement: Doom pool via botoes

Botoes de doom (add, remove, roll) SHALL estar disponiveis apenas quando o modulo doom_pool esta habilitado na campanha. Doom add via botao SHALL apresentar 5 botoes de dado (d4-d12) em vez de select. Doom remove SHALL apresentar botoes com dados presentes no pool (deduplicados por tamanho). Doom roll SHALL executar diretamente.

#### Scenario: Doom add via botao

- **WHEN** GM clica botao "Doom Add"
- **THEN** bot apresenta 5 botoes de dado: d4, d6, d8, d10, d12
- **WHEN** GM clica botao de dado
- **THEN** bot adiciona ao doom pool e exibe resultado com botoes de doom

#### Scenario: Doom remove via botao

- **WHEN** GM clica botao "Doom Remove"
- **AND** doom pool contem d6, d8, d8
- **THEN** bot apresenta botoes: d6, d8 (deduplicados por tamanho)
- **WHEN** GM clica d8
- **THEN** bot remove um d8 do pool e exibe resultado

#### Scenario: Botoes de doom nao aparecem sem modulo

- **WHEN** campanha nao tem doom_pool habilitado
- **THEN** nenhuma resposta SHALL incluir botoes relacionados a doom
