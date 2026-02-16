## ADDED Requirements

### Requirement: Criar campanha via setup

O sistema SHALL permitir criar uma campanha via `/setup` informando nome, jogadores (menções Discord), e tipos de stress. Cada canal Discord SHALL ter no máximo uma campanha ativa. O usuário que cria a campanha SHALL ser registrado como GM automaticamente.

#### Scenario: Setup completo

- **WHEN** GM executa `/setup name:"Shadows of Karthun" players:@Alice @Bob @Carol stress_types:"Physical,Mental,Social"`
- **THEN** campanha é criada com 3 jogadores vinculados aos Discord IDs, 3 tipos de stress configurados, GM registrado, e cada jogador inicia com 1 PP e 0 XP.

#### Scenario: Canal já tem campanha ativa

- **WHEN** usuário executa `/setup` em canal que já tem campanha ativa
- **THEN** bot recusa e informa que já existe campanha ativa, sugerindo `/campaign end` primeiro.

#### Scenario: Setup sem jogadores

- **WHEN** usuário executa `/setup` sem mencionar jogadores
- **THEN** bot recusa e informa que pelo menos 1 jogador é necessário.

### Requirement: Configurar módulos opcionais

O sistema SHALL permitir ativar/desativar módulos no setup: doom pool, hero dice, trauma, best mode. Todos os módulos SHALL ter um default (doom pool: off, hero dice: off, trauma: off, best mode: on).

#### Scenario: Ativar doom pool

- **WHEN** GM executa `/setup name:"Game" players:@Alice stress_types:"Physical" doom_pool:yes`
- **THEN** campanha é criada com doom pool habilitado, iniciando com pool vazio.

#### Scenario: Defaults aplicados

- **WHEN** GM executa `/setup` sem especificar módulos
- **THEN** doom pool desabilitado, hero dice desabilitado, trauma desabilitado, best mode habilitado.

### Requirement: Vincular jogadores a Discord IDs

Cada jogador registrado na campanha SHALL ser vinculado ao seu Discord user ID. O bot SHALL identificar automaticamente o jogador pelo autor do comando, sem necessidade de informar nome.

#### Scenario: Jogador executa comando

- **WHEN** Alice (Discord ID vinculado) executa `/roll dice:1d8`
- **THEN** bot identifica Alice automaticamente e usa o estado dela (assets, stress, PP, etc.).

#### Scenario: Usuário não registrado na campanha

- **WHEN** um usuário não registrado na campanha executa um comando de jogo
- **THEN** bot informa que o usuário não é jogador registrado nesta campanha.

### Requirement: Permissões por papel

Jogadores SHALL modificar apenas o próprio estado. O GM SHALL modificar o estado de qualquer jogador e acessar comandos restritos (scene, doom pool, adicionar stress em outros).

#### Scenario: Jogador tenta modificar outro

- **WHEN** Alice executa `/stress add player:Bob type:Physical die:d8`
- **THEN** bot recusa informando que apenas o GM pode modificar estado de outro jogador.

#### Scenario: GM modifica estado de jogador

- **WHEN** GM executa `/stress add player:Alice type:Physical die:d8`
- **THEN** stress Physical d8 é adicionado a Alice.

### Requirement: Visualizar estado da campanha

O sistema SHALL fornecer `/info` para exibir o estado completo da campanha em texto estruturado.

#### Scenario: Info com campanha ativa

- **WHEN** qualquer jogador ou GM executa `/info`
- **THEN** bot exibe: nome da campanha, cena ativa (se houver), estado de cada jogador (stress, assets, complications, PP, XP, hero dice), doom pool (se habilitado), complications de cena.

### Requirement: Encerrar campanha

O sistema SHALL permitir ao GM encerrar a campanha via `/campaign end`, removendo todos os dados associados.

#### Scenario: GM encerra campanha

- **WHEN** GM executa `/campaign end`
- **THEN** bot pede confirmação, e ao confirmar, remove todos os dados da campanha do banco.

#### Scenario: Jogador tenta encerrar

- **WHEN** jogador (não-GM) executa `/campaign end`
- **THEN** bot recusa informando que apenas o GM pode encerrar a campanha.
