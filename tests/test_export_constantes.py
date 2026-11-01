# tests/test_export_constantes.py — el export nativo toma sus constantes de config.py
import os
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "tools"))

import pygame  # noqa: E402

pygame.init()

from config import (  # noqa: E402
    APEX_GRAVEDAD_FACTOR,
    APEX_VY_UMBRAL,
    ATAQUE_COOLDOWN,
    ATAQUE_DURACION,
    COYOTE_TIME,
    DASH_COOLDOWN,
    DASH_JUMP_IMPULSO_X,
    GRAVEDAD,
    JUMP_BUFFER,
    POST_DASH_DURACION,
    POST_DASH_GRAVEDAD_FACTOR,
    REBOTE_ENEMIGO,
    SALTO,
    VELOCIDAD,
)

FUENTE_GENERAR = RAIZ / "tools" / "generar_proyecto_nativo.py"
FUENTE_GDEVELOP = RAIZ / "tools" / "exportador" / "gdevelop.py"


def fuente_generar():
    return FUENTE_GENERAR.read_text(encoding="utf-8")


def fuente_gdevelop():
    return FUENTE_GDEVELOP.read_text(encoding="utf-8")


def _tipo(nodo):
    tipo = nodo.get("type")
    if isinstance(tipo, dict):
        return tipo.get("value")
    return tipo


def _parametros(nodo):
    crudos = nodo.get("parameters", [])
    return [p.get("value", "") if isinstance(p, dict) else p for p in crudos]


def acciones(nodo, tipo):
    """Parámetros de cada acción del tipo dado, en todo el árbol de eventos."""
    salida = []

    def recorrer(x):
        if isinstance(x, dict):
            if _tipo(x) == tipo and "parameters" in x:
                salida.append(_parametros(x))
            for valor in x.values():
                recorrer(valor)
        elif isinstance(x, list):
            for valor in x:
                recorrer(valor)

    recorrer(nodo)
    return salida


def posiciones(nodo, tipo, variable=None):
    """Orden de recorrido de las acciones del tipo (y variable, si se indica)."""
    orden = []
    contador = [0]

    def recorrer(x):
        if isinstance(x, dict):
            if _tipo(x) == tipo and "parameters" in x:
                params = _parametros(x)
                if variable is None or (len(params) > 1 and params[1] == variable):
                    orden.append(contador[0])
            contador[0] += 1
            for valor in x.values():
                recorrer(valor)
        elif isinstance(x, list):
            for valor in x:
                recorrer(valor)

    recorrer(nodo)
    return orden


def asignados_a(eventos, variable, operador="="):
    """Valores asignados con el operador dado a una variable de Jugador."""
    return [
        p[3]
        for p in acciones(eventos, "SetNumberObjectVariable")
        if len(p) >= 4 and p[0] == "Jugador" and p[1] == variable and p[2] == operador
    ]


def eventos_de_todas_las_escenas():
    import generar_proyecto_nativo as gen
    from nivel import Nivel
    from niveles import NIVELES

    eventos = []
    for indice, datos in enumerate(NIVELES, start=1):
        nivel = Nivel(datos["mapa"], datos["nombre"], datos["pista"], datos.get("tema", "camposanto"))
        eventos += gen.eventos_nivel(nivel, indice, len(NIVELES))
    return eventos


def probar_buffer_salto_usa_config(eventos):
    valores = [float(v) for v in asignados_a(eventos, "buffer_salto") if float(v) > 0]
    assert valores, "no hay asignación positiva al buffer de salto"
    assert all(abs(v - JUMP_BUFFER) < 1e-9 for v in valores), f"buffer_salto usa {valores}, debe ser {JUMP_BUFFER}"


def probar_coyote_usa_config(eventos):
    valores = [float(v) for v in asignados_a(eventos, "coyote") if float(v) > 0]
    assert valores, "no hay asignación positiva al coyote time"
    assert all(abs(v - COYOTE_TIME) < 1e-9 for v in valores), f"coyote usa {valores}, debe ser {COYOTE_TIME}"


def probar_ataque_usa_config(eventos):
    tiempo = [float(v) for v in asignados_a(eventos, "ataque_time") if float(v) > 0]
    cooldown = [float(v) for v in asignados_a(eventos, "ataque_cd") if float(v) > 0]
    assert tiempo and all(abs(v - ATAQUE_DURACION) < 1e-9 for v in tiempo), f"ataque_time usa {tiempo}"
    assert cooldown and all(abs(v - ATAQUE_COOLDOWN) < 1e-9 for v in cooldown), f"ataque_cd usa {cooldown}"


def probar_velocidades_de_salto_usan_config(eventos):
    permitidas = {round(-SALTO, 6), round(REBOTE_ENEMIGO, 6)}
    usadas = {round(float(p[3]), 6) for p in acciones(eventos, "PlatformBehavior::JumpSpeed") if p[0] == "Jugador"}
    assert usadas <= permitidas, f"JumpSpeed usa {usadas}, permitido {permitidas}"


def probar_sin_literales_de_config_en_el_export():
    texto = fuente_generar()
    prohibidos = ['"0.15"', '"0.18"', '"0.40"', '"0.60"', '"620"', '"360"', "* 1.18"]
    encontrados = [lit for lit in prohibidos if lit in texto]
    assert not encontrados, f"literales que deben venir de config.py: {encontrados}"


PRUEBAS_EVENTOS = [
    probar_buffer_salto_usa_config,
    probar_coyote_usa_config,
    probar_ataque_usa_config,
    probar_velocidades_de_salto_usan_config,
]
PRUEBAS_TEXTO = [probar_sin_literales_de_config_en_el_export]


if __name__ == "__main__":
    eventos = eventos_de_todas_las_escenas()
    fallos = 0
    for prueba in PRUEBAS_EVENTOS:
        try:
            prueba(eventos)
            print(f"PASS {prueba.__name__}")
        except AssertionError as error:
            fallos += 1
            print(f"FAIL {prueba.__name__}: {error}")
    for prueba in PRUEBAS_TEXTO:
        try:
            prueba()
            print(f"PASS {prueba.__name__}")
        except AssertionError as error:
            fallos += 1
            print(f"FAIL {prueba.__name__}: {error}")
    if fallos:
        print(f"TESTS_CONSTANTES_FALLAN: {fallos}")
        sys.exit(1)
    print("TESTS_CONSTANTES_OK")
