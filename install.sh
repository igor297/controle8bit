#!/usr/bin/env bash
#
# Reconhece o 8BitDo Ultimate C Wired Controller for Xbox (USB 2dc8:2026)
# como "Microsoft X-Box One pad" (type:xboxone) na camada SDL usada por
# Steam, Steam Link, Proton e jogos no Linux.
#
set -euo pipefail

CONF_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/environment.d"
CONF_FILE="$CONF_DIR/90-8bitdo-xbox.conf"
MAP='03000000c82d00002620000014010000,Microsoft X-Box One pad,a:b0,b:b1,x:b2,y:b3,back:b6,guide:b8,start:b7,leftstick:b9,rightstick:b10,leftshoulder:b4,rightshoulder:b5,dpup:h0.1,dpdown:h0.4,dpleft:h0.8,dpright:h0.2,leftx:a0,lefty:a1,rightx:a3,righty:a4,lefttrigger:a2,righttrigger:a5,type:xboxone,platform:Linux'

mkdir -p "$CONF_DIR"
printf 'SDL_GAMECONTROLLERCONFIG="%s"\n' "$MAP" > "$CONF_FILE"
echo "[ok] Arquivo criado: $CONF_FILE"

# Aplica na sessao atual (se systemd --user estiver disponivel)
if command -v systemctl >/dev/null 2>&1 && systemctl --user show-environment >/dev/null 2>&1; then
    systemctl --user set-environment SDL_GAMECONTROLLERCONFIG="$MAP" || true
    echo "[ok] Variavel aplicada no systemd --user (sessao atual)"
fi

# Steam via Flatpak nao herda variaveis da sessao; aplica override
if command -v flatpak >/dev/null 2>&1; then
    if flatpak list --app --columns=application 2>/dev/null | grep -qx 'com.valvesoftware.Steam'; then
        flatpak override --user --env="SDL_GAMECONTROLLERCONFIG=$MAP" com.valvesoftware.Steam || true
        echo "[ok] Override aplicado no Steam Flatpak"
    fi
fi

cat <<'EOF'

Proximos passos:
  1. Feche e reabra o Steam/jogo.
  2. Se a conta usa systemd com Linger=yes, o environment.d so e lido no
     boot: reinicie a maquina para valer permanentemente.
     Confira com: loginctl show-user "$USER" -p Linger
  3. Verifique com: python3 check-sdl.py
     O controle deve aparecer como "Microsoft X-Box One pad" (tipo xboxone).

Para remover: bash uninstall.sh
EOF
