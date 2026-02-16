## Context

O bot usa um `config.py` com dois `os.environ.get` sem validação. O token do Discord é checado só no `main()` com um `if not` manual. Não existe mecanismo de deploy; o bot roda via `uv run python -m cortex_bot.bot` em terminal. O repositório foi publicado no GitHub sem README nem licença.

O servidor de destino é Linux com systemd.

## Goals / Non-Goals

**Goals:**

- Configuração validada no startup com mensagens de erro claras quando variáveis obrigatórias estão ausentes
- Suporte a arquivo `.env` para desenvolvimento local
- Unit file systemd funcional para deploy como serviço
- README que permita alguém clonar e rodar o bot sem assistência
- Licença definida no repositório

**Non-Goals:**

- Docker, containers ou orquestração
- CI/CD pipeline
- Configuração hot-reload
- Documentação de uso dos comandos do bot (isso é para o README do Discord, não do repo)

## Decisions

### pydantic-settings para configuração

Usar `pydantic-settings` com `BaseSettings` e `SettingsConfigDict(env_file=".env")`. Duas variáveis: `CORTEX_BOT_TOKEN` (obrigatória, `SecretStr`) e `CORTEX_BOT_DB` (opcional, default `cortex_bot.db`). Instância global `settings` criada no módulo.

Alternativa considerada: python-dotenv puro. Descartada porque não dá validação de tipo nem falha rápida com mensagem clara. pydantic-settings resolve ambas com menos código.

O `bot.py` passa a importar `settings.bot_token` em vez de `DISCORD_TOKEN`. A validação de token vazio sai do `main()` porque pydantic já recusa string vazia como SecretStr obrigatório.

### systemd como mecanismo de serviço

Unit file simples com `Type=simple`, `Restart=on-failure`, `EnvironmentFile` apontando para um arquivo de env no servidor. O serviço roda como usuário dedicado (`cortex-bot`), sem root.

Alternativa considerada: supervisor. Descartada porque o servidor alvo já usa systemd e adicionar supervisor é dependência desnecessária.

O unit file vai na raiz do repositório como referência. O deploy real envolve copiar para `/etc/systemd/system/` e ajustar paths.

### MIT como licença

Projeto open-source sem restrições. MIT é a escolha padrão quando não há razão para algo mais restritivo.

## Risks / Trade-offs

- [pydantic-settings como dependência de produção] → Já usamos pydantic indiretamente via discord.py. O overhead é marginal e o benefício de validação compensa.
- [Unit file como template, não deploy automatizado] → Aceitável para um bot pessoal. Se o deploy escalar, vale criar um script. Por ora, copiar manualmente é suficiente.
- [SecretStr esconde o token em repr/logs] → Positivo para segurança, mas debug de conexão pode ser menos óbvio. Mitigação: log explícito de "token loaded" sem valor.
