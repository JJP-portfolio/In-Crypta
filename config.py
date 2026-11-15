#---- Importamos ----#
import sys

#---- Variables del entorno ----#
ES_WEB = sys.platform == "emscripten"
PERFIL_WEB_SHADER = 2
PERFIL_WEB_CALIDAD = 2
CALIDAD_GLOBAL_ACTIVA = 0

#---- Datos del proyecto ----#
TITULO = "IN CRYPTA"
SUBTITULO = "El sepulturero de la cripta"
EQUIPO = "Equipo 6"
VERSION = "1.0.3"
INTEGRANTES = (
    "Ovelar Alejandro Ezequiel",
    "Joaquín Cardiel Gomez",
    "Jonathan Javier Pietracci",
)
REFERENCIAS = ("Blasphemous", "Castlevania", "Ender Lilies")

#---- Dimensiones y pantalla ----#
ANCHO = 1280
ALTO = 720
CAMARA_ZOOM = 1.25
VIRTUAL_ANCHO = 1024
VIRTUAL_ALTO = 576
FPS = 60
MAX_DT = 1 / 30

#---- Escala y valores base ----#
TILE = 32
VIDAS_INICIALES = 3
VIDAS_MAXIMAS = 5
ALMAS_POR_VIDA = 10

#---- Fisica y movimiento del jugador ----#
GRAVEDAD = 1500.0
SALTO = -620.0
VELOCIDAD = 250.0
MAX_CAIDA = 900.0
COYOTE_TIME = 0.10
JUMP_BUFFER = 0.12
CORTE_SALTO = 0.45
INVULNERABILIDAD = 1.2
REBOTE_ENEMIGO = 360.0

#---- Mecanica de dash ----#
DASH_VELOCIDAD = 560.0
DASH_DURACION = 0.20
DASH_COOLDOWN = 0.60
DASH_USOS_AIRE = 1
DASH_DASHTURQUESA = (92, 190, 174)
HUD_DASHTURQUESA = DASH_DASHTURQUESA

#---- Ajustes de control y sensacion de salto ----#
APEX_GRAVEDAD_FACTOR = 0.55
APEX_VY_UMBRAL = 70.0
POST_DASH_DURACION = 0.06
POST_DASH_GRAVEDAD_FACTOR = 0.50
DASH_JUMP_IMPULSO_X = 1.18
CORNER_NUDGE_TECHO = 5

#---- Dimensiones del jugador ----#
JUGADOR_ANCHO = 24
JUGADOR_ALTO = 30

#---- Ataque con pala ----#
ATAQUE_DURACION = 0.20
ATAQUE_COOLDOWN = 0.35
ATAQUE_ALCANCE = 34
ATAQUE_ALTO = 26
ATAQUE_ALCANCE_MEJORADO = 76

#---- Jefe final: El Custodio ----#
JEFE_VIDA = 6
JEFE_ANCHO = 48
JEFE_ALTO = 64
JEFE_VELOCIDAD = 32.0
JEFE_ONDA_VELOCIDAD = 300.0
JEFE_CARGA_VELOCIDAD = 240.0
JEFE_VULN_FASE2 = 0.85

#---- Minijefe: El Carcelero ----#
MINIJEFE_VIDA = 3
MINIJEFE_ANCHO = 36
MINIJEFE_ALTO = 48
MINIJEFE_VELOCIDAD = 70.0
MINIJEFE_TELEGRAFO = 0.55
MINIJEFE_TIMER_EMBESTIDA = 0.40
MINIJEFE_VULNERABLE = 1.3

#---- Farol y mejoras de almas ----#
ALMAS_MANTO_FAROL = 5
ALMAS_FILO_ANIMA = 8
FILO_ANIMA_ALCANCE = 12
FILO_ANIMA_DASH_FACTOR = 0.80

#---- Elementos del escenario ----#
LOSA_TIEMPO_QUIEBRE = 0.40
LOSA_TIEMPO_RECONSTRUCCION = 2.5
INCENSARIO_COOLDOWN = 0.5
INCENSARIO_ANCHO = 24
INCENSARIO_ALTO = 28
TOLERANCIA_PISOTON = 18

