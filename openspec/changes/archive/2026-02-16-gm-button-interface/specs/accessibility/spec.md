## MODIFIED Requirements

### Requirement: Toda funcionalidade via slash command direto

Toda operação do bot SHALL ser executável via slash command com parâmetros OU via buttons/select menus. Slash commands continuam como interface completa. Buttons e select menus oferecem interface alternativa completa para operações de gameplay, permitindo uso do bot sem digitar slash commands.

#### Scenario: Rolagem completa sem interação visual

- **WHEN** jogador executa `/roll dice:1d8 1d10 include:wrench difficulty:11`
- **THEN** bot executa rolagem completa e exibe resultado sem exigir cliques adicionais.

#### Scenario: Componentes visuais como interface alternativa

- **WHEN** bot apresenta botões após uma ação
- **THEN** cada botão inicia uma ação completa via callbacks, sem exigir slash commands.
- **AND** a mesma ação permanece disponível via slash command correspondente.

#### Scenario: Operação completa via botões sem slash

- **WHEN** GM usa exclusivamente botões e select menus durante uma sessão inteira
- **THEN** todas as operações de gameplay (scene, roll, stress, asset, complication, doom, undo) são executáveis sem digitar nenhum slash command.
