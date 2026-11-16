#---- Validador de niveles ----#
# Validador de invariantes y alcanzabilidad de niveles.

import math
import os
import sys
from collections import deque

_RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _RAIZ not in sys.path:
    sys.path.insert(0, _RAIZ)

from config import (
    DASH_DURACION,
    DASH_VELOCIDAD,
    GRAVEDAD,
    REBOTE_ENEMIGO,
    SALTO,
    TILE,
    VELOCIDAD,
)
import niveles as _n

#---- Simbolos del mapa ----#
SOLIDO = set("#~MV=")           # bloquea el cuerpo y sirve de apoyo (incluye cripta '=')
TRAMPOLIN = "I"                 # campana de resonancia: permite rebotar y recargar dash sin bloquear el paso
PELIGRO = "^"                   # daño al pisar o caer en él
APOYADAS = set("EKBLAFWDX")     # entidades que deben tener suelo debajo (I2)
FAROL = "F"
ALTO_PISO = 18                  # filas por piso lógico (V1)

#---- Fisica de comprobacion ----#
# Altura máxima del salto puro: v²/(2g). Con SALTO=-620 y GRAVEDAD=1500 da ~128 px.
ALTURA_SALTO_FISICA = (SALTO * SALTO) / (2 * GRAVEDAD) / TILE           # tiles
# Altura máxima del rebote en campana: v²/(2g). Con REBOTE_ENEMIGO=360 da ~43.2 px (1.35 tiles).
ALTURA_REBOTE_FISICA = (REBOTE_ENEMIGO * REBOTE_ENEMIGO) / (2 * GRAVEDAD) / TILE
# Alcance horizontal del salto puro: v_x * t_vuelo. t_vuelo = 2|SALTO|/g.
ALCANCE_SALTO_FISICO = VELOCIDAD * (2 * abs(SALTO) / GRAVEDAD) / TILE   # tiles
# Desplazamiento extra del dash: velocidad * duración.
ALCANCE_DASH = DASH_VELOCIDAD * DASH_DURACION / TILE                    # tiles

# El alcance de llegada se usa conservador (por debajo del físico).
JH_LLEGADA = int(math.floor(ALTURA_SALTO_FISICA)) - 1                   # 3
JH_REBOTE = int(math.floor(ALTURA_REBOTE_FISICA))                       # 1
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


#---- Invariantes de forma ----#
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


#---- I2 apoyo de entidades ----#
def _validar_apoyo(filas, res):
    nf = len(filas)
    for r in range(nf):
        for c, ch in enumerate(filas[r]):
            if ch not in APOYADAS:
                continue
            if r + 1 >= nf or filas[r + 1][c] not in SOLIDO:
                res.errores.append(f"I2: '{ch}' en (col {c}, fila {r}) sin suelo debajo")


#---- I3 faroles ----#
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


#---- V2 / V3 aberturas en la losa de cada piso ----#
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


#---- V4 alcanzabilidad conservadora ----#
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


def _reconstruir_camino(padre, estado):
    camino = []
    actual = estado
    while actual is not None:
        camino.append(actual)
        actual = padre[actual]
    camino.reverse()
    return camino


def _sucesores_caminando(filas, c, r, nc):
    sucesores = []
    for d in (-1, 1):
        nx = c + d
        if nx < 0 or nx >= nc:
            continue
        if _es_solido(filas, nx, r) or _es_solido(filas, nx, r - 1):
            if (
                not _es_solido(filas, nx, r - 1)
                and not _es_solido(filas, nx, r - 2)
                and _es_solido(filas, nx, r)
                and filas[r - 1][nx] != PELIGRO
            ):
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
    return sucesores


def _sucesores_salto_y_rebote(filas, c, r, nc, jx):
    es_rebote_campana = r + 1 < len(filas) and filas[r + 1][c] == TRAMPOLIN
    arco_h = JH_REBOTE if es_rebote_campana else JH_ARCO
    max_dy = JH_REBOTE if es_rebote_campana else JH_LLEGADA
    if not all(not _es_solido(filas, c, y) for y in range(max(1, r - arco_h - 1), r)):
        return []

    sucesores = []
    for sentido in (-1, 1):
        for k in range(1, jx + 1):
            nx = c + sentido * k
            if nx < 0 or nx >= nc:
                break
            for dy in range(0, max_dy + 1):
                ny = r - dy
                if ny < 1 or _es_solido(filas, nx, ny) or _es_solido(filas, nx, ny - 1):
                    continue
                if filas[ny][nx] == PELIGRO:
                    continue
                if _apoyo(filas, nx, ny):
                    sucesores.append((nx, ny))
                else:
                    pie = _caer(filas, nx, ny)
                    if pie is not None:
                        sucesores.append((nx, pie))
            if any(_es_solido(filas, nx, y) for y in range(max(1, r - arco_h - 1), r)):
                break
    return sucesores


