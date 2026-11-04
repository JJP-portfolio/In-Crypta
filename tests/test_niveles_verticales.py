# ============================================================
# tests/test_niveles_verticales.py — Osario vertical (2 pisos).
# ============================================================
# Ejecutar (sin pygame, solo datos y validador):
#   python tests/test_niveles_verticales.py
#
# Las pruebas marcadas [pygame] usan el parser y la cámara reales.
# Se saltan si pygame no está instalado.
#
# Este archivo NO sustituye tests/test_logica.py: ese sigue siendo el
# gate principal de comportamiento. Aquí se cubre lo nuevo.
# ============================================================

import hashlib
import os
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "tools"))

import niveles  # noqa: E402  (puro: no importa pygame)
import validar_niveles as V  # noqa: E402
import config  # noqa: E402

HAS_PYGAME = True
try:
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
    import pygame  # noqa: F401
except ImportError:
    HAS_PYGAME = False

TILE = config.TILE
HABILIDADES_OSARIO = ("dash", "pala")

# SHA-256 del texto del mapa original (niveles.py antes del cambio, leído con el AST).
HASH_MAPA_ORIGINAL = {
    "NIVEL_1": "1cce7d024c90f6d3c5f75e69a37823f65746d88833d656d8eb94ee169132dd28",
    "NIVEL_2": "63632f767544492c63675bb970d00c9c6fae6b4b833a6356b34b246fa9682110",
    "NIVEL_3": "6a328ef2c5c1bd8fb770433e0b5bdba2bfcac4c658d693bdb0c7f216e7e933d3",
    "NIVEL_TUTORIAL": "5f3697aeafa5ec9d088f298a598f53d6aef6a5013fa6ec2be167c1360b1e452b",
}


# --- Datos y validador (sin pygame) ---------------------------------------

def probar_niveles_originales_sin_cambios():
    for nombre, esperado in HASH_MAPA_ORIGINAL.items():
        real = hashlib.sha256(getattr(niveles, nombre).encode()).hexdigest()
        assert real == esperado, f"{nombre} cambió respecto al original"
    assert len(niveles.NIVELES) == 3, "NIVELES no debe cambiar de tamaño"


def probar_osario_vertical_forma():
    filas = niveles.NIVEL_3_VERTICAL.strip("\n").splitlines()
    assert len(filas) == 36, f"se esperaban 36 filas, hay {len(filas)}"
    assert len(filas) % 18 == 0, "V1: múltiplo de 18"
    assert all(len(f) == len(filas[0]) for f in filas), "filas de igual largo"


def probar_osario_vertical_invariantes():
    res = V.validar(niveles.NIVEL_3_VERTICAL, "osario_vertical",
                    habilidades=HABILIDADES_OSARIO, principal=True, estricto=False)
    assert res.ok(), "errores de invariantes:\n" + "\n".join(res.errores)


def probar_tramo_inferior_demostrado():
    res = V.validar(niveles.NIVEL_3_VERTICAL, "osario_vertical",
                    habilidades=HABILIDADES_OSARIO, principal=True, estricto=False)
    tramo = [i for i in res.info if i.startswith("V4-inf") and "demostrado" in i]
    assert tramo, "el aterrizaje -> B -> G debe estar demostrado por el modelo"


def probar_validador_detecta_fallos_plantados():
    base = [list(f) for f in niveles.NIVEL_3_VERTICAL.strip("\n").splitlines()]

    def con(mod):
        m = [list(f) for f in base]
        mod(m)
        return "\n".join("".join(f) for f in m)

    casos = {
        "pinchos bajo el aterrizaje": lambda m: m[34].__setitem__(313, "^"),
        "abertura antes del spawn": lambda m: m[17].__setitem__(2, "."),
        "sin meta G": lambda m: m.__setitem__(34, [("." if c == "G" else c) for c in m[34]]),
        "abertura dentro de la sala del jefe": lambda m: m[17].__setitem__(62, "."),
    }
    for nombre, mod in casos.items():
        res = V.validar(con(mod), nombre, habilidades=HABILIDADES_OSARIO,
                        principal=True, estricto=False)
        assert not res.ok(), f"el validador debía fallar con: {nombre}"


def probar_interruptor_activado():
    assert config.OSARIO_VERTICAL is True, "la variante debe estar activada en v1.0.3"


# --- Con parser y cámara reales (requieren pygame) -------------------------

