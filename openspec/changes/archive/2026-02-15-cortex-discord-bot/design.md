## Context

O CortexPal2000 é um bot Python que roda como WSGI app atrás de Apache, recebendo webhooks do Discord. Usa discord_interactions (biblioteca leve), SQLite com schema flat (GUIDs como PKs, sem índices, sem foreign keys), e um script cron separado para purge de jogos inativos. Funciona para uso casual mas a arquitetura dificulta manutenção, deploy e extensão.

O novo bot substitui tudo. Python moderno com discord.py (WebSocket persistente), SQLite com schema relacional limpo, slash commands com autocomplete, e output acessível para screen readers. Máximo 6 jogadores por campanha, escala pequena, sem necessidade de multi-tenancy robusta.

Referência mecânica completa do Cortex Prime disponível em `cortex-prime-rules-extraction.md` (extraída do handbook de 256 páginas).

## Goals / Non-Goals

**Goals:**

- Bot funcional que rastreia estado de sessão Cortex Prime (assets, stress, complications, PP, XP, hero dice, doom pool, crisis pools) com lifecycle campanha/cena.
- Rolagem assistida que sugere inclusão de elementos rastreados e interpreta resultados mecanicamente (hitches, heroic success, best mode).
- Totalmente acessível via screen reader: output em texto linear estruturado, toda operação via slash command com parâmetros explícitos.
- Undo simples para reverter última ação.
- Deploy simples como processo persistente (sem Apache/WSGI/cron).

**Non-Goals:**

- Character sheets no bot. Traits, distinctions, skills, SFX, milestones ficam na ficha do jogador.
- Rastreamento de contests (fluxo de ida e volta gerenciado pelos jogadores).
- Action order / iniciativa.
- Criação de personagem.
- Multi-tenancy para centenas de servidores. O bot atende um grupo pequeno.
- Interface web ou dashboard.

## Decisions

### 1. discord.py com app_commands

**Escolha:** discord.py 2.x com `app_commands` (slash commands nativos do Discord).

**Alternativas consideradas:**
- discord_interactions (usado pelo bot antigo): biblioteca leve mas requer WSGI, sem WebSocket, menos mantida.
- discord.js (JavaScript): ecossistema maior mas Caio prefere Python e usa uv.
- Pycord: fork do discord.py, comunidade menor, API similar.

**Razão:** discord.py é a biblioteca Python mais madura para Discord, mantida ativamente, suporta slash commands com autocomplete (importante para acessibilidade), e roda como processo persistente via WebSocket (elimina a complexidade WSGI).

### 2. SQLite com aiosqlite

**Escolha:** SQLite via aiosqlite (wrapper async para não bloquear o event loop do discord.py).

**Alternativas consideradas:**
- PostgreSQL: overkill para max 6 jogadores e 1 campanha ativa.
- JSON files: frágil, sem transações, race conditions.
- SQLAlchemy: abstração desnecessária para schema simples.

**Razão:** SQLite é zero-config, embarcado, e suporta transações. aiosqlite garante compatibilidade com o event loop async do discord.py. Schema relacional com foreign keys e índices resolve os problemas do bot antigo (GUIDs, sem integridade referencial).

### 3. Schema relacional com lifecycle explícito

```
campaigns
├── players (discord_user_id, name, is_gm, pp, xp)
├── stress_types (name)
├── scenes (name, is_active)
│   ├── assets (scope=scene)
│   ├── complications (scope=scene)
│   └── crisis_pools → crisis_pool_dice
├── assets (scope=session, player-owned)
├── stress (player, type, die_size)
├── trauma (player, type, die_size)
├── complications (scope=persistent)
├── hero_dice (player, die_size)
├── doom_pool_dice (die_size)
└── action_log (para undo)
```

Die sizes armazenados como inteiros (4, 6, 8, 10, 12). Config da campanha (módulos ativos) em JSON column. Um canal Discord = uma campanha ativa.

### 4. Organização em Cogs

discord.py usa Cogs como padrão para agrupar comandos relacionados. Estrutura:

