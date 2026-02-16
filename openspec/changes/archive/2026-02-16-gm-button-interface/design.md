## Context

O GM do bot é cego e usa screen reader. Slash commands do Discord são inacessíveis via VoiceOver (o overlay congela) e a configuração "Legacy Chat Input" quebra slash commands por completo. Discord UI components (buttons, select menus) são elementos HTML focáveis padrão, bem suportados por screen readers. O bot já tem toda a lógica de jogo desacoplada nos services; os cogs são apenas plumbing de interação Discord. Isso permite adicionar uma segunda camada de entrada (buttons) sem duplicar lógica.

Toda resposta do bot hoje usa `interaction.response.send_message()` com texto linear, exceto `/scene end` que usa defer + followup. Nenhum cog usa embeds ou componentes visuais.

## Goals / Non-Goals

**Goals:**
- GM consegue executar todas as operações do bot via buttons e select menus, sem digitar slash commands.
- Botões são contextuais: cada resposta do bot oferece as ações mais prováveis como próximo passo.
- Views sobrevivem ao timeout de 15 minutos e a restarts do bot (persistent views com `timeout=None`).
- Players videntes continuam usando slash commands normalmente; a presença de botões não interfere.

**Non-Goals:**
- Não substituir slash commands. Ambas as interfaces coexistem.
- Não cobrir operações raras de admin (campaign_end, delegate, undelegate) via botões. Essas ficam apenas em slash.
- Não implementar prefix commands (m!roll). A investigação mostrou que buttons resolvem o problema de acessibilidade de forma superior.
- Não usar modals com campos de texto livre. Select menus com opções pré-populadas do DB são mais acessíveis e eliminam erros de digitação.
- Não usar embeds. Output continua como texto linear por acessibilidade.

## Decisions

### 1. Views com `timeout=None` + DynamicItem para persistência

**Decisão:** Usar `timeout=None` em todas as Views e `discord.ui.DynamicItem` com custom_ids parseáveis por regex para que botões sobrevivam restarts do bot sem manter estado em memória.

**Alternativa considerada:** Views normais com timeout padrão (15min). Rejeitada porque o GM pode demorar para interagir e o bot pode reiniciar a qualquer momento.

**Alternativa considerada:** Estado em instance variables da View. Rejeitada porque se perde no restart. Estado vive no DB (já existente) e no custom_id.

### 2. Custom ID schema: `cortex:{action}:{param1}:{param2}:...`

**Decisão:** Custom IDs codificam a ação e parâmetros necessários diretamente na string, parseáveis via regex. Máximo 100 caracteres (limite Discord).

Exemplos:
- `cortex:scene_start` → botão para iniciar cena (sem params)
- `cortex:stress_add:player_select:{campaign_id}` → abre select de jogadores
- `cortex:stress_add:type_select:{campaign_id}:{player_id}` → abre select de tipos de stress
- `cortex:stress_add:die_select:{campaign_id}:{player_id}:{type_id}` → abre select de dados
- `cortex:roll_quick:{campaign_id}` → botão para rolagem rápida
- `cortex:undo:{campaign_id}` → botão de undo

**Alternativa considerada:** Estado em banco separado indexado por UUID no custom_id. Rejeitada por adicionar complexidade sem ganho; os IDs de campanha/jogador/tipo já cabem nos 100 chars.

### 3. Select menu chains para comandos multi-parâmetro

**Decisão:** Comandos que exigem múltiplos parâmetros (stress add, complication add, asset add) usam sequência de select menus. Cada seleção gera nova mensagem com o próximo select, até completar a ação.

**Flow típico (stress add):**
```
[Botão "Stress Add" clicado]
  → Mensagem com Select: "Selecione jogador" (opções do DB)
    → [Jogador selecionado]
      → Mensagem com Select: "Selecione tipo de stress" (opções do DB)
        → [Tipo selecionado]
          → Mensagem com Select: "Selecione dado" (d4, d6, d8, d10, d12)
            → [Dado selecionado]
              → Executa stress add via StateManager
              → Resposta com resultado + novos botões contextuais
```

Cada mensagem intermediária é efêmera (ephemeral=True) para não poluir o canal. Apenas o resultado final é público.

