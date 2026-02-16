## ADDED Requirements

### Requirement: Output em texto linear estruturado

Todas as respostas do bot SHALL ser formatadas como texto linear, sem box art, sem ASCII art, sem layout espacial que dependa de posicionamento visual. Informações SHALL ser apresentadas em frases completas ou listas simples separadas por quebras de linha.

#### Scenario: Resultado de rolagem acessível

- **WHEN** bot exibe resultado de rolagem
- **THEN** output segue formato: "[Jogador] rolou [N] dados. [die_size]: [valor], [die_size]: [valor], ... [análise em texto corrido]."

#### Scenario: Info da campanha acessível

- **WHEN** bot exibe `/info`
- **THEN** output segue formato: "Campanha: [nome]. Cena atual: [nome ou nenhuma]. [Para cada jogador:] [nome]: [stress/assets/complications em texto]. PP [N], XP [N]. [Doom pool, se habilitado:] Doom Pool: [lista de dados]."

### Requirement: Sem dependência de emojis para informação

O bot SHALL NOT usar emojis como único veículo de informação. Emojis decorativos são permitidos apenas se acompanhados de texto equivalente. Status (sucesso, falha, aviso) SHALL ser comunicado em palavras.

#### Scenario: Sucesso sem emoji obrigatório

- **WHEN** bot indica sucesso numa rolagem
- **THEN** output diz "Sucesso, margem [N]." em texto, sem depender de checkmark visual.

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

### Requirement: Autocomplete em parâmetros de comandos

Parâmetros que referenciam elementos existentes (nomes de jogadores, assets, tipos de stress, crisis pools) SHALL usar autocomplete do Discord para permitir seleção via teclado.

#### Scenario: Autocomplete de nome de jogador

- **WHEN** GM digita `/stress add player:` e começa a digitar "Al"
- **THEN** Discord sugere "Alice" via autocomplete, selecionável por teclado.

#### Scenario: Autocomplete de asset

- **WHEN** Alice digita `/roll include:` e começa a digitar "wr"
- **THEN** Discord sugere "Big Wrench" via autocomplete.

### Requirement: Feedback textual para toda ação

Toda ação executada SHALL receber confirmação em texto descrevendo o que foi feito. O feedback SHALL ser suficiente para um usuário de screen reader entender o estado resultante sem consultar `/info`.

#### Scenario: Confirmação de adição de stress

- **WHEN** GM executa `/stress add player:Alice type:Physical die:d8`
- **THEN** bot responde "Stress Physical d8 adicionado a Alice. Alice agora tem: Physical d8, Mental d6. PP 3."

#### Scenario: Confirmação de fim de cena

- **WHEN** GM executa `/scene end bridge:yes`
- **THEN** bot descreve em texto cada elemento removido, cada step down de stress por jogador, e o estado persistente.
