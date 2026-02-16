## Why

O bot funciona mas não está pronto para rodar em produção. A configuração depende de `os.environ.get` sem validação, não existe unit file para rodar como serviço, e o repositório público no GitHub não tem README nem licença.

## What Changes

- Substituir `config.py` baseado em `os.environ` por pydantic-settings com validação, typing e valores default documentados
- Criar unit file systemd para rodar o bot como serviço no servidor
- Criar README com instruções de setup, configuração e execução
- Adicionar arquivo LICENSE ao repositório

## Capabilities

### New Capabilities

- `environment-config`: Gestão de configuração via pydantic-settings com validação de variáveis de ambiente, tipagem e suporte a `.env`
- `systemd-service`: Unit file systemd para deploy como serviço persistente no servidor
- `repo-docs`: README com documentação de setup/uso e arquivo LICENSE

### Modified Capabilities

(nenhuma capability existente tem requisitos alterados)

## Impact

- `src/cortex_bot/config.py`: reescrito para usar pydantic-settings
- `src/cortex_bot/bot.py`: import de config muda para usar o objeto Settings
- `pyproject.toml`: nova dependência pydantic-settings
- Novos arquivos na raiz: `cortex-bot.service`, `README.md`, `LICENSE`
- Testes existentes não devem quebrar (config é injetado via DB fixture, não via env vars)
