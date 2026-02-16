#!/usr/bin/env bash
set -euo pipefail

REPO_URL="https://github.com/caiocgomes/discord-cortex-prime-bot.git"
INSTALL_DIR="/opt/cortex-bot"
ENV_DIR="/etc/cortex-bot"
SERVICE_USER="cortex-bot"
SERVICE_GROUP="cortex-bot"

if [ "$(id -u)" -ne 0 ]; then
    echo "Este script precisa ser executado como root (sudo)."
    exit 1
fi

echo "=== Instalando Cortex Prime Discord Bot ==="

# 1. Verificar se uv esta disponivel
if ! command -v uv &>/dev/null; then
    echo "uv nao encontrado. Instalando..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"
fi

UV_BIN=$(command -v uv)
echo "uv encontrado em: $UV_BIN"

# 2. Criar usuario de servico
if ! id "$SERVICE_USER" &>/dev/null; then
    echo "Criando usuario $SERVICE_USER..."
    useradd -r -s /usr/sbin/nologin "$SERVICE_USER"
else
    echo "Usuario $SERVICE_USER ja existe."
fi

# 3. Clonar ou atualizar o repositorio
if [ -d "$INSTALL_DIR/.git" ]; then
    echo "Repositorio ja existe. Atualizando..."
    git -C "$INSTALL_DIR" pull --ff-only
else
    echo "Clonando repositorio..."
    git clone "$REPO_URL" "$INSTALL_DIR"
fi

# 4. Instalar dependencias
echo "Instalando dependencias com uv..."
cd "$INSTALL_DIR"
"$UV_BIN" sync

# 5. Ajustar permissoes
echo "Ajustando permissoes..."
chown -R "$SERVICE_USER":"$SERVICE_GROUP" "$INSTALL_DIR"

# 6. Configurar environment file
if [ ! -f "$ENV_DIR/env" ]; then
    echo "Criando arquivo de ambiente..."
    mkdir -p "$ENV_DIR"
    cp "$INSTALL_DIR/.env.example" "$ENV_DIR/env"
    chmod 600 "$ENV_DIR/env"
    chown "$SERVICE_USER":"$SERVICE_GROUP" "$ENV_DIR/env"
    echo ""
    echo "IMPORTANTE: Edite $ENV_DIR/env e configure CORTEX_BOT_TOKEN"
    echo "   sudo nano $ENV_DIR/env"
    echo ""
else
    echo "Arquivo de ambiente ja existe em $ENV_DIR/env."
fi

# 7. Instalar e ativar o servico
echo "Instalando servico systemd..."
cp "$INSTALL_DIR/cortex-bot.service" /etc/systemd/system/
systemctl daemon-reload
systemctl enable cortex-bot

# 8. Verificar se o token esta configurado antes de iniciar
if grep -q "your-token-here" "$ENV_DIR/env" 2>/dev/null; then
    echo ""
    echo "=== Instalacao completa ==="
    echo "O servico NAO foi iniciado porque o token ainda nao foi configurado."
    echo "Configure o token e inicie manualmente:"
    echo "   sudo nano $ENV_DIR/env"
    echo "   sudo systemctl start cortex-bot"
else
    echo "Iniciando servico..."
    systemctl restart cortex-bot
    echo ""
    echo "=== Instalacao completa ==="
    echo "Servico iniciado. Verifique com:"
    echo "   sudo systemctl status cortex-bot"
    echo "   sudo journalctl -u cortex-bot -f"
fi
