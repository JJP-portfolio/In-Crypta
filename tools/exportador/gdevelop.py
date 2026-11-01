"""Primitivas de serialización del formato de proyecto de GDevelop 5.

No hay nada de IN CRYPTA en este módulo: sólo el formato. Todo lo que el
exportador necesita para escribir un proyecto válido vive acá, para que el
resto del paquete no toque el JSON a mano.
"""

from __future__ import annotations

import uuid

from config import (
    GRAVEDAD,
    JEFE_ONDA_VELOCIDAD,
    JEFE_VIDA,
    MAX_CAIDA,
    SALTO,
    VELOCIDAD,
    VELOCIDAD_ENEMIGO,
)

from . import metadatos

FONT_RESOURCE = "FuenteHUD"


# ------------------------------------------------------------
# Identificadores y envoltorios de eventos
# ------------------------------------------------------------
def uid() -> str:
    return str(uuid.uuid4())


def cond(tipo: str, parametros=None, invertida: bool = False) -> dict:
    """Condición de GDevelop.

    Los parámetros *code-only* que el IDE espera (por ejemplo
    ``conditionInverted`` y ``currentScene`` en ``CollisionNP``) se insertan
    solos como cadenas vacías, en la posición exacta en la que el core los
    lee. Si se omiten, el IDE interpreta todos los parámetros siguientes
    corridos un lugar.
    """
    data = {"value": tipo}
    if invertida:
        data["inverted"] = True
    return {
        "type": data,
        "parameters": metadatos.completar(tipo, list(parametros or []), "condition"),
    }


def accion(tipo: str, parametros=None) -> dict:
    """Acción de GDevelop.

    Igual que ``cond``, completa los parámetros *code-only* (``objectsContext``
    en ``Create``, ``currentScene`` en ``Delete``/``PlaySound``/``Scene``...)
    en su posición exacta.
    """
    return {
        "type": {"value": tipo},
        "parameters": metadatos.completar(tipo, list(parametros or []), "action"),
    }


def evento(condiciones=None, acciones=None, subeventos=None) -> dict:
    return {
        "type": "BuiltinCommonInstructions::Standard",
        "conditions": condiciones or [],
        "actions": acciones or [],
        "events": subeventos or [],
    }


def cond_or(*condiciones) -> dict:
    return {
        "type": {"value": "BuiltinCommonInstructions::Or"},
        "parameters": [],
        "subInstructions": list(condiciones),
    }


def escena_mangled(nombre: str) -> str:
    return nombre.replace(" ", "_32_")


# ------------------------------------------------------------
# Recursos
# ------------------------------------------------------------
def recurso_imagen(nombre: str, archivo: str) -> dict:
    return {
        "file": archivo,
        "kind": "image",
        "metadata": "",
        "name": nombre,
        "smoothed": False,
        "userAdded": True,
    }


def recurso_fuente(nombre: str, archivo: str) -> dict:
    return {
        "file": archivo,
        "kind": "font",
        "metadata": "",
        "name": nombre,
        "userAdded": True,
    }


def recurso_audio(nombre: str, archivo: str) -> dict:
    return {
        "file": archivo,
        "kind": "audio",
        "metadata": "",
        "name": nombre,
        "preloadAsMusic": False,
        "preloadAsSound": True,
        "userAdded": True,
    }


# ------------------------------------------------------------
# Objetos
# ------------------------------------------------------------
def objeto_sprite(nombre: str, imagen: str, variables=None, comportamientos=None) -> dict:
    return {
        "adaptCollisionMaskAutomatically": False,
        "assetStoreId": "",
        "name": nombre,
        "persistentUuid": uid(),
        "type": "Sprite",
        "updateIfNotVisible": False,
        "variables": variables or [],
        "effects": [],
        "behaviors": comportamientos or [],
        "animations": [_animacion("Idle", [imagen], False, 0.08)],
    }