#---- Enemigos basicos ----#
ENEMIGO_ANCHO = 26
ENEMIGO_ALTO = 26
VELOCIDAD_ENEMIGO = 55.0

#---- Camara y sacudida ----#
CAMARA_SUAVIZADO = 7.0
SACUDIDA_FUERZA = 7.0
SACUDIDA_DURACION = 0.18

#---- Paleta de colores ----#
NEGRO_NOCHE = (9, 8, 13)
HUESO_MARFIL = (215, 207, 184)
CARMESI_SANGRE = (112, 22, 34)
CARMESÍ_SANGRE = CARMESI_SANGRE
TURQUESA_ANIMA = (92, 190, 174)
TURQUESA_ÁNIMA = TURQUESA_ANIMA
ORO_LITURGICO = (198, 156, 62)
ORO_LITÚRGICO = ORO_LITURGICO
VIOLETA_POE = (75, 40, 75)
SALITRE_CRIPTA = (181, 185, 194)
FAROL_CALIDO = (240, 196, 90)
FAROL_CÁLIDO = FAROL_CALIDO

NEGRO = NEGRO_NOCHE
BLANCO = (225, 220, 205)
GRIS = (105, 108, 118)
AMARILLO = FAROL_CALIDO
ORO = ORO_LITURGICO
NARANJA = (190, 104, 48)
ROJO = (142, 32, 44)
SANGRE = CARMESI_SANGRE
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
TURQUESA = TURQUESA_ANIMA
NIEBLA = (104, 122, 130)

# Fondos y capas
BG_NOCHE_PROFUNDA = (9, 10, 18)
BG_PIEDRA_NIEBLA = (20, 24, 38)
BG_SILUETA_FRIA = (28, 34, 50)

# Bloques y muros
TILE_CUERPO_SOMBRA = (38, 36, 46)
TILE_MAMPOSTERIA = (58, 56, 70)
TILE_BISEL_LUZ = (172, 182, 202)
TILE_SOMBRA_CORTE = (10, 8, 14)

# Colores de enemigos y efectos
ENEMIGO_MORTAJA = (36, 48, 72)
ENEMIGO_PURPURA = (52, 28, 64)
ENEMIGO_RIM_LUZ = (225, 228, 240)
ENEMIGO_OJO_FUEGO = (255, 52, 68)
MELEE_ACERO_CLARO = (165, 178, 198)
FX_IMPACTO_BLANCO = (250, 248, 240)

#---- Citas de Edgar Allan Poe ----#
CITAS_POE = {
    0: "«Los límites entre la Vida y la Muerte son borrosos e indefinidos.» — E. A. Poe",
    1: "«En lo más profundo de la fosa... una sombra más negra que la noche.» — E. A. Poe",
    2: "«¡Y la Muerte Roja reinó triunfal sobre todo el dominio!» — E. A. Poe",
    "tutorial": "«Bajo la losa sellada, la campana espera en silencio.» — E. A. Poe",
}

#---- Colores y configuracion del HUD ----#
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

HUD_ANGOSTO_ALTO = 36
HUD_MAX_ANCHO = 1280
HUD_ESQUINAS_X = [14, 478, 14, 0]
HUD_ESQUINAS_Y = [12, 12, 82, 12]
HUD_ESQUINAS_ANCHO = [292, 324, 292, HUD_MAX_ANCHO - 14]
HUD_ESQUINAS_ALTO = [36, 36, 36, HUD_MAX_ANCHO - 14]

# Opciones de renderizado
ESTILO_HUD = "AUTO"
ESTILO_MUNDO = "AUTO"
ESTILO_ENEMIGOS = "AUTO"
ESTILO_EFECTOS = "AUTO"

# Variante de nivel
OSARIO_VERTICAL = True


#---- Funciones auxiliares ----#
def resolver_estilo(preferencia, calidad_idx=None):
    # Resuelve el estilo segun calidad o preferencia fija
    if calidad_idx is None:
        calidad_idx = CALIDAD_GLOBAL_ACTIVA
    if preferencia in ("NES", "SNES", "PROC"):
        return preferencia
    return {0: "PROC", 1: "SNES", 2: "NES"}.get(calidad_idx, "PROC")