def probar_parser_osario_vertical():
    from nivel import Nivel
    n = Nivel(niveles.NIVEL_3_VERTICAL, "osario_vertical")
    assert n.alto == 36 * TILE == 1152, f"alto esperado 1152, hay {n.alto}"
    assert n.meta.y // TILE == 34, "la meta G debe estar en el piso inferior"
    assert all(j.rect.y // TILE >= 18 for j in n.jefes), "el jefe B debe estar en el piso inferior"
    assert all(s.colliderect(pygame.Rect(313 * TILE, 17 * TILE, TILE, TILE)) is False
               for s in n.solidos), "la losa de la fila 17 debe estar abierta en la col 313"


def probar_caida_por_pozo_con_camara_real():
    from nivel import Nivel
    from camara import Camara
    n = Nivel(niveles.NIVEL_3_VERTICAL, "osario_vertical")

    class _J:
        pass
    jug = _J()
    jug.rect = pygame.Rect(313 * TILE + 4, 14 * TILE + 2, 24, 30)
    cam = Camara()
    dt = 1 / 60
    vy = 0.0
    y = float(jug.rect.y)
    cam.actualizar(jug, n, dt)
    margen_minimo = 1e9
    for _ in range(60 * 5):
        vy = min(config.MAX_CAIDA, vy + config.GRAVEDAD * dt)
        y += vy * dt
        jug.rect.y = int(y)
        cam.actualizar(jug, n, dt)
        en_pantalla = jug.rect.y - cam.y
        margen_minimo = min(margen_minimo, en_pantalla, config.VIRTUAL_ALTO - (en_pantalla + jug.rect.h))
        if jug.rect.bottom >= 35 * TILE:
            break
    assert jug.rect.bottom >= 35 * TILE, "la caída debe terminar en el piso inferior"
    assert margen_minimo >= 0, "el jugador debe permanecer dentro de la vista durante la caída"
    assert abs(cam.y - (n.alto - config.VIRTUAL_ALTO)) < 1.0, "la cámara debe llegar al fondo del nivel"
    assert jug.rect.top <= n.alto + 120, "la caída al piso inferior no debe matar"


def probar_camara_nivel_18_filas_no_se_mueve():
    from nivel import Nivel
    from camara import Camara

    class _J:
        pass
    n = Nivel(niveles.NIVEL_1, "nivel_1")
    jug = _J()
    jug.rect = pygame.Rect(100, 400, 24, 30)
    cam = Camara()
    for _ in range(120):
        cam.actualizar(jug, n, 1 / 60)
    assert cam.y == 0.0, "en niveles de 18 filas la cámara debe quedarse en y = 0"


def probar_mismo_piso_identico_en_niveles_de_18_filas():
    """El filtro de franja de piso debe ser siempre verdadero en los niveles originales,
    así que el reinicio desde faro no cambia para ellos."""
    import ast
    from nivel import Nivel
    arbol = ast.parse((RAIZ / "juego.py").read_text(encoding="utf-8"))
    fn = next(n for n in arbol.body if isinstance(n, ast.FunctionDef) and n.name == "_mismo_piso")
    espacio = {"TILE": TILE}
    exec(compile(ast.Module(body=[fn], type_ignores=[]), "juego_mismo_piso", "exec"), espacio)
    mismo_piso = espacio["_mismo_piso"]
    for nombre in ("NIVEL_1", "NIVEL_2", "NIVEL_3"):
        n = Nivel(getattr(niveles, nombre), nombre)
        entidades = (list(n.almas) + n.enemigos + n.enemigos_melee)
        for ref_y in (n.spawn[1], 0, n.alto - 1):
            for e in entidades:
                assert mismo_piso(e.rect, ref_y), f"{nombre}: filtro falso para {type(e).__name__} en y={e.rect.y}"


def probar_mismo_piso_separa_franjas():
    import ast
    arbol = ast.parse((RAIZ / "juego.py").read_text(encoding="utf-8"))
    fn = next(n for n in arbol.body if isinstance(n, ast.FunctionDef) and n.name == "_mismo_piso")
    espacio = {"TILE": TILE}
    exec(compile(ast.Module(body=[fn], type_ignores=[]), "juego_mismo_piso", "exec"), espacio)
    mismo_piso = espacio["_mismo_piso"]
    r_superior = pygame.Rect(0, 14 * TILE, 24, 30)
    r_inferior = pygame.Rect(0, 34 * TILE, 24, 30)
    assert mismo_piso(r_superior, 14 * TILE + 2)
    assert not mismo_piso(r_superior, 34 * TILE + 2), "un faro del piso inferior no debe reiniciar entidades superiores"


# --- Ejecución directa ------------------------------------------------------

_SIN_PYGAME = [
    probar_niveles_originales_sin_cambios,
    probar_osario_vertical_forma,
    probar_osario_vertical_invariantes,
    probar_tramo_inferior_demostrado,
    probar_validador_detecta_fallos_plantados,
    probar_interruptor_activado,
]
_CON_PYGAME = [
    probar_mismo_piso_identico_en_niveles_de_18_filas,
    probar_mismo_piso_separa_franjas,
    probar_parser_osario_vertical,
    probar_caida_por_pozo_con_camara_real,
    probar_camara_nivel_18_filas_no_se_mueve,
]

if __name__ == "__main__":
    for prueba in _SIN_PYGAME:
        prueba()
        print(f"OK  {prueba.__name__}")
    if HAS_PYGAME:
        for prueba in _CON_PYGAME:
            prueba()
            print(f"OK  [pygame] {prueba.__name__}")
    else:
        print("SALTADAS (sin pygame): " + ", ".join(p.__name__ for p in _CON_PYGAME))
    print("\nTESTS_NIVELES_VERTICALES_OK")


# Alias para ejecución automática bajo pytest
test_niveles_originales_sin_cambios = probar_niveles_originales_sin_cambios
test_osario_vertical_forma = probar_osario_vertical_forma
test_osario_vertical_invariantes = probar_osario_vertical_invariantes
test_tramo_inferior_demostrado = probar_tramo_inferior_demostrado
test_validador_detecta_fallos_plantados = probar_validador_detecta_fallos_plantados
test_interruptor_activado = probar_interruptor_activado
test_mismo_piso_identico_en_niveles_de_18_filas = probar_mismo_piso_identico_en_niveles_de_18_filas
test_mismo_piso_separa_franjas = probar_mismo_piso_separa_franjas
test_parser_osario_vertical = probar_parser_osario_vertical
test_caida_por_pozo_con_camara_real = probar_caida_por_pozo_con_camara_real
test_camara_nivel_18_filas_no_se_mueve = probar_camara_nivel_18_filas_no_se_mueve
