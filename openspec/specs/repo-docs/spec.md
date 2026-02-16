## Requirements

### Requirement: README com instrucoes de setup

O repositorio SHALL conter um `README.md` na raiz com informacao suficiente para alguem clonar, configurar e rodar o bot sem assistencia externa.

#### Scenario: Conteudo minimo do README

- **WHEN** alguem acessa o README
- **THEN** o documento MUST conter: descricao do projeto, pre-requisitos (Python 3.12+, uv), instrucoes de instalacao, configuracao de variaveis de ambiente, e comando para executar o bot

#### Scenario: Instrucoes de deploy com systemd

- **WHEN** alguem quer fazer deploy em servidor
- **THEN** o README MUST referenciar o unit file e descrever os passos para configurar o servico

### Requirement: Licenca no repositorio

O repositorio SHALL conter um arquivo `LICENSE` na raiz com a licenca MIT.

#### Scenario: Licenca presente e valida

- **WHEN** alguem acessa o arquivo LICENSE
- **THEN** o conteudo MUST ser o texto padrao da licenca MIT com o ano e nome do autor preenchidos
