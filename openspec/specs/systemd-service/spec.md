## Requirements

### Requirement: Unit file systemd

O repositorio SHALL conter um arquivo `cortex-bot.service` na raiz com uma unit file systemd funcional para rodar o bot como servico.

#### Scenario: Servico inicia com sucesso

- **WHEN** o unit file e copiado para `/etc/systemd/system/` e o servico e iniciado com `systemctl start cortex-bot`
- **THEN** o bot MUST iniciar usando `uv run python -m cortex_bot.bot`

#### Scenario: Restart automatico em falha

- **WHEN** o processo do bot termina com erro
- **THEN** systemd MUST reiniciar o servico automaticamente apos intervalo configurado

#### Scenario: Variaveis de ambiente via EnvironmentFile

- **WHEN** o servico e iniciado
- **THEN** systemd MUST carregar variaveis de ambiente de um `EnvironmentFile` configuravel (default: `/etc/cortex-bot/env`)

### Requirement: Execucao como usuario dedicado

O unit file SHALL configurar o servico para rodar como um usuario nao-root dedicado.

#### Scenario: Servico roda sem root

- **WHEN** o servico e iniciado
- **THEN** o processo MUST rodar como usuario `cortex-bot` sem privilegios de root
