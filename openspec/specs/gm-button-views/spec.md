## Requirements

### Requirement: Botões contextuais em toda resposta do bot

Toda resposta de sucesso do bot SHALL incluir uma View com botões representando as ações mais prováveis como próximo passo, determinadas pelo contexto da ação que acabou de ser executada. Respostas de erro SHALL NOT incluir botões.

#### Scenario: Botões após rolagem

- **WHEN** jogador ou GM executa roll ou gmroll com sucesso
- **THEN** resposta inclui botões: Roll, Undo
- **AND** se a rolagem produziu hitches, inclui botões: Criar complicação, +Doom (se doom habilitado)
- **AND** se doom_pool habilitado, inclui botão Doom Roll
- **AND** inclui botão Menu

#### Scenario: Botões após scene start

- **WHEN** GM executa scene start com sucesso
- **THEN** resposta inclui botões: Roll, Stress Add, Asset Add, Complication Add, Menu
- **AND** se doom_pool habilitado, inclui botão Doom Add

#### Scenario: Botões após scene end

- **WHEN** GM encerra uma cena com sucesso
- **THEN** resposta inclui botões: Scene Start, Campaign Info, Menu

#### Scenario: Botões após ação de state (stress/asset/complication)

- **WHEN** GM executa stress add, asset add, ou complication add com sucesso
- **THEN** resposta inclui botão Undo, botão para repetir a mesma categoria de ação, e botão Menu

#### Scenario: Botões após campaign setup

- **WHEN** GM cria campanha com sucesso
- **THEN** resposta inclui botão Scene Start e botão Menu

#### Scenario: Botões após campaign/scene info

- **WHEN** usuário consulta campaign info ou scene info
- **THEN** se há cena ativa, resposta inclui botão Roll e botão Menu
- **AND** se não há cena ativa, resposta inclui botão Scene Start e botão Menu

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

Botoes de doom (add, remove, roll) SHALL estar disponiveis apenas quando o modulo doom_pool esta habilitado na campanha. Doom add via botao SHALL apresentar 5 botoes de dado (d4-d12) em vez de select. Doom remove SHALL apresentar botoes com dados presentes no pool (deduplicados por tamanho). Doom roll SHALL executar diretamente. Doom Roll SHALL estar disponivel tambem na PostRollView quando doom_pool esta habilitado, permitindo o GM rolar oposicao diretamente apos uma rolagem de jogador.

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

#### Scenario: Doom Roll na PostRollView

- **WHEN** doom_pool habilitado e jogador executa roll com sucesso
- **THEN** PostRollView inclui botao "Doom Roll"
- **WHEN** GM clica "Doom Roll"
- **THEN** bot rola todo o doom pool e exibe resultado com best options e sugestao de dificuldade

#### Scenario: Botoes de doom nao aparecem sem modulo

- **WHEN** campanha nao tem doom_pool habilitado
- **THEN** nenhuma resposta SHALL incluir botoes relacionados a doom

### Requirement: PP via botoes com up/down

O botao PP SHALL iniciar um flow de ajuste de plot points. GM/delegate SHALL selecionar jogador primeiro; jogador comum SHALL operar no proprio estado sem selecao intermediaria. Apos selecao, bot SHALL apresentar dois botoes: PP +1 e PP -1. Cada clique SHALL executar a operacao, editar a mensagem ephemeral com o resultado atualizado, enviar followup publico, e manter os botoes para novo ajuste. PP -1 SHALL respeitar a regra de PP nunca negativo.

#### Scenario: GM clica PP e seleciona jogador

- **WHEN** GM clica botao "PP"
- **AND** campanha tem 4 jogadores (excluindo GM)
- **THEN** bot apresenta botoes com nomes dos jogadores para selecao
- **WHEN** GM clica botao do jogador
- **THEN** bot apresenta dois botoes: "PP +1" e "PP -1"

#### Scenario: Jogador clica PP (auto-selecao)

- **WHEN** jogador (nao-GM) clica botao "PP"
- **THEN** bot pula selecao de jogador e apresenta diretamente dois botoes: "PP +1" e "PP -1" para o proprio jogador

#### Scenario: PP +1 executado

