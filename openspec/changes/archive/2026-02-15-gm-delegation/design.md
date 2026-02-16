## Context

O Cortex Bot usa `is_gm INTEGER` na tabela `players` como flag binária de permissão. Quem executa `/campaign setup` recebe `is_gm=1`, todos os outros recebem `is_gm=0`. Cada cog faz checks como `if not actor["is_gm"]: return erro` para comandos privilegiados (stress em outros jogadores, doom pool, scene management, undo global).

O GM principal é cego e opera via screen reader. Na prática, outro jogador executa comandos de sistema em nome dele. Essa pessoa precisa de permissões de GM sem perder seu estado de jogador (stress, assets, PP, XP).

O comando `/roll` atualmente injeta o estado pessoal do executor (stress, complications como "opposition" e assets disponíveis). Quando o delegado rola dados para NPCs, esse estado pessoal contamina o output.

## Goals / Non-Goals

**Goals:**
- Permitir que o GM promova jogadores a delegados com acesso a comandos GM-only
- Manter o estado de jogador do delegado intacto (stress, assets, bridge scene step down)
- Comando de rolagem sem contexto pessoal para GM e delegados
- Rastreabilidade: action log registra quem executou, não "o GM"

**Non-Goals:**
- Delegado não pode delegar (cadeia de confiança direta GM → delegado)
- Delegado não pode encerrar campanha (`/campaign campaign_end` fica restrito a `is_gm`)
- Não há "modo" toggle; a separação é por comando (`/roll` vs `/gmroll`)
- Não há limite imposto de número de delegados

## Decisions

### 1. Coluna `is_delegate` em vez de coluna `role`

Adicionar `is_delegate INTEGER NOT NULL DEFAULT 0` à tabela `players` em vez de substituir `is_gm` por uma coluna `role TEXT`.

**Alternativa considerada**: `role TEXT ('gm'|'delegate'|'player')`. Mais limpa semanticamente, mas exige migrar `is_gm` pra `role` em todo o codebase (schema, queries, checks nos 6 cogs, testes). A coluna extra é aditiva: não quebra nada existente, os checks mudam de `is_gm` para `is_gm or is_delegate` nos pontos necessários.

### 2. Helper function para check de permissão

Criar `has_gm_permission(player: dict) -> bool` que retorna `player["is_gm"] or player.get("is_delegate", 0)`. Centraliza a lógica em vez de espalhar `or` por todos os cogs. O check de bridge scene e campaign_end continuam usando `is_gm` diretamente.

### 3. `/gmroll` como comando separado em vez de flag no `/roll`

Comando dedicado em `rolling.py` (mesmo cog). Reutiliza `roll_pool`, `find_hitches`, `is_botch`, `calculate_best_options` do roller service. Não busca assets, stress, ou complications do executor. Aceita parâmetro `name` opcional (default "GM") para identificar o NPC no output.

**Alternativa considerada**: `gm:bool` no `/roll`. Funcional, mas o delegado pode esquecer a flag e vazar estado pessoal. Comando separado falha seguro.

### 4. Schema migration inline

Adicionar `ALTER TABLE players ADD COLUMN is_delegate INTEGER NOT NULL DEFAULT 0` no `Database.initialize()` com try/except para idempotência (coluna já existe = ignora). Não há migration framework no projeto; o padrão existente é executar schema via `executescript` no init.

## Risks / Trade-offs

- **Coluna duplicada**: `is_gm` e `is_delegate` são duas flags com semântica próxima. Se no futuro surgir um terceiro papel, a abordagem de flags escala mal. → Aceitável para o escopo atual; migrar para `role` pode ser feito depois sem breaking changes.
- **Esquecimento de check**: Novo comando adicionado no futuro pode checar só `is_gm` e ignorar delegados. → Mitigação: `has_gm_permission()` centralizado. Documentar no CLAUDE.md que novos comandos GM-only devem usar o helper.
- **Delegado com undo global**: O delegado pode desfazer ações de qualquer jogador (mesmo comportamento do GM no undo). → Intencional. O delegado opera em nome do GM; restringir o undo criaria fricção desnecessária.
