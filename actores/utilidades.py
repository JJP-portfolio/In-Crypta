#---- Importamos librerias ----#
import pygame


#---- Funciones auxiliares ----#
def _escalar_rect_visual_enemigo(
    rect_camara: pygame.Rect, ancho_vis: int, alto_vis: int
) -> pygame.Rect:
    """Reduce la caja visual manteniendo los pies apoyados en rect_camara.bottom."""
    return pygame.Rect(
        rect_camara.centerx - ancho_vis // 2,
        rect_camara.bottom - alto_vis,
        ancho_vis,
        alto_vis,
    )


def limitar(valor, minimo, maximo):
    """Acota un valor numerico al rango cerrado [minimo, maximo]."""
    return max(minimo, min(valor, maximo))


def _tecla_activa(teclas, key):
    # Soporta dict de tests o arreglo devuelto por pygame.key.get_pressed
    if teclas is None:
        return False
    if isinstance(teclas, dict):
        return bool(teclas.get(key, False))
    try:
        return bool(teclas[key])
    except (IndexError, TypeError, KeyError):
        return False