def _animacion(nombre: str, imagenes: list[str], looping: bool, tiempo: float) -> dict:
    return {
        "name": nombre,
        "useMultipleDirections": False,
        "directions": [
            {
                "looping": looping,
                "timeBetweenFrames": tiempo,
                "sprites": [
                    {
                        "hasCustomCollisionMask": False,
                        "image": imagen,
                        "points": [],
                        "originPoint": {"name": "origine", "x": 0, "y": 0},
                        # Ancla explícita en la esquina: con "automatic" el IDE
                        # recalcula el centro del sprite y todas las instancias
                        # quedan corridas media imagen.
                        "centerPoint": {"automatic": False, "name": "centre", "x": 0, "y": 0},
                    }
                    for imagen in imagenes
                ],
            }
        ],
    }


def objeto_tiled(nombre: str, textura: str, ancho: int, alto: int, comportamientos=None) -> dict:
    return {
        "assetStoreId": "",
        "height": alto,
        "name": nombre,
        "persistentUuid": uid(),
        "texture": textura,
        "type": "TiledSpriteObject::TiledSprite",
        "width": ancho,
        "variables": [],
        "effects": [],
        "behaviors": comportamientos or [],
    }


def objeto_texto(
    nombre: str,
    texto: str,
    tamano: int,
    color: tuple[int, int, int],
    alineacion: str = "left",
) -> dict:
    color_txt = f"{color[0]};{color[1]};{color[2]}"
    return {
        "assetStoreId": "",
        "bold": True,
        "italic": False,
        "name": nombre,
        "smoothed": False,
        "type": "TextObject::Text",
        "underlined": False,
        "variables": [],
        "effects": [],
        "behaviors": [],
        "string": texto,
        "font": FONT_RESOURCE,
        "textAlignment": alineacion,
        "characterSize": tamano,
        "color": {"b": color[2], "g": color[1], "r": color[0]},
        "content": {
            "bold": True,
            "isOutlineEnabled": True,
            "isShadowEnabled": True,
            "italic": False,
            "outlineColor": "9;8;13",
            "outlineThickness": 2,
            "shadowAngle": 90,
            "shadowBlurRadius": 0,
            "shadowColor": "0;0;0",
            "shadowDistance": 2,
            "shadowOpacity": 160,
            "smoothed": False,
            "underlined": False,
            "text": texto,
            "font": FONT_RESOURCE,
            "textAlignment": alineacion,
            "verticalTextAlignment": "top",
            "characterSize": tamano,
            "lineHeight": 0,
            "color": color_txt,
        },
    }


# ------------------------------------------------------------
# Instancias
# ------------------------------------------------------------
def instancia(
    nombre: str,
    x: float,
    y: float,
    z: int,
    capa: str = "",
    tam=None,
    variables=None,
) -> dict:
    """Instancia de GDevelop.

    ``variables`` se escribe en ``initialVariables`` (clave que usa el IDE).
    Ojo: si se omite, el objeto conserva los valores por defecto y las reglas
    que dependen de variables (patrulla de enemigos, recorrido de plataformas)
    se quedan sin parámetros.
    """
    ancho = 0
    alto = 0
    personalizado = False
    if tam is not None:
        ancho, alto = tam
        personalizado = True
    return {
        "angle": 0,
        "customSize": personalizado,
        "height": alto,
        "keepRatio": True,
        "layer": capa,
        "name": nombre,
        "persistentUuid": uid(),
        "width": ancho,
        "x": x,
        "y": y,
        "zOrder": z,
        "numberProperties": [],
        "stringProperties": [],
        "initialVariables": variables or [],
    }


# ------------------------------------------------------------
# Capas y escenas
# ------------------------------------------------------------
def capa_base() -> dict:
    return {
        "ambientLightColorB": 200,
        "ambientLightColorG": 200,
        "ambientLightColorR": 200,
        "camera2DPlaneMaxDrawingDistance": 5000,
        "camera3DFarPlaneDistance": 10000,
        "camera3DFieldOfView": 45,
        "camera3DNearPlaneDistance": 3,
        "cameraType": "",
        "followBaseLayerCamera": False,
        "isLightingLayer": False,
        "isLocked": False,
        "name": "",
        "renderingType": "",
        "visibility": True,
        "cameras": [
            {
                "defaultSize": True,
                "defaultViewport": True,
                "height": 0,
                "viewportBottom": 1,
                "viewportLeft": 0,
                "viewportRight": 1,
                "viewportTop": 0,
                "width": 0,
            }
        ],
        "effects": [],
    }


