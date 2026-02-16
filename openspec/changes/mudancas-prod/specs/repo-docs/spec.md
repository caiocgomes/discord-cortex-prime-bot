## ADDED Requirements

### Requirement: README com instruções de setup

O repositório SHALL conter um `README.md` na raiz com informação suficiente para alguém clonar, configurar e rodar o bot sem assistência externa.

#### Scenario: Conteúdo mínimo do README

- **WHEN** alguém acessa o README
- **THEN** o documento MUST conter: descrição do projeto, pré-requisitos (Python 3.12+, uv), instruções de instalação, configuração de variáveis de ambiente, e comando para executar o bot

#### Scenario: Instruções de deploy com systemd

- **WHEN** alguém quer fazer deploy em servidor
- **THEN** o README MUST referenciar o unit file e descrever os passos para configurar o serviço

### Requirement: Licença no repositório

O repositório SHALL conter um arquivo `LICENSE` na raiz com a licença MIT.

#### Scenario: Licença presente e válida

- **WHEN** alguém acessa o arquivo LICENSE
- **THEN** o conteúdo MUST ser o texto padrão da licença MIT com o ano e nome do autor preenchidos