def _cerca(p, q, dist=2):
    return q is not None and abs(p[0] - q[0]) <= dist and abs(p[1] - q[1]) <= dist


def _actualizar_flags_llave(c, r, fk, fb, k_cel, b_cel):
    if k_cel is not None and not fk and _cerca((c, r), k_cel):
        fk = True
    if b_cel is not None and (k_cel is None or fk) and not fb and _cerca((c, r), b_cel):
        fb = True
    return fk, fb


def _alcanzable(
    filas, habilidades, inicio=None, meta=None, usar_k=True, usar_b=True, visitados_cr=None
):
    """BFS sobre (columna, fila_de_pie, flagK, flagB). Devuelve (ok, camino)."""
    spawn = inicio or _posiciones(filas, "P")[0]
    meta = meta or _posiciones(filas, "G")[0]
    kx = _posiciones(filas, "K") if usar_k else []
    bx = _posiciones(filas, "B") if usar_b else []
    k_cel, b_cel = (kx[0] if kx else None), (bx[0] if bx else None)
    jx = JX_DASH if "dash" in habilidades else JX_SALTO

    estado0 = (spawn[0], spawn[1], False, False)
    visitados = {estado0}
    if visitados_cr is not None:
        visitados_cr.add((spawn[0], spawn[1]))
    cola = deque([estado0])
    padre = {estado0: None}
    nc = len(filas[0])
    camino_ok = None

    while cola:
        estado = cola.popleft()
        c, r, fk, fb = estado
        meta_lista = _cerca((c, r), meta, 0) and (k_cel is None or fk) and (b_cel is None or fb)
        if camino_ok is None and meta_lista:
            camino_ok = _reconstruir_camino(padre, estado)
            if visitados_cr is None:
                return True, camino_ok

        sucesores = _sucesores_caminando(filas, c, r, nc) + _sucesores_salto_y_rebote(
            filas, c, r, nc, jx
        )
        for nx, ny in sucesores:
            if visitados_cr is not None:
                visitados_cr.add((nx, ny))
            nfk, nfb = _actualizar_flags_llave(nx, ny, fk, fb, k_cel, b_cel)
            nuevo = (nx, ny, nfk, nfb)
            if nuevo not in visitados:
                visitados.add(nuevo)
                padre[nuevo] = estado
                cola.append(nuevo)

    return (True, camino_ok) if camino_ok is not None else (False, None)


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


def _detectar_superficies_huerfanas(filas, visitados_cr):
    """Agrupa plataformas horizontales (>= 2 tiles) con espacio superior libre no alcanzadas por el BFS."""
    nf, nc = len(filas), len(filas[0])
    suelo_superficie = set("#~=")
    bloquea_arriba = SOLIDO | {PELIGRO, "|"}
    huerfanas_celdas = []
    for r in range(2, nf - 1):
        for c in range(1, nc - 1):
            if not (filas[r + 1][c] in suelo_superficie
                    and filas[r][c] not in bloquea_arriba
                    and filas[r - 1][c] not in bloquea_arriba
                    and (c, r) not in visitados_cr):
                continue
            # Ignorar la tapa de muros verticales macizos de cierre tras la losa divisoria.
            if r + 1 == ALTO_PISO - 1 and all(
                filas[rr][c] in SOLIDO for rr in range(r + 1, nf - 1)
            ):
                continue
            huerfanas_celdas.append((r, c))

    grupos = []
    for r, c in sorted(huerfanas_celdas):
        if grupos and grupos[-1][0] == r and grupos[-1][2] == c - 1:
            grupos[-1][2] = c
        else:
            grupos.append([r, c, c])
    return [(r, a, b) for r, a, b in grupos if b - a + 1 >= 2]


def _validar_sin_pozos(filas, res, habilidades, estricto, visitados_cr):
    pasos = [x for x, ok in (("K", bool(_posiciones(filas, "K"))), ("B", bool(_posiciones(filas, "B")))) if ok]
    etiqueta = "P -> " + (" -> ".join(pasos) + " -> " if pasos else "") + "G"
    ok, camino = _alcanzable(filas, habilidades, visitados_cr=visitados_cr)
    if ok:
        res.info.append(f"V4: ruta conservadora {etiqueta} ({len(camino)} estados)")
        return
    mensaje = (
        f"V4: {etiqueta} no demostrado con el modelo conservador "
        "(esto no prueba que sea imposible)"
    )
    (res.errores if estricto else res.avisos).append(mensaje)


