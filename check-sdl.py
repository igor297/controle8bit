#!/usr/bin/env python3
"""Mostra como o SDL (Steam, Proton, jogos) enxerga os controles conectados.

Uso:
    python3 check-sdl.py

O 8BitDo Ultimate C Wired Controller for Xbox deve aparecer como:
    GameController: Microsoft X-Box One pad
    Tipo SDL: xboxone
"""

import ctypes
import sys

TIPOS = ["unknown", "xbox360", "xboxone", "ps3", "ps4", "switchpro", "virtual", "ps5"]


class SDL_GUID(ctypes.Structure):
    _fields_ = [("data", ctypes.c_ubyte * 16)]


def carregar_sdl():
    for nome in ("libSDL2-2.0.so.0", "libSDL2.so", "libSDL2-2.0.so"):
        try:
            return ctypes.CDLL(nome)
        except OSError:
            pass
    sys.exit(
        "SDL2 nao encontrado. Instale o pacote da libsdl2 "
        "(ex.: sudo apt install libsdl2-2.0-0 / sudo dnf install SDL2)."
    )


def main():
    sdl = carregar_sdl()

    sdl.SDL_Init.argtypes = [ctypes.c_uint32]
    sdl.SDL_Init.restype = ctypes.c_int
    sdl.SDL_NumJoysticks.restype = ctypes.c_int
    sdl.SDL_IsGameController.argtypes = [ctypes.c_int]
    sdl.SDL_IsGameController.restype = ctypes.c_int
    sdl.SDL_JoystickNameForIndex.argtypes = [ctypes.c_int]
    sdl.SDL_JoystickNameForIndex.restype = ctypes.c_char_p
    sdl.SDL_JoystickGetDeviceGUID.argtypes = [ctypes.c_int]
    sdl.SDL_JoystickGetDeviceGUID.restype = SDL_GUID
    sdl.SDL_JoystickGetGUIDString.argtypes = [SDL_GUID, ctypes.c_char_p, ctypes.c_int]
    sdl.SDL_GameControllerOpen.argtypes = [ctypes.c_int]
    sdl.SDL_GameControllerOpen.restype = ctypes.c_void_p
    sdl.SDL_GameControllerName.argtypes = [ctypes.c_void_p]
    sdl.SDL_GameControllerName.restype = ctypes.c_char_p
    sdl.SDL_GameControllerGetType.argtypes = [ctypes.c_void_p]
    sdl.SDL_GameControllerGetType.restype = ctypes.c_int
    sdl.SDL_GameControllerGetVendor.argtypes = [ctypes.c_void_p]
    sdl.SDL_GameControllerGetVendor.restype = ctypes.c_uint16
    sdl.SDL_GameControllerGetProduct.argtypes = [ctypes.c_void_p]
    sdl.SDL_GameControllerGetProduct.restype = ctypes.c_uint16
    sdl.SDL_GameControllerMapping.argtypes = [ctypes.c_void_p]
    sdl.SDL_GameControllerMapping.restype = ctypes.c_char_p

    SDL_INIT_JOYSTICK = 0x00000200
    SDL_INIT_GAMECONTROLLER = 0x00002000

    if sdl.SDL_Init(SDL_INIT_JOYSTICK | SDL_INIT_GAMECONTROLLER) != 0:
        sys.exit("Falha ao iniciar o SDL.")

    total = sdl.SDL_NumJoysticks()
    print(f"Controles encontrados: {total}\n")

    for i in range(total):
        nome = sdl.SDL_JoystickNameForIndex(i) or b"?"
        guid = sdl.SDL_JoystickGetDeviceGUID(i)
        buf = ctypes.create_string_buffer(33)
        sdl.SDL_JoystickGetGUIDString(guid, buf, 33)
        eh_gamepad = sdl.SDL_IsGameController(i)

        print(f"[{i}] {nome.decode(errors='replace')}")
        print(f"    GUID: {buf.value.decode()}")
        print(f"    Reconhecido como gamepad: {'sim' if eh_gamepad else 'nao'}")

        if eh_gamepad:
            handle = sdl.SDL_GameControllerOpen(i)
            if handle:
                gc_nome = sdl.SDL_GameControllerName(handle)
                tipo = sdl.SDL_GameControllerGetType(handle)
                vendor = sdl.SDL_GameControllerGetVendor(handle)
                product = sdl.SDL_GameControllerGetProduct(handle)
                tipo_nome = TIPOS[tipo] if 0 <= tipo < len(TIPOS) else str(tipo)
                print(f"    GameController: {gc_nome.decode(errors='replace') if gc_nome else '?'}")
                print(f"    Tipo SDL: {tipo_nome}")
                print(f"    VID:PID: {vendor:04x}:{product:04x}")
                mapping = sdl.SDL_GameControllerMapping(handle)
                if mapping:
                    print(f"    Mapeamento: {mapping.decode(errors='replace')}")
        print()


if __name__ == "__main__":
    main()
