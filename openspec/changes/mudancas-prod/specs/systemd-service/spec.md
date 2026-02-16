## ADDED Requirements

### Requirement: Unit file systemd

O repositório SHALL conter um arquivo `cortex-bot.service` na raiz com uma unit file systemd funcional para rodar o bot como serviço.

#### Scenario: Serviço inicia com sucesso

- **WHEN** o unit file é copiado para `/etc/systemd/system/` e o serviço é iniciado com `systemctl start cortex-bot`
- **THEN** o bot MUST iniciar usando `uv run python -m cortex_bot.bot`

#### Scenario: Restart automático em falha

- **WHEN** o processo do bot termina com erro
- **THEN** systemd MUST reiniciar o serviço automaticamente após intervalo configurado

#### Scenario: Variáveis de ambiente via EnvironmentFile

- **WHEN** o serviço é iniciado
- **THEN** systemd MUST carregar variáveis de ambiente de um `EnvironmentFile` configurável (default: `/etc/cortex-bot/env`)

### Requirement: Execução como usuário dedicado

O unit file SHALL configurar o serviço para rodar como um usuário não-root dedicado.

#### Scenario: Serviço roda sem root

- **WHEN** o serviço é iniciado
- **THEN** o processo MUST rodar como usuário `cortex-bot` sem privilégios de root