def _validar_tramos_pozo(filas, aberturas, res, habilidades, estricto, visitados_cr):
    for losa, c in aberturas:
        if losa >= len(filas) - 1:
            continue
        borde = _borde_del_pozo(filas, losa, c)
        if borde is None:
            res.avisos.append(f"V4-sup: no hay borde de pozo para la abertura col {c}")
            continue
        ok, _ = _alcanzable(
            filas,
            habilidades,
            inicio=_posiciones(filas, "P")[0],
            meta=borde,
            usar_k=True,
            usar_b=False,
            visitados_cr=visitados_cr,
        )
        mensaje = f"V4-sup: P -> K -> borde del pozo (col {borde[0]}, fila {borde[1]})"
        if ok:
            res.info.append(mensaje + " demostrado")
        else:
            aviso = (
                mensaje
                + " NO demostrado con el modelo (el modelo no entiende plataformas móviles, "
                "rebote de pisotón ni tramos de salto largo; validar en juego)"
            )
            (res.errores if estricto else res.avisos).append(aviso)

    for losa, c in aberturas:
        pie = _aterrizaje(filas, losa, c)
        if pie is None:
            continue
        ok, _ = _alcanzable(
            filas,
            habilidades,
            inicio=(c, pie),
            meta=_posiciones(filas, "G")[0],
            usar_k=False,
            usar_b=True,
            visitados_cr=visitados_cr,
        )
        mensaje = f"V4-inf: aterrizaje (col {c}, fila {pie}) -> B -> G"
        if ok:
            res.info.append(mensaje + " demostrado")
        else:
            (res.errores if estricto else res.avisos).append(
                mensaje + " NO demostrado con el modelo conservador"
            )


def _validar_alcance(filas, res, habilidades, principal, estricto):
    if not _posiciones(filas, "P") or not _posiciones(filas, "G"):
        res.avisos.append("V4: omitido (falta P o G)")
        return

    aberturas = [(losa, c) for losa, c in _pozos(filas) if losa < len(filas) - 1]
    visitados_cr = set()
    if not aberturas:
        _validar_sin_pozos(filas, res, habilidades, estricto, visitados_cr)
    else:
        _validar_tramos_pozo(filas, aberturas, res, habilidades, estricto, visitados_cr)

    # V5: plataformas huerfanas con fisica real (error en multipiso principales).
    huerfanas = _detectar_superficies_huerfanas(filas, visitados_cr)
    es_multipiso_principal = principal and len(filas) > ALTO_PISO
    if not huerfanas:
        res.info.append("V5: 0 plataformas huérfanas con física real")
    else:
        destino = res.errores if es_multipiso_principal else res.info
        for r, a, b in huerfanas:
            destino.append(f"V5: plataforma huérfana en fila {r} (cols {a}..{b})")


DECORACIONES_PISO = set("tcrbsgu")
DECORACIONES_TECHO = set("j")
ENTIDADES_PISO = APOYADAS | set("PG")
ENEMIGOS_PISO = set("ELA")
HITOS_SEGURIDAD = set("FPGDWX")


def _validar_apoyo_decoraciones(filas, res):
    """I6a: verifica que ninguna decoración de piso o cadena 'j' quede flotando."""
    nf = len(filas)
    for r, fila in enumerate(filas):
        for c, ch in enumerate(fila):
            if ch in DECORACIONES_PISO:
                abajo = filas[r + 1][c] if r + 1 < nf else "#"
                arriba = filas[r - 1][c] if r > 0 else "."
                if abajo not in "#=":
                    res.errores.append(
                        f"I6: decoración '{ch}' flotando sin piso sólido ('#'/'=') en col {c}, fila {r}"
                    )
                elif arriba in SOLIDO:
                    res.errores.append(
                        f"I6: decoración '{ch}' incrustada bajo sólido en col {c}, fila {r}"
                    )
            elif ch in DECORACIONES_TECHO and r > 0 and filas[r - 1][c] not in "#j":
                res.errores.append(
                    f"I6: cadena 'j' suelta sin techo ni eslabón encima en col {c}, fila {r}"
                )


def _grupos_horizontales(filas, caracteres, min_largo=1):
    """Agrupa corridas horizontales contiguas de `caracteres` como tuplas (fila, col_ini, col_fin)."""
    grupos = []
    for r, fila in enumerate(filas):
        for c, ch in enumerate(fila):
            if ch not in caracteres:
                continue
            if grupos and grupos[-1][0] == r and grupos[-1][2] == c - 1:
                grupos[-1][2] = c
            else:
                grupos.append([r, c, c])
    return [(r, a, b) for r, a, b in grupos if b - a + 1 >= min_largo]