def capa_ui() -> dict:
    data = capa_base()
    data["name"] = "UI"
    data["cameras"] = capa_base()["cameras"]
    data["effects"] = []
    return data


def escena(nombre: str, objetos: list[dict], instancias: list[dict], eventos: list[dict]) -> dict:
    return {
        "b": 13,
        "disableInputWhenNotFocused": True,
        "mangledName": escena_mangled(nombre),
        "name": nombre,
        "r": 9,
        "renderer3DWorldScale": 100,
        "standardSortMethod": True,
        "stopSoundsOnStartup": False,
        "title": "",
        "v": 8,
        "uiSettings": {
            "grid": False,
            "gridType": "rectangular",
            "gridWidth": 32,
            "gridHeight": 32,
            "gridDepth": 32,
            "gridOffsetX": 0,
            "gridOffsetY": 0,
            "gridOffsetZ": 0,
            "gridColor": 10401023,
            "gridAlpha": 0.8,
            "snap": False,
            "zoomFactor": 0.36,
            "windowMask": False,
            "selectedLayer": "",
            "gameEditorMode": "instances-editor",
        },
        "objectsGroups": [],
        "variables": [],
        "instances": instancias,
        "objects": objetos,
        "objectsFolderStructure": {"folderName": "__ROOT"},
        "events": eventos,
        "layers": [capa_base(), capa_ui()],
        "behaviorsSharedData": [],
    }


def objeto_jugador() -> dict:
    data = objeto_sprite("Jugador", "Jugador", variables_jugador(), [comportamiento_jugador()])
    data["animations"] = [
        _animacion("Idle", ["Jugador"], True, 0.12),
        _animacion("Caida", ["JugadorCaida1", "JugadorCaida2"], True, 0.14),
        _animacion("Ataque", ["JugadorAtaque1", "JugadorAtaque2", "JugadorAtaque3"], False, 0.06),
        _animacion("IdleIzq", ["JugadorIzq"], True, 0.12),
        _animacion("CaidaIzq", ["JugadorCaidaIzq1", "JugadorCaidaIzq2"], True, 0.14),
        _animacion(
            "AtaqueIzq",
            ["JugadorAtaqueIzq1", "JugadorAtaqueIzq2", "JugadorAtaqueIzq3"],
            False,
            0.06,
        ),
        _animacion("IdleSinPala", ["JugadorSinPala"], True, 0.12),
        _animacion(
            "CaidaSinPala",
            ["JugadorCaidaSinPala1", "JugadorCaidaSinPala2"],
            True,
            0.14,
        ),
        _animacion("IdleIzqSinPala", ["JugadorIzqSinPala"], True, 0.12),
        _animacion(
            "CaidaIzqSinPala",
            ["JugadorCaidaIzqSinPala1", "JugadorCaidaIzqSinPala2"],
            True,
            0.14,
        ),
    ]
    return data


def objeto_pala() -> dict:
    return objeto_sprite("PalaRecogible", "Pala")


def objeto_plataforma() -> dict:
    return objeto_sprite(
        "PlataformaMovil",
        "PlataformaMovil",
        variables_plataforma(),
        [comportamiento_plataforma()],
    )


def objeto_golpe() -> dict:
    data = objeto_sprite(
        "GolpePala",
        "GolpePala",
        variables=[{"name": "vida", "type": "number", "value": 0.18}],
    )
    data["animations"] = [
        _animacion("Der1", ["GolpeDer1"], False, 0.18),
        _animacion("Der2", ["GolpeDer2"], False, 0.18),
        _animacion("Der3", ["GolpeDer3"], False, 0.18),
        _animacion("Izq1", ["GolpeIzq1"], False, 0.18),
        _animacion("Izq2", ["GolpeIzq2"], False, 0.18),
        _animacion("Izq3", ["GolpeIzq3"], False, 0.18),
    ]
    return data


def variables_minijefe() -> list[dict]:
    return [
        {"name": "vida", "type": "number", "value": 3},
        {"name": "dir", "type": "number", "value": 1},
        {"name": "min_x", "type": "number", "value": 0},
        {"name": "max_x", "type": "number", "value": 0},
        {"name": "estado", "type": "number", "value": 0},
        {"name": "timer", "type": "number", "value": 2.0},
        {"name": "vulnerable", "type": "number", "value": 0},
    ]