**Alternativa considerada:** Modal com campos de texto. Rejeitada porque modals com text input são menos acessíveis que selects pré-populados, e o GM teria que digitar nomes exatamente certos.

### 4. Botões contextuais por tipo de resposta

**Decisão:** Cada resposta do bot anexa uma View com botões relevantes ao contexto atual. Não existe um "painel geral" fixo.

Mapeamento de contexto → botões:

| Resposta de... | Botões oferecidos |
|---|---|
| `/campaign setup` | Scene Start |
| `/scene start` | Roll, Stress Add, Asset Add, Complication Add, Doom Add* |
| `/scene end` | Scene Start, Campaign Info |
| `/roll` ou `/gmroll` | Roll, Undo |
| `/stress add/stepup/stepdown` | Stress Add, Undo, Campaign Info |
| `/asset add/stepup/stepdown` | Asset Add, Undo |
| `/complication add/stepup/stepdown` | Complication Add, Undo |
| `/doom add/remove/stepup/stepdown` | Doom Add, Doom Remove, Doom Roll |
| `/crisis add/remove` | Crisis Add, Crisis Roll |
| `/campaign info`, `/scene info` | Scene Start (se sem cena), Roll (se com cena) |
| `/undo` | Undo (outro), Campaign Info |
| `/pp add/remove`, `/xp add/remove` | (sem botões extras, ações raras) |

*Doom Add aparece apenas se `config.doom_pool` está habilitado.

### 5. Filtragem por permissão via interaction check

**Decisão:** Botões GM-only (stress, doom, complication, scene) verificam `has_gm_permission()` no callback. Se um jogador clicar, recebe mensagem efêmera "Apenas o GM pode usar este comando." Os botões aparecem para todos (Discord não permite esconder componentes por usuário), mas a execução é protegida.

**Alternativa considerada:** Enviar botões apenas em DM para o GM. Rejeitada porque quebraria o fluxo de jogo no canal e os outros jogadores não veriam o contexto.

### 6. Organização do código: módulo `views/`

**Decisão:** Criar `src/cortex_bot/views/` com:
- `__init__.py` → exporta todas as views para registro no setup_hook
- `base.py` → classe base CortexView(discord.ui.View) com timeout=None e helpers comuns
- `scene_views.py` → botões de scene start/end
- `rolling_views.py` → botões de roll/gmroll
- `state_views.py` → botões e selects para stress/asset/complication/pp/xp/hero
- `doom_views.py` → botões de doom pool e crisis pool
- `common.py` → botões compartilhados (undo, campaign info)

Cada cog importa a view apropriada e passa como parâmetro `view=` no send_message/followup.

### 7. Registro de persistent views no setup_hook

**Decisão:** `bot.py` setup_hook registra todas as views e DynamicItems:

```python
async def setup_hook(self) -> None:
    await self.db.initialize()
    # Register persistent views before loading cogs
    register_persistent_views(self)
    for cog in COGS:
        await self.load_extension(cog)
    await self.tree.sync()
```

A função `register_persistent_views()` vive em `views/__init__.py` e chama `bot.add_view()` e `bot.add_dynamic_items()` para cada classe.

## Risks / Trade-offs

**[Limite de 25 componentes por mensagem]** → O mapeamento contextual mantém no máximo 5-6 botões por resposta. Bem dentro do limite.

**[Mensagens intermediárias de select chain são efêmeras e expiram em 15min]** → Se o GM demorar mais de 15min no meio de uma chain, precisa recomeçar. Mitigação: chains têm no máximo 3 steps, cada um leva segundos.

**[Custom IDs de 100 chars podem ser apertados com muitos parâmetros]** → O formato `cortex:action:id:id:id` usa no máximo ~60 chars nos piores casos (IDs numéricos de DB). Folga suficiente.

**[Botões visíveis para todos mas executáveis só pelo GM]** → Jogadores podem se confundir clicando botões que não funcionam para eles. Mitigação: mensagem efêmera clara explicando a restrição. Em uso real, jogadores aprendem rápido.

**[Cada resposta com View consome um pouco mais de payload]** → Impacto negligível. Discord suporta isso nativamente.
