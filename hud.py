# ============================================================
# hud.py — HUD de IN CRYPTA (renovación integral)
# ============================================================
# Solo dibujo del HUD. No toca gameplay, lógica de almas, vidas,
# dash, ataque ni jefe. Lee un snapshot (HudModel) y lo renderiza.
#
# Diseño: riel superior único full-width con 3 zonas fijas,
# grilla 2×2 a la derecha, canal de mensajes único debajo del riel.
# ============================================================

import math
from dataclasses import dataclass, field
from pathlib import Path

import pygame

from config import (
    ALMAS_POR_VIDA,
    ANCHO,
    ALTO,
    ATAQUE_COOLDOWN,
    DASH_COOLDOWN,
    DASH_USOS_AIRE,
    HUD_ALMA,
    HUD_BORDE,
    HUD_DASHTURQUESA,
    HUD_MUTED,
    HUD_NEGRO,
    HUD_ORO,
    HUD_ROJO,
    HUD_TEXTO,
    HUD_VERDE,
    JEFE_VIDA,
    MAX_DT,
    VIDAS_MAXIMAS,
)
from efectos import ease_out_back, ease_out_cubic, ease_in_out_cubic

try:
    from niveles import NIVELES
except ImportError:
    NIVELES = []

# ---------------------------------------------------------------------------
# Constantes del riel (no existen todavía en config.py; se declaran acá)
# ---------------------------------------------------------------------------
HUD_MARGEN_X = 24
HUD_MARGEN_Y = 16
HUD_ALTO = 72
HUD_GAP = 12
HUD_PADDING = 12
HUD_ZONA_IZQ = 336
HUD_ZONA_CENTRO = 512
HUD_ZONA_DER = 360
HUD_MENSAJE_ANCHO = 560
HUD_MENSAJE_ALTO = 48
HUD_MENSAJE_Y = 96

# Tamaños de fuente
FUENTE_LABEL = 12
FUENTE_CONTADOR = 14
FUENTE_NOMBRE = 18

# Ruta absoluta de la fuente gótica
_RUTA_FUENTE = Path(__file__).resolve().parent / "export/gdevelop_nativo/assets/NotoSerifDisplay-Bold.ttf"

DEBUG_HUD = False


# ---------------------------------------------------------------------------
# Tween — animación basada en dt (no time.time)
# ---------------------------------------------------------------------------
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
            return ease_out_back(t)
        if self.curva == "in_out_cubic":
            return ease_in_out_cubic(t)
        if self.curva == "linear":
            return t
        return ease_out_cubic(t)

    def esta_activo(self) -> bool:
        return self.transcurrido < self.duracion

    def reiniciar(self, duracion: float, curva: str = "out_cubic") -> None:
        self.duracion = duracion
        self.curva = curva
        self.transcurrido = 0.0


# ---------------------------------------------------------------------------
# TextoCache — caché de superficies renderizadas por (texto, tamaño, color, sombra)
# ---------------------------------------------------------------------------
class TextoCache:
    def __init__(self, cargar_fuente):
        self.cargar_fuente = cargar_fuente
        self.cache = {}

    def render(self, texto, tamano, color, sombra=False):
        clave = (texto, tamano, tuple(color), sombra)
        imagen = self.cache.get(clave)
        if imagen is None:
            fuente = self.cargar_fuente(tamano)
            imagen = fuente.render(texto, True, color)
            if sombra:
                base = pygame.Surface(
                    (imagen.get_width() + 3, imagen.get_height() + 3),
                    pygame.SRCALPHA,
                )
                base.blit(fuente.render(texto, True, (0, 0, 0)), (3, 3))
                base.blit(imagen, (0, 0))
                imagen = base
            self.cache[clave] = imagen
        return imagen


# ---------------------------------------------------------------------------
# HudTheme — paleta, tamaños y espaciado
# ---------------------------------------------------------------------------
@dataclass
class HudTheme:
    panel_bg: tuple = (9, 8, 13, 190)
    panel_border: tuple = HUD_BORDE
    panel_border_alpha: int = 200
    linea_oro: tuple = (198, 156, 62, 140)
    texto: tuple = HUD_TEXTO
    texto_secundario: tuple = (170, 158, 146)
    oro: tuple = (198, 156, 62)
    alma: tuple = (92, 190, 174)
    dash_turquesa: tuple = (92, 190, 174)
    rojo: tuple = (112, 22, 34)
    verde: tuple = HUD_VERDE
    negro: tuple = (9, 8, 13)
    corazon_lleno: tuple = (195, 24, 46)
    corazon_vacio_fill: tuple = (38, 30, 42)
    corazon_vacio_borde: tuple = (110, 95, 120)
    jefe_borde_fase1: tuple = (*HUD_BORDE, 200)
    jefe_borde_fase2: tuple = (215, 45, 55)
    jefe_segmento_lleno: tuple = (225, 38, 52)
    jefe_segmento_vacio: tuple = (36, 26, 30)
    guadaña: tuple = (215, 85, 255)
    pala: tuple = (198, 156, 62)

    # Tamaños
    fuente_label: int = FUENTE_LABEL
    fuente_contador: int = FUENTE_CONTADOR
    fuente_nombre: int = FUENTE_NOMBRE
    icono_tamano: int = 16
    corazon_radio: int = 7
    corazon_pitch: int = 28


