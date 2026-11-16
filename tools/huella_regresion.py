#---- Importamos librerias ----#
import hashlib
import json
import os
from pathlib import Path
import random
import sys

# Aseguramos entorno dummy y ruta del proyecto antes de importar pygame
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

RAIZ = Path(__file__).resolve().parent.parent
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

import pygame

from juego import Juego


#---- Configuracion de la huella ----#
SEMILLA_BASE = 1234
DT_FIJO = 1.0 / 60.0
CUADROS_POR_NIVEL = 600
INTERVALO_REGISTRO = 60
NIVELES_HUELLA = ("tutorial", 0, 1, 2)
RUTA_BASE = RAIZ / "tests" / "datos" / "huella_base.json"


#---- Captura de estado ----#
def _estado_enemigos(nivel):
    # Registramos tipo, estado, vida y posicion de cada enemigo
    grupos = (
        ("patrulla", nivel.enemigos),
        ("melee", getattr(nivel, "enemigos_melee", ())),
        ("cuervo", nivel.cuervos),
        ("polilla", nivel.polillas),
        ("arana", nivel.aranias),
        ("minijefe", getattr(nivel, "minijefes", ())),
    )
    salida = []
    for nombre_tipo, lista in grupos:
        for ent in lista:
            salida.append([
                nombre_tipo,
                bool(getattr(ent, "vivo", True)),
                getattr(ent, "estado", None),
                ent.rect.x,
                ent.rect.y,
            ])
    return salida


def _estado_jefe(jefe):
    # Registramos el estado del Custodio si el nivel tiene jefe
    if jefe is None:
        return None
    return {
        "estado": jefe.estado,
        "fase": jefe.fase,
        "vida": jefe.vida,
        "vivo": bool(jefe.vivo),
    }


def _instantanea_frame(juego, cuadro, incluir_pixeles=False):
    # Armamos la tupla serializable del estado en el cuadro actual
    j = juego.jugador
    n = juego.nivel
    datos = {
        "frame": cuadro,
        "estado": juego.estado,
        "jugador": {
            "x": round(float(j.x), 4),
            "y": round(float(j.y), 4),
            "vx": round(float(j.vx), 4),
            "vy": round(float(j.vy), 4),
            "vidas": j.vidas,
        },
        "almas": {
            "jugador": j.almas,
            "totales": juego.almas_totales,
            "restantes": sum(1 for a in n.almas if not a.recogida),
        },
        "enemigos": _estado_enemigos(n),
        "jefe": _estado_jefe(juego.jefe),
    }
    if incluir_pixeles:
        crudo = pygame.image.tobytes(juego.pantalla, "RGB")
        datos["pantalla_sha256"] = hashlib.sha256(crudo).hexdigest()
    return datos


def _cargar_objetivo(juego, objetivo):
    # Cargamos tutorial o nivel numerico sobre la instancia
    if objetivo == "tutorial":
        juego.iniciar_tutorial()
    else:
        juego.cargar_nivel(objetivo)


def _simular_nivel(objetivo, incluir_pixeles=False):
    # Ejecutamos 600 cuadros con guion fijo de entradas
    random.seed(SEMILLA_BASE)
    juego = Juego()
    _cargar_objetivo(juego, objetivo)

    teclas_derecha = {pygame.K_RIGHT: True}
    original_get_pressed = pygame.key.get_pressed
    pygame.key.get_pressed = lambda: teclas_derecha
    registros = []

    try:
        for cuadro in range(1, CUADROS_POR_NIVEL + 1):
            if cuadro % 40 == 0:
                juego.jugador.pedir_salto()
            if cuadro % 90 == 0:
                juego.jugador.pedir_dash()
            if cuadro % 25 == 0:
                juego.intentar_ataque()

            juego.actualizar(DT_FIJO)
            juego.dibujar()

            if cuadro % INTERVALO_REGISTRO == 0:
                registros.append(
                    _instantanea_frame(juego, cuadro, incluir_pixeles=incluir_pixeles)
                )
    finally:
        pygame.key.get_pressed = original_get_pressed

    return registros


def capturar_huella(incluir_pixeles=False):
    """Genera el diccionario completo de huella de regresion por nivel."""
    return {
        str(objetivo): _simular_nivel(objetivo, incluir_pixeles=incluir_pixeles)
        for objetivo in NIVELES_HUELLA
    }


def main():
    """Genera o verifica la huella de regresion desde linea de comandos."""
    incluir_pixeles = "--con-pixeles" in sys.argv
    datos = capturar_huella(incluir_pixeles=incluir_pixeles)
    if "--stdout" in sys.argv:
        print(json.dumps(datos, indent=2, ensure_ascii=False))
        return 0
    RUTA_BASE.parent.mkdir(parents=True, exist_ok=True)
    RUTA_BASE.write_text(
        json.dumps(datos, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"Huella guardada en {RUTA_BASE.relative_to(RAIZ)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
