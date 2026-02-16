## Context

O bot tem ~45 slash commands em 14 grupos top-level, sem nenhum mecanismo de help ou orientacao. Uma avaliacao UX com tres personas (GM novo, jogador novo, usuario retornando) identificou que a barreira de entrada e alta e o formato de output penaliza screen readers. O GM primario e cego. As specs existentes de acessibilidade exigem texto linear e feedback textual para toda acao, mas nao especificam ordenacao de informacao nem mecanismo de help.

Estado atual relevante: nao existe cog de help, mensagens de erro sao inconsistentes entre cogs (algumas em ingles, referencia a /setup inexistente), e o formatter.py coloca conclusao (total da rolagem) depois do detalhe (dados individuais).

## Goals / Non-Goals

**Goals:**

- Um usuario novo consegue descobrir o fluxo basico (setup -> scene -> roll) sem ajuda externa
- Um usuario retornando consegue relembrar comandos por contexto (sou GM ou jogador? estou em cena ou entre cenas?)
- Output de rolagem transmite a informacao mais actionable primeiro (total, sucesso/falha) para screen readers
- Toda mensagem de erro do bot esta em portugues e aponta para o comando correto
- Feedback de undo e legivel por um humano, nao por um debugger

**Non-Goals:**

- Help contextual que detecta estado da campanha/cena automaticamente (reservado para fase 2+3)
- Comando /status ou /me individual por jogador (change separado)
- Internacionalizacao (i18n) para outros idiomas
- Alteracao de config de campanha em runtime (/campaign config)
- Mensagem de boas-vindas ao bot entrar no servidor (on_guild_join)

## Decisions

### D1: /help como comando unico com parametro topic (Choice)

Alternativa considerada: GroupCog com subcomandos (/help gm, /help jogador, /help rolagem). Rejeitada porque adicionar mais um grupo com subcomandos ao tree aumenta a poluicao visual na lista de slash commands, que ja tem 14 grupos. Um unico `/help` com parametro opcional `topic` (Choices: geral, gm, jogador, rolagem) mantem a lista limpa. Sem parametro, retorna a visao geral.

Implementacao: novo `cogs/help.py` com um Cog simples (nao GroupCog). Conteudo hardcoded como strings no proprio cog. Para um bot desse porte, nao justifica arquivos externos ou template engine.

### D2: Conteudo do help organizado por papel e momento

Quatro variantes:

- **geral** (default): Fluxo do lifecycle (setup -> scene -> roll), lista de grupos de comandos com uma frase cada, dica de que /help gm ou /help jogador da mais detalhes.
- **gm**: Comandos organizados por momento (setup, durante cena, entre cenas, administracao). Inclui exemplos de /campaign setup, /scene start, /stress add, /doom.
- **jogador**: Apenas o que o player precisa: /roll (com explicacao de include e extra), /asset, /pp, /complication, /campaign info. Omite tudo que e GM-only.
- **rolagem**: Referencia completa de notacao de dados, include de assets, extra com PP, dificuldade, hitches, botch, best mode, effect die.

Cada variante retorna texto linear amigavel para screen reader, sem tabelas ou formatacao visual complexa.

### D3: Mensagens guiadas append ao output existente

As mensagens de transicao serao adicionadas ao final do output ja existente, separadas por uma linha em branco. Nao alteram a estrutura das respostas atuais.

- **Pos-setup** (campaign.py): Adicionar bloco "Proximos passos: use /scene start para iniciar uma cena. Jogadores podem usar /roll para rolar dados. /campaign info mostra o estado completo. /help para referencia de comandos."
- **Pos-scene start** (scene.py): Adicionar "Comandos de jogo: /roll para rolar, /asset add para criar assets, /campaign info para ver estado. GM: /stress add, /complication add, /doom (se habilitado)."
- **Pos-scene end** (scene.py): Ja tem output detalhado. Adicionar ao final: "Use /scene start para iniciar nova cena, ou /campaign info para ver estado persistente."

