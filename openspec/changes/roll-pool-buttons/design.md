## Context

O bot usa componentes de UI do Discord (botões e selects) para fluxos de jogo. O usuário primário é um GM cego usando NVDA no Windows. O NVDA tem um bug documentado (nvaccess/nvda#18224) onde `aria-selected` não é anunciado em selects, e o Discord não implementa aria-live em mensagens editadas. Isso torna selects (especialmente multi-selects) e padrões de atualização incremental problemáticos para o screen reader.

O sistema atual funciona em duas camadas paralelas: slash commands com autocomplete (cobertura total de funcionalidade) e views com botões/selects (atalhos visuais). As views usam select menus para seleção de dados, jogadores e tipos. Os botões pós-ação desaparecem quando o chat rola, forçando o GM a digitar slash commands para recuperar contexto.

Componentes relevantes do discord.py 2.x:
- `discord.ui.Modal` com `discord.ui.TextInput` para formulários com focus trap nativo
- `discord.ui.Button` com `DynamicItem` para botões persistentes que sobrevivem a restarts
- `discord.ui.Select` com até 25 opções
- `discord.ui.View` com max 5 ActionRows, cada uma com até 5 botões ou 1 select

## Goals / Non-Goals

**Goals:**

- Eliminar uso de multi-select (DicePoolSelectView) que é inutilizável com NVDA
- Substituir selects de valor único por botões em todos os fluxos onde <= 5 opções
- Implementar dice pool via Modal com TextInput, reaproveitando `parse_dice_notation`
- Adicionar `/menu` que gera painel contextual de ações como mensagem pública pinável
- Manter 100% de cobertura via slash commands (botões são conveniência, não substituição)

**Non-Goals:**

- Trocar a arquitetura de views/DynamicItem existente. O padrão de DynamicItem com regex template funciona e vai ser mantido.
- Suportar pools incrementais via botões. A análise de acessibilidade demonstrou que re-renders com perda de foco no NVDA são piores que um modal.
- Fazer o `/menu` atualizar automaticamente a mensagem (aria-live não funciona, o usuário não ouviria a mudança).
- Modificar slash commands existentes. Eles permanecem intactos como interface primária.

## Decisions

### 1. Dice pool: Modal com TextInput em vez de select multi-value

**Escolha:** `discord.ui.Modal` com dois campos `TextInput`.

**Alternativas consideradas:**
- Botões incrementais (d4, d6, ..., cada clique adiciona ao pool) -- descartado porque cada clique gera `edit_message`, o NVDA perde foco, e o Discord não anuncia a mudança via aria-live. Seria 8-12 interações com 3 re-renders para um pool de 3 dados.
- Manter select multi-value -- descartado porque `aria-selected` não é anunciado pelo NVDA. O usuário não sabe quais opções marcou.

**Implementação:**

O `RollStartButton.callback` abre o modal em vez de criar `DicePoolSelectView`. O modal tem:
- Campo 1 (obrigatório): "Dados" com placeholder "Ex: 2d8 1d6 1d10". `TextInput(style=TextStyle.short)`.
- Campo 2 (opcional): "Assets para incluir" com placeholder dinâmico listando assets ativos do jogador (ex: "Disponiveis: Sword d8, Shield d6"). `TextInput(style=TextStyle.short, required=False)`.

O `on_submit` do modal chama `parse_dice_notation` no campo 1, resolve assets pelo nome no campo 2 (mesma lógica do `_include_autocomplete` no cog rolling.py), e executa a rolagem. A lógica de rolagem (roll_pool, hitches, botch, best_options, opposition_elements) é extraída de `DicePoolSelectView._execute_roll` e `AssetIncludeSelectView._execute_roll` para uma função compartilhada, eliminando a duplicação de código que já existe entre essas duas classes.

O modal responde com `interaction.response.send_message` (mensagem pública com resultado) + `PostRollView` com botões de follow-up.

Para `parse_dice_notation`: já aceita "2d8 1d6", "d8 d6 d6", "1d8 1d6". Nenhuma mudança necessária.

Para resolução de assets no campo 2: aceita nomes separados por vírgula (mesma convenção do parâmetro `include` no `/roll`). Case-insensitive. Se um nome não for encontrado, responde com erro listando os assets disponíveis.

### 2. Selects de valor único -> botões com helper genérico

**Escolha:** Criar uma factory function `make_die_buttons(view, callback, campaign_id)` que gera 5 botões (d4-d12) numa ActionRow.

**Alternativas consideradas:**
- Manter selects de valor único -- descartado pelo problema de `aria-selected` no NVDA. Um select com 5 opções é 1 componente focável mas o estado não é anunciado. 5 botões são 5 componentes focáveis mas cada ação é clara.
- Subclasse de Button por die size -- overhead desnecessário. Uma factory que cria botões com callback parametrizado é suficiente.

**Implementação:**

Nova função em `views/base.py`:

```python
def add_die_buttons(view: CortexView, callback, style=ButtonStyle.primary):
    for size in VALID_SIZES:
        btn = Button(label=f"d{size}", style=style, custom_id=f"cortex:die_{size}_{id(view)}")
        btn.callback = lambda inter, s=size: callback(inter, s)
        view.add_item(btn)
```

Cada view que hoje tem `add_die_select(options)` troca para `add_die_buttons(self, self._on_die_selected)`.

Fluxos afetados: `StressDieSelectView`, `AssetDieSelectView`, `CompDieSelectView`, `DoomDieSelectView`.

### 3. Player select: botões quando <= 5, select quando > 5

**Escolha:** Threshold de 5 jogadores. Até 5, gera um botão por jogador. Acima, mantém o select existente.

5 é o limite por ActionRow do Discord. Mesas de Cortex Prime raramente excedem 5 jogadores (excluindo GM), mas delegates e mesas grandes existem.

**Implementação:**

Nova função em `views/base.py`:

```python
def add_player_options(view: CortexView, players: list[dict], callback):
    if len(players) <= 5:
        for p in players:
            btn = Button(label=p["name"], style=ButtonStyle.secondary)
            btn.callback = lambda inter, pid=p["id"]: callback(inter, pid)
            view.add_item(btn)
    else:
        options = [SelectOption(label=p["name"], value=str(p["id"])) for p in players[:25]]
        select = Select(placeholder="Selecione jogador", options=options)
        select.callback = lambda inter: callback(inter, int(inter.data["values"][0]))
        view.add_item(select)
```

Fluxos afetados: `StressPlayerSelectView`, `AssetOwnerSelectView`, `CompTargetSelectView`.

Para `AssetOwnerSelectView`: mantém a opção "Asset de Cena" como botão adicional (ou 6o item no select se > 5 jogadores).

### 4. Stress type: sempre botões

Stress types são configurados no setup da campanha e raramente passam de 4 (Physical, Mental, Emotional, Social). Sempre cabem em 1 row.

**Implementação:**

`StressTypeSelectView` recebe a lista de stress types e gera um botão por tipo.

### 5. /menu como comando em cog novo

**Escolha:** Novo cog `cogs/menu.py` com um único slash command `/menu`.

**Alternativas consideradas:**
- Adicionar `/menu` ao `cogs/campaign.py` -- o campaign cog já tem 7 comandos. `/menu` é conceitualmente diferente (painel de ações vs gestão de campanha).
- Mensagem automática do bot após cada ação -- o Discord não anuncia mensagens editadas para NVDA. Uma mensagem nova após cada ação criaria spam no canal.

**Implementação:**

`/menu` verifica o estado da campanha no canal e gera uma mensagem pública (não efêmera) com botões DynamicItem:

```
Sem cena ativa:
  Row 1: [Scene Start] [Campaign Info]

Com cena ativa:
  Row 1: [Roll] [Stress Add] [Asset Add] [Complication Add] [Undo]
  Row 2: [Campaign Info]
  Row 3 (se doom habilitado): [Doom Add] [Doom Remove] [Doom Roll]
```

A mensagem inclui texto descritivo: "Painel de acoes. Cena ativa: {nome}. Use os botoes abaixo ou digite / para slash commands."

Todos os botões são DynamicItem existentes (já registrados no bot). O `/menu` não cria novas classes de botão, apenas compõe os existentes numa view.

O GM pode pinar a mensagem. Como os botões são DynamicItem com `timeout=None`, funcionam indefinidamente mesmo sem pin.

### 6. Extração da lógica de rolagem

A lógica de execução de roll está duplicada em `DicePoolSelectView._execute_roll` e `AssetIncludeSelectView._execute_roll` (linhas 109-152 e 217-260 de rolling_views.py). Ambos fazem: roll_pool -> hitches -> botch -> best_options -> stress_list -> complication_list -> format_roll_result.

**Escolha:** Extrair para uma função `execute_player_roll(db, campaign_id, player_id, player_name, pool, included_assets)` em `views/rolling_views.py` (ou em `services/roller.py`). O modal e as views de pós-ação chamam essa função.

Preferência por manter em `views/rolling_views.py` porque a função precisa de acesso ao db para buscar stress/complications/config, e não é lógica pura de serviço.

### 7. custom_id para botões efêmeros

Botões efêmeros (dentro de views não-persistentes como a chain de stress) não precisam de DynamicItem nem de custom_id com campaign_id. Eles existem apenas durante a interação efêmera. Usar custom_id simples como `cortex:die_4`, `cortex:die_6` etc. ou gerar IDs únicos para evitar conflito entre views simultâneas.

Para evitar conflito: usar `f"cortex:{action}:{uuid4().hex[:8]}"` nos botões efêmeros. Isso garante que duas chains de stress abertas simultaneamente por diferentes GMs/delegates não colidam.

## Risks / Trade-offs

**Modal de texto exige que o jogador saiba a notação de dados.** Mitigação: placeholder text com exemplo claro ("Ex: 2d8 1d6 1d10"), e o parser já dá mensagens de erro descritivas em português. Jogadores que usam o slash command `/roll dice:` já conhecem a notação.

**Assets no modal dependem de nomes digitados corretamente.** Mitigação: o placeholder dinâmico lista os assets disponíveis com tamanho do dado. Matching é case-insensitive. Erro retorna lista completa de assets para o jogador tentar de novo. Alternativa: o jogador pode sempre usar `/roll dice:X include:Y` com autocomplete se preferir precisão.

**Botões de jogador com > 5 jogadores caem para select.** Isso reintroduz o problema de `aria-selected`. Mitigação: mesas com > 5 jogadores são raras em Cortex Prime. Para esses casos, o slash command com autocomplete continua funcionando perfeitamente. O select é fallback, não caminho principal.

**custom_id com uuid efêmero não sobrevive a restart do bot.** Isso é aceitável porque views efêmeras (chains de stress, asset, etc.) já não sobrevivem a restart. Apenas os DynamicItem (botões de ação nos post-views) precisam ser persistentes, e esses já usam o padrão `cortex:{action}:{campaign_id}`.

**`/menu` gera mensagem pública que pode ser spammada.** Mitigação: cooldown de 10 segundos no comando. A mensagem é lightweight (texto curto + botões). Se o GM pina, raramente precisa chamar de novo.
