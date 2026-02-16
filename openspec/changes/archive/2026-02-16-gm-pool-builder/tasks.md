## 1. Generalizar PoolBuilderView para toggle_items

- [x] 1.1 Renomear parametro `assets_data` para `toggle_items: list[dict]` onde cada item tem `{"id": str, "label": str, "die_size": int}`. Atualizar `_build_components` para usar `item["label"]` no botao e `item["id"]` no tracking (em vez de `asset["name"]` e `asset["id"]`)
- [x] 1.2 Renomear `included_assets: set[int]` para `included_toggles: set[str]` (IDs agora sao strings como `"asset:3"`, `"stress:5"`, `"comp:12"`)
- [x] 1.3 Atualizar `_on_roll` para montar `included_labels` a partir de `toggle_items` usando `item["label"]` em vez de `asset["name"] + die_label`
- [x] 1.4 Atualizar `_on_remove_last` e `_make_asset_callback` (renomear para `_make_toggle_callback`) para usar `item["id"]` (string) em vez de `asset["id"]` (int)
- [x] 1.5 Atualizar history entries: `("asset_on", aid)` e `("asset_off", aid)` passam a usar `("toggle_on", str_id)` e `("toggle_off", str_id)`

## 2. RollStartButton diferencia GM vs jogador

- [x] 2.1 No `RollStartButton.callback`, apos buscar `player`, verificar `has_gm_permission(player)`. Se GM/delegate, chamar `_build_gm_toggles(db, campaign_id)`. Se jogador, manter fluxo atual convertendo assets para formato toggle_items (`{"id": f"asset:{a['id']}", "label": f"{a['name']} {die_label(a['die_size'])}", "die_size": a["die_size"]}`)
- [x] 2.2 Implementar `_build_gm_toggles(db, campaign_id)` como funcao async que: busca todos os players, para cada player busca stress e complications, busca scene complications via `get_active_scene` + `get_scene_complications`. Retorna `list[dict]` no formato toggle_items
- [x] 2.3 Labels de GM seguem formato: stress -> `"NomeJogador: TipoStress dX"`, complication de jogador -> `"NomeJogador: NomeComp dX"`, complication de cena -> `"Cena: NomeComp dX"`
- [x] 2.4 IDs de GM usam prefixo: `"stress:{stress_id}"`, `"comp:{comp_id}"`
- [x] 2.5 Limitar toggle_items a 15 itens (3 rows x 5 botoes). Se exceder, truncar e adicionar mensagem no status_text indicando que ha mais itens

## 3. Resultado do GM via pool builder

- [x] 3.1 Quando GM rola via pool builder, `execute_player_roll` recebe `included_assets` com labels dos toggles incluidos (ex: `["Alice: Physical d8", "Cena: Trapped d6"]`). O resultado mostra "Incluidos: ..." na formatacao
- [x] 3.2 Rolagem do GM SHALL NOT buscar opposition_elements (GM E a oposicao). Adicionar parametro `is_gm_roll: bool = False` em `execute_player_roll`; quando True, pular busca de stress/complications do jogador para opposition_elements
- [x] 3.3 Rolagem do GM SHALL NOT alterar estado (sem PP, sem undo). Verificar que `execute_player_roll` com `is_gm_roll=True` nao injeta nenhum side effect

## 4. Testes

- [x] 4.1 Teste: PoolBuilderView aceita toggle_items com id string e label formatado, botoes mostram label correto
- [x] 4.2 Teste: RollStartButton.callback para GM monta toggles com stress e complications de todos os jogadores + cena
- [x] 4.3 Teste: RollStartButton.callback para jogador monta toggles apenas com assets proprios
- [x] 4.4 Teste: GM sem jogadores com stress ou complications ve pool builder sem toggles
- [x] 4.5 Teste: labels seguem formato correto ("NomeJogador: TipoStress dX", "Cena: NomeComp dX")
- [x] 4.6 Teste: resultado do GM com toggles incluidos mostra "Incluidos: ..." e sem opposition_elements
- [x] 4.7 Teste: resultado do GM sem toggles nao mostra linha de incluidos
- [x] 4.8 Teste: truncamento em 15 toggle items com mensagem indicativa