### D4: Formato de rolagem total-first

O formatter atual constroi: "d10 com 7 mais d8 com 5, igual a 12. Effect die: d8."

Novo formato: "Total 12 (d10 tirou 7, d8 tirou 5). Effect die: d8."

A mudanca coloca o numero mais relevante (total) como primeira informacao da frase. Para best_options, o label vem primeiro, depois total, depois detalhe: "Melhor total: 12 (d10 tirou 7, d8 tirou 5). Effect die: d8."

Quando difficulty esta presente, o resultado (sucesso/falha) vem imediatamente apos o total: "Melhor total: 12. Sucesso, margem 4 (d10 tirou 7, d8 tirou 5). Effect die: d8."

### D5: Separadores entre jogadores no campaign info

Inserir "---" entre blocos de jogadores no output de format_campaign_info. Simples, efetivo para screen reader distinguir onde acaba um jogador e comeca outro. Mesma logica para scene info que reutiliza format_campaign_info.

### D6: Mensagens de erro de dice.py em portugues

As funcoes parse_single_die e parse_dice_notation retornam ValueError com mensagem em ingles. Traduzir para portugues mantendo o mesmo padrao informativo:
- "d7 is not a valid Cortex die. Use d4, d6, d8, d10, or d12." -> "d7 nao e um dado Cortex valido. Use d4, d6, d8, d10 ou d12."
- "Invalid die notation: abc" -> "Notacao de dado invalida: abc"

### D7: Feedback legivel no undo

O undo.py atualmente monta a mensagem iterando sobre action_data com f"{key}={value}". Substituir por um mapa de action_type para templates legiveis:

```
ACTION_LABELS = {
    "add_asset": "Asset '{name}' {die_label} adicionado",
    "remove_asset": "Asset '{name}' removido",
    "step_up_asset": "Step up de asset '{name}' ({from} -> {to})",
    "add_stress": "Stress {type} {die_label} adicionado a {player}",
    "step_up_stress": "Step up de stress {type} ({from} -> {to}) em {player}",
    ...
}
```

Chaves do action_data sao mapeadas para os placeholders. Se action_type nao estiver no mapa, fallback para o formato atual (defensivo contra actions futuros).

### D8: Bugfixes cirurgicos

- **"/setup" -> "/campaign setup"**: Quatro ocorrencias em campaign.py, state.py, rolling.py (2x). Tambem padronizar scene.py e doom.py para incluir a sugestao "/campaign setup".
- **confirm como Choice**: Trocar `confirm: str = ""` por `confirm: app_commands.Choice` com opcao "sim". Se omitido, mostra aviso.
- **Description de player em /asset add**: Remover "Omitir para asset de cena." da description. Manter apenas "Jogador dono do asset (default: voce)".

## Risks / Trade-offs

**Conteudo do help desatualiza se comandos mudam.** O help e hardcoded, entao qualquer novo comando exige atualizar o cog de help manualmente. Mitigacao: o help cobre categorias e exemplos, nao lista exaustiva de cada subcomando. Alem disso, o bot e pequeno e estavel.

**Mensagens guiadas podem ficar verbosas para usuarios experientes.** Os blocos "Proximos passos" aparecem toda vez, mesmo para quem ja sabe. Mitigacao aceitavel: sao curtos (2-3 linhas) e textuais, nao atrapalham screen reader. Alternativa de suprimir com flag de config foi descartada por overengineering para o contexto atual.

**Mudanca no formato de rolagem quebra expectativa de quem ja memorizou o output.** O grupo atual usa o bot ha meses. Mitigacao: a mudanca e na ordem das mesmas informacoes, nao na presenca delas. Periodo de ajuste curto.

**Mapa de action labels no undo pode ficar incompleto.** Se novas actions forem adicionadas sem atualizar o mapa, o fallback para formato tecnico cobre. Nao e silencioso nem quebra.
