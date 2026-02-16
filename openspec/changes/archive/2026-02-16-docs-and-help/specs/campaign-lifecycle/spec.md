## MODIFIED Requirements

### Requirement: Criar campanha via setup

O sistema SHALL permitir criar uma campanha via `/campaign setup` informando nome, jogadores (mencoes Discord), e tipos de stress. Cada canal Discord SHALL ter no maximo uma campanha ativa. O usuario que cria a campanha SHALL ser registrado como GM automaticamente.

#### Scenario: Setup completo

- **WHEN** GM executa `/campaign setup name:"Shadows of Karthun" players:@Alice @Bob @Carol stress_types:"Physical,Mental,Social"`
- **THEN** campanha e criada com 3 jogadores vinculados aos Discord IDs, 3 tipos de stress configurados, GM registrado, e cada jogador inicia com 1 PP e 0 XP.

#### Scenario: Canal ja tem campanha ativa

- **WHEN** usuario executa `/campaign setup` em canal que ja tem campanha ativa
- **THEN** bot recusa e informa que ja existe campanha ativa, sugerindo `/campaign end` primeiro.

#### Scenario: Setup sem jogadores

- **WHEN** usuario executa `/campaign setup` sem mencionar jogadores
- **THEN** bot recusa e informa que pelo menos 1 jogador e necessario.

### Requirement: Encerrar campanha

O sistema SHALL permitir ao GM encerrar a campanha via `/campaign end`. O parametro `confirm` SHALL ser do tipo Choice com opcao "sim", em vez de texto livre. Se omitido, bot exibe aviso pedindo confirmacao.

#### Scenario: GM encerra campanha com confirmacao

- **WHEN** GM executa `/campaign end confirm:sim`
- **THEN** bot remove todos os dados da campanha do banco.

#### Scenario: GM encerra campanha sem confirmacao

- **WHEN** GM executa `/campaign end` sem parametro confirm
- **THEN** bot exibe aviso pedindo para executar novamente com `confirm:sim`.

#### Scenario: Jogador tenta encerrar

- **WHEN** jogador (nao-GM) executa `/campaign end`
- **THEN** bot recusa informando que apenas o GM pode encerrar a campanha.
