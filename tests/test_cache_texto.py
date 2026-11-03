# ============================================================
# test_cache_texto.py — caché LRU de render de texto (juego.py)
# ============================================================
# No importa juego.py (requiere pygame). Extrae la función
# renderizar_texto_cacheado y TEXTO_CACHE_MAX directamente del
# AST y las prueba con una fuente falsa que cuenta renders.
#
# Uso:  python tests/test_cache_texto.py   (o pytest tests/test_cache_texto.py)
# ============================================================

import ast
from collections import OrderedDict
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent


def _cargar_funcion():
    arbol = ast.parse((RAIZ / "juego.py").read_text(encoding="utf-8"))
    nodos = [
        n for n in arbol.body
        if (isinstance(n, ast.FunctionDef) and n.name == "renderizar_texto_cacheado")
        or (isinstance(n, ast.Assign) and any(getattr(t, "id", None) == "TEXTO_CACHE_MAX" for t in n.targets))
    ]
    assert len(nodos) == 2, "no se encontraron renderizar_texto_cacheado y TEXTO_CACHE_MAX en juego.py"
    modulo = ast.Module(body=nodos, type_ignores=[])
    ns = {"OrderedDict": OrderedDict}
    exec(compile(modulo, "juego.py", "exec"), ns)
    return ns["renderizar_texto_cacheado"], ns["TEXTO_CACHE_MAX"]


renderizar, MAXIMO_DEFECTO = _cargar_funcion()


class FuenteFalsa:
    """Imita pygame.font.Font.render y cuenta cuántas veces se rasteriza."""

    def __init__(self):
        self.renders = 0

    def render(self, texto, antialias, color):
        self.renders += 1
        return ("superficie", texto, tuple(color), self.renders)


def test_misma_clave_renderiza_una_sola_vez():
    cache, fuente = OrderedDict(), FuenteFalsa()
    a = renderizar(cache, fuente, 24, "VIGILIA", (200, 180, 120))
    b = renderizar(cache, fuente, 24, "VIGILIA", (200, 180, 120))
    assert fuente.renders == 1
    assert a is b, "el acierto debe devolver la misma superficie"


def test_color_distinto_es_otra_entrada():
    cache, fuente = OrderedDict(), FuenteFalsa()
    renderizar(cache, fuente, 24, "VIGILIA", (200, 180, 120))
    renderizar(cache, fuente, 24, "VIGILIA", (201, 180, 120))
    assert fuente.renders == 2


def test_tamano_y_texto_forman_parte_de_la_clave():
    cache, fuente = OrderedDict(), FuenteFalsa()
    renderizar(cache, fuente, 24, "A", (1, 2, 3))
    renderizar(cache, fuente, 20, "A", (1, 2, 3))
    renderizar(cache, fuente, 24, "B", (1, 2, 3))
    assert fuente.renders == 3


def test_color_como_lista_equivale_a_tupla():
    cache, fuente = OrderedDict(), FuenteFalsa()
    renderizar(cache, fuente, 24, "X", [1, 2, 3])
    renderizar(cache, fuente, 24, "X", (1, 2, 3))
    assert fuente.renders == 1


def test_limite_expulsa_la_entrada_mas_antigua():
    cache, fuente = OrderedDict(), FuenteFalsa()
    for i in range(5):
        renderizar(cache, fuente, 24, f"t{i}", (0, 0, 0), maximo=3)
    assert len(cache) == 3
    assert (24, "t0", (0, 0, 0)) not in cache and (24, "t1", (0, 0, 0)) not in cache
    assert (24, "t4", (0, 0, 0)) in cache


def test_uso_reciente_protege_de_la_expulsion():
    cache, fuente = OrderedDict(), FuenteFalsa()
    renderizar(cache, fuente, 24, "vieja", (0, 0, 0), maximo=2)
    renderizar(cache, fuente, 24, "nueva", (0, 0, 0), maximo=2)
    renderizar(cache, fuente, 24, "vieja", (0, 0, 0), maximo=2)  # la toca de nuevo
    renderizar(cache, fuente, 24, "otra", (0, 0, 0), maximo=2)   # debe expulsar "nueva"
    assert (24, "vieja", (0, 0, 0)) in cache
    assert (24, "nueva", (0, 0, 0)) not in cache


def test_cuadros_repetidos_de_titulo_casi_no_renderizan():
    """Simula 600 cuadros de la pantalla de título con prompt pulsante."""
    cache, fuente = OrderedDict(), FuenteFalsa()
    textos = [("IN CRYPTA", 76, (229, 193, 88)), ("El sepulturero", 22, (180, 170, 150))]
    for cuadro in range(600):
        for texto, tamano, color in textos:
            renderizar(cache, fuente, tamano, texto, color)
        # prompt pulsante: 86 niveles de alfa, como en dibujar_titulo
        alfa = 170 + int(((cuadro % 60) / 60) * 85)
        renderizar(cache, fuente, 20, "PRESIONÁ ENTER", (int(64 * alfa / 255), int(224 * alfa / 255), 200))
    assert fuente.renders <= 2 + 86, f"renders inesperados: {fuente.renders}"
    assert len(cache) <= MAXIMO_DEFECTO


if __name__ == "__main__":
    pruebas = [v for k, v in dict(globals()).items() if k.startswith("test_")]
    for prueba in pruebas:
        prueba()
        print(f"✔ {prueba.__name__}")
    print(f"\n{len(pruebas)} pruebas pasaron.")
