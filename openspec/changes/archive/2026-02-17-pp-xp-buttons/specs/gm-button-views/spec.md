## ADDED Requirements

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