# ---------------------------------------------------------------------------
# HudLayout — rectángulos fijos de zonas, mensajes y barra de jefe
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class HudLayout:
    riel: pygame.Rect
    zona_izq: pygame.Rect
    zona_centro: pygame.Rect
    zona_der: pygame.Rect
    contenido_izq: pygame.Rect
    contenido_centro: pygame.Rect
    contenido_der: pygame.Rect
    canal_mensajes: pygame.Rect

    @classmethod
    def construir(cls, ancho=ANCHO, alto=ALTO):
        riel = pygame.Rect(HUD_MARGEN_X, HUD_MARGEN_Y,
                           ancho - 2 * HUD_MARGEN_X, HUD_ALTO)
        zona_izq = pygame.Rect(HUD_MARGEN_X, HUD_MARGEN_Y,
                               HUD_ZONA_IZQ, HUD_ALTO)
        zona_centro = pygame.Rect(
            HUD_MARGEN_X + HUD_ZONA_IZQ + HUD_GAP, HUD_MARGEN_Y,
            HUD_ZONA_CENTRO, HUD_ALTO)
        zona_der = pygame.Rect(
            HUD_MARGEN_X + HUD_ZONA_IZQ + HUD_GAP +
            HUD_ZONA_CENTRO + HUD_GAP, HUD_MARGEN_Y,
            HUD_ZONA_DER, HUD_ALTO)
        contenido_izq = pygame.Rect(
            zona_izq.x + HUD_PADDING, HUD_MARGEN_Y + 12,
            HUD_ZONA_IZQ - 2 * HUD_PADDING, HUD_ALTO - 24)
        contenido_centro = pygame.Rect(
            zona_centro.x + HUD_PADDING, HUD_MARGEN_Y + 12,
            HUD_ZONA_CENTRO - 2 * HUD_PADDING, HUD_ALTO - 24)
        contenido_der = pygame.Rect(
            zona_der.x + HUD_PADDING, HUD_MARGEN_Y + 12,
            HUD_ZONA_DER - 2 * HUD_PADDING, HUD_ALTO - 24)
        canal_mensajes = pygame.Rect(
            360, HUD_MENSAJE_Y, HUD_MENSAJE_ANCHO, HUD_MENSAJE_ALTO)
        return cls(
            riel=riel,
            zona_izq=zona_izq,
            zona_centro=zona_centro,
            zona_der=zona_der,
            contenido_izq=contenido_izq,
            contenido_centro=contenido_centro,
            contenido_der=contenido_der,
            canal_mensajes=canal_mensajes,
        )

    def solapamientos(self):
        """Devuelve lista de pares de rects que se solapan (para tests)."""
        rects = [
            ("izq", self.zona_izq),
            ("centro", self.zona_centro),
            ("der", self.zona_der),
            ("mensajes", self.canal_mensajes),
        ]
        resultado = []
        for i in range(len(rects)):
            for j in range(i + 1, len(rects)):
                if rects[i][1].colliderect(rects[j][1]):
                    resultado.append((rects[i][0], rects[j][0]))
        return resultado


