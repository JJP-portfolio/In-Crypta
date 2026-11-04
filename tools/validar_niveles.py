# ============================================================
# tools/validar_niveles.py — Validador de niveles SIN pygame.
# ============================================================
# Comprueba los invariantes de niveles sobre la cadena ASCII, sin
# instanciar el motor. Solo depende de config.py y niveles.py, que son
# puros (no importan pygame), así que corre en cualquier entorno.
#
#   python tools/validar_niveles.py            # valida todos los niveles
#   python tools/validar_niveles.py --estricto # V4 fallido cuenta como error
#
# Invariantes (ver REPORTE_SISTEMA_NIVELES_v2.md, sección 6):
#   I1  Exactamente un P y un G.
#   I2  Entidades con apoyo (E L A K B F W D X) tienen suelo justo debajo.
#   I3  Faroles consecutivos: como máximo 80 columnas y 36 filas.
#   I5  Columna 0, última columna y fila superior sólidas. Fila inferior
#       sólida salvo aberturas (foso mortal).
#   V1  Niveles principales: número de filas múltiplo de 18.
#   V2  Cada abertura en la losa de un piso tiene aterrizaje válido.
#   V3  Ninguna abertura antes del spawn P en el piso superior.
#   V4  Alcanzabilidad conservadora P -> K -> ... -> B -> G.
#
# NOTA: V4 es un modelo CONSERVADOR. Si encuentra ruta, la ruta es
# físicamente posible con las constantes de config.py. Si no la
# encuentra, NO prueba que sea imposible: significa que el modelo no
# la pudo demostrar. Por eso V4 fallido es aviso salvo con --estricto.
# ============================================================

import math
import os
import sys
from collections import deque

_RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _RAIZ not in sys.path:
    sys.path.insert(0, _RAIZ)

from config import DASH_DURACION, DASH_VELOCIDAD, GRAVEDAD, SALTO, TILE, VELOCIDAD  # noqa: E402

# --- Símbolos del mapa ---------------------------------------------------
SOLIDO = set("#~MV")            # bloquea el cuerpo y sirve de apoyo
TRAMPOLIN = "I"                 # campana de resonancia: permite rebotar y recargar dash sin bloquear el paso
PELIGRO = "^"                   # daño al pisar o caer en él
APOYADAS = set("EKBLAFWDX")     # entidades que deben tener suelo debajo (I2)
FAROL = "F"
ALTO_PISO = 18                  # filas por piso lógico (V1)

# --- Física conservadora, derivada de config.py -------------------------
# Altura máxima del salto puro: v²/(2g). Con SALTO=-620 y GRAVEDAD=1500 da ~128 px.
ALTURA_SALTO_FISICA = (SALTO * SALTO) / (2 * GRAVEDAD) / TILE           # tiles
# Alcance horizontal del salto puro: v_x * t_vuelo. t_vuelo = 2|SALTO|/g.
ALCANCE_SALTO_FISICO = VELOCIDAD * (2 * abs(SALTO) / GRAVEDAD) / TILE   # tiles
# Desplazamiento extra del dash: velocidad * duración.
ALCANCE_DASH = DASH_VELOCIDAD * DASH_DURACION / TILE                    # tiles

# El alcance de llegada se usa conservador (por debajo del físico).
JH_LLEGADA = int(math.floor(ALTURA_SALTO_FISICA)) - 1                   # 3
JX_SALTO = int(math.floor(ALCANCE_SALTO_FISICO)) - 1                    # 5
JX_DASH = JX_SALTO + int(math.floor(ALCANCE_DASH)) - 1                  # 8
# La caja de colisión del arco usa la altura física completa (conservador).
JH_ARCO = int(math.floor(ALTURA_SALTO_FISICA))                          # 4


class Resultado:
    def __init__(self, nombre):
        self.nombre = nombre
        self.errores = []
        self.avisos = []
        self.info = []

    def ok(self):
        return not self.errores


def _normalizar(mapa):
    filas = mapa.strip("\n").splitlines()
    ancho = max(len(f) for f in filas)
    return [f.ljust(ancho, ".") for f in filas]


