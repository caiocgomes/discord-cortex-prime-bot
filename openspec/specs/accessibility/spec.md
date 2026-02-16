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

Toda operação do bot SHALL ser executável via um único slash command com parâmetros, sem necessidade de interação com componentes visuais (botões, selects, modals) como etapa obrigatória.

#### Scenario: Rolagem completa sem interação visual

- **WHEN** jogador executa `/roll dice:1d8 1d10 include:wrench difficulty:11`
- **THEN** bot executa rolagem completa e exibe resultado sem apresentar botões ou menus que precisem ser clicados.

#### Scenario: Componentes visuais como opcional

- **WHEN** bot apresenta botões após uma ação (ex: "Incluir assets?")
- **THEN** a operação já foi executada ou é executável sem clicar nos botões. Botões são atalhos opcionais.

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
