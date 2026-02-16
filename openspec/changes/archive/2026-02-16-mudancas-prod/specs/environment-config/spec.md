## ADDED Requirements

### Requirement: Configuration via pydantic-settings

O módulo `config.py` SHALL usar `pydantic_settings.BaseSettings` para definir e validar todas as variáveis de ambiente do bot. A classe Settings SHALL carregar variáveis de ambiente e, opcionalmente, de um arquivo `.env` na raiz do projeto.

#### Scenario: Bot token obrigatório presente

- **WHEN** a variável `CORTEX_BOT_TOKEN` está definida no ambiente
- **THEN** `settings.bot_token` retorna o valor como `SecretStr`

#### Scenario: Bot token ausente

- **WHEN** a variável `CORTEX_BOT_TOKEN` não está definida no ambiente nem no `.env`
- **THEN** o bot MUST falhar no startup com `ValidationError` indicando o campo ausente

#### Scenario: Database path com default

- **WHEN** a variável `CORTEX_BOT_DB` não está definida
- **THEN** `settings.database_path` MUST retornar `"cortex_bot.db"`

#### Scenario: Database path customizado

- **WHEN** a variável `CORTEX_BOT_DB` está definida como `/data/bot.db`
- **THEN** `settings.database_path` MUST retornar `"/data/bot.db"`

### Requirement: Suporte a arquivo .env

O sistema SHALL suportar carregamento de variáveis a partir de um arquivo `.env` na raiz do projeto para desenvolvimento local. O arquivo `.env` SHALL ser listado no `.gitignore`.

#### Scenario: Variáveis carregadas do .env

- **WHEN** um arquivo `.env` existe na raiz com `CORTEX_BOT_TOKEN=test-token`
- **THEN** `settings.bot_token` MUST carregar o valor do arquivo

#### Scenario: Variável de ambiente sobrescreve .env

- **WHEN** `CORTEX_BOT_TOKEN` está definida tanto no ambiente quanto no `.env`
- **THEN** o valor do ambiente MUST ter precedência sobre o `.env`

### Requirement: Instância global de settings

O módulo `config.py` SHALL exportar uma instância `settings` criada no import time. Todos os consumidores SHALL importar `settings` em vez de ler `os.environ` diretamente.

#### Scenario: Import de settings no bot.py

- **WHEN** `bot.py` importa `from cortex_bot.config import settings`
- **THEN** `settings.bot_token` e `settings.database_path` estão disponíveis sem instanciação adicional
