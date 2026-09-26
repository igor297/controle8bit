# controle8bit

Reconhece o **8BitDo Ultimate C Wired Controller for Xbox** (USB `2dc8:2026`) como um controle Xbox de verdade no Linux, para **Steam, Steam Link, Proton e jogos** (camada SDL).

## O problema

- O kernel já trata o controle como Xbox One (driver `xpad`, protocolo GIP), mas o PID `2dc8:2026` não está na tabela do driver, então ele aparece como `Generic X-Box pad`.
- O SDL (usado pelo Steam/Proton/jogos) até gera o mapeamento de botões correto, mas reporta o **tipo como `unknown`** porque o vendor é 8BitDo (`2dc8`) e não Microsoft (`045e`).
- Resultado: o Steam classifica como **"Generic Gamepad"** em vez de Xbox.

## O que este repositório faz

Instala um mapeamento SDL que identifica o controle como:

- Nome: `Microsoft X-Box One pad`
- Tipo: `xboxone` (via campo `type:xboxone` do SDL)
- Layout: botões/eixos no padrão Xbox (A/B/X/Y, LB/RB, gatilhos analógicos, D-pad, Guide)

Assim o Steam, Steam Link e os jogos passam a tratá-lo como um controle Xbox licenciado.

## Requisitos

- Linux com SDL2/SDL3 (Steam, Proton, RetroArch etc. usam SDL)
- systemd (para o `environment.d`) — na maioria das distros
- Python 3 (apenas para o script de verificação)

## Instalação

```bash
git clone https://github.com/igor297/controle8bit.git
cd controle8bit
bash install.sh
```

O script:

1. Cria `~/.config/environment.d/90-8bitdo-xbox.conf`
2. Aplica a variável na sessão atual (`systemctl --user set-environment`)
3. Aplica override no Steam Flatpak, se existir
4. Mostra os próximos passos

### Instalação manual

Copie `90-8bitdo-xbox.conf` para `~/.config/environment.d/` e reinicie a máquina.

## Verificação

```bash
python3 check-sdl.py
```

Saída esperada para o controle:

```
[0] Generic X-Box pad
    GUID: 03008665c82d00002620000014010000
    Reconhecido como gamepad: sim
    GameController: Microsoft X-Box One pad
    Tipo SDL: xboxone
    VID:PID: 2dc8:2026
```

## Observações importantes

- **Reinicie a máquina** (não só o Steam). Se a conta tem `Linger=yes` no systemd, o `~/.config/environment.d/` só é lido no boot; logout/login não basta. Confira com:

  ```bash
  loginctl show-user "$USER" -p Linger
  ```

- **Steam via snap** herda as variáveis da sessão (funciona).
- **Steam via Flatpak** não herda variáveis da sessão — o `install.sh` aplica o override automaticamente. Para aplicar na mão:

  ```bash
  flatpak override --user --env="SDL_GAMECONTROLLERCONFIG=..." com.valvesoftware.Steam
  ```

- Isso altera a camada SDL (jogos/Steam). O nome do dispositivo no kernel (`evdev`) e o VID/PID continuam sendo 8BitDo (`2dc8:2026`); mudar isso exigiria um controle virtual via `/dev/uinput` ou patch no driver `xpad`.

## Desinstalação

```bash
bash uninstall.sh
```

## Detalhes técnicos

O mapeamento SDL é identificado pelo GUID:

```
03000000c82d00002620000014010000
```

Onde: `bus=0003` (USB), `crc=0000`, `vendor=c82d` (`0x2dc8`), `product=2620` (`0x2026`), `version=1401` (`0x0114`). A versão e o CRC são ignorados na busca quando não batem, então o mapeamento continua válido após atualização de firmware.

Mapeamento usado:

```
Microsoft X-Box One pad,a:b0,b:b1,x:b2,y:b3,back:b6,guide:b8,start:b7,leftstick:b9,rightstick:b10,leftshoulder:b4,rightshoulder:b5,dpup:h0.1,dpdown:h0.4,dpleft:h0.8,dpright:h0.2,leftx:a0,lefty:a1,rightx:a3,righty:a4,lefttrigger:a2,righttrigger:a5,type:xboxone,platform:Linux
```
