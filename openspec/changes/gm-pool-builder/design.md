## Context

O PoolBuilderView atual recebe `assets_data: list[dict]` como itens toggleaveis. Para jogadores, sao assets. Para o GM, precisam ser stress e complications de todos os jogadores + complications de cena. A estrutura do toggle e a mesma: nome, die_size, e um identificador. A diferenca e a origem dos dados e o label (que precisa incluir o nome do jogador dono).

## Goals / Non-Goals

**Goals:**
- GM usa o mesmo pool builder (botao Roll) para montar pools de oposicao
- Toggles do GM mostram stress e complications de todos os jogadores + complications de cena
- Labels identificam o dono: "Alice: Physical d8", "Cena: Trapped d6"
- Jogador continua vendo apenas seus assets como toggles
- Resultado da rolagem do GM identifica os elementos incluidos

**Non-Goals:**
- Substituir /gmroll (continua como alternativa via slash command)
- Mostrar doom pool no pool builder (doom tem fluxo proprio)
- Mostrar assets de cena pro jogador (jogador ve so os seus)
- Tracking de quais dados foram usados na oposicao (e efemero)

## Decisions

### Decision 1: Generalizar toggles do PoolBuilderView

Em vez de `assets_data`, o PoolBuilderView recebe `toggle_items: list[dict]` onde cada item tem `{"id": str, "label": str, "die_size": int}`. O `id` e uma string unica (ex: `"stress:5"`, `"comp:12"`, `"asset:3"`). O `label` ja vem formatado pelo caller ("Alice: Physical d8" ou "Sword d8").

**Alternativa descartada:** Ter duas subclasses (PlayerPoolBuilder, GMPoolBuilder). Descartado porque a unica diferenca e o conteudo dos toggles, nao o comportamento.

### Decision 2: RollStartButton.callback diferencia GM vs jogador

O callback verifica `has_gm_permission(player)`. Se GM/delegate, busca stress + complications de todos + complications de cena e monta toggle_items. Se jogador comum, busca assets do jogador como hoje.

### Decision 3: Resultado do GM usa mesma execute_player_roll

O GM que rola via pool builder usa `execute_player_roll` com `included_assets` substituido por labels dos toggles incluidos (ex: "Incluidos: Alice: Physical d8, Cena: Trapped d6"). Nao ha injecao de estado (sem PP, sem undo de stress) -- e uma rolagem informativa.

### Decision 4: Scene complications via query existente

`db.get_scene_complications(scene_id)` ja existe e retorna complications com `player_name`. Para complications de cena (`player_id=NULL`), `player_name` e NULL, entao o label usa "Cena" como prefixo.

## Risks / Trade-offs

**[Limite de 15 toggles]** Com 5 jogadores muito castigados, podemos exceder 15 items (3 rows x 5). Mitigacao: truncar em 15 com mensagem indicando que ha mais items. Na pratica, cenarios com >15 stress+complications simultaneos sao raros.

**[GM que tambem e jogador]** Um delegate que clica Roll ve o painel de GM (stress/complications de todos) em vez dos seus assets. Isso e intencional: o delegate tem permissao de GM e o fluxo de jogador esta disponivel via /roll.
