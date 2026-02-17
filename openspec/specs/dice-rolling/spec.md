## ADDED Requirements

### Requirement: Rolar pool de dados

O sistema SHALL permitir rolagem de dice pool via `/roll` com dados informados como parâmetro. O formato de entrada SHALL aceitar notação padrão (1d8, 2d6, etc.) separada por espaços. O bot SHALL rolar todos os dados e exibir cada resultado individual com tamanho e valor.

#### Scenario: Rolagem simples

- **WHEN** Alice executa `/roll dice:1d8 1d10 1d6`
- **THEN** bot rola 3 dados (d8, d10, d6), exibe cada resultado com tamanho e valor rolado em texto linear.

#### Scenario: Múltiplos dados do mesmo tamanho

- **WHEN** Alice executa `/roll dice:3d8 1d6`
- **THEN** bot rola 4 dados (d8, d8, d8, d6), exibe cada resultado individualmente.

### Requirement: Sugerir inclusão de elementos rastreados

Ao rolar, o bot SHALL informar ao jogador quais elementos rastreados estão disponíveis para inclusão no pool. O jogador SHALL poder incluir elementos via parâmetro `include` no comando, ou o bot SHALL apresentar os elementos disponíveis após o comando para inclusão opcional.

#### Scenario: Rolagem com inclusão explícita

- **WHEN** Alice tem asset "Big Wrench d6" e executa `/roll dice:1d8 1d10 include:big-wrench`
- **THEN** bot adiciona d6 do asset ao pool, rola d8+d10+d6, identifica quais dados vieram de assets no resultado.

#### Scenario: Rolagem sem inclusão, bot informa disponíveis

- **WHEN** Alice tem assets e stress rastreados e executa `/roll dice:1d8 1d10` sem `include`
- **THEN** bot rola d8+d10 e exibe abaixo do resultado: "Elementos disponíveis: Asset Big Wrench d6, Asset Lucky Charm d8. Stress Physical d8 e Complication Broken Arm d6 no pool da oposição."

### Requirement: Identificar hitches e botches

O bot SHALL identificar dados que rolaram 1 (hitches) e reportar no resultado. Se todos os dados rolarem 1, SHALL identificar como botch. Hitches SHALL ser excluídos das sugestões de total e effect die.

#### Scenario: Rolagem com hitch

- **WHEN** resultado contém d8:1 entre outros dados
- **THEN** bot marca d8 como hitch, informa "Hitch no d8. GM pode dar PP e criar complication d6, ou adicionar d6 ao Doom Pool."

#### Scenario: Botch

- **WHEN** todos os dados rolam 1
- **THEN** bot informa "Botch. Total zero. GM cria complication d6 grátis, step up por hitch adicional."

### Requirement: Sugerir melhor combinação (best mode)

Quando best mode está habilitado, o bot SHALL primeiro exibir todos os resultados individuais dos dados com tamanho e valor, e depois calcular e exibir as combinações mais relevantes de 2 dados para total + 1 dado para effect die. SHALL exibir pelo menos: a combinação com maior total e a combinação com maior effect die. Dados que rolaram 1 (hitches) SHALL ser excluídos das sugestões mas SHALL aparecer na lista de resultados individuais marcados como hitch.

#### Scenario: Best mode com 4 dados

- **WHEN** best mode habilitado e resultado é d10:7, d8:5, d6:4, d6:3
- **THEN** bot exibe primeiro todos os resultados: "d10 tirou 7, d8 tirou 5, d6 tirou 4, d6 tirou 3."
- **AND** depois exibe "Melhor total: d10 com 7 mais d8 com 5, igual a 12. Effect die: d6." e "Maior effect: d10 com 7 mais d6 com 3, igual a 10. Effect die: d8."

#### Scenario: Best mode com hitches

- **WHEN** best mode habilitado e d6:1 entre os resultados
- **THEN** bot exibe todos os resultados individuais incluindo "d6 tirou 1 (hitch)"
- **AND** d6 com hitch é excluído das combinações sugeridas para total e effect die.

#### Scenario: Best mode desabilitado

- **WHEN** best mode desabilitado
- **THEN** bot exibe apenas os resultados individuais sem sugestões de combinação.

### Requirement: Comparar com dificuldade

O bot SHALL aceitar dificuldade como parâmetro opcional. Quando informada, SHALL comparar o melhor total com a dificuldade e indicar sucesso (total > dificuldade), falha (total <= dificuldade), e heroic success (total >= dificuldade + 5).

#### Scenario: Sucesso contra dificuldade

- **WHEN** melhor total é 12 e dificuldade informada é 11
- **THEN** bot indica "Sucesso, margem 1."

#### Scenario: Heroic success

- **WHEN** melhor total é 17 e dificuldade é 11
- **THEN** bot indica "Heroic success, margem 6. Effect die faz step up uma vez."

#### Scenario: Falha

- **WHEN** melhor total é 10 e dificuldade é 11
- **THEN** bot indica "Falha por 1."

#### Scenario: Sem dificuldade informada

- **WHEN** jogador rola sem informar dificuldade
- **THEN** bot exibe resultados e sugestões sem comparação de dificuldade.

### Requirement: Dados adicionais via PP

O bot SHALL aceitar parâmetro `extra` para dados adicionais incluídos via gasto de PP. Quando usado, SHALL decrementar PP do jogador automaticamente (1 PP por dado extra) e incluir os dados no pool.

#### Scenario: Adicionar dado extra com PP

- **WHEN** Alice com 3 PP executa `/roll dice:1d8 1d10 extra:1d6`
- **THEN** bot gasta 1 PP de Alice (PP passa a 2), adiciona d6 ao pool, rola d8+d10+d6.

#### Scenario: PP insuficiente para extra

- **WHEN** Alice com 0 PP tenta `/roll dice:1d8 extra:1d6`
- **THEN** bot informa que Alice não tem PP suficiente para dados extras.

### Requirement: Botao Roll executa rolagem direta

O botao Roll SHALL abrir um pool builder interativo com conteudo diferenciado por papel. Para jogadores, o pool builder SHALL mostrar botoes de dado (d4-d12) e assets do jogador como toggles. Para GM/delegates, o pool builder SHALL mostrar botoes de dado (d4-d12) e stress + complications de todos os jogadores + complications de cena como toggles. Cada toggle SHALL incluir o nome do dono no label.

#### Scenario: Jogador abre pool builder com seus assets

- **WHEN** jogador comum clica botao "Roll"
- **THEN** pool builder mostra botoes de dado (d4-d12) e assets do jogador como toggles
- **AND** labels dos assets seguem formato "NomeAsset dX"

#### Scenario: GM abre pool builder com stress e complications de todos

- **WHEN** GM clica botao "Roll"
- **THEN** pool builder mostra botoes de dado (d4-d12) e toggles com stress e complications de todos os jogadores + complications de cena
- **AND** labels seguem formato "NomeJogador: TipoStress dX" ou "NomeJogador: NomeComp dX"
- **AND** complications de cena usam "Cena: NomeComp dX"

#### Scenario: GM sem jogadores com stress ou complications

- **WHEN** GM clica "Roll" e nenhum jogador tem stress ou complications
- **THEN** pool builder mostra apenas botoes de dado e controles, sem row de toggles

#### Scenario: Delegate abre pool builder como GM

- **WHEN** delegate clica botao "Roll"
- **THEN** pool builder mostra visao de GM (stress/complications de todos)
- **AND** SHALL NOT mostrar assets do delegate
