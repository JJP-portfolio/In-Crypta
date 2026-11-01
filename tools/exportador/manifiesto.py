"""Manifiesto declarativo de las escenas que se exportan.

Acá vive el "qué": qué escenas existen, con qué mapa, con qué texto y cómo se
encadenan. Ningún ``if nivel == 3``: las reglas de campaña se derivan del
orden de la lista, y las diferencias entre escenas son datos.

Para agregar una escena nueva alcanza con agregar una entrada acá (o en
``niveles.py`` y que ``escenas_campaña`` la recoja).
"""

from __future__ import annotations

from dataclasses import dataclass, replace

from niveles import NIVELES, NIVEL_TUTORIAL, SALAS_PRUEBA

# Pistas adaptadas para la versión nativa (el juego original ya tiene su
# propia pista en niveles.py; estas reemplazan la redacción por la del HUD
# nativo, que usa ESPACIO y SHIFT en lugar de las teclas del Pygame).
PISTAS_NATIVAS = {
    1: (
        "FLECHAS: MOVERTE. ARRIBA: SALTAR. SHIFT: DASH. CRUZA EL PRIMER HUECO CON "
        "LA PLATAFORMA. LAS ALMAS DEL SALTO DE 3 BLOQUES MARCAN EL SALTO + DASH. "
        "EL POZO DE 7 NECESITA SHIFT EN EL AIRE. EN EL GRAN ABISMO SUBI EL ESCALON Y "
        "LA CORNISA, Y DASHEA DESDE ARRIBA."
    ),
    2: (
        "PRIMER ABISMO: SALTA Y USA SHIFT EN EL AIRE. LA PALA ESTA EN LA CORNISA. "
        "CRUZA EL HUECO GRANDE CON LA PLATAFORMA Y SUS ALMAS. EL ASCENSOR VERTICAL "
        "TE SUBE AL MURO. 10 ALMAS = 1 VIDA EXTRA."
    ),
    3: (
        "EL CUSTODIO TE PERSIGUE. ATACA SOLO CUANDO BRILLA EN ROJO. BUSCA LAS ALMAS "
        "Y ABRE EL PORTON."
    ),
}

HUD_SALTO_DASH = "ESPACIO: SALTO · SHIFT: DASH"
HUD_BUSCAR_PALA = "ESPACIO: SALTO · SHIFT: DASH · BUSCÁ LA PALA"
HUD_CON_PALA = "ESPACIO: SALTO · SHIFT: DASH · A: PALA"

# El juego arranca con la pala a partir del tercer nivel (juego.py:
# `tiene_pala = indice >= 2` en base 0).
NIVEL_CON_PALA = 3


@dataclass(frozen=True)
class EscenaSpec:
    """Todo lo que el exportador necesita saber de una escena."""

    clave: str
    nombre: str
    mapa: str
    nombre_juego: str
    pista: str
    tema: str
    titulo: str
    hud: str
    hud_sin_pala: str
    fondo: str
    pala_inicial: bool = False
    siguiente: str | None = None
    destino_muerte: str = "Derrota"
    reiniciar_vidas: bool = False
    es_sala: bool = False
    es_tutorial: bool = False


def _hud(con_pala: bool, indice: int) -> str:
    if con_pala:
        return HUD_CON_PALA
    if indice == 2:
        return HUD_BUSCAR_PALA
    return HUD_SALTO_DASH


def escenas_campaña() -> list[EscenaSpec]:
    """Los niveles de la campaña, encadenados en orden."""
    specs = []
    for indice, datos in enumerate(NIVELES, start=1):
        con_pala = indice >= NIVEL_CON_PALA
        specs.append(
            EscenaSpec(
                clave=f"nivel_{indice}",
                nombre=f"Nivel {indice}",
                mapa=datos["mapa"],
                nombre_juego=datos["nombre"],
                pista=PISTAS_NATIVAS.get(indice, datos["pista"]),
                tema=datos.get("tema", "camposanto"),
                titulo=f"NIVEL {indice} - {datos['nombre'].upper()}",
                hud=_hud(con_pala, indice),
                hud_sin_pala=_hud(False, indice),
                fondo=f"FondoNivel{indice}",
                pala_inicial=con_pala,
            )
        )

    # El encadenado se deriva del orden: el último nivel va a la victoria.
    encadenadas = []
    for posicion, spec in enumerate(specs):
        siguiente = "Victoria" if posicion == len(specs) - 1 else specs[posicion + 1].nombre
        encadenadas.append(replace(spec, siguiente=siguiente))
    return encadenadas


def escenas_salas(cantidad: int | None = None) -> list[EscenaSpec]:
    """Las salas de prueba (todas las que existan en SALAS_PRUEBA por defecto)."""
    salas = SALAS_PRUEBA if cantidad is None else SALAS_PRUEBA[:cantidad]
    specs = []
    for indice, datos in enumerate(salas, start=1):
        specs.append(
            EscenaSpec(
                clave=f"sala_{indice}",
                nombre=f"Sala {indice}",
                mapa=datos["mapa"],
                nombre_juego=datos["nombre"],
                # Las salas están escritas con la tecla "J" para la pala; en la
                # versión nativa la tecla de ataque es "A".
                pista=datos["pista"].replace(" J ", " A "),
                tema=datos.get("tema", "camposanto"),
                titulo=datos["nombre"].upper(),
                hud=_hud(bool(datos.get("pala")), indice),
                hud_sin_pala=_hud(False, indice),
                fondo=f"FondoSala{indice}",
                pala_inicial=bool(datos.get("pala")),
                siguiente="Salas",
                destino_muerte="Salas",
                reiniciar_vidas=True,
                es_sala=True,
            )
        )
    return specs


def escena_tutorial() -> EscenaSpec:
    """Escena de tutorial didáctico (Ritual del Sepulturero)."""
    return EscenaSpec(
        clave="tutorial",
        nombre="Tutorial",
        mapa=NIVEL_TUTORIAL,
        nombre_juego="Ritual del Sepulturero",
        pista=(
            "FLECHAS: MOVER · ARRIBA: SALTAR · SHIFT: DASH EN EL AIRE. "
            "EL FOSO DE 7 TILES EXIGE DASH EN EL AIRE. "
            "RECOGÉ LA PALA EN EL ALTAR, APLASTÁ AL GUARDIA CON PISOTÓN Y CRUZÁ EL UMBRAL."
        ),
        tema="camposanto",
        titulo="TUTORIAL - RITUAL DEL SEPULTURERO",
        hud=_hud(False, 2),
        hud_sin_pala=_hud(False, 2),
        fondo="FondoTutorial",
        pala_inicial=False,
        siguiente="Titulo",
        destino_muerte="Derrota",
        reiniciar_vidas=True,
        es_tutorial=True,
    )


def manifiesto_completo(cantidad_salas: int | None = None) -> list[EscenaSpec]:
    return [escena_tutorial()] + escenas_campaña() + escenas_salas(cantidad_salas)
