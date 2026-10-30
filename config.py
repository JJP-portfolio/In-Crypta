# ============================================================
# config.py — Constantes de IN CRYPTA
# ============================================================
# Regla de Clean Code: los números que se ajustan durante el
# balanceo viven acá, no repartidos por la lógica.
# ============================================================

# --- Identidad ---
TITULO = "IN CRYPTA"
SUBTITULO = "El sepulturero de la cripta"
EQUIPO = "Equipo 6"
INTEGRANTES = (
    "Ovelar Alejandro Ezequiel",
    "Joaquín Cardiel Gomez",
    "Jonathan Javier Pietracci",
)
REFERENCIAS = ("Blasphemous", "Castlevania", "Ender Lilies")

# --- Ventana y tiempo ---
ANCHO = 960
ALTO = 540
FPS = 60
MAX_DT = 1 / 30

# --- Escala del mundo ---
TILE = 32
VIDAS_INICIALES = 3
VIDAS_MAXIMAS = 5
ALMAS_POR_VIDA = 10

# --- Física del jugador ---
GRAVEDAD = 1500.0
SALTO = -620.0
VELOCIDAD = 250.0
MAX_CAIDA = 900.0
COYOTE_TIME = 0.18
JUMP_BUFFER = 0.15
CORTE_SALTO = 0.45
INVULNERABILIDAD = 1.2
REBOTE_ENEMIGO = 360.0

# --- Dash: la segunda mecánica ---
DASH_VELOCIDAD = 560.0
DASH_DURACION = 0.20
DASH_COOLDOWN = 0.60
DASH_USOS_AIRE = 1

# --- Jugador ---
JUGADOR_ANCHO = 24
JUGADOR_ALTO = 30

# --- Ataque con pala ---
ATAQUE_DURACION = 0.20
ATAQUE_COOLDOWN = 0.38
ATAQUE_ALCANCE = 32
ATAQUE_ALTO = 24

# --- Jefe final ---
JEFE_VIDA = 6
JEFE_ANCHO = 48
JEFE_ALTO = 64
JEFE_VELOCIDAD = 26.0
JEFE_ONDA_VELOCIDAD = 300.0

# --- Enemigos ---
ENEMIGO_ANCHO = 26
ENEMIGO_ALTO = 26
VELOCIDAD_ENEMIGO = 55.0

# --- Cámara ---
CAMARA_SUAVIZADO = 7.0
SACUDIDA_FUERZA = 7.0
SACUDIDA_DURACION = 0.18

# --- Paleta gótica (R, G, B) ---
NEGRO = (9, 8, 13)
BLANCO = (225, 220, 205)
GRIS = (105, 108, 118)
AMARILLO = (214, 174, 82)
ORO = (198, 156, 62)
NARANJA = (190, 104, 48)
ROJO = (142, 32, 44)
SANGRE = (112, 22, 34)
VERDE = (86, 118, 82)
VERDE_OSCURO = (42, 66, 52)
MUSGO = (72, 94, 62)
MARRON = (86, 63, 48)
MARRON_OSCURO = (52, 38, 31)
AZUL = (52, 66, 92)
AZUL_OSCURO = (27, 34, 51)
CELESTE = (150, 180, 190)
CREMA = (214, 199, 168)
HUESO = (215, 207, 184)
SOMBRA = (7, 6, 10, 205)
PASTO = (66, 88, 60)
PIEDRA = (72, 74, 84)
PIEDRA_OSCURA = (43, 45, 54)
PIEDRA_FRIA = (58, 61, 72)
VIOLETA = (128, 96, 168)
TURQUESA = (92, 190, 174)
NIEBLA = (104, 122, 130)

# --- HUD (paleta de referencia: SOTN / Blasphemous / Ender Lilies) ---
HUD_PANEL = (18, 14, 24, 196)
HUD_PANEL_ALTO = (28, 22, 34, 214)
HUD_BORDE = (104, 82, 52)
HUD_ORO = (216, 180, 104)
HUD_TEXTO = (232, 222, 203)
HUD_MUTED = (150, 139, 129)
HUD_ROJO = (188, 53, 62)
HUD_VERDE = (112, 194, 154)
HUD_ALMA = (178, 146, 236)
HUD_NEGRO = (9, 8, 13)
HUD_GRIS_CLARO = (105, 108, 118)
HUD_GRIS_OSCURO = (43, 45, 54)
HUD_DASHTURQUESA = (92, 190, 174)
HUD_NEGRO_X = (18, 16, 24, 196)

# --- HUD Mejoras ---
HUD_ANGOSTO_ALTO = 36
HUD_MAX_ANCHO = 960
HUD_ESQUINAS_X = [14, 478, 14, 0]
HUD_ESQUINAS_Y = [12, 12, 82, 12]
HUD_ESQUINAS_ANCHO = [292, 324, 292, HUD_MAX_ANCHO-14]
HUD_ESQUINAS_ALTO = [36, 36, 36, HUD_MAX_ANCHO-14]
