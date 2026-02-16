## MODIFIED Requirements

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