- **WHEN** usuario clica "PP +1"
- **THEN** bot adiciona 1 PP ao jogador alvo
- **AND** edita mensagem ephemeral com resultado (ex: "Alice: 2 para 3 PP (+1)")
- **AND** envia followup publico com confirmacao
- **AND** mantém botoes PP +1 e PP -1 ativos na mensagem ephemeral para novo ajuste

#### Scenario: PP -1 com PP suficiente

- **WHEN** usuario clica "PP -1" e jogador alvo tem pelo menos 1 PP
- **THEN** bot remove 1 PP do jogador alvo
- **AND** edita mensagem ephemeral com resultado
- **AND** envia followup publico com confirmacao
- **AND** mantém botoes ativos

#### Scenario: PP -1 com PP insuficiente

- **WHEN** usuario clica "PP -1" e jogador alvo tem 0 PP
- **THEN** bot edita mensagem ephemeral informando que PP nao pode ficar negativo
- **AND** mantém botoes ativos (usuario pode clicar +1 em seguida)

#### Scenario: PP com > 5 jogadores usa select

- **WHEN** GM clica botao "PP"
- **AND** campanha tem 7 jogadores (excluindo GM)
- **THEN** bot apresenta select menu com jogadores como opcoes

### Requirement: XP via botoes com modal

O botao XP SHALL iniciar um flow de adicao de XP. GM/delegate SHALL selecionar jogador primeiro; jogador comum SHALL operar no proprio estado sem selecao intermediaria. Apos selecao, bot SHALL abrir um discord.ui.Modal com campo numerico para digitar quantidade. Bot SHALL executar add de XP com a quantidade informada.

#### Scenario: GM clica XP e seleciona jogador

- **WHEN** GM clica botao "XP"
- **AND** campanha tem 4 jogadores (excluindo GM)
- **THEN** bot apresenta botoes com nomes dos jogadores para selecao
- **WHEN** GM clica botao do jogador
- **THEN** bot abre modal com campo "Quantidade de XP"

#### Scenario: Jogador clica XP (auto-selecao)

- **WHEN** jogador (nao-GM) clica botao "XP"
- **THEN** bot pula selecao de jogador e abre modal diretamente com campo "Quantidade de XP"

#### Scenario: XP adicionado via modal

- **WHEN** usuario submete modal com quantidade "5"
- **THEN** bot adiciona 5 XP ao jogador alvo
- **AND** edita mensagem ephemeral (ou envia nova) com confirmacao
- **AND** envia followup publico com resultado

#### Scenario: Quantidade invalida no modal

- **WHEN** usuario submete modal com valor nao-numerico ou <= 0
- **THEN** bot responde com mensagem ephemeral de erro informando que quantidade deve ser um numero positivo

#### Scenario: XP com > 5 jogadores usa select

- **WHEN** GM clica botao "XP"
- **AND** campanha tem 7 jogadores (excluindo GM)
- **THEN** bot apresenta select menu com jogadores como opcoes

### Requirement: PP e XP DynamicItems persistentes

Os botoes PP e XP SHALL usar DynamicItem com custom_ids estaveis parseaveis por regex, seguindo o padrao `cortex:{action}:{params}`. Botoes SHALL sobreviver restart do bot. Botoes intermediarios (player select, up/down) SHALL usar custom_ids efemeros.

#### Scenario: PP botao funciona apos restart

- **WHEN** bot reinicia
- **AND** usuario clica botao "PP" em mensagem anterior ao restart
- **THEN** bot processa a interacao normalmente

#### Scenario: XP botao funciona apos restart

- **WHEN** bot reinicia
- **AND** usuario clica botao "XP" em mensagem anterior ao restart
- **THEN** bot processa a interacao normalmente

### Requirement: Verificacao de permissao em PP e XP via botoes

PP e XP via botoes SHALL verificar que o usuario e jogador registrado na campanha. PP -1 SHALL verificar que o jogador alvo tem PP suficiente. Nenhuma verificacao adicional de papel e necessaria porque jogador opera em si mesmo e GM seleciona target.

#### Scenario: Usuario nao registrado clica PP

- **WHEN** usuario nao registrado na campanha clica botao "PP"
- **THEN** bot responde com mensagem ephemeral informando que nao esta registrado

#### Scenario: Usuario nao registrado clica XP

- **WHEN** usuario nao registrado na campanha clica botao "XP"
- **THEN** bot responde com mensagem ephemeral informando que nao esta registrado
