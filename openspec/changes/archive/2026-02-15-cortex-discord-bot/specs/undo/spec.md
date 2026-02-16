## ADDED Requirements

### Requirement: Reverter última ação

O sistema SHALL manter um log de ações de estado por campanha. `/undo` SHALL reverter a última ação não-desfeita, restaurando o estado anterior. Apenas o GM ou o autor original da ação SHALL poder desfazê-la.

#### Scenario: Undo de adição de stress

- **WHEN** GM adicionou stress Physical d8 a Alice e executa `/undo`
- **THEN** stress Physical d8 é removido de Alice. Bot confirma "Desfeito: stress Physical d8 adicionado a Alice."

#### Scenario: Undo de remoção de asset

- **WHEN** Alice removeu asset "Big Wrench" d6 e executa `/undo`
- **THEN** asset "Big Wrench" d6 é restaurado para Alice.

#### Scenario: Undo de step up

- **WHEN** última ação foi step up de stress Mental de d6 para d8 e GM executa `/undo`
- **THEN** stress Mental retorna a d6.

#### Scenario: Nada para desfazer

- **WHEN** usuário executa `/undo` sem ações no log (ou todas já desfeitas)
- **THEN** bot informa que não há ações para desfazer.

#### Scenario: Jogador tenta desfazer ação de outro

- **WHEN** Alice tenta `/undo` mas a última ação foi do GM em Bob
- **THEN** bot recusa, informando que apenas o GM ou o autor da ação pode desfazê-la. Para Alice, bot busca a última ação feita por ela.

### Requirement: Rolagens não são desfeitas

Rolagens de dados SHALL NOT ser registradas no log de undo. Apenas operações de estado (add, remove, step up, step down de assets, stress, complications, PP, XP, hero dice, doom pool, crisis pools) são reversíveis.

#### Scenario: Undo pula rolagens

- **WHEN** última ação foi uma rolagem e antes dela Alice adicionou um asset
- **THEN** `/undo` desfaz a adição do asset, ignorando a rolagem.

### Requirement: Transições de cena não são desfeitas

Transições de cena (`/scene end`) SHALL NOT ser reversíveis via `/undo`. A limpeza de cena é uma operação estrutural, não uma ação de estado.

#### Scenario: Undo após transição de cena

- **WHEN** GM encerrou cena e depois executa `/undo`
- **THEN** bot busca última ação de estado anterior à transição de cena. Se não houver, informa que não há ações para desfazer.