def _posiciones(filas, simbolo):
    return [(c, r) for r, fila in enumerate(filas)
            for c, ch in enumerate(fila) if ch == simbolo]


# --- Invariantes de forma ----------------------------------------------
def _validar_forma(filas, res, principal):
    nf, nc = len(filas), len(filas[0])

    # I1
    p = _posiciones(filas, "P")
    g = _posiciones(filas, "G")
    if len(p) != 1:
        res.errores.append(f"I1: se esperaba 1 P (spawn), hay {len(p)}")
    if len(g) != 1:
        res.errores.append(f"I1: se esperaba 1 G (meta), hay {len(g)}")

    # I5 bordes
    for r in range(nf):
        if filas[r][0] != "#" or filas[r][nc - 1] != "#":
            res.errores.append(f"I5: borde lateral abierto en fila {r} "
                               f"(col 0='{filas[r][0]}', col {nc-1}='{filas[r][nc-1]}')")
            break
    if any(ch != "#" for ch in filas[0]):
        res.errores.append("I5: fila superior no sólida")
    abiertos_abajo = [c for c, ch in enumerate(filas[nf - 1]) if ch != "#"]
    if abiertos_abajo:
        res.info.append(f"I5: fila inferior con {len(abiertos_abajo)} aberturas "
                        f"(foso mortal si atraviesa la losa inferior)")

    # V1
    if principal and nf % ALTO_PISO != 0:
        res.errores.append(f"V1: {nf} filas, no es múltiplo de {ALTO_PISO}")
    if not principal:
        res.info.append(f"V1: nivel no principal ({nf} filas), se omite la regla de múltiplos")


# --- I2 apoyo de entidades ---------------------------------------------
def _validar_apoyo(filas, res):
    nf = len(filas)
    for r in range(nf):
        for c, ch in enumerate(filas[r]):
            if ch not in APOYADAS:
                continue
            if r + 1 >= nf or filas[r + 1][c] not in SOLIDO:
                res.errores.append(f"I2: '{ch}' en (col {c}, fila {r}) sin suelo debajo")


# --- I3 faroles ----------------------------------------------------------
def _validar_faroles(filas, res):
    faroles = sorted(_posiciones(filas, FAROL))
    if not faroles:
        res.avisos.append("I3: el nivel no tiene faroles")
        return
    for (c1, r1), (c2, r2) in zip(faroles, faroles[1:]):
        if c2 - c1 > 80:
            res.errores.append(f"I3: {c2-c1} columnas entre faroles (col {c1} a {c2}), máximo 80")
        if abs(r2 - r1) > 36:
            res.errores.append(f"I3: {abs(r2-r1)} filas entre faroles, máximo 36")


