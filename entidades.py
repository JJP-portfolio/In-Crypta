#---- Fachada de actores y entidades ----#
from actores.carcelero import MiniJefe
from actores.custodio import Custodio, OndaCustodio
from actores.enemigos import (
    Araña,
    Cuervo,
    Enemigo,
    EnemigoMelee,
    EntidadPatrullera,
    Polilla,
)
from actores.estampas import (
    _CACHE_ARCOS,
    _CACHE_AURAS,
    _CACHE_GHOSTS,
    _CACHE_HALOS,
    _CACHE_LUCES,
    obtener_arco_guadaña,
    obtener_aura_custodio,
    obtener_aura_farol,
    obtener_aura_pickup,
    obtener_estampa_fantasma,
    obtener_estampa_luz,
    obtener_fantasma_losa,
    obtener_halo_alma,
    obtener_halo_campana,
    obtener_halo_vela_farol,
    obtener_onda_campana,
)
from actores.interactivos import (
    BloqueCripta,
    CompuertaArena,
    FarolCheckpoint,
    IncensarioRebote,
    LosaQuebradiza,
    MuroMovilCompuerta,
)
from actores.jugador import Jugador
from actores.recogibles import (
    Alma,
    DashPowerUp,
    PalaRecogible,
    PowerUpBase,
    RangoPowerUp,
)
from actores.utilidades import _escalar_rect_visual_enemigo, _tecla_activa, limitar

__all__ = [
    "Alma",
    "Araña",
    "BloqueCripta",
    "CompuertaArena",
    "Cuervo",
    "Custodio",
    "DashPowerUp",
    "Enemigo",
    "EnemigoMelee",
    "EntidadPatrullera",
    "FarolCheckpoint",
    "IncensarioRebote",
    "Jugador",
    "LosaQuebradiza",
    "MiniJefe",
    "MuroMovilCompuerta",
    "OndaCustodio",
    "PalaRecogible",
    "Polilla",
    "PowerUpBase",
    "RangoPowerUp",
    "limitar",
    "obtener_arco_guadaña",
    "obtener_aura_custodio",
    "obtener_aura_farol",
    "obtener_aura_pickup",
    "obtener_estampa_fantasma",
    "obtener_estampa_luz",
    "obtener_fantasma_losa",
    "obtener_halo_alma",
    "obtener_halo_campana",
    "obtener_halo_vela_farol",
    "obtener_onda_campana",
]
