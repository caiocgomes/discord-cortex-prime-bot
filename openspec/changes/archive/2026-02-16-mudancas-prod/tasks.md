## 1. Configuração com pydantic-settings

- [x] 1.1 Adicionar `pydantic-settings` ao `pyproject.toml` e rodar `uv sync`
- [x] 1.2 Reescrever `src/cortex_bot/config.py` usando `BaseSettings` com `bot_token` (SecretStr, obrigatório) e `database_path` (str, default `cortex_bot.db`), com suporte a `.env`
- [x] 1.3 Atualizar `bot.py` para importar e usar `settings` em vez de `DISCORD_TOKEN` e `DATABASE_PATH`
- [x] 1.4 Criar `.env.example` na raiz com as variáveis documentadas
- [x] 1.5 Rodar testes existentes para garantir que nada quebrou

## 2. Systemd service

- [x] 2.1 Criar `cortex-bot.service` na raiz com unit file systemd (Type=simple, Restart=on-failure, EnvironmentFile, User=cortex-bot)

## 3. Documentação do repositório

- [x] 3.1 Criar `README.md` com descrição, pré-requisitos, instalação, configuração, execução e referência ao deploy com systemd
- [x] 3.2 Criar `LICENSE` com licença MIT (ano 2025, Caio Gomes)

## 4. Validação final

- [x] 4.1 Rodar todos os testes e verificar que passam
- [x] 4.2 Verificar que o bot inicia localmente com `.env` configurado
