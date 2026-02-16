## Why

O bot funciona bem para quem ja conhece os comandos, mas nao oferece nenhum mecanismo de discoverability. Nao existe /help, nao existe orientacao pos-setup, nao existe sugestao de proximo passo em nenhum ponto do lifecycle. O primeiro contato de um usuario novo termina em tentativa e erro. Alem disso, o formato de output atual prioriza detalhe sobre conclusao, o que penaliza uso com screen reader (o GM primario e cego). Mensagens de erro misturam ingles e portugues, e o feedback do /undo expoe internals tecnicos em vez de texto legivel.

## What Changes

- Novo comando `/help` com variantes contextuais: visao geral, comandos de GM, comandos de jogador, referencia de rolagem
- Mensagens guiadas nos pontos de transicao do lifecycle: pos-setup (proximos passos), pos-scene start (comandos de jogo), pos-scene end (o que persiste)
- Formato de output de rolagem reestruturado: total e conclusao primeiro, detalhe dos dados depois
- Separadores entre blocos de jogadores no output de /campaign info e /scene info
- Mensagens de validacao de dados traduzidas para portugues (dice.py)
- Feedback do /undo reescrito com texto narrativo em vez de action_type/key=value
- **Bugfix**: mensagens de erro referenciam `/setup` (inexistente) em vez de `/campaign setup`
- Parametro `confirm` no `/campaign campaign_end` convertido de texto livre para Choice
- Description corrigida do parametro `player` em `/asset add` (remover "Omitir para asset de cena")

## Capabilities

### New Capabilities
- `help-system`: Comando /help com variantes estaticas (geral, gm, jogador, rolagem) e mensagens guiadas nos pontos de transicao do lifecycle (pos-setup, pos-scene start, pos-scene end)

### Modified Capabilities
- `accessibility`: Formato de output de rolagem reestruturado (total-first), separadores entre jogadores no campaign/scene info, mensagens de erro em portugues, feedback legivel no /undo
- `campaign-lifecycle`: Bugfix na referencia a /setup, confirm como Choice no campaign_end, mensagem de onboarding pos-setup
- `state-tracking`: Correcao da description do parametro player em /asset add

## Impact

- Novo cog: `cogs/help.py`
- Alteracoes em `services/formatter.py` (formato de rolagem, separadores no campaign info)
- Alteracoes em `models/dice.py` (mensagens de erro em portugues)
- Alteracoes em `cogs/undo.py` (feedback legivel)
- Alteracoes em `cogs/campaign.py` (onboarding pos-setup, confirm como Choice, bugfix /setup)
- Alteracoes em `cogs/state.py` (bugfix /setup, description corrigida)
- Alteracoes em `cogs/rolling.py` (bugfix /setup)
- Alteracoes em `cogs/scene.py` (mensagem guiada pos-scene start/end, consistencia de erro)
- Alteracoes em `cogs/doom.py` (consistencia de mensagem "nenhuma campanha")
- Registro do novo cog em `bot.py`
