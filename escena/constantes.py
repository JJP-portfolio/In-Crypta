#---- Importamos librerias ----#
import pygame

#---- Presets de configuracion de controles ----#
PRESET_MODERNO = {
    "id": "moderno",
    "nombre": "Preset 1: WASD Moderno (WASD + Espacio + Shift + J/Click)",
    "etiqueta": "WASD Moderno",
    "desc": "Estilo PC plataformero: WASD/Flechas para mover, Espacio salto, Shift dash, J/Z/Click ataque",
    "teclas_izq": (pygame.K_a, pygame.K_LEFT),
    "teclas_der": (pygame.K_d, pygame.K_RIGHT),
    "teclas_salto": (pygame.K_SPACE, pygame.K_w, pygame.K_UP),
    "teclas_dash": (pygame.K_LSHIFT, pygame.K_RSHIFT, pygame.K_x),
    "teclas_ataque": (pygame.K_j, pygame.K_z, pygame.K_k),
    "mouse_ataque": True,
    "resumen": "Mov: WASD/←→ | Salto: ESPACIO/W | Dash: SHIFT/X | Ataque: J/Z/Click",
}

PRESET_RETRO = {
    "id": "retro",
    "nombre": "Preset 2: Retro Arcada (Flechas + Z/X/C)",
    "etiqueta": "Retro Arcada (Z-X-C)",
    "desc": "Estilo clásico de consola: Flechas para mover, Z = Salto, X = Dash, C = Ataque",
    "teclas_izq": (pygame.K_LEFT, pygame.K_a),
    "teclas_der": (pygame.K_RIGHT, pygame.K_d),
    "teclas_salto": (pygame.K_z, pygame.K_SPACE, pygame.K_UP),
    "teclas_dash": (pygame.K_x, pygame.K_LSHIFT, pygame.K_RSHIFT),
    "teclas_ataque": (pygame.K_c, pygame.K_j, pygame.K_z),
    "mouse_ataque": True,
    "resumen": "Mov: Flechas/AD | Salto: Z/ESPACIO | Dash: X/SHIFT | Ataque: C/J/Click",
}

PRESETS_TECLADO = (PRESET_MODERNO, PRESET_RETRO)

#---- Opciones de configuracion ----#
OPCIONES_CALIDAD = ("Alta", "Media", "Baja")
OPCIONES_HUD = ("Completo", "Compacto", "Inmersivo")
OPCIONES_SHADER = ("Gótico (Bloom + CRT)", "Suave (Solo Bloom)", "Puro (Pixel Art Clásico)")

#---- Teclas y parametros de combate ----#
TECLAS_SALTO = PRESET_MODERNO["teclas_salto"]
TECLAS_ATAQUE = PRESET_MODERNO["teclas_ataque"]
TOLERANCIA_PISOTON = 18
ALMAS_MINIJEFE = 5
