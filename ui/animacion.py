#---- Importamos librerias ----#
from dataclasses import dataclass

import pygame

import config


#---- Funciones de easing para transiciones ----#
def _ease_out_back(x: float) -> float:
    """Rebote suave hacia afuera al finalizar la transicion."""
    c = 4
    return float((1 + c) * x**3 - c * x**2)


def _ease_out_cubic(x: float) -> float:
    """Desaceleracion cubica hacia el valor objetivo."""
    return float(1 - (1 - x) ** 3)


def _ease_in_out_cubic(x: float) -> float:
    """Aceleracion inicial y desaceleracion final simetrica."""
    if x < 0.5:
        return 4 * x**3
    return 1 - 4 * (1 - x) ** 3


#---- Interpolacion y cache de texto ----#
@dataclass
class Tween:
    duracion: float
    transcurrido: float = 0.0
    curva: str = "out_cubic"

    def update(self, dt: float) -> None:
        self.transcurrido = min(self.duracion, self.transcurrido + dt)

    @property
    def t(self) -> float:
        if self.duracion <= 0:
            return 1.0
        return self.transcurrido / self.duracion

    def valor(self) -> float:
        t = self.t
        if self.curva == "out_back":
            return _ease_out_back(t)
        if self.curva == "in_out_cubic":
            return _ease_in_out_cubic(t)
        if self.curva == "linear":
            return t
        return _ease_out_cubic(t)

    def esta_activo(self) -> bool:
        return self.transcurrido < self.duracion

    def reiniciar(self, duracion: float, curva: str = "out_cubic") -> None:
        self.duracion = duracion
        self.curva = curva
        self.transcurrido = 0.0


#---- Cache de textos renderizados ----#
class TextoCache:
    def __init__(self, cargar_fuente):
        self.cargar_fuente = cargar_fuente
        self.cache = {}

    def render(self, texto, tamano, color, sombra=False):
        escala = round(float(getattr(config, "ESCALA_FUENTES_ACTIVA", 1.15)), 2)
        clave = (texto, tamano, escala, tuple(color), sombra)
        imagen = self.cache.get(clave)
        if imagen is None:
            fuente = self.cargar_fuente(tamano)
            imagen = fuente.render(texto, True, color)
            if sombra:
                s_sombra = fuente.render(texto, True, (8, 6, 12))
                base = pygame.Surface(
                    (imagen.get_width() + 4, imagen.get_height() + 4),
                    pygame.SRCALPHA,
                )
                for ox, oy in ((-1, 0), (1, 0), (0, -1), (0, 1), (1, 1)):
                    base.blit(s_sombra, (2 + ox, 2 + oy))
                base.blit(imagen, (2, 2))
                imagen = base
            self.cache[clave] = imagen
        return imagen


#---- Formateo y ajuste de texto ----#
def fmt_tiempo(segundos: float) -> str:
    total = max(0, int(segundos))
    return f"{total // 60:02d}:{total % 60:02d}"


def envolver(texto, fuente, ancho_max, max_lineas=2):
    """Wrap por píxeles (font.size), nunca textwrap por caracteres."""
    palabras = texto.split()
    lineas, actual = [], ""
    for palabra in palabras:
        if fuente.size(palabra)[0] > ancho_max:
            if actual:
                lineas.append(actual)
                actual = ""
            partes = _partir_palabra(palabra, fuente, ancho_max)
            lineas.extend(partes[:-1])
            actual = partes[-1]
            continue
        prueba = f"{actual} {palabra}".strip()
        if fuente.size(prueba)[0] <= ancho_max:
            actual = prueba
        else:
            if actual:
                lineas.append(actual)
            actual = palabra
    if actual:
        lineas.append(actual)
    if len(lineas) > max_lineas:
        lineas = lineas[:max_lineas]
        ultima = lineas[-1]
        while ultima and fuente.size(ultima + "…")[0] > ancho_max:
            ultima = ultima[:-1]
        lineas[-1] = ultima.rstrip(".,;: ") + "…"
    return lineas


def _partir_palabra(palabra, fuente, ancho_max):
    partes, actual = [], ""
    for caracter in palabra:
        prueba = actual + caracter
        if not actual or fuente.size(prueba)[0] <= ancho_max:
            actual = prueba
        else:
            partes.append(actual)
            actual = caracter
    if actual:
        partes.append(actual)
    return partes
