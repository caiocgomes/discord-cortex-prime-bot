## Requirements

### Requirement: Configuration via pydantic-settings

O modulo `config.py` SHALL usar `pydantic_settings.BaseSettings` para definir e validar todas as variaveis de ambiente do bot. A classe Settings SHALL carregar variaveis de ambiente e, opcionalmente, de um arquivo `.env` na raiz do projeto.

#### Scenario: Bot token obrigatorio presente

- **WHEN** a variavel `CORTEX_BOT_TOKEN` esta definida no ambiente
- **THEN** `settings.bot_token` retorna o valor como `SecretStr`

#### Scenario: Bot token ausente

- **WHEN** a variavel `CORTEX_BOT_TOKEN` nao esta definida no ambiente nem no `.env`
- **THEN** o bot MUST falhar no startup com `ValidationError` indicando o campo ausente

#### Scenario: Database path com default

- **WHEN** a variavel `CORTEX_BOT_DB` nao esta definida
- **THEN** `settings.database_path` MUST retornar `"cortex_bot.db"`

#### Scenario: Database path customizado

- **WHEN** a variavel `CORTEX_BOT_DB` esta definida como `/data/bot.db`
- **THEN** `settings.database_path` MUST retornar `"/data/bot.db"`

### Requirement: Suporte a arquivo .env

O sistema SHALL suportar carregamento de variaveis a partir de um arquivo `.env` na raiz do projeto para desenvolvimento local. O arquivo `.env` SHALL ser listado no `.gitignore`.

#### Scenario: Variaveis carregadas do .env

- **WHEN** um arquivo `.env` existe na raiz com `CORTEX_BOT_TOKEN=test-token`
- **THEN** `settings.bot_token` MUST carregar o valor do arquivo

#### Scenario: Variavel de ambiente sobrescreve .env

- **WHEN** `CORTEX_BOT_TOKEN` esta definida tanto no ambiente quanto no `.env`
- **THEN** o valor do ambiente MUST ter precedencia sobre o `.env`

### Requirement: Instancia global de settings

O modulo `config.py` SHALL exportar uma instancia `settings` criada no import time. Todos os consumidores SHALL importar `settings` em vez de ler `os.environ` diretamente.

#### Scenario: Import de settings no bot.py

- **WHEN** `bot.py` importa `from cortex_bot.config import settings`
- **THEN** `settings.bot_token` e `settings.database_path` estao disponiveis sem instanciacao adicional
