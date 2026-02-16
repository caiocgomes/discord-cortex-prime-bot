## ADDED Requirements

### Requirement: Pool builder interativo com botoes

O botao Roll SHALL abrir uma view efemera com botoes para montagem incremental do dice pool. A view SHALL conter uma ActionRow com 5 botoes de dado (d4, d6, d8, d10, d12), botoes para cada asset ativo do jogador, e botoes de controle (Rolar, Limpar, Remover ultimo). Cada clique de dado SHALL adicionar um dado ao pool. Assets SHALL funcionar como toggle (clique inclui, clique novamente remove).

#### Scenario: Pool builder abre ao clicar Roll

- **WHEN** jogador registrado clica botao "Roll"
- **THEN** bot abre mensagem efemera com botoes de dado (d4-d12), botoes de assets ativos, e controles
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

#### Scenario: Incluir asset no pool

- **WHEN** jogador tem asset "Sword d8" e clica botao "Sword d8"
- **THEN** d8 do asset e adicionado ao pool
- **AND** label do botao muda para "Sword d8 (no pool)"
- **AND** estilo do botao muda para indicar inclusao

#### Scenario: Remover asset do pool (toggle off)

- **WHEN** jogador clica em asset ja incluido "Sword d8 (no pool)"
- **THEN** d8 do asset e removido do pool
- **AND** label do botao volta para "Sword d8"
- **AND** estilo do botao volta ao original

#### Scenario: Remover ultimo dado adicionado

- **WHEN** pool contem d8, d8, d6 (nesta ordem de adicao)
- **AND** jogador clica "Remover ultimo"
- **THEN** d6 e removido do pool
- **AND** labels dos botoes atualizam para refletir o pool sem o d6

#### Scenario: Limpar pool

- **WHEN** pool contem dados e/ou assets
- **AND** jogador clica "Limpar"
- **THEN** pool e esvaziado completamente
- **AND** todos os botoes voltam ao estado inicial
- **AND** botao "Remover ultimo" desaparece

### Requirement: Labels dos botoes carregam estado do pool

Os labels dos botoes de dado SHALL mostrar a quantidade ja adicionada ao pool entre parenteses quando > 0. O botao "Rolar" SHALL mostrar o total de dados no pool. Assets incluidos SHALL ter indicacao no label.

#### Scenario: Labels refletem estado

- **WHEN** pool contem 2x d8, 1x d6, e asset Sword d8 incluido
- **THEN** botao d8 mostra "+d8 (2)"
- **AND** botao d6 mostra "+d6 (1)"
- **AND** botao d4 mostra "+d4" (sem contagem)
- **AND** botao Sword mostra "Sword d8 (no pool)"
- **AND** botao Rolar mostra "Rolar 4 dados"

### Requirement: Assets do jogador aparecem como botoes no pool builder

A view SHALL buscar assets ativos do jogador e apresenta-los como botoes individuais. Se o jogador nao tiver assets, a row de assets SHALL ser omitida.

#### Scenario: Jogador com assets ativos

- **WHEN** jogador tem assets "Sword d8" e "Shield d6"
- **THEN** pool builder mostra 2 botoes de asset: "Sword d8" e "Shield d6"

#### Scenario: Jogador sem assets

- **WHEN** jogador sem assets ativos clica Roll
- **THEN** pool builder mostra apenas botoes de dado e controles, sem row de assets

### Requirement: Rolar executa a rolagem com o pool montado

Clicar "Rolar" SHALL executar a rolagem usando o pool montado. O resultado SHALL ser enviado como mensagem publica com PostRollView. A logica de rolagem (hitches, botch, best_options, opposition_elements) SHALL ser identica a do slash command /roll.

#### Scenario: Rolar com pool valido

- **WHEN** jogador montou pool com d8, d8, d6 e asset Sword d8
- **AND** clica "Rolar 4 dados"
- **THEN** bot executa rolagem com pool [8, 8, 6, 8]
- **AND** resultado e enviado como mensagem publica
- **AND** resultado mostra "Incluido: Sword d8"
- **AND** mensagem inclui PostRollView com botoes Roll e Undo

#### Scenario: Rolar com pool vazio

- **WHEN** jogador clica "Rolar" sem ter adicionado dados
- **THEN** bot responde com mensagem efemera informando que o pool esta vazio
- **AND** pool builder permanece aberto para continuacao
