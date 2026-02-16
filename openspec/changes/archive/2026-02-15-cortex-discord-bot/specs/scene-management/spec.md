## ADDED Requirements

### Requirement: Iniciar cena

O sistema SHALL permitir ao GM iniciar uma nova cena via `/scene start`. Apenas uma cena pode estar ativa por vez. Se não houver cena ativa, comandos de estado que criam elementos de escopo "cena" SHALL informar que não há cena ativa.

#### Scenario: Iniciar cena nomeada

- **WHEN** GM executa `/scene start name:"Dungeon of Shadows"`
- **THEN** nova cena é criada como ativa, com nome registrado.

#### Scenario: Iniciar cena com cena já ativa

- **WHEN** GM executa `/scene start` enquanto uma cena está ativa
- **THEN** bot informa que há cena ativa e sugere `/scene end` primeiro.

### Requirement: Encerrar cena com limpeza automática

O sistema SHALL, ao encerrar uma cena, remover automaticamente: assets com duração "cena", complications com escopo "cena", e crisis pools da cena. Elementos persistentes (stress, trauma, PP, XP, assets de sessão, doom pool) SHALL ser preservados.

#### Scenario: Encerrar cena normal

- **WHEN** GM executa `/scene end`
- **THEN** bot remove assets de cena, complications de cena, crisis pools. Exibe resumo do que foi removido e do que persiste.

#### Scenario: Encerrar cena como bridge

- **WHEN** GM executa `/scene end bridge:yes`
- **THEN** além da limpeza normal, bot aplica step down em todos os stress de todos os jogadores. Stress d4 é eliminado. Exibe mudanças de stress no resumo.

### Requirement: Resumo de transição de cena

Ao encerrar uma cena, o bot SHALL exibir um resumo textual com: elementos removidos (assets, complications, crisis pools de cena), mudanças de stress (se bridge), e estado persistente relevante (stress restante, doom pool).

#### Scenario: Resumo de transição

- **WHEN** cena é encerrada
- **THEN** bot lista cada elemento removido por nome e die, cada mudança de stress por jogador, e o estado persistente restante.

### Requirement: Consultar cena atual

O sistema SHALL permitir consultar o estado da cena ativa via `/scene info`, exibindo nome, assets de cena, complications de cena, e crisis pools.

#### Scenario: Info sem cena ativa

- **WHEN** qualquer usuário executa `/scene info` sem cena ativa
- **THEN** bot informa que não há cena ativa.

#### Scenario: Info com cena ativa

- **WHEN** qualquer usuário executa `/scene info` com cena "Dungeon of Shadows" ativa
- **THEN** bot exibe nome da cena, assets de cena, complications de cena, e crisis pools com seus dados.
