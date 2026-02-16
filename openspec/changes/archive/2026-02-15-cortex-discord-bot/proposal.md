## Why

O bot existente para Cortex Prime no Discord (CortexPal2000) está abandonado há anos, roda numa arquitetura WSGI que dificulta deployment e manutenção, e tem falhas de usabilidade que fazem o jogo mais lento do que deveria. O problema central: elementos rastreados pelo bot (assets, stress, complications) são desconectados das rolagens. O jogador adiciona um asset e na hora de rolar precisa lembrar de incluí-lo manualmente. Além disso, o bot é inacessível para usuários de screen reader, o que impede um dos jogadores (que frequentemente é GM) de operar o bot de forma independente.

## What Changes

- Bot novo em Python com discord.py, substituindo o CortexPal2000 por completo.
- Modelo de lifecycle com três camadas: campanha (persistente), cena (temporária), rolagem (efêmera). Transição de cena limpa estado temporário automaticamente, com suporte a bridge scenes (step down automático de stress).
- Rolagem assistida: o jogador informa os dados da ficha, o bot sugere inclusão de elementos rastreados (assets, stress, complications) e interpreta o resultado (hitches, heroic success, melhor combinação de total + effect die).
- Vinculação jogador/Discord ID no setup da campanha. O bot identifica quem está rolando e puxa o estado correto sem o jogador precisar se identificar a cada comando.
- Permissões por papel: jogador modifica o próprio estado, GM modifica tudo (adicionar stress em jogadores, gerenciar doom pool, transicionar cenas).
- Módulos configuráveis no setup: doom pool, hero dice, trauma, best mode (sugestão de rolagem ótima). Tipos de stress definidos por campanha.
- Output em texto estruturado e linear, sem depender de layout visual, emojis decorativos ou box art. Toda operação executável via slash command com parâmetros explícitos, sem etapas intermediárias obrigatórias. UI interativa (botões) como caminho opcional para quem enxerga.
- Undo: stack de ações por campanha, `/undo` reverte a última ação.
- Sem character sheets no bot. Traits, distinctions, skills, SFX e milestones ficam na ficha do jogador. O bot rastreia apenas estado de sessão: assets, stress, trauma, complications, PP, XP, hero dice, doom pool, crisis pools.
- Contests não rastreados pelo bot. Jogadores gerenciam o fluxo de ida e volta; o bot processa cada rolagem individualmente.

## Capabilities

### New Capabilities

- `campaign-lifecycle`: Setup de campanha (jogadores, tipos de stress, módulos ativos), vinculação jogador/Discord ID, configurações por campanha, encerramento de campanha.
- `scene-management`: Criação, transição e encerramento de cenas. Limpeza automática de estado temporário. Suporte a bridge scenes com step down de stress. Info/status da cena atual.
- `state-tracking`: Gerenciamento de assets (cena/sessão), stress (por tipo configurado), trauma, complications, plot points, XP, hero dice. Operações: add, step up, step down, remove. Permissões por papel (jogador vs GM).
- `dice-rolling`: Montagem de pool com dados informados + elementos rastreados sugeridos. Rolagem, identificação de hitches/botches, cálculo de heroic success, sugestão de melhor total + effect die (best mode). Suporte a dificuldade informada manualmente ou via doom pool.
- `doom-and-crisis-pools`: Doom pool do GM (add, remove, step up, step down, rolar como dificuldade). Crisis pools por cena.
- `undo`: Stack de ações por campanha, reversão da última ação com `/undo`.
- `accessibility`: Output em texto linear estruturado para screen readers. Toda funcionalidade acessível via slash commands com parâmetros, sem dependência de componentes visuais interativos.

### Modified Capabilities

(nenhuma, projeto novo)

## Impact

- Nenhum código existente afetado (projeto novo).
- Dependências: Python 3.12+, discord.py, SQLite para persistência.
- Requer bot application registrada no Discord Developer Portal com permissões de slash commands.
- Deploy como processo persistente (WebSocket), diferente do modelo WSGI do bot antigo.
