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

# --- Ventana, Zoom y Viewport ---
ANCHO = 1280
ALTO = 720
CAMARA_ZOOM = 1.25
VIRTUAL_ANCHO = 1024  # 1280 / 1.25
VIRTUAL_ALTO = 576    # 720 / 1.25
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
DASH_DASHTURQUESA = (92, 190, 174)
HUD_DASHTURQUESA = DASH_DASHTURQUESA

# --- Jugador ---
JUGADOR_ANCHO = 24
JUGADOR_ALTO = 30

# --- Ataque con pala ---
ATAQUE_DURACION = 0.20
ATAQUE_COOLDOWN = 0.35
ATAQUE_ALCANCE = 34
ATAQUE_ALTO = 26
ATAQUE_ALCANCE_MEJORADO = 76

# --- Jefe final ---
JEFE_VIDA = 6
JEFE_ANCHO = 48
JEFE_ALTO = 64
JEFE_VELOCIDAD = 32.0
JEFE_ONDA_VELOCIDAD = 300.0
JEFE_CARGA_VELOCIDAD = 240.0
JEFE_VULN_FASE2 = 0.85

# --- Mini-Jefe: El Carcelero del Osario ---
MINIJEFE_VIDA = 3
MINIJEFE_ANCHO = 36
MINIJEFE_ALTO = 48
MINIJEFE_VELOCIDAD = 70.0
MINIJEFE_TELEGRAFO = 0.55
MINIJEFE_VULNERABLE = 1.3
ALMAS_MANTO_FAROL = 5

# --- Enemigos ---
ENEMIGO_ANCHO = 26
ENEMIGO_ALTO = 26
VELOCIDAD_ENEMIGO = 55.0

# --- Cámara ---
CAMARA_SUAVIZADO = 7.0
SACUDIDA_FUERZA = 7.0
SACUDIDA_DURACION = 0.18

# --- Paleta poeana de claroscuro ---
NEGRO_NOCHE = (9, 8, 13)
HUESO_MARFIL = (215, 207, 184)
CARMESÍ_SANGRE = (112, 22, 34)
CARMESI_SANGRE = CARMESÍ_SANGRE
TURQUESA_ÁNIMA = (92, 190, 174)
TURQUESA_ANIMA = TURQUESA_ÁNIMA
ORO_LITÚRGICO = (198, 156, 62)
ORO_LITURGICO = ORO_LITÚRGICO
VIOLETA_POE = (75, 40, 75)
SALITRE_CRIPTA = (181, 185, 194)
FAROL_CÁLIDO = (240, 196, 90)
FAROL_CALIDO = FAROL_CÁLIDO

# --- Paleta gótica armonizada (R, G, B) ---
NEGRO = NEGRO_NOCHE
BLANCO = (225, 220, 205)
GRIS = (105, 108, 118)
AMARILLO = FAROL_CÁLIDO
ORO = ORO_LITÚRGICO
NARANJA = (190, 104, 48)
ROJO = (142, 32, 44)
SANGRE = CARMESÍ_SANGRE
VERDE = (86, 118, 82)
VERDE_OSCURO = (42, 66, 52)
MUSGO = (72, 94, 62)
MARRON = (86, 63, 48)
MARRON_OSCURO = (52, 38, 31)
AZUL = (52, 66, 92)
AZUL_OSCURO = (27, 34, 51)
CELESTE = (150, 180, 190)
CREMA = (214, 199, 168)
GRIS_OSCURO = (43, 45, 54)
HUESO = HUESO_MARFIL
SOMBRA = (9, 8, 13, 205)
PASTO = (66, 88, 60)
PIEDRA = (72, 74, 84)
PIEDRA_OSCURA = (43, 45, 54)
PIEDRA_FRIA = (58, 61, 72)
VIOLETA = (128, 70, 140)
TURQUESA = TURQUESA_ÁNIMA
NIEBLA = (104, 122, 130)

# --- Citas literarias de Edgar Allan Poe ---
CITAS_POE = {
    0: "«Los límites entre la Vida y la Muerte son borrosos e indefinidos.» — E. A. Poe",
    1: "«En lo más profundo de la fosa... una sombra más negra que la noche.» — E. A. Poe",
    2: "«¡Y la Muerte Roja reinó triunfal sobre todo el dominio!» — E. A. Poe",
    "tutorial": "«Bajo la losa sellada, la campana espera en silencio.» — E. A. Poe",
}

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
HUD_DASHTURQUESA = DASH_DASHTURQUESA
HUD_NEGRO = (9, 8, 13)
HUD_NEGRO_X = (18, 16, 24, 196)
HUD_GRIS_CLARO = (105, 108, 118)

# --- HUD Mejoras ---
HUD_ANGOSTO_ALTO = 36
HUD_MAX_ANCHO = 1280
HUD_ESQUINAS_X = [14, 478, 14, 0]
HUD_ESQUINAS_Y = [12, 12, 82, 12]
HUD_ESQUINAS_ANCHO = [292, 324, 292, HUD_MAX_ANCHO-14]
HUD_ESQUINAS_ALTO = [36, 36, 36, HUD_MAX_ANCHO-14]