def objeto_minijefe() -> dict:
    return objeto_sprite("MiniJefe", "MiniJefe", variables_minijefe())


def variables_jefe() -> list[dict]:
    return [
        {"name": "vida", "type": "number", "value": JEFE_VIDA},
        {"name": "fase", "type": "number", "value": 1},
        {"name": "estado", "type": "number", "value": 0},
        {"name": "timer", "type": "number", "value": 1.25},
        {"name": "vulnerable", "type": "number", "value": 0},
        {"name": "golpes_fase", "type": "number", "value": 0},
    ]


def variables_onda() -> list[dict]:
    return [
        {"name": "vida", "type": "number", "value": 3.4},
        {"name": "velocidad", "type": "number", "value": int(JEFE_ONDA_VELOCIDAD)},
    ]


def objeto_jefe() -> dict:
    return objeto_sprite("Jefe", "Jefe", variables_jefe())


def objeto_onda() -> dict:
    return objeto_sprite("OndaIzq", "OndaJefe", variables_onda())


def objeto_onda_der() -> dict:
    return objeto_sprite("OndaDer", "OndaJefe", variables_onda())


def comportamiento_plataforma() -> dict:
    return {
        "name": "Platform",
        "type": "PlatformBehavior::PlatformBehavior",
        "canBeGrabbed": True,
        "platformType": "NormalPlatform",
        "yGrabOffset": 0,
    }


def comportamiento_jugador() -> dict:
    return {
        "name": "PlatformerObject",
        "type": "PlatformBehavior::PlatformerObjectBehavior",
        "acceleration": 20000,
        "canGoDownFromJumpthru": True,
        "canGrabPlatforms": False,
        "canGrabWithoutMoving": True,
        "deceleration": 20000,
        "gravity": 1500,
        "ignoreDefaultControls": True,
        "jumpSpeed": 620,
        "jumpSustainTime": 0,
        "ladderClimbingSpeed": 150,
        "maxFallingSpeed": 900,
        "maxSpeed": 250,
        "slopeMaxAngle": 60,
        "useLegacyTrajectory": False,
        "useRepeatedJump": False,
        "xGrabTolerance": 10,
        "yGrabOffset": 0,
    }


def comportamiento_enemigo() -> dict:
    data = comportamiento_jugador()
    data.update(
        {
            "acceleration": 1000,
            "deceleration": 1000,
            "gravity": 1500,
            "ignoreDefaultControls": True,
            "jumpSpeed": 0,
            "maxFallingSpeed": 900,
            "maxSpeed": VELOCIDAD_ENEMIGO,
        }
    )
    return data


def variables_jugador() -> list[dict]:
    return [
        {"name": "dir", "type": "number", "value": 1},
        {"name": "tiene_pala", "type": "number", "value": 0},
        {"name": "tiene_dash", "type": "number", "value": 0},
        {"name": "dashing", "type": "number", "value": 0},
        {"name": "dash_time", "type": "number", "value": 0},
        {"name": "dash_cd", "type": "number", "value": 0},
        {"name": "dash_aire", "type": "number", "value": 1},
        {"name": "post_dash", "type": "number", "value": 0},
        {"name": "coyote", "type": "number", "value": 0},
        {"name": "buffer_salto", "type": "number", "value": 0},
        {"name": "gravedad_actual", "type": "number", "value": 1500},
        {"name": "atacando", "type": "number", "value": 0},
        {"name": "ataque_time", "type": "number", "value": 0},
        {"name": "ataque_cd", "type": "number", "value": 0},
    ]


def variables_enemigo() -> list[dict]:
    return [
        {"name": "dir", "type": "number", "value": 1},
        {"name": "min_x", "type": "number", "value": 0},
        {"name": "max_x", "type": "number", "value": 0},
    ]


def variables_plataforma() -> list[dict]:
    return [
        {"name": "origen_x", "type": "number", "value": 0},
        {"name": "origen_y", "type": "number", "value": 0},
        {"name": "amplitud", "type": "number", "value": 96},
        {"name": "velocidad", "type": "number", "value": 1.35},
        {"name": "fase", "type": "number", "value": 0},
        {"name": "eje", "type": "number", "value": 1},
    ]
