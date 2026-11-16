#---- Configuracion global ----#
CALIDAD_GLOBAL_ACTIVA = 0

#---- Datos del proyecto ----#
TITULO = "IN CRYPTA"
SUBTITULO = "El sepulturero de la cripta"
EQUIPO = "Equipo 6"
INTEGRANTES = (
    "Ovelar Alejandro Ezequiel",
    "Joaquín Cardiel Gomez",
    "Jonathan Javier Pietracci",
)
ROLES_EQUIPO = {
    "Jonathan Javier Pietracci": "Programación, arquitectura, audio y documentación",
    "Ovelar Alejandro Ezequiel": "Diseño de niveles, dirección artística y testing",
    "Joaquín Cardiel Gomez": "Diseño de niveles, ambientación visual y testing",
}

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
MINIJEFE_VULNERABLE = 1.3

#---- Farol y mejoras de almas ----#
ALMAS_MANTO_FAROL = 5
ALMAS_FILO_ANIMA = 8
FILO_ANIMA_ALCANCE = 12
FILO_ANIMA_DASH_FACTOR = 0.80

#---- Elementos del escenario ----#
LOSA_TIEMPO_QUIEBRE = 0.40
LOSA_TIEMPO_RECONSTRUCCION = 2.5
INCENSARIO_COOLDOWN = 0.32
INCENSARIO_ANCHO = 24
INCENSARIO_ALTO = 28
TOLERANCIA_PISOTON = 18

#---- Tipografía y pistas crípticas ----#
OPCIONES_ESCALA_FUENTE = ((1.15, "+15%"), (1.20, "+20%"), (1.25, "+25%"))
ESCALA_FUENTES_ACTIVA = 1.15

# Inscripciones crípticas por nivel y farol (inspiradas en las pistas del arcade MK1).
INSCRIPCIONES_FAROLES = {
    0: (
        "EL OJO TEME AL ABISMO. EN ALGÚN MOMENTO HAY QUE CREER.",
        "NO MIDAS EL HUECO CON LA VISTA: IMPÚLSATE EN EL AIRE.",
        "GOLPEA EL BRONCE Y EL CIELO TE SOSTENDRÁ.",
    ),
    1: (
        "MUROS CALLADOS CEDEN ANTE EL FILO.",
        "LAS ALMAS MARCAN EL SENDERO QUE LA PIEDRA OCULTA.",
        "QUIEN DUDA EN EL AIRE SE ENTREGA A LA CAÍDA.",
    ),
    2: (
        "SOBRE EL HIERRO SE REBOTA; DEBAJO AGUARDA LA TUMBA.",
        "EL SUELO TIEMBLA ANTES DE HUNDIRSE.",
        "DETRÁS DEL CARCELERO SE CIERRA EL SEPULCRO.",
    ),
    3: (
        "EL IMPULSO EN EL AIRE VALE MÁS QUE MIL PASOS EN TIERRA.",
        "CUANDO SU FURIA BESA EL MURO, LA CORAZA SE ABRE.",
        "ENCADENA ACERO Y CARNE SIN TOCAR LA LOSA.",
        "NO BUSQUES PUENTE: EN ALGÚN MOMENTO HAY QUE CREER.",
        "LAS COMPUERTAS SE CIERRAN. ÉL MISMO CAVARÁ SU TUMBA.",
        "CADA REBOTE REABRE LA SENDA INVISIBLE.",
    ),
}
PISTA_SALTO_DE_FE_DUDA = "LO INVISIBLE SOSTIENE AL QUE CAMINA SIN VER."

#---- Enemigos basicos ----#
ENEMIGO_ANCHO = 26
ENEMIGO_ALTO = 26
ARANA_ALTO = 18
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
MUSGO = (72, 94, 62)
MARRON = (86, 63, 48)
MARRON_OSCURO = (52, 38, 31)
AZUL_OSCURO = (27, 34, 51)
CREMA = (214, 199, 168)
HUESO = HUESO_MARFIL
MARFIL_XILOGRAFICO = (228, 224, 210)
TINTA_ABISMO = (6, 5, 10)
SOMBRA = (9, 8, 13, 205)
PIEDRA = (72, 74, 84)
PIEDRA_OSCURA = (43, 45, 54)
PIEDRA_FRIA = (58, 61, 72)
VIOLETA = (128, 70, 140)
TURQUESA = TURQUESA_ANIMA

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
RUTA_FUENTE_GOTICA = "assets/NotoSerif-Bold.ttf"
HUD_BORDE = (104, 82, 52)
HUD_ORO = (216, 180, 104)
HUD_TEXTO = (232, 222, 203)
HUD_MUTED = (150, 139, 129)
HUD_ROJO = (188, 53, 62)
HUD_VERDE = (112, 194, 154)

# Opciones de renderizado
ESTILO_HUD = "AUTO"
ESTILO_MUNDO = "AUTO"
ESTILO_ENEMIGOS = "AUTO"
ESTILO_EFECTOS = "AUTO"

# Variante de nivel y continues de partida
OSARIO_VERTICAL = True
CONTINUES_INICIALES = 2


#---- Funciones auxiliares ----#
def resolver_estilo(preferencia, calidad_idx=None):
    # Resuelve el estilo segun calidad o preferencia fija
    if calidad_idx is None:
        calidad_idx = CALIDAD_GLOBAL_ACTIVA
    if preferencia in ("NES", "SNES", "PROC"):
        return preferencia
    return {0: "PROC", 1: "SNES", 2: "NES"}.get(calidad_idx, "PROC")