def _validar_recorridos_moviles(filas, res, destino_no_critico):
    """I6b: verifica recorridos de plataformas M (±3 cols), V (±2 filas) y órbita de Cuervos C."""
    nf, nc = len(filas), len(filas[0])
    # Plataformas horizontales M (oscilan ±3 columnas)
    for r, c0, c1 in _grupos_horizontales(filas, "M"):
        for dc in (-3, -2, -1):
            cc = c0 + dc
            if 0 <= cc < nc and filas[r][cc] not in (".", "o"):
                destino_no_critico.append(
                    f"I6: recorrido izquierdo de M({c0}..{c1}, {r}) choca con '{filas[r][cc]}' en ({cc}, {r})"
                )
        for dc in (1, 2, 3):
            cc = c1 + dc
            if 0 <= cc < nc and filas[r][cc] not in (".", "o"):
                destino_no_critico.append(
                    f"I6: recorrido derecho de M({c0}..{c1}, {r}) choca con '{filas[r][cc]}' en ({cc}, {r})"
                )
    # Plataformas verticales V (oscilan ±2 filas) y Cuervos C (órbita de radio 3 tiles)
    for r, fila in enumerate(filas):
        for c, ch in enumerate(fila):
            if ch == "V":
                for dr in (-2, -1, 1, 2):
                    rr = r + dr
                    if 0 <= rr < nf and filas[rr][c] not in (".", "o"):
                        destino_no_critico.append(
                            f"I6: recorrido vertical de V({c}, {r}) choca con '{filas[rr][c]}' en ({c}, {rr})"
                        )
            elif ch == "C":
                choque = next(
                    ((c + dc, r + dr, filas[r + dr][c + dc])
                     for dr in range(-3, 4) for dc in range(-3, 4)
                     if dc * dc + dr * dr <= 9
                     and 0 <= r + dr < nf and 0 <= c + dc < nc
                     and filas[r + dr][c + dc] in "#=~"),
                    None,
                )
                if choque is not None:
                    destino_no_critico.append(
                        f"I6: órbita de Cuervo C({c}, {r}) intersecta '{choque[2]}' en ({choque[0]}, {choque[1]})"
                    )


def _validar_espaciado_natural(filas, destino):
    """I6c: evita decoraciones pegadas celda a celda, aglomeraciones y enemigos junto a hitos."""
    nc = len(filas[0])
    ocupantes_piso = DECORACIONES_PISO | ENTIDADES_PISO
    for r, fila in enumerate(filas):
        for c in range(nc - 1):
            if fila[c] in ocupantes_piso and fila[c + 1] in ocupantes_piso:
                destino.append(
                    f"I6: objetos '{fila[c]}{fila[c + 1]}' pegados sin aire en fila {r}, cols {c}..{c + 1}"
                )
        for c, ch in enumerate(fila):
            if ch in ENEMIGOS_PISO:
                for cc in range(max(0, c - 2), min(nc, c + 3)):
                    if fila[cc] in HITOS_SEGURIDAD:
                        destino.append(
                            f"I6: enemigo '{ch}' en ({c}, {r}) demasiado cerca del hito '{fila[cc]}' (col {cc})"
                        )
        # Detectar "trencitos": 3+ decoraciones de piso en una ventana <= 7 columnas
        decos_cols = [c for c, ch in enumerate(fila) if ch in DECORACIONES_PISO]
        i = 0
        while i < len(decos_cols):
            j = i
            while j + 1 < len(decos_cols) and decos_cols[j + 1] - decos_cols[i] <= 6:
                j += 1
            if j - i + 1 >= 3:
                tramo = fila[decos_cols[i]:decos_cols[j] + 1]
                destino.append(
                    f"I6: aglomeración de decoraciones '{tramo}' en fila {r}, cols {decos_cols[i]}..{decos_cols[j]}"
                )
                i = j + 1
            else:
                i += 1


def _validar_coherencia_espacial(filas, res, nombre, principal):
    """I6: coherencia espacial, recorridos móviles y separación natural de decoraciones."""
    es_historico = (
        "NIVELES[2]" in nombre
        or (principal and len(filas) == ALTO_PISO and bool(_posiciones(filas, "K")) and bool(_posiciones(filas, "B")))
    )
    errores_antes = len(res.errores)
    avisos_antes = len(res.avisos)
    destino = res.avisos if es_historico else res.errores

    _validar_apoyo_decoraciones(filas, res)
    _validar_recorridos_moviles(filas, res, destino)
    _validar_espaciado_natural(filas, destino)

    if len(res.errores) == errores_antes and len(res.avisos) == avisos_antes:
        res.info.append("I6: coherencia espacial y decoraciones limpias")


#---- Entrada publica ----#
def validar(mapa, nombre="nivel", habilidades=("dash",), principal=True, estricto=False):
    res = Resultado(nombre)
    filas = _normalizar(mapa)
    _validar_forma(filas, res, principal)
    _validar_apoyo(filas, res)
    _validar_faroles(filas, res)
    _validar_huecos(filas, res, principal)
    _validar_coherencia_espacial(filas, res, nombre, principal)
    _validar_alcance(filas, res, habilidades, principal, estricto)
    return res


def _cargar_niveles():
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
