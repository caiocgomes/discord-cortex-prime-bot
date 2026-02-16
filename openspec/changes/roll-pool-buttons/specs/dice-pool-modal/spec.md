## ADDED Requirements

### Requirement: Botão Roll abre modal para montar dice pool

O botão Roll SHALL abrir um `discord.ui.Modal` com campos TextInput em vez de select menus. O modal SHALL conter um campo obrigatório para notação de dados e um campo opcional para inclusão de assets.

#### Scenario: Modal abre ao clicar Roll

- **WHEN** jogador registrado clica botão "Roll"
- **THEN** bot abre modal com título "Montar Pool"
- **AND** campo 1 é TextInput obrigatório com label "Dados" e placeholder "Ex: 2d8 1d6 1d10"
- **AND** campo 2 é TextInput opcional com label "Assets para incluir"

#### Scenario: Jogador não registrado clica Roll

- **WHEN** usuário não registrado na campanha clica botão "Roll"
- **THEN** bot responde com mensagem efêmera informando que não está registrado

### Requirement: Campo de assets mostra assets disponíveis no placeholder

O campo de assets no modal SHALL ter placeholder dinâmico listando os assets ativos do jogador com nome e dado. Se o jogador não tiver assets ativos, o campo SHALL ter placeholder informando que não há assets disponíveis.

#### Scenario: Jogador com assets ativos

- **WHEN** jogador com assets "Sword d8" e "Shield d6" clica Roll
- **THEN** campo de assets tem placeholder "Disponiveis: Sword d8, Shield d6"

#### Scenario: Jogador sem assets

- **WHEN** jogador sem assets ativos clica Roll
- **THEN** campo de assets tem placeholder "Nenhum asset ativo"

### Requirement: Modal processa notação de dados existente

O submit do modal SHALL processar o campo de dados usando `parse_dice_notation` existente. A mesma notação aceita pelo `/roll dice:` SHALL funcionar no modal. Erros de parsing SHALL ser exibidos como mensagem efêmera.

#### Scenario: Notação válida

- **WHEN** jogador submete modal com dados "2d8 1d6"
- **THEN** bot parseia como pool [8, 8, 6] e executa rolagem

#### Scenario: Notação inválida

- **WHEN** jogador submete modal com dados "2d7"
- **THEN** bot responde com mensagem efêmera "d7 nao e um dado Cortex valido. Use d4, d6, d8, d10 ou d12."

#### Scenario: Campo vazio

- **WHEN** jogador submete modal com campo de dados vazio
- **THEN** bot responde com mensagem efêmera informando que o campo é obrigatório

### Requirement: Modal resolve assets por nome

O campo de assets SHALL aceitar nomes de assets separados por vírgula. Matching SHALL ser case-insensitive. Cada asset encontrado SHALL adicionar seu dado ao pool. Assets não encontrados SHALL gerar erro listando assets disponíveis.

#### Scenario: Asset encontrado

- **WHEN** jogador submete modal com dados "1d8" e assets "sword"
- **AND** jogador tem asset "Sword d8"
- **THEN** bot adiciona d8 ao pool, rola [8, 8], resultado mostra "Incluido: Sword d8"

#### Scenario: Asset não encontrado

- **WHEN** jogador submete modal com assets "katana"
- **AND** jogador não tem asset com esse nome
- **THEN** bot responde com mensagem efêmera listando assets disponíveis

#### Scenario: Múltiplos assets separados por vírgula

- **WHEN** jogador submete modal com assets "sword, shield"
- **AND** jogador tem ambos os assets
- **THEN** bot adiciona ambos os dados ao pool

#### Scenario: Campo de assets vazio

- **WHEN** jogador submete modal com campo de assets vazio
- **THEN** bot executa rolagem apenas com os dados do campo obrigatório

### Requirement: Resultado da rolagem via modal é público

O resultado da rolagem SHALL ser enviado como mensagem pública (não efêmera), visível para todos no canal. O resultado SHALL incluir post-roll view com botões contextuais (Roll, Undo). A lógica de rolagem (hitches, botch, best_options, opposition_elements) SHALL ser identica à do slash command `/roll`.

#### Scenario: Resultado público com post-roll view

- **WHEN** jogador submete modal com pool válido
- **THEN** bot envia resultado da rolagem como mensagem pública
- **AND** resultado inclui nome do jogador, dados rolados, hitches, best options (se habilitado)
- **AND** mensagem inclui PostRollView com botões Roll e Undo
