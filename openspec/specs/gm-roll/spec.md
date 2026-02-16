## ADDED Requirements

### Requirement: Comando /gmroll para rolagem sem contexto de jogador
O sistema SHALL fornecer o comando `/gmroll` que rola dados sem injetar estado pessoal do executor (sem opposition, sem assets, sem complications). O comando MUST ser restrito a usuários com `is_gm=1` ou `is_delegate=1`.

#### Scenario: GM roll básico
- **WHEN** o GM ou delegado executa `/gmroll dice:2d8 1d10`
- **THEN** o sistema rola os dados, mostra resultados individuais, hitches e botch, sem incluir stress, complications ou assets do executor

#### Scenario: GM roll com nome de NPC
- **WHEN** o delegado executa `/gmroll dice:2d8 1d10 name:Guarda da Torre`
- **THEN** o output mostra "Guarda da Torre rolou 3 dados." em vez de "GM rolou 3 dados."

#### Scenario: GM roll sem nome
- **WHEN** o delegado executa `/gmroll dice:2d8 1d10` sem parâmetro `name`
- **THEN** o output mostra "GM rolou 2 dados."

#### Scenario: Jogador comum tenta usar gmroll
- **WHEN** um jogador sem `is_gm` e sem `is_delegate` executa `/gmroll dice:1d8`
- **THEN** o comando retorna erro "Apenas o GM ou delegados podem usar este comando."

### Requirement: GM roll calcula best options
O `/gmroll` SHALL calcular e exibir best options (melhor total + melhor effect die) quando `best_mode` está habilitado na campanha e o roll não é botch, usando a mesma lógica de `calculate_best_options`.

#### Scenario: GM roll com best_mode habilitado
- **WHEN** o delegado executa `/gmroll dice:2d8 1d10 1d6` e `best_mode` está ligado
- **THEN** o output inclui as melhores combinações de 2 dados com effect die

#### Scenario: GM roll com best_mode desabilitado
- **WHEN** o delegado executa `/gmroll dice:2d8 1d10` e `best_mode` está desligado
- **THEN** o output mostra resultados individuais e total padrão (dois maiores) sem lista de best options

### Requirement: GM roll aceita parâmetro difficulty
O `/gmroll` SHALL aceitar um parâmetro opcional `difficulty` para comparar o total contra um número alvo, exibindo sucesso/falha/heroic success.

#### Scenario: GM roll com difficulty
- **WHEN** o delegado executa `/gmroll dice:2d8 1d10 difficulty:10`
- **THEN** o output compara o melhor total contra 10 e indica sucesso ou falha com margem

### Requirement: GM roll não gasta PP nem altera estado
O `/gmroll` SHALL NOT aceitar parâmetro `extra` (dados comprados com PP) nem alterar qualquer estado no banco de dados. É uma operação puramente de leitura.

#### Scenario: GM roll é stateless
- **WHEN** o delegado executa `/gmroll dice:2d8 1d10`
- **THEN** nenhum registro é criado ou modificado no banco de dados

### Requirement: GM pode rolar via pool builder

O GM SHALL poder usar o pool builder interativo (botao Roll) como alternativa ao /gmroll. O resultado SHALL identificar quais elementos de oposicao foram incluidos no pool. O /gmroll SHALL continuar funcionando como fallback via slash command.

#### Scenario: GM rola com toggles de oposicao incluidos

- **WHEN** GM monta pool com d8, d10 e inclui toggles "Alice: Physical d8" e "Cena: Trapped d6"
- **THEN** bot rola pool [8, 10, 8, 6]
- **AND** resultado mostra "Incluidos: Alice: Physical d8, Cena: Trapped d6"
- **AND** resultado e enviado como mensagem publica com PostRollView

#### Scenario: GM rola sem toggles

- **WHEN** GM monta pool com d8, d10 sem incluir nenhum toggle
- **THEN** bot rola pool [8, 10]
- **AND** resultado nao mostra linha de incluidos

#### Scenario: Resultado do GM nao injeta estado

- **WHEN** GM rola via pool builder
- **THEN** rolagem SHALL NOT alterar stress, complications, PP ou qualquer estado
- **AND** rolagem SHALL NOT ter opposition_elements no resultado (GM e a oposicao)