# ---------------------------------------------------------------------------
# HudModel — snapshot de solo lectura con *_prev para detectar eventos
# ---------------------------------------------------------------------------
@dataclass
class HudModel:
    # Jugador
    vidas: int = 0
    vidas_max: int = VIDAS_MAXIMAS
    almas: int = 0
    almas_total: int = 0
    almas_para_vida: int = 0
    dash_cooldown: float = 0.0
    dash_usos_aire: int = 0
    tiene_dash: bool = True
    en_suelo: bool = True
    ataque_cooldown: float = 0.0
    tiene_pala: bool = False
    rango_ataque_mejorado: bool = False
    # Jefe
    jefe_vivo: bool = False
    jefe_vida: int = 0
    jefe_fase: int = 1
    jefe_nombre: str = "EL CUSTODIO DEL OSARIO"
    # Nivel / tiempo
    nivel_indice: int = 0
    nivel_total: int = 1
    nivel_nombre: str = "CAMPOSANTO"
    tiempo: float = 0.0
    # Estado / mensajes
    estado: str = "jugando"
    pista: str = ""
    aviso_jefe: float = 0.0
    # Snapshots previos (para detectar eventos sin tocar gameplay)
    vidas_prev: int = field(init=False, default=0)
    almas_prev: int = field(init=False, default=0)
    almas_para_vida_prev: int = field(init=False, default=0)
    dash_cooldown_prev: float = field(init=False, default=0.0)
    ataque_cooldown_prev: float = field(init=False, default=0.0)
    jefe_vida_prev: int = field(init=False, default=0)
    jefe_fase_prev: int = field(init=False, default=1)

    def snapshot_prev(self):
        self.vidas_prev = self.vidas
        self.almas_prev = self.almas
        self.almas_para_vida_prev = self.almas_para_vida
        self.dash_cooldown_prev = self.dash_cooldown
        self.ataque_cooldown_prev = self.ataque_cooldown
        self.jefe_vida_prev = self.jefe_vida
        self.jefe_fase_prev = self.jefe_fase

    # --- Detección de eventos (solo lectura, no muta lógica) ---
    def evento_alma_recogida(self):
        return self.almas > self.almas_prev

    def evento_perdio_vida(self):
        return self.vidas < self.vidas_prev

    def evento_vida_extra(self):
        return self.vidas > self.vidas_prev

    def evento_dash_listo(self):
        return self.dash_cooldown_prev > 0 and self.dash_cooldown <= 0

    def evento_arma_listo(self):
        return self.ataque_cooldown_prev > 0 and self.ataque_cooldown <= 0

    def evento_jefe_dañado(self):
        return self.jefe_vida < self.jefe_vida_prev

    def evento_jefe_cambio_fase(self):
        return self.jefe_fase > self.jefe_fase_prev


# ---------------------------------------------------------------------------
# MensajeHUD — un solo canal, prioridad, máquina de estados
# ---------------------------------------------------------------------------
class MensajeHUD:
    OCULTO = "oculto"
    ENTRANDO = "entrando"
    VISIBLE = "visible"
    SALIENDO = "saliendo"

    def __init__(self, layout: HudLayout, tema: HudTheme, texto_cache: TextoCache):
        self.layout = layout
        self.tema = tema
        self.texto_cache = texto_cache
        self.estado = self.OCULTO
        self.tween = Tween(0.2, 0.0, "out_cubic")
        self.hold_timer = 0.0
        self.texto = ""
        self.prioridad = 0
        self.hold = 0.0
        self.t_entrada = 0.2
        self.t_salida = 0.15

    def mostrar(self, texto, prioridad, hold):
        # Solo reemplaza si hay prioridad mayor, o si está oculto.
        # Un mensaje entrando/visible/saliendo con prioridad >= se respeta.
        if self.esta_visible() and prioridad <= self.prioridad:
            return
        self.texto = texto
        self.prioridad = prioridad
        self.hold = hold
        self.estado = self.ENTRANDO
        self.tween.reiniciar(self.t_entrada, "out_cubic")
        self.hold_timer = 0.0

    def actualizar(self, dt):
        if self.estado == self.OCULTO:
            return
        if self.estado == self.ENTRANDO:
            self.tween.update(dt)
            if not self.tween.esta_activo():
                self.estado = self.VISIBLE
                self.hold_timer = 0.0
        elif self.estado == self.VISIBLE:
            self.hold_timer += dt
            if self.hold_timer >= self.hold:
                self.estado = self.SALIENDO
                self.tween.reiniciar(self.t_salida, "in_out_cubic")
        elif self.estado == self.SALIENDO:
            self.tween.update(dt)
            if not self.tween.esta_activo():
                self.estado = self.OCULTO
                self.texto = ""
                self.prioridad = 0

    def esta_visible(self):
        return self.estado in (self.ENTRANDO, self.VISIBLE, self.SALIENDO)

    def alpha(self):
        if self.estado == self.OCULTO:
            return 0
        t = self.tween.valor()
        if self.estado == self.ENTRANDO:
            return int(255 * t)
        if self.estado == self.VISIBLE:
            return 255
        if self.estado == self.SALIENDO:
            return int(255 * (1.0 - t))
        return 0

    def offset_y(self):
        """Slide vertical de 8 px al entrar."""
        if self.estado == self.OCULTO:
            return 0
        t = self.tween.valor()
        if self.estado == self.ENTRANDO:
            # ease-out: empieza rápido, llega a 0
            return int(8 * (1.0 - t))
        if self.estado == self.VISIBLE:
            return 0
        if self.estado == self.SALIENDO:
            return int(8 * t)
        return 0


# ---------------------------------------------------------------------------
# Helpers de formato (exactos, §6.3 del plan)
# ---------------------------------------------------------------------------
def fmt_cooldown(restante: float) -> str:
    if restante <= 0:
        return "LISTO"
    decimas = math.ceil(restante * 10) / 10
    return f"{decimas:.1f}s"