```
cortex-bot/
├── bot.py                 # Entry point
├── cogs/
│   ├── campaign.py        # /setup, /info, /campaign
│   ├── scene.py           # /scene start, /scene end
│   ├── state.py           # /asset, /stress, /complication, /pp, /xp, /hero
│   ├── rolling.py         # /roll
│   ├── doom.py            # /doom, /crisis
│   └── undo.py            # /undo
├── models/
│   ├── database.py        # Schema, migrations, conexão
│   ├── campaign.py        # Campaign CRUD
│   └── dice.py            # Die utilities (step up/down, validação)
├── services/
│   ├── roller.py          # Lógica de rolagem, best mode, interpretação
│   ├── state_manager.py   # Operações de estado com action log
│   └── formatter.py       # Formatação de texto acessível
└── config.py              # Token, DB path
```

### 5. Undo via action log

**Escolha:** Cada operação de estado grava uma entrada no `action_log` com os dados para reverter (inverse_data). `/undo` lê a última entrada não-desfeita e aplica a operação inversa.

**Alternativas consideradas:**
- Event sourcing completo: reconstruir estado a partir de eventos. Overkill para o escopo.
- Snapshots: salvar estado completo antes de cada ação. Simples mas desperdiça espaço.

**Razão:** Action log é leve, reversível, e serve também como audit trail (quem fez o quê quando). Cada ação grava: tipo, dados forward, dados inverse, actor, timestamp.

Exemplo: `/stress add player:Alice type:Physical die:d8` grava inverse `{action: "remove", table: "stress", id: 42}`. `/undo` executa o remove.

### 6. Output acessível como padrão

Toda resposta do bot segue o formato: texto linear estruturado, sem emojis decorativos, sem box art, sem dependência de layout espacial. Componentes visuais do Discord (botões, selects) são opcionais e complementares, nunca o único caminho.

O formatter.py centraliza a produção de texto para garantir consistência. Cada resposta tem uma versão texto-puro que funciona em screen reader.

### 7. Slash commands com parâmetros completos

Todo comando aceita todos os parâmetros necessários inline, sem etapas intermediárias obrigatórias. Autocomplete do Discord (que funciona via teclado) ajuda na descoberta.

Exemplos:
- `/roll dice:1d8 1d10 include:wrench difficulty:11`
- `/stress add player:Alice type:Physical die:d8`
- `/scene end bridge:yes`

Para usuários que preferem UI interativa: o bot pode apresentar botões/selects depois do comando, mas a operação já é executável sem eles.

## Risks / Trade-offs

**[Complexidade do best mode com muitos dados]** Calcular todas as combinações de 2 dados para total + 1 para effect num pool de 8+ dados é combinatório. Para pools típicos (3-8 dados) é trivial, mas pools muito grandes podem ter latência.
→ Mitigação: Limitar cálculo a pools de até 12 dados. Acima disso, mostrar apenas o resultado bruto.

**[SQLite e concorrência]** Se dois comandos chegarem simultaneamente na mesma campanha, SQLite pode ter lock contention.
→ Mitigação: Com max 6 jogadores e um processo único, a probabilidade é baixa. aiosqlite serializa escritas naturalmente. WAL mode habilitado para leituras concorrentes.

**[discord.py manutenção]** discord.py já teve período de abandono (2021-2022) antes de ser retomado.
→ Mitigação: A API do Discord é estável. Se discord.py morrer de novo, Pycord é drop-in replacement.

**[Acessibilidade de componentes Discord]** Botões e selects do Discord têm suporte variável em screen readers dependendo do cliente (desktop vs mobile vs web).
→ Mitigação: Componentes são sempre opcionais. Toda funcionalidade acessível via slash command direto.

**[Scope creep via regras do Cortex]** Cortex Prime é modular e extenso. A tentação de implementar mais subsistemas (SFX, milestones, action order) pode inflacionar o escopo.
→ Mitigação: Non-goals explícitos na proposal. Features adicionais via changes separados se necessário.
