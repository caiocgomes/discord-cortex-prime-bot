## ADDED Requirements

### Requirement: Gerenciar doom pool

Quando o módulo doom pool está habilitado, o sistema SHALL permitir ao GM adicionar, remover, step up e step down dados no doom pool. O doom pool SHALL ser visível a todos os jogadores via `/info`.

#### Scenario: Adicionar dado ao doom pool

- **WHEN** GM executa `/doom add die:d6`
- **THEN** d6 é adicionado ao doom pool.

#### Scenario: Step up dado do doom pool

- **WHEN** doom pool contém d6 e GM executa `/doom stepup die:d6`
- **THEN** d6 no doom pool passa a d8.

#### Scenario: Remover dado do doom pool

- **WHEN** GM executa `/doom remove die:d8`
- **THEN** um d8 é removido do doom pool. Se não houver d8, bot informa.

#### Scenario: Doom pool desabilitado

- **WHEN** módulo doom pool está desabilitado e GM executa `/doom add die:d6`
- **THEN** bot informa que doom pool não está habilitado nesta campanha.

### Requirement: Rolar doom pool como dificuldade

O sistema SHALL permitir ao GM rolar o doom pool (todos ou alguns dados) e usar o resultado como dificuldade para o próximo test.

#### Scenario: Rolar doom pool completo

- **WHEN** GM executa `/doom roll`
- **THEN** bot rola todos os dados do doom pool, exibe resultados, sugere melhor total (soma de 2 dados) como dificuldade. Dados rolados permanecem no pool.

#### Scenario: Rolar doom pool parcial

- **WHEN** GM executa `/doom roll dice:d8 d6` (selecionando dados específicos)
- **THEN** bot rola apenas d8 e d6 do pool, sugere total como dificuldade.

#### Scenario: GM gasta dado do doom pool no total

- **WHEN** GM executa `/doom spend die:d6` após rolar doom pool
- **THEN** d6 é removido do doom pool e seu resultado é somado ao total de dificuldade.

### Requirement: Gerenciar crisis pools

O sistema SHALL suportar crisis pools nomeados, vinculados à cena ativa. Crisis pools SHALL ter operações de add, remove e roll. Crisis pools SHALL ser removidos automaticamente ao encerrar a cena.

#### Scenario: Criar crisis pool

- **WHEN** GM executa `/crisis add name:"Crumbling Walls" dice:d8 d6`
- **THEN** crisis pool "Crumbling Walls" é criado na cena ativa com d8 e d6.

#### Scenario: Rolar crisis pool como dificuldade

- **WHEN** GM executa `/crisis roll name:"Crumbling Walls"`
- **THEN** bot rola os dados do crisis pool e exibe resultado.

#### Scenario: Remover dado de crisis pool

- **WHEN** GM executa `/crisis remove name:"Crumbling Walls" die:d8`
- **THEN** d8 é removido do crisis pool. Se pool ficar vazio, bot informa que o crisis foi resolvido.

#### Scenario: Crisis pool sem cena ativa

- **WHEN** GM executa `/crisis add` sem cena ativa
- **THEN** bot informa que é necessário iniciar uma cena primeiro.
