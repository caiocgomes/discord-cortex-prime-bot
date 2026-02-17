## Requirements

### Requirement: Botao para criar complicacao a partir de hitch

Quando uma rolagem produz hitches (dados que rolaram 1), a PostRollView SHALL incluir um botao "Criar complicacao" visivel apenas para GM/delegates. O botao SHALL iniciar uma chain: selecao de jogador alvo, input de nome da complicacao via modal, e execucao automatica de criacao de complicacao d6 + concessao de 1 PP ao jogador alvo.

#### Scenario: GM cria complicacao via botao de hitch

- **WHEN** rolagem de jogador produz hitch e GM clica "Criar complicacao"
- **THEN** bot apresenta selecao de jogadores da campanha (botoes se <= 5, select se > 5)
- **WHEN** GM seleciona jogador alvo
- **THEN** bot apresenta modal com campo de texto para nome da complicacao
- **WHEN** GM submete o modal com nome "Desarmado"
- **THEN** bot cria complicacao "Desarmado" d6 no jogador alvo
- **AND** bot concede 1 PP ao jogador alvo
- **AND** bot envia mensagem publica confirmando: "Complicacao Desarmado d6 criada em [jogador]. [jogador] recebeu 1 PP."
- **AND** ambas as acoes (complicacao e PP) sao registradas no action_log para undo

#### Scenario: Jogador nao vê botao de hitch action

- **WHEN** rolagem produz hitch
- **AND** jogador sem permissao GM vê a PostRollView
- **THEN** botoes de hitch action SHALL NOT ser visiveis ou clicaveis pelo jogador

#### Scenario: Multiplos hitches permitem multiplos usos

- **WHEN** rolagem produz 3 hitches
- **THEN** GM pode clicar "Criar complicacao" multiplas vezes
- **AND** cada clique inicia uma nova chain independente

#### Scenario: Complicacao via hitch em jogador que ja tem complicacao com mesmo nome

- **WHEN** GM cria complicacao "Ferido" via hitch em jogador que ja tem "Ferido d6"
- **THEN** bot SHALL fazer step up da complicacao existente (d6 para d8) em vez de criar duplicata
- **AND** PP ainda é concedido ao jogador

### Requirement: Botao para adicionar hitch ao doom pool

Quando uma rolagem produz hitches e doom_pool esta habilitado, a PostRollView SHALL incluir um botao "+Doom" visivel apenas para GM/delegates. O botao SHALL adicionar d6 ao doom pool diretamente, sem chain intermediaria.

#### Scenario: GM adiciona hitch ao doom pool

- **WHEN** rolagem produz hitch e GM clica "+Doom"
- **THEN** bot adiciona d6 ao doom pool
- **AND** bot envia mensagem publica: "Adicionado d6 ao Doom Pool. Doom Pool: [lista atual]."
- **AND** acao registrada no action_log para undo

#### Scenario: Botao +Doom nao aparece sem doom habilitado

- **WHEN** rolagem produz hitch
- **AND** campanha nao tem doom_pool habilitado
- **THEN** botao "+Doom" SHALL NOT aparecer na PostRollView

#### Scenario: Botao +Doom nao aparece sem hitches

- **WHEN** rolagem nao produz hitches
- **THEN** botoes de hitch action (Criar complicacao e +Doom) SHALL NOT aparecer na PostRollView
