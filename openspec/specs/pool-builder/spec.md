## Requirements

### Requirement: Pool builder interativo com botoes

O botao Roll SHALL abrir uma view efemera com botoes para montagem incremental do dice pool. A view SHALL conter uma ActionRow com 5 botoes de dado (d4, d6, d8, d10, d12), botoes toggle para elementos do jogador ou GM, e botoes de controle (Rolar, Limpar, Remover ultimo). Cada clique de dado SHALL adicionar um dado ao pool. Toggles SHALL funcionar como toggle (clique inclui, clique novamente remove).

#### Scenario: Pool builder abre ao clicar Roll

- **WHEN** jogador registrado clica botao "Roll"
- **THEN** bot abre mensagem efemera com botoes de dado (d4-d12), botoes de toggles ativos, e controles
- **AND** texto da mensagem indica "Pool vazio"

#### Scenario: Jogador nao registrado clica Roll

- **WHEN** usuario nao registrado na campanha clica botao "Roll"
- **THEN** bot responde com mensagem efemera informando que nao esta registrado

#### Scenario: Adicionar dado ao pool

- **WHEN** jogador clica botao "+d8" no pool builder
- **THEN** bot adiciona d8 ao pool
- **AND** label do botao atualiza para "+d8 (1)"
- **AND** botao "Rolar" atualiza para "Rolar 1 dado"
- **AND** botao "Remover ultimo" aparece
- **AND** mensagem edita para mostrar pool atual

#### Scenario: Adicionar multiplos dados do mesmo tipo

- **WHEN** jogador clica "+d8" duas vezes
- **THEN** pool contem 2x d8
- **AND** label do botao atualiza para "+d8 (2)"
- **AND** botao "Rolar" atualiza para "Rolar 2 dados"

#### Scenario: Incluir toggle no pool

- **WHEN** jogador clica botao de toggle (ex: "Sword d8")
- **THEN** dado do toggle e adicionado ao pool
- **AND** label do botao muda para "Sword d8 (no pool)"
- **AND** estilo do botao muda para indicar inclusao

#### Scenario: Remover toggle do pool (toggle off)

- **WHEN** jogador clica em toggle ja incluido "Sword d8 (no pool)"
- **THEN** dado do toggle e removido do pool
- **AND** label do botao volta para "Sword d8"
- **AND** estilo do botao volta ao original

#### Scenario: Remover ultimo dado adicionado

- **WHEN** pool contem d8, d8, d6 (nesta ordem de adicao)
- **AND** jogador clica "Remover ultimo"
- **THEN** d6 e removido do pool
- **AND** labels dos botoes atualizam para refletir o pool sem o d6

#### Scenario: Limpar pool

- **WHEN** pool contem dados e/ou toggles
- **AND** jogador clica "Limpar"
- **THEN** pool e esvaziado completamente
- **AND** todos os botoes voltam ao estado inicial
- **AND** botao "Remover ultimo" desaparece

#### Scenario: Truncamento de toggles em 15 itens

- **WHEN** mais de 15 toggle items estao disponiveis
- **THEN** pool builder mostra apenas os 15 primeiros
- **AND** status_text indica quantos itens estao disponiveis

### Requirement: Labels dos botoes carregam estado do pool

Os labels dos botoes de dado SHALL mostrar a quantidade ja adicionada ao pool entre parenteses quando > 0. O botao "Rolar" SHALL mostrar o total de dados no pool. Toggles incluidos SHALL ter indicacao no label.

#### Scenario: Labels refletem estado

- **WHEN** pool contem 2x d8, 1x d6, e toggle Sword d8 incluido
- **THEN** botao d8 mostra "+d8 (2)"
- **AND** botao d6 mostra "+d6 (1)"
- **AND** botao d4 mostra "+d4" (sem contagem)
- **AND** botao Sword mostra "Sword d8 (no pool)"
- **AND** botao Rolar mostra "Rolar 4 dados"

### Requirement: Toggles do jogador sao assets

A view SHALL buscar assets ativos do jogador e apresenta-los como botoes toggle com id "asset:{id}" e label formatado. Se o jogador nao tiver assets, a row de toggles SHALL ser omitida.

#### Scenario: Jogador com assets ativos

- **WHEN** jogador tem assets "Sword d8" e "Shield d6"
- **THEN** pool builder mostra 2 botoes de toggle: "Sword d8" e "Shield d6"

#### Scenario: Jogador sem assets

- **WHEN** jogador sem assets ativos clica Roll
- **THEN** pool builder mostra apenas botoes de dado e controles, sem row de toggles

### Requirement: Toggles do GM sao stress e complications

Quando GM/delegate clica Roll, a view SHALL buscar stress e complications de todos os jogadores mais complications de cena e apresenta-los como toggles. Labels SHALL identificar o dono: "NomeJogador: TipoStress dX", "NomeJogador: NomeComp dX", "Cena: NomeComp dX". IDs SHALL usar prefixo "stress:{id}" ou "comp:{id}".

#### Scenario: GM abre pool builder com stress e complications de todos

- **WHEN** GM clica botao "Roll"
- **THEN** pool builder mostra toggles com stress e complications de todos os jogadores + complications de cena
- **AND** labels seguem formato "NomeJogador: TipoStress dX" ou "Cena: NomeComp dX"

#### Scenario: GM sem jogadores com stress ou complications

- **WHEN** GM clica "Roll" e nenhum jogador tem stress ou complications
- **THEN** pool builder mostra apenas botoes de dado e controles, sem row de toggles

#### Scenario: Delegate abre pool builder como GM

- **WHEN** delegate clica botao "Roll"
- **THEN** pool builder mostra visao de GM (stress/complications de todos)
- **AND** SHALL NOT mostrar assets do delegate

### Requirement: Rolar executa a rolagem com o pool montado

Clicar "Rolar" SHALL executar a rolagem usando o pool montado. O resultado SHALL ser enviado como mensagem publica com PostRollView. A logica de rolagem (hitches, botch, best_options, opposition_elements) SHALL ser identica a do slash command /roll para jogadores. Para GM, SHALL NOT buscar opposition_elements e SHALL NOT alterar estado.

#### Scenario: Rolar com pool valido

- **WHEN** jogador montou pool com d8, d8, d6 e toggle Sword d8
- **AND** clica "Rolar 4 dados"
- **THEN** bot executa rolagem com pool [8, 8, 6, 8]
- **AND** resultado e enviado como mensagem publica
- **AND** resultado mostra "Incluidos: Sword d8"
- **AND** mensagem inclui PostRollView com botoes Roll e Undo

#### Scenario: Rolar com pool vazio

- **WHEN** jogador clica "Rolar" sem ter adicionado dados
- **THEN** bot responde com mensagem efemera informando que o pool esta vazio
- **AND** pool builder permanece aberto para continuacao

#### Scenario: GM rola com toggles de oposicao incluidos

- **WHEN** GM monta pool com d8, d10 e inclui toggles "Alice: Physical d8" e "Cena: Trapped d6"
- **THEN** bot rola pool [8, 10, 8, 6]
- **AND** resultado mostra "Incluidos: Alice: Physical d8, Cena: Trapped d6"
- **AND** resultado SHALL NOT conter opposition_elements

#### Scenario: GM rola sem toggles

- **WHEN** GM monta pool sem incluir nenhum toggle
- **THEN** resultado nao mostra linha de incluidos
