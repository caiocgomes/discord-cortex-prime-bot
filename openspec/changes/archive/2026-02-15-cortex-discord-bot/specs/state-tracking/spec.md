## ADDED Requirements

### Requirement: Gerenciar assets

O sistema SHALL suportar operações de add, step up, step down e remove em assets. Assets SHALL ter nome, die size (d4-d12), dono (jogador ou cena), e duração (cena ou sessão). Jogadores SHALL gerenciar seus próprios assets; GM SHALL gerenciar qualquer asset.

#### Scenario: Adicionar asset de cena para si mesmo

- **WHEN** Alice executa `/asset add name:"Improvised Torch" die:d6`
- **THEN** asset "Improvised Torch" d6 é criado para Alice com duração "cena".

#### Scenario: Adicionar asset de sessão

- **WHEN** Alice executa `/asset add name:"Magic Ring" die:d8 duration:session`
- **THEN** asset "Magic Ring" d8 é criado para Alice com duração "sessão" (persiste entre cenas).

#### Scenario: Step up de asset

- **WHEN** Alice executa `/asset stepup name:"Improvised Torch"`
- **THEN** asset passa de d6 para d8.

#### Scenario: Step up além de d12

- **WHEN** usuário tenta step up de asset que já é d12
- **THEN** bot informa que d12 é o máximo.

#### Scenario: Step down de asset d4

- **WHEN** usuário tenta step down de asset d4
- **THEN** asset é eliminado (step down de d4 remove o dado).

#### Scenario: GM cria asset de cena (sem dono)

- **WHEN** GM executa `/asset add name:"Slippery Floor" die:d8 scene_asset:yes`
- **THEN** asset de cena "Slippery Floor" d8 é criado sem dono específico.

### Requirement: Gerenciar stress

O sistema SHALL suportar operações de add, step up, step down e remove em stress. Tipos de stress são os configurados no setup da campanha. Cada jogador SHALL ter no máximo um die por tipo de stress. Apenas GM SHALL adicionar/remover stress em outros jogadores.

#### Scenario: GM adiciona stress

- **WHEN** GM executa `/stress add player:Alice type:Physical die:d8`
- **THEN** stress Physical d8 é registrado para Alice.

#### Scenario: Stress substitui menor existente

- **WHEN** Alice tem stress Physical d6 e GM adiciona Physical d8
- **THEN** stress Physical de Alice passa a d8 (substitui).

#### Scenario: Stress step up em existente igual ou maior

- **WHEN** Alice tem stress Physical d8 e GM adiciona Physical d6 (igual ou menor que existente)
- **THEN** stress Physical de Alice faz step up para d10 (regra Cortex: incoming <= existente causa step up).

#### Scenario: Stress além de d12

- **WHEN** stress de um jogador faz step up além de d12
- **THEN** bot informa que o jogador está stressed out (taken out). Se trauma está habilitado, cria trauma d6 do mesmo tipo.

#### Scenario: Jogador remove próprio stress

- **WHEN** Alice executa `/stress remove type:Physical`
- **THEN** stress Physical de Alice é removido.

### Requirement: Gerenciar trauma

Quando o módulo de trauma está habilitado, o sistema SHALL suportar trauma como extensão de stress. Trauma SHALL ter as mesmas operações de stress (add, step up, step down, remove). Trauma além de d12 SHALL indicar remoção permanente do personagem.

#### Scenario: Trauma criado por stress out

- **WHEN** stress de Alice faz step up além de d12 e trauma está habilitado
- **THEN** stress de Alice fica em d12 (stressed out) e trauma d6 do mesmo tipo é criado.

#### Scenario: Trauma além de d12

- **WHEN** trauma de Alice faz step up além de d12
- **THEN** bot informa que o personagem sofre remoção permanente.

### Requirement: Gerenciar complications

O sistema SHALL suportar operações de add, step up, step down e remove em complications. Complications SHALL ter nome, die size, e escopo (cena ou persistente). GM SHALL gerenciar complications de qualquer jogador. Jogadores SHALL poder remover/step down suas próprias complications (recovery).

#### Scenario: GM cria complication em jogador

- **WHEN** GM executa `/complication add player:Alice name:"Broken Arm" die:d6`
- **THEN** complication "Broken Arm" d6 é criada para Alice.

#### Scenario: Complication step up além de d12

- **WHEN** complication faz step up além de d12
- **THEN** bot informa que o jogador está taken out.

#### Scenario: Complication de cena

- **WHEN** GM executa `/complication add name:"Slippery Floor" die:d8 scene:yes`
- **THEN** complication de cena "Slippery Floor" d8 é criada, será removida ao encerrar cena.

### Requirement: Gerenciar plot points

O sistema SHALL rastrear plot points por jogador. Operações: add e remove. Jogadores SHALL gerenciar seus próprios PP. GM SHALL gerenciar PP de qualquer jogador. PP nunca SHALL ficar negativo.

#### Scenario: Jogador gasta PP

- **WHEN** Alice com 3 PP executa `/pp remove amount:1`
- **THEN** PP de Alice passa a 2.

#### Scenario: PP insuficiente

- **WHEN** Alice com 0 PP tenta `/pp remove amount:1`
- **THEN** bot informa que Alice não tem PP suficiente.

#### Scenario: GM dá PP

- **WHEN** GM executa `/pp add player:Alice amount:1`
- **THEN** PP de Alice aumenta em 1.

### Requirement: Gerenciar XP

O sistema SHALL rastrear XP por jogador com operações add e remove. Qualquer jogador SHALL gerenciar seu próprio XP. GM SHALL gerenciar XP de qualquer jogador. XP nunca SHALL ficar negativo.

#### Scenario: Adicionar XP

- **WHEN** Alice executa `/xp add amount:3`
- **THEN** XP de Alice aumenta em 3.

### Requirement: Gerenciar hero dice

Quando o módulo de hero dice está habilitado, o sistema SHALL permitir bancar e usar hero dice por jogador. Hero dice SHALL ter die size. Operações: bank (adicionar) e use (remover).

#### Scenario: Bancar hero die

- **WHEN** Alice executa `/hero bank die:d8`
- **THEN** hero die d8 é adicionado ao banco de Alice.

#### Scenario: Usar hero die

- **WHEN** Alice executa `/hero use die:d8`
- **THEN** hero die d8 é removido do banco. Bot informa para rolar e somar ao total.

#### Scenario: Hero dice desabilitado

- **WHEN** módulo hero dice está desabilitado e jogador executa `/hero bank die:d8`
- **THEN** bot informa que hero dice não está habilitado nesta campanha.