def fmt_dash(model: HudModel) -> str:
    if not getattr(model, "tiene_dash", False):
        return "[DASH] --"
    if model.dash_cooldown > 0:
        return f"[DASH] {fmt_cooldown(model.dash_cooldown)}"
    if not model.en_suelo and model.dash_usos_aire <= 0:
        return "[DASH] SIN USO"
    return "[DASH] LISTO"


def fmt_arma(model: HudModel) -> str:
    if not model.tiene_pala:
        return "[PALA] --"
    etiqueta = "GUADAÑA" if model.rango_ataque_mejorado else "PALA"
    if model.ataque_cooldown > 0:
        return f"[{etiqueta}] {fmt_cooldown(model.ataque_cooldown)}"
    return f"[{etiqueta}] LISTO"


def fmt_tiempo(segundos: float) -> str:
    total = max(0, int(segundos))
    return f"{total // 60:02d}:{total % 60:02d}"


def fmt_tiempo_dec(segundos: float) -> str:
    segundos = max(0.0, segundos)
    total = int(segundos)
    decima = int((segundos - total) * 10)
    return f"{total // 60:02d}:{total % 60:02d}.{decima}"


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


# ---------------------------------------------------------------------------
# HudRenderer — dibuja el modelo; no conoce Juego
# ---------------------------------------------------------------------------
class HudRenderer:
    def __init__(self, layout: HudLayout, tema: HudTheme, texto_cache: TextoCache):
        self.layout = layout
        self.tema = tema
        self.texto_cache = texto_cache
        self._fuentes = {}
        self._paneles_cache = {}
        self._iconos_cache = {}
        self._panel_der_surface = None

    def _fuente(self, tamano):
        if tamano not in self._fuentes:
            try:
                self._fuentes[tamano] = pygame.font.Font(str(_RUTA_FUENTE), tamano)
            except Exception:
                self._fuentes[tamano] = pygame.font.Font(None, tamano)
        return self._fuentes[tamano]

    def _texto(self, texto, tamano, color, sombra=False):
        return self.texto_cache.render(texto, tamano, color, sombra)

    # --- Paneles cacheados ---
    def _panel(self, ancho, alto, alpha=None):
        clave = (ancho, alto, alpha)
        surf = self._paneles_cache.get(clave)
        if surf is None:
            a = alpha if alpha is not None else self.tema.panel_bg[3]
            surf = pygame.Surface((ancho, alto), pygame.SRCALPHA)
            pygame.draw.rect(surf, (*self.tema.panel_bg[:3], a),
                             surf.get_rect(), border_radius=12)
            pygame.draw.rect(surf, (*self.tema.panel_border,
                                    self.tema.panel_border_alpha),
                             surf.get_rect(), 1, border_radius=12)
            pygame.draw.line(surf, self.tema.linea_oro, (12, 1), (ancho - 12, 1), 1)
            # Vértices góticos
            for vx, vy, vdx, vdy in ((0, 0, 1, 1), (ancho, 0, -1, 1),
                                     (0, alto, 1, -1), (ancho, alto, -1, -1)):
                pygame.draw.line(surf, HUD_ORO, (vx + 4 * vdx, vy),
                                 (vx + 16 * vdx, vy), 1)
                pygame.draw.line(surf, HUD_ORO, (vx, vy + 4 * vdy),
                                 (vx, vy + 14 * vdy), 1)
            surf = surf.convert_alpha()
            self._paneles_cache[clave] = surf
        return surf

    # --- Iconos dibujados con pygame.draw (sin assets) ---
    def _icono_corazon(self, cx, cy, lleno, escala=1.0, tema=None):
        t = tema or self.tema
        r = int(t.corazon_radio * escala)
        top_y = cy - 4
        tip_y = cy + 14
        pantalla = None  # se dibuja en superficie destino por el llamador
        return (cx, cy, r, top_y, tip_y, lleno, t)

    def dibujar_corazon(self, pantalla, cx, cy, lleno, escala=1.0):
        t = self.tema
        r = int(t.corazon_radio * escala)
        top_y = cy - 4
        tip_y = cy + 14
        if lleno:
            color_base = t.corazon_lleno
            color_borde = (160, 18, 32)
            color_destello = (255, 235, 240)
            color_brillo = (255, 110, 130)
        else:
            color_base = t.corazon_vacio_fill
            color_borde = t.corazon_vacio_borde
            color_destello = None
            color_brillo = None
        color_sombra = (16, 12, 18)
        # Marco de hierro forjado gótico
        pygame.draw.circle(pantalla, color_sombra, (cx - 6, top_y + 1), r + 2)
        pygame.draw.circle(pantalla, color_sombra, (cx + 6, top_y + 1), r + 2)
        pygame.draw.polygon(pantalla, color_sombra,
                            [(cx - 13, top_y + 1), (cx + 13, top_y + 1), (cx, tip_y + 2)])
        # Cuerpo principal del corazón
        pygame.draw.circle(pantalla, color_base, (cx - 6, top_y), r)
        pygame.draw.circle(pantalla, color_base, (cx + 6, top_y), r)
        pygame.draw.polygon(pantalla, color_base,
                            [(cx - 11, top_y), (cx + 11, top_y), (cx, tip_y)])
        pygame.draw.line(pantalla, color_borde, (cx - 11, top_y), (cx, tip_y), 1)
        pygame.draw.line(pantalla, color_borde, (cx + 11, top_y), (cx, tip_y), 1)
        pygame.draw.arc(pantalla, color_borde,
                        (cx - 6 - r, top_y - r, r * 2, r * 2), 0, 3.14, 1)
        pygame.draw.arc(pantalla, color_borde,
                        (cx + 6 - r, top_y - r, r * 2, r * 2), 0, 3.14, 1)
        if lleno:
            # Faceta facetada de rubí (sombra lateral y arista central)
            pygame.draw.polygon(pantalla, (135, 15, 28), [(cx, top_y + 4), (cx + 10, top_y), (cx, tip_y)])
            pygame.draw.line(pantalla, (255, 140, 160), (cx, top_y + 4), (cx, tip_y), 1)
            pygame.draw.line(pantalla, (255, 180, 200), (cx - 8, top_y - 1), (cx, top_y + 4), 1)
            if color_destello:
                pygame.draw.circle(pantalla, color_destello, (cx - 3, top_y - 2), 2)
                pygame.draw.circle(pantalla, color_brillo, (cx + 4, top_y - 1), 1)
        else:
            pygame.draw.circle(pantalla, (18, 14, 20), (cx - 5, top_y), 3)
            pygame.draw.circle(pantalla, (18, 14, 20), (cx + 5, top_y), 3)

    def _icono_alma(self, pantalla, ix, iy, color):
        cy = iy + 8
        pygame.draw.polygon(pantalla, color, [(ix + 6, cy - 7), (ix + 12, cy),
                                              (ix + 6, cy + 7), (ix, cy)])
        pygame.draw.polygon(pantalla, (230, 255, 250),
                             [(ix + 6, cy - 3), (ix + 9, cy),
                              (ix + 6, cy + 3), (ix + 3, cy)])

    def _icono_ala_dash(self, pantalla, x, y, color):
        # Dial rúnico exterior
        pygame.draw.circle(pantalla, (24, 18, 28), (x + 8, y + 8), 8)
        pygame.draw.circle(pantalla, color, (x + 8, y + 8), 8, 1)
        pygame.draw.polygon(pantalla, color, [
            (x + 2, y + 14),
            (x + 7, y + 8),
            (x + 5, y + 8),
            (x + 10, y + 3),
            (x + 6, y + 9),
            (x + 8, y + 9),
        ])
        pygame.draw.polygon(pantalla, color, [
            (x + 7, y + 14),
            (x + 12, y + 8),
            (x + 10, y + 8),
            (x + 15, y + 4),
            (x + 11, y + 9),
            (x + 13, y + 9),
        ])

    def _icono_pala(self, pantalla, x, y, es_guadaña, color):
        # Medallón de habilidad labrado
        pygame.draw.circle(pantalla, (24, 18, 28), (x + 8, y + 8), 8)
        pygame.draw.circle(pantalla, color, (x + 8, y + 8), 8, 1)
        if es_guadaña:
            pygame.draw.arc(pantalla, color, (x + 2, y + 2, 12, 12), 0, 3.14, 2)
            pygame.draw.line(pantalla, (180, 95, 220), (x + 9, y + 7), (x + 4, y + 14), 2)
        else:
            pygame.draw.line(pantalla, (160, 120, 60), (x + 4, y + 14), (x + 10, y + 7), 2)
            pygame.draw.polygon(pantalla, (200, 205, 215), [
                (x + 8, y + 8),
                (x + 13, y + 3),
                (x + 15, y + 5),
                (x + 10, y + 10),
            ])

    def _icono_reloj(self, pantalla, x, y, color):
        pygame.draw.circle(pantalla, color, (x + 8, y + 8), 6, 2)
        pygame.draw.line(pantalla, color, (x + 8, y + 8), (x + 8, y + 3), 2)
        pygame.draw.line(pantalla, color, (x + 8, y + 8), (x + 13, y + 8), 2)

    def _icono_calavera(self, pantalla, x, y, color):
        pygame.draw.circle(pantalla, color, (x + 8, y + 8), 7, 2)
        pygame.draw.line(pantalla, color, (x + 5, y + 12), (x + 11, y + 12), 2)
        pygame.draw.line(pantalla, color, (x + 5, y + 14), (x + 11, y + 14), 2)

    # --- Dibujo principal ---
    def dibujar(self, pantalla, modelo: HudModel, mensajes: MensajeHUD,
                reducir_movimiento=False, dt=0.0):
        # Fondo del riel
        panel_riel = self._panel(self.layout.riel.w, self.layout.riel.h)
        pantalla.blit(panel_riel, self.layout.riel.topleft)

        # Divisores góticos entre zonas
        x_div1 = self.layout.zona_izq.right + HUD_GAP // 2
        x_div2 = self.layout.zona_centro.right + HUD_GAP // 2
        pygame.draw.line(pantalla, (*HUD_BORDE, 100),
                         (x_div1, self.layout.riel.top + 8),
                         (x_div1, self.layout.riel.bottom - 8), 1)
        pygame.draw.line(pantalla, (*HUD_BORDE, 100),
                         (x_div2, self.layout.riel.top + 8),
                         (x_div2, self.layout.riel.bottom - 8), 1)

        if DEBUG_HUD:
            for rect in (self.layout.zona_izq, self.layout.zona_centro,
                         self.layout.zona_der, self.layout.canal_mensajes):
                pygame.draw.rect(pantalla, (255, 0, 255), rect, 1)

        self._dibujar_izquierda(pantalla, modelo, reducir_movimiento, dt)
        self._dibujar_centro(pantalla, modelo, reducir_movimiento, dt)
        self._dibujar_derecha(pantalla, modelo, reducir_movimiento, dt)
        self._dibujar_mensajes(pantalla, modelo, mensajes, reducir_movimiento, dt)

    # --- Zona izquierda: vida, corazones, tiempo ---
    def _dibujar_izquierda(self, pantalla, modelo, reducir_movimiento, dt):
        c = self.layout.contenido_izq
        # [HP] 3/5
        texto_hp = f"[HP] {modelo.vidas}/{modelo.vidas_max}"
        img = self._texto(texto_hp, self.tema.fuente_contador, self.tema.oro, sombra=True)
        pantalla.blit(img, (c.x, c.y))
        # TIEMPO 01:23 (alineado a derecha de la zona izquierda)
        texto_tiempo = fmt_tiempo(modelo.tiempo)
        img_t = self._texto(texto_tiempo, self.tema.fuente_contador,
                            self.tema.texto_secundario, sombra=True)
        pantalla.blit(img_t, (c.right - img_t.get_width(), c.y))
        # Corazones (2ª fila)
        pulso = 0.0
        if modelo.vidas == 1 and not reducir_movimiento:
            pulso = 0.5 + 0.5 * math.sin(pygame.time.get_ticks() / 1000.0 * 1.2 * math.tau)
        escala_corazon = 1.0 + 0.12 * pulso if modelo.vidas == 1 and not reducir_movimiento else 1.0
        for i in range(modelo.vidas_max):
            cx = c.x + i * self.tema.corazon_pitch
            cy = c.y + 30
            lleno = i < modelo.vidas
            self.dibujar_corazon(pantalla, cx, cy, lleno, escala_corazon)

    # --- Zona centro: nivel / jefe ---
    def _dibujar_centro(self, pantalla, modelo, reducir_movimiento, dt):
        c = self.layout.contenido_centro
        if modelo.jefe_vivo:
            # Nombre del jefe
            nombre = modelo.jefe_nombre
            fuente_nombre = self._fuente(self.tema.fuente_nombre)
            if fuente_nombre.size(nombre)[0] > 300:
                nombre = "EL CUSTODIO"
            img_n = self._texto(nombre, self.tema.fuente_nombre,
                                self.tema.rojo if modelo.jefe_fase >= 2 else self.tema.oro, sombra=True)
            pantalla.blit(img_n, (c.x, c.y))
            # Fase
            fase_txt = f"FASE {'II' if modelo.jefe_fase >= 2 else 'I'}"
            img_f = self._texto(fase_txt, self.tema.fuente_label,
                                self.tema.rojo if modelo.jefe_fase >= 2 else self.tema.texto_secundario)
            pantalla.blit(img_f, (c.right - img_f.get_width(), c.y))
            # Barra de jefe: 6 segmentos de 68×12, gap 4, slot 48 para número
            barra_y = c.y + 30
            segmento_w, segmento_h = 68, 12
            gap = 4
            x_seg = c.x
            for i in range(JEFE_VIDA):
                llena = i < modelo.jefe_vida
                color = (self.tema.jefe_segmento_lleno if llena
                         else self.tema.jefe_segmento_vacio)
                rect = pygame.Rect(x_seg, barra_y, segmento_w, segmento_h)
                pygame.draw.rect(pantalla, color, rect, border_radius=4)
                if not llena:
                    pygame.draw.rect(pantalla, (22, 16, 20), rect, 1, border_radius=4)
                x_seg += segmento_w + gap
            # Número y fase a la derecha de la barra
            num_txt = f"{modelo.jefe_vida}/{JEFE_VIDA}"
            img_num = self._texto(num_txt, self.tema.fuente_label, self.tema.texto)
            pantalla.blit(img_num, (x_seg + 8, barra_y))
        else:
            # Nivel
            if modelo.nivel_indice < 0:
                nivel_txt = "TUTORIAL"
            else:
                nivel_txt = f"NIVEL {modelo.nivel_indice + 1}/{modelo.nivel_total}"
            img_n = self._texto(nivel_txt, self.tema.fuente_label, self.tema.oro)
            pantalla.blit(img_n, (c.x, c.y))
            nombre_txt = modelo.nivel_nombre.upper()
            img_nom = self._texto(nombre_txt, self.tema.fuente_nombre,
                                  self.tema.texto_secundario, sombra=True)
            pantalla.blit(img_nom, (c.x, c.y + 18))

    # --- Zona derecha: grilla 2×2 (almas, vida extra, dash, pala) ---
    def _dibujar_derecha(self, pantalla, modelo, reducir_movimiento, dt):
        c = self.layout.contenido_der
        celda_w, celda_h = 164, 22
        gap_x, gap_y = 8, 4
        # Fila 1: [ALMA] X/Y | [DASH] estado
        # Col 0: Almas
        x0 = c.x
        y0 = c.y
        self._icono_alma(pantalla, x0 + 4, y0 + 3, self.tema.alma)
        txt_alma = f"[ALMA] {modelo.almas}/{modelo.almas_total}"
        img_a = self._texto(txt_alma, self.tema.fuente_contador, self.tema.oro)
        pantalla.blit(img_a, (x0 + 24, y0))
        # Col 1: Dash
        x1 = x0 + celda_w + gap_x
        txt_dash = fmt_dash(modelo)
        listo = modelo.tiene_dash and modelo.dash_cooldown <= 0
        color_dash = self.tema.dash_turquesa if listo else self.muted_color()
        img_d = self._texto(txt_dash, self.tema.fuente_contador, color_dash)
        self._icono_ala_dash(pantalla, x1 + 2, y0, color_dash)
        pantalla.blit(img_d, (x1 + 24, y0))
        # Fila 2: VIDA EXTRA X/10 + pips | [PALA] estado
        y1 = y0 + celda_h + gap_y
        # Col 0: Vida extra
        txt_ve = f"VIDA EXTRA {modelo.almas_para_vida}/{ALMAS_POR_VIDA}"
        img_ve = self._texto(txt_ve, self.tema.fuente_contador,
                             self.tema.oro if modelo.almas_para_vida < ALMAS_POR_VIDA else self.muted_color())
        pantalla.blit(img_ve, (x0, y1))
        # Pips del rosario (10 cuentas de marfil con fulgor turquesa)
        pip_y = y1 + 17
        es_consagracion = modelo.almas_para_vida >= ALMAS_POR_VIDA
        for i in range(ALMAS_POR_VIDA):
            bx = x0 + 4 + i * 8
            llena = i < modelo.almas_para_vida
            if es_consagracion:
                color_cuenta = (255, 220, 90) if (int(pygame.time.get_ticks() / 150) % 2 == 0) else (198, 156, 62)
            elif llena:
                color_cuenta = self.tema.alma
            else:
                color_cuenta = (40, 32, 44)
            pygame.draw.circle(pantalla, (20, 16, 24), (bx + 3, pip_y + 2), 3)
            pygame.draw.circle(pantalla, color_cuenta, (bx + 3, pip_y + 2), 2)
            if llena and not es_consagracion:
                pygame.draw.circle(pantalla, (220, 255, 250), (bx + 3, pip_y + 2), 1)
        # Col 1: Pala/Guadaña
        txt_arma = fmt_arma(modelo)
        color_arma = (self.tema.guadaña if modelo.rango_ataque_mejorado
                      else self.tema.pala) if modelo.tiene_pala else self.muted_color()
        img_ar = self._texto(txt_arma, self.tema.fuente_contador, color_arma)
        self._icono_pala(pantalla, x1 + 2, y1, modelo.rango_ataque_mejorado, color_arma)
        pantalla.blit(img_ar, (x1 + 24, y1))

    # --- Canal de mensajes ---
    def _dibujar_mensajes(self, pantalla, modelo, mensajes, reducir_movimiento, dt):
        if modelo.estado != "jugando":
            return
        if not mensajes.esta_visible():
            return
        m = self.layout.canal_mensajes
        alpha = mensajes.alpha()
        if alpha <= 0:
            return
        caja = pygame.Surface((m.w, m.h), pygame.SRCALPHA)
        pygame.draw.rect(caja, (*self.tema.panel_bg[:3], min(240, alpha)),
                         caja.get_rect(), border_radius=10)
        pygame.draw.rect(caja, (*self.tema.panel_border,
                                min(self.tema.panel_border_alpha, alpha)),
                         caja.get_rect(), 1, border_radius=10)
        pygame.draw.rect(caja, (*self.tema.oro, min(180, alpha)), (0, 0, 4, m.h), border_radius=2)
        # Icono pequeño según prioridad
        icono_x = m.x + 8
        icono_y = m.y + 4 + mensajes.offset_y()
        color_icono = self.tema.rojo if mensajes.prioridad >= 3 else self.tema.oro
        if mensajes.prioridad >= 3:
            self._icono_calavera(pantalla, icono_x, icono_y, color_icono)
        else:
            self._icono_reloj(pantalla, icono_x, icono_y, color_icono)
        # Texto
        texto_x = m.x + 32
        texto_y = m.y + 4 + mensajes.offset_y()
        ancho_util = 520
        fuente = self._fuente(self.tema.fuente_contador)
        lineas = envolver(mensajes.texto, fuente, ancho_util, max_lineas=2)
        for i, linea in enumerate(lineas):
            img = self._texto(linea, self.tema.fuente_contador, self.tema.texto, sombra=True)
            if alpha < 255:
                copia = img.copy()
                copia.set_alpha(alpha)
                pantalla.blit(copia, (texto_x, texto_y + i * 20))
            else:
                pantalla.blit(img, (texto_x, texto_y + i * 20))
        pantalla.blit(caja, (m.x, m.y + mensajes.offset_y()),
                      special_flags=pygame.BLEND_RGBA_ADD if alpha < 255 else 0)

    # --- Utilidad ---
    def muted_color(self):
        return self.tema.texto_secundario


