# tests/test_export_gravedad.py — la gravedad del jugador en GDevelop tiene un único escritor
from test_export_constantes import (
    FUENTE_GDEVELOP,
    acciones,
    asignados_a,
    eventos_de_todas_las_escenas,
    fuente_generar,
    posiciones,
)
from config import APEX_GRAVEDAD_FACTOR, GRAVEDAD, POST_DASH_DURACION, POST_DASH_GRAVEDAD_FACTOR


def probar_un_solo_escritor_de_gravedad(eventos):
    escrituras = acciones(eventos, "PlatformBehavior::Gravity")
    assert escrituras, "debe haber al menos una acción PlatformBehavior::Gravity"
    # Un único escritor del comportamiento: toda la gravedad lee gravedad_actual
    for params in escrituras:
        assert "gravedad_actual" in params[3], f"gravedad no usa gravedad_actual: {params}"


def probar_valores_de_gravedad_permitidos(eventos):
    permitidos = [GRAVEDAD, GRAVEDAD * APEX_GRAVEDAD_FACTOR, GRAVEDAD * POST_DASH_GRAVEDAD_FACTOR, 0.0]
    for valor in asignados_a(eventos, "gravedad_actual"):
        assert any(abs(float(valor) - p) < 1.0 for p in permitidos), f"valor no permitido para gravedad_actual: {valor}"


def probar_aplicacion_de_gravedad_al_final(eventos):
    escrituras = posiciones(eventos, "SetNumberObjectVariable", "gravedad_actual")
    aplicacion = posiciones(eventos, "PlatformBehavior::Gravity")
    assert escrituras and aplicacion, "faltan escrituras de gravedad_actual o la aplicación"
    # La aplicación de gravedad ocurre después de calcular gravedad_actual (primer apply tras el primer write)
    assert min(aplicacion) > min(escrituras), "gravedad se aplica antes de calcularse"


def probar_post_dash_se_escribe(eventos):
    valores = [float(v) for v in asignados_a(eventos, "post_dash") if float(v) > 0]
    assert any(abs(v - POST_DASH_DURACION) < 1e-9 for v in valores), f"post_dash no se escribe con {POST_DASH_DURACION}: {valores}"


def probar_sin_variables_muertas():
    for texto_fuente in (fuente_generar(), FUENTE_GDEVELOP.read_text(encoding="utf-8")):
        for nombre in ['"velocidad_vertical"', '"velocidad_vertical_abs"', '"velocidad_vertical_umbral"', '"post_dash_timer"']:
            assert nombre not in texto_fuente, f"variable muerta todavía presente: {nombre}"


PRUEBAS_EVENTOS = [
    probar_un_solo_escritor_de_gravedad,
    probar_valores_de_gravedad_permitidos,
    probar_aplicacion_de_gravedad_al_final,
    probar_post_dash_se_escribe,
]
PRUEBAS_TEXTO = [probar_sin_variables_muertas]


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
        print(f"TESTS_GRAVEDAD_FALLAN: {fallos}")
        raise SystemExit(1)
    print("TESTS_GRAVEDAD_OK")
