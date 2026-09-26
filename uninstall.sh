#!/usr/bin/env bash
#
# Remove a configuracao instalada pelo install.sh.
#
set -euo pipefail

CONF_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/environment.d"
CONF_FILE="$CONF_DIR/90-8bitdo-xbox.conf"

rm -f "$CONF_FILE"
echo "[ok] Removido: $CONF_FILE"

if command -v systemctl >/dev/null 2>&1 && systemctl --user show-environment >/dev/null 2>&1; then
    systemctl --user unset-environment SDL_GAMECONTROLLERCONFIG 2>/dev/null || true
fi

if command -v flatpak >/dev/null 2>&1; then
    flatpak override --user --unset-env=SDL_GAMECONTROLLERCONFIG com.valvesoftware.Steam 2>/dev/null || true
fi

echo "[ok] Pronto. Reinicie a maquina para aplicar."