# ---------------------------------------------------------------------------
# HudOrquestador — une modelo, renderer y mensajes; usado por Juego
# ---------------------------------------------------------------------------
class HudOrquestador:
    def __init__(self):
        self.layout = HudLayout.construir()
        self.tema = HudTheme()
        self.texto_cache = TextoCache(lambda t: pygame.font.Font(str(_RUTA_FUENTE), t)
                                      if _RUTA_FUENTE.exists()
                                      else pygame.font.Font(None, t))
        self.renderer = HudRenderer(self.layout, self.tema, self.texto_cache)
        self.mensajes = MensajeHUD(self.layout, self.tema, self.texto_cache)
        self.modelo = HudModel()
        self.reducir_movimiento = False

    def actualizar(self, dt):
        self.mensajes.actualizar(dt)

    def armar_modelo(self, juego):
        j = juego.jugador
        n = juego.nivel
        jefe = juego.jefe
        self.modelo.vidas = j.vidas if j else VIDAS_MAXIMAS
        self.modelo.vidas_max = VIDAS_MAXIMAS
        self.modelo.almas = j.almas if j else 0
        self.modelo.almas_total = n.total_almas if n else 0
        self.modelo.almas_para_vida = j.almas_para_vida if j else 0
        self.modelo.dash_cooldown = j.dash_cooldown if j else 0.0
        self.modelo.dash_usos_aire = j.dash_usos_aire if j else DASH_USOS_AIRE
        self.modelo.tiene_dash = getattr(j, "tiene_dash", False) if j else False
        self.modelo.en_suelo = j.en_suelo if j else True
        self.modelo.ataque_cooldown = j.ataque_cooldown if j else 0.0
        self.modelo.tiene_pala = j.tiene_pala if j else False
        self.modelo.rango_ataque_mejorado = getattr(j, "rango_ataque_mejorado", False) if j else False
        self.modelo.jefe_vivo = jefe is not None and getattr(jefe, "vivo", False)
        self.modelo.jefe_vida = jefe.vida if jefe else 0
        self.modelo.jefe_fase = jefe.fase if jefe else 1
        self.modelo.jefe_nombre = "EL CUSTODIO DEL OSARIO"
        if getattr(juego, "es_tutorial", False):
            self.modelo.nivel_indice = -1
            self.modelo.nivel_total = 3
            self.modelo.nivel_nombre = "RITUAL DEL SEPULTURERO"
        else:
            self.modelo.nivel_indice = juego.nivel_indice
            total = len(getattr(juego, "niveles", [])) or (len(NIVELES) if "NIVELES" in globals() and NIVELES else 3)
            self.modelo.nivel_total = total
            self.modelo.nivel_nombre = n.nombre.upper() if n and hasattr(n, "nombre") else "CAMPOSANTO"
        self.modelo.tiempo = juego.tiempo_total
        self.modelo.estado = juego.estado
        self.modelo.pista = getattr(juego, "texto_ayuda", "") or (n.pista if n and hasattr(n, "pista") else "")
        self.modelo.aviso_jefe = juego.aviso_jefe

    def dibujar(self, pantalla, juego, dt):
        self.armar_modelo(juego)
        self.renderer.dibujar(pantalla, self.modelo, self.mensajes,
                              self.reducir_movimiento, dt)

    def mostrar_mensaje(self, texto, prioridad, hold):
        self.mensajes.mostrar(texto, prioridad, hold)