# --- V2 / V3 aberturas en la losa de cada piso -------------------------
def _aberturas_de_losas(filas):
    """Devuelve lista de (fila_losa, columna) para cada hueco en una losa.
    Las losas son las filas con índice 18k+17 (fondo de cada piso). La
    última fila también cuenta, para detectar fosos mortales."""
    nf, nc = len(filas), len(filas[0])
    huecos = []
    for k in range(0, nf // ALTO_PISO + 1):
        losa = ALTO_PISO * k + (ALTO_PISO - 1)
        if losa >= nf - 1 and losa != nf - 1:
            continue
        if losa >= nf:
            continue
        for c in range(1, nc - 1):
            if filas[losa][c] not in SOLIDO and filas[losa][c] != PELIGRO:
                huecos.append((losa, c))
    return huecos


def _aterrizaje(filas, losa, c):
    """Primera fila con apoyo bajo la abertura. Devuelve (fila_de_pie) o None (foso mortal)."""
    nf = len(filas)
    r = losa
    while r + 1 < nf:
        r += 1
        if filas[r][c] in SOLIDO:
            return r - 1
    return None


def _validar_huecos(filas, res, principal):
    spawn = _posiciones(filas, "P")
    col_spawn = spawn[0][0] if spawn else 0
    bosses = _posiciones(filas, "B")
    col_boss = bosses[0][0] if bosses else None
    huecos = _aberturas_de_losas(filas)
    if not huecos:
        res.info.append("V2: no hay aberturas en las losas")
        return
    for losa, c in huecos:
        pie = _aterrizaje(filas, losa, c)
        if pie is None:
            res.info.append(f"V2: foso mortal en col {c} (sin suelo bajo la losa {losa})")
            continue
        if filas[pie][c] == PELIGRO or (c > 0 and filas[pie][c - 1] == PELIGRO) or \
           (c + 1 < len(filas[0]) and filas[pie][c + 1] == PELIGRO):
            res.errores.append(f"V2: aterrizaje de la abertura col {c} sobre pinchos")
        # Entidades cercanas al aterrizaje (3 tiles)
        for dc in range(-3, 4):
            cc = c + dc
            if 0 <= cc < len(filas[0]) and filas[pie][cc] in APOYADAS - set("FWDX"):
                res.avisos.append(f"V2: enemigo '{filas[pie][cc]}' a {abs(dc)} tiles del aterrizaje (col {c})")
                break
        # V3
        if principal and c < col_spawn and losa < ALTO_PISO:
            res.errores.append(f"V3: abertura en col {c} antes del spawn (col {col_spawn})")
        if col_boss is not None and abs(c - col_boss) <= 8 and pie >= 0:
            # Si la abertura cae en la sala del jefe, se salta el combate.
            res.errores.append(f"V3: abertura en col {c} dentro de la zona del jefe (col {col_boss})")
    res.info.append(f"V2: {len(huecos)} aberturas en losas revisadas")


# --- V4 alcanzabilidad conservadora ------------------------------------
def _es_solido(filas, c, r):
    if c < 0 or c >= len(filas[0]) or r < 0 or r >= len(filas):
        return True
    return filas[r][c] in SOLIDO


def _apoyo(filas, c, r):
    """La celda (c, r+1) sirve de suelo o campana de rebote (I) para un personaje que está en (c, r)."""
    if c < 0 or c >= len(filas[0]) or r + 1 < 0 or r + 1 >= len(filas):
        return True
    return _es_solido(filas, c, r + 1) or filas[r + 1][c] == TRAMPOLIN



def _caer(filas, x, y):
    """Desde (x, y) en el aire cae en vertical. Devuelve la fila de pie o None si muere o pincha."""
    nf = len(filas)
    while True:
        if y + 1 >= nf:
            return None                       # cae fuera del nivel
        if _apoyo(filas, x, y):
            if filas[y][x] == PELIGRO:
                return None
            return y
        y += 1


def _alcanzable(filas, habilidades, inicio=None, meta=None, usar_k=True, usar_b=True):
    """BFS sobre (columna, fila_de_pie, flagK, flagB). Devuelve (ok, camino).

    inicio / meta: celdas (columna, fila de pie). Por defecto P y G.
    usar_k / usar_b: exigir pasar por K / B (si existen en el mapa)."""
    spawn = inicio or _posiciones(filas, "P")[0]
    meta = meta or _posiciones(filas, "G")[0]
    kx = _posiciones(filas, "K") if usar_k else []
    bx = _posiciones(filas, "B") if usar_b else []
    k_cel = kx[0] if kx else None
    b_cel = bx[0] if bx else None
    jx = JX_DASH if "dash" in habilidades else JX_SALTO

    def cerca(p, q, d=2):
        return q is not None and abs(p[0] - q[0]) <= d and abs(p[1] - q[1]) <= d

    estado0 = (spawn[0], spawn[1], False, False)
    visitados = {estado0}
    cola = deque([estado0])
    padre = {estado0: None}
    nc = len(filas[0])

    def conviene(c, r, fk, fb):
        if k_cel is not None and not fk and cerca((c, r), k_cel):
            fk = True
        if b_cel is not None and (k_cel is None or fk) and not fb and cerca((c, r), b_cel):
            fb = True
        return fk, fb

    while cola:
        estado = cola.popleft()
        c, r, fk, fb = estado
        if cerca((c, r), meta, 0) and (k_cel is None or fk) and (b_cel is None or fb):
            camino = []
            s = estado
            while s is not None:
                camino.append(s)
                s = padre[s]
            camino.reverse()
            return True, camino

        sucesores = []
        # 1) Caminar a izquierda/derecha; si hay escalón de 1 tile, subir.
        for d in (-1, 1):
            nx = c + d
            if nx < 0 or nx >= nc:
                continue
            if _es_solido(filas, nx, r) or _es_solido(filas, nx, r - 1):
                # Escalón de un tile: el cuerpo cabe una fila más arriba.
                if (not _es_solido(filas, nx, r - 1) and not _es_solido(filas, nx, r - 2)
                        and _es_solido(filas, nx, r) and filas[r - 1][nx] != PELIGRO):
                    sucesores.append((nx, r - 1))
                continue
            if filas[r][nx] == PELIGRO:
                continue
            if _apoyo(filas, nx, r):
                sucesores.append((nx, r))
            else:
                pie = _caer(filas, nx, r)
                if pie is not None:
                    sucesores.append((nx, pie))

        # 2) Salto. Aproximación del arco: el cuerpo sube hasta JH_ARCO filas
        #    por encima de los pies. Las columnas INTERMEDIAS entre la de
        #    partida y la de llegada deben estar libres en esa altura (si no,
        #    el arco choca). La columna de llegada solo se comprueba en su
        #    propia altura de aterrizaje. Se recorre columna a columna y se
        #    corta en la primera columna que bloquea el arco.
        es_rebote_campana = (r + 1 < len(filas) and filas[r + 1][c] == TRAMPOLIN)
        arco_h = 2 if es_rebote_campana else JH_ARCO
        max_dy = 2 if es_rebote_campana else JH_LLEGADA
        if all(not _es_solido(filas, c, y) for y in range(max(1, r - arco_h - 1), r)):
            for sentido in (-1, 1):
                for k in range(1, jx + 1):
                    nx = c + sentido * k
                    if nx < 0 or nx >= nc:
                        break
                    for dy in range(0, max_dy + 1):
                        ny = r - dy
                        if ny < 1:
                            continue
                        if _es_solido(filas, nx, ny) or _es_solido(filas, nx, ny - 1):
                            continue
                        if filas[ny][nx] == PELIGRO:
                            continue
                        if _apoyo(filas, nx, ny):
                            sucesores.append((nx, ny))
                        else:
                            pie = _caer(filas, nx, ny)
                            if pie is not None:
                                sucesores.append((nx, pie))
                    # Esta columna bloquea las siguientes si el arco la cruza.
                    if any(_es_solido(filas, nx, y)
                           for y in range(max(1, r - arco_h - 1), r)):
                        break

        for nx, ny in sucesores:
            nfk, nfb = conviene(nx, ny, fk, fb)
            nuevo = (nx, ny, nfk, nfb)
            if nuevo not in visitados:
                visitados.add(nuevo)
                padre[nuevo] = estado
                cola.append(nuevo)

    return False, None


def _pozos(filas):
    """Agrupa aberturas contiguas de cada losa en pozos. Devuelve (losa, col_izq)."""
    grupos = []
    for losa, c in _aberturas_de_losas(filas):
        if grupos and grupos[-1][0] == losa and grupos[-1][2] == c - 1:
            grupos[-1][2] = c
        else:
            grupos.append([losa, c, c])
    return [(losa, izq) for losa, izq, _ in grupos]


def _borde_del_pozo(filas, losa, c):
    """Celda de pie justo a la izquierda de una abertura de losa (desde donde se cae)."""
    for r in range(losa - 1, max(-1, losa - 8), -1):
        if not _es_solido(filas, c - 1, r) and _apoyo(filas, c - 1, r):
            return (c - 1, r)
    return None


def _validar_alcance(filas, res, habilidades, estricto):
    if not _posiciones(filas, "P") or not _posiciones(filas, "G"):
        res.avisos.append("V4: omitido (falta P o G)")
        return

    aberturas = [(losa, c) for losa, c in _pozos(filas) if losa < len(filas) - 1]
    if not aberturas:
        # Sin pozos entre pisos: se comprueba P -> G completo.
        etiqueta = " -> ".join(x for x, presente in (
            ("K", bool(_posiciones(filas, "K"))), ("B", bool(_posiciones(filas, "B")))) if presente)
        etiqueta = "P -> " + (etiqueta + " -> " if etiqueta else "") + "G"
        ok, camino = _alcanzable(filas, habilidades)
        if ok:
            res.info.append(f"V4: ruta conservadora {etiqueta} ({len(camino)} estados)")
        else:
            mensaje = (f"V4: {etiqueta} no demostrado con el modelo conservador "
                       "(esto no prueba que sea imposible)")
            (res.errores if estricto else res.avisos).append(mensaje)
        return

    # Tramo superior: P -> borde del pozo, pasando por K.
    for losa, c in aberturas:
        if losa >= len(filas) - 1:
            continue
        borde = _borde_del_pozo(filas, losa, c)
        if borde is None:
            res.avisos.append(f"V4-sup: no hay borde de pozo para la abertura col {c}")
            continue
        ok, _ = _alcanzable(filas, habilidades, inicio=_posiciones(filas, "P")[0],
                            meta=borde, usar_k=True, usar_b=False)
        mensaje = f"V4-sup: P -> K -> borde del pozo (col {borde[0]}, fila {borde[1]})"
        if ok:
            res.info.append(mensaje + " demostrado")
        else:
            aviso = (mensaje + " NO demostrado con el modelo (el modelo no entiende plataformas "
                     "móviles, rebote de pisotón ni tramos de salto largo; validar en juego)")
            (res.errores if estricto else res.avisos).append(aviso)

    # Tramo inferior: aterrizaje -> G, pasando por B.
    for losa, c in aberturas:
        pie = _aterrizaje(filas, losa, c)
        if pie is None:
            continue
        ok, _ = _alcanzable(filas, habilidades, inicio=(c, pie),
                            meta=_posiciones(filas, "G")[0], usar_k=False, usar_b=True)
        mensaje = f"V4-inf: aterrizaje (col {c}, fila {pie}) -> B -> G"
        if ok:
            res.info.append(mensaje + " demostrado")
        else:
            (res.errores if estricto else res.avisos).append(
                mensaje + " NO demostrado con el modelo conservador")


# --- Entrada pública -----------------------------------------------------
def validar(mapa, nombre="nivel", habilidades=("dash",), principal=True, estricto=False):
    res = Resultado(nombre)
    filas = _normalizar(mapa)
    _validar_forma(filas, res, principal)
    _validar_apoyo(filas, res)
    _validar_faroles(filas, res)
    _validar_huecos(filas, res, principal)
    _validar_alcance(filas, res, habilidades, estricto)
    return res


def _cargar_niveles():
    import niveles as _n
    catalogo = []
    catalogo.append(("TUTORIAL", _n.NIVEL_TUTORIAL, (), False))
    habilidades_por_indice = [(), ("dash",), ("dash", "pala")]
    for i, nivel in enumerate(_n.NIVELES):
        catalogo.append((f"NIVELES[{i}] {nivel.get('nombre', '')}", nivel["mapa"],
                         habilidades_por_indice[i] if i < len(habilidades_por_indice) else ("dash",), True))
    for i, nivel in enumerate(getattr(_n, "NIVELES_VERTICALES", [])):
        catalogo.append((f"NIVELES_VERTICALES[{i}] {nivel.get('nombre', '')}", nivel["mapa"],
                         ("dash", "pala"), True))
    return catalogo


def main(argv):
    estricto = "--estricto" in argv
    fallos = 0
    for nombre, mapa, habilidades, principal in _cargar_niveles():
        res = validar(mapa, nombre, habilidades, principal, estricto)
        estado = "OK" if res.ok() else "FALLA"
        print(f"\n== {nombre}  [{estado}]  habilidades={list(habilidades)}")
        for e in res.errores:
            print(f"   ERROR  {e}")
        for a in res.avisos:
            print(f"   aviso  {a}")
        for i in res.info:
            print(f"   info   {i}")
        if not res.ok():
            fallos += 1
    print(f"\nNiveles con errores: {fallos}")
    return 1 if fallos else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
