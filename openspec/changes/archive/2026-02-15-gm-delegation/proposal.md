## Why

O GM principal é cego e usa screen reader. Na prática, outro jogador frequentemente opera o sistema em nome dele: abre cenas, aplica stress, rola dados de NPCs. O modelo atual de permissão é binário (`is_gm` = 0 ou 1) e não permite que um jogador mantenha seu estado de personagem (stress, assets, PP) enquanto exerce funções de GM. Além disso, quando esse jogador usa `/roll`, o bot despeja o stress e complications pessoais dele no output, contaminando informação que deveria ser exclusiva de um roll de GM.

## What Changes

- Novo papel "delegado" no sistema de permissões. O GM pode promover qualquer jogador a delegado via `/campaign delegate` e revogar via `/campaign undelegate`. O delegado ganha acesso a todos os comandos GM-only (stress, doom, scene, complications de cena, undo global) sem perder seu estado de jogador.
- Novo comando `/gmroll` exclusivo para GM e delegados. Rola dados sem injetar estado pessoal (sem opposition, sem assets do executor). Aceita parâmetro opcional `name` para identificar o NPC ("Guarda da Torre rolou 3 dados" em vez de "GM rolou 3 dados").
- `/campaign info` passa a mostrar "(delegado)" ao lado do nome de jogadores com essa flag.
- Bridge scene (step down de stress no fim de cena) continua pulando apenas `is_gm`, não delegados. Delegados recebem step down normalmente como jogadores.
- `/campaign campaign_end` continua restrito ao GM original. Delegado não pode encerrar campanha.

## Capabilities

### New Capabilities
- `gm-delegation`: Sistema de delegação de permissões GM para jogadores, incluindo comandos delegate/undelegate e lógica de permissão expandida.
- `gm-roll`: Comando `/gmroll` para rolagem de dados sem contexto de jogador, restrito a GM e delegados.

### Modified Capabilities

## Impact

- **Schema DB**: Coluna `is_delegate INTEGER NOT NULL DEFAULT 0` na tabela `players`.
- **Cogs afetados**: `campaign.py` (novos subcomandos delegate/undelegate), `state.py` (checks de permissão), `scene.py` (checks de permissão), `doom.py` (checks de permissão), `undo.py` (checks de permissão), novo cog ou extensão de `rolling.py` para `/gmroll`.
- **Formatter**: Exibição do label "(delegado)" em `format_campaign_info`.
- **Testes**: Novos testes para delegate, gmroll, e expansão dos testes de permissão existentes.
