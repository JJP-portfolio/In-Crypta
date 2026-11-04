# ============================================================
# hud.py — HUD de IN CRYPTA (renovación integral)
# ============================================================
# Solo dibujo del HUD. No toca gameplay, lógica de almas, vidas,
# dash, ataque ni jefe. Lee un snapshot (HudModel) y lo renderiza.
#
# Diseño: riel superior único full-width con 3 zonas fijas,
# grilla 2×2 a la derecha, canal de mensajes único debajo del riel.
# ============================================================

from __future__ import annotations

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
_RAIZ_HUD = Path(__file__).resolve().parent
_RUTA_FUENTE = _RAIZ_HUD / "assets/NotoSerifDisplay-Bold.ttf"

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
    escudo_farol: bool = False
    filo_anima: bool = False
    almas_volatiles: int = 0
    # Jefe
    jefe_vivo: bool = False
    jefe_vida: int = 0
    jefe_vida_max: int = JEFE_VIDA
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

    @property
    def dash_listo(self) -> bool:
        return self.tiene_dash and self.dash_cooldown <= 0 and (self.en_suelo or self.dash_usos_aire > 0)

    @property
    def dash_cooldown_norm(self) -> float:
        return min(1.0, max(0.0, self.dash_cooldown / 0.6)) if self.dash_cooldown > 0 else 0.0

    @property
    def rango_mejorado(self) -> bool:
        return getattr(self, "rango_ataque_mejorado", False)

    @property
    def nombre_nivel(self) -> str:
        return getattr(self, "nivel_nombre", "CAMPOSANTO")

    @property
    def vidas_maximas(self) -> int:
        return getattr(self, "vidas_max", VIDAS_MAXIMAS)


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
        self.t_salida = 0.30

    def mostrar(self, texto, prioridad, hold, forzar=False):
        # Solo reemplaza si hay prioridad mayor, si se fuerza, o si está oculto.
        # Un mensaje entrando/visible/saliendo con prioridad >= se respeta salvo que forzar=True.
        if self.esta_visible() and not forzar and prioridad <= self.prioridad:
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
        self._surf_riel_buffer = None
        self.tiempo = 0.0
        self.modo_hud = 0
        # Tweens reactivos para feedback de eventos
        self.tween_alma = Tween(0.25, 0.25, "out_back")
        self.tween_dash = Tween(0.30, 0.30, "out_back")
        self.tween_arma = Tween(0.25, 0.25, "out_back")
        self.tween_jefe = Tween(0.22, 0.22, "out_cubic")

    def _fuente(self, tamano):
        if tamano not in self._fuentes:
            try:
                self._fuentes[tamano] = pygame.font.Font(str(_RUTA_FUENTE), tamano)
            except Exception:
                self._fuentes[tamano] = pygame.font.Font(None, tamano)
        return self._fuentes[tamano]

    def _obtener_fuente(self, tamano: int):
        return self._fuente(tamano)

    def _texto(self, texto, tamano, color, sombra=False):
        return self.texto_cache.render(texto, tamano, color, sombra)

    # --- Paneles cacheados ---
    def _panel(self, ancho, alto, alpha=None):
        import config
        estilo = config.resolver_estilo(getattr(config, "ESTILO_HUD", "AUTO"))
        clave = (ancho, alto, alpha, estilo)
        surf = self._paneles_cache.get(clave)
        if surf is None:
            if estilo == "NES":
                # Modelo A1: 100% opaco, esquinas escalonadas de 4px, cero costo de alpha para Vaio
                surf = pygame.Surface((ancho, alto))
                surf.fill((9, 8, 13))
                pygame.draw.rect(surf, (104, 82, 52), (0, 0, ancho, alto), 1)
                pygame.draw.rect(surf, (216, 180, 104), (3, 3, ancho - 6, alto - 6), 1)
                for cx, cy in ((0, 0), (ancho - 4, 0), (0, alto - 4), (ancho - 4, alto - 4)):
                    pygame.draw.rect(surf, (9, 8, 13), (cx, cy, 4, 4))
                    pygame.draw.rect(surf, (216, 180, 104), (cx + 1, cy + 1, 2, 2))
                try:
                    surf = surf.convert()
                except Exception:
                    pass
            elif estilo == "SNES":
                # Modelo A2: Marco biselado 3D con remaches en esquinas
                a = alpha if alpha is not None else 225
                surf = pygame.Surface((ancho, alto), pygame.SRCALPHA)
                pygame.draw.rect(surf, (16, 14, 26, a), (0, 0, ancho, alto), border_radius=6)
                pygame.draw.line(surf, (238, 202, 118), (4, 1), (ancho - 5, 1), 2)
                pygame.draw.line(surf, (216, 180, 104), (1, 4), (1, alto - 5), 2)
                pygame.draw.line(surf, (72, 52, 28), (4, alto - 2), (ancho - 5, alto - 2), 2)
                pygame.draw.line(surf, (72, 52, 28), (ancho - 2, 4), (ancho - 2, alto - 5), 2)
                pygame.draw.rect(surf, (140, 110, 65, 240), (3, 3, ancho - 6, alto - 6), 1, border_radius=4)
                for rx, ry in ((7, 7), (ancho - 8, 7), (7, alto - 8), (ancho - 8, alto - 8)):
                    pygame.draw.circle(surf, (40, 30, 20), (rx, ry), 3)
                    pygame.draw.circle(surf, (238, 202, 118), (rx, ry), 2)
                try:
                    surf = surf.convert_alpha()
                except Exception:
                    pass
            else:
                # Modelo A3: Marco gótico detallado con filigrana
                a = alpha if alpha is not None else self.tema.panel_bg[3]
                surf = pygame.Surface((ancho, alto), pygame.SRCALPHA)
                pygame.draw.rect(surf, (*self.tema.panel_bg[:3], a),
                                 surf.get_rect(), border_radius=12)
                pygame.draw.rect(surf, (*self.tema.panel_border,
                                        self.tema.panel_border_alpha),
                                 surf.get_rect(), 1, border_radius=12)
                pygame.draw.rect(surf, (58, 46, 36, 180), (3, 3, ancho - 6, alto - 6), 1, border_radius=9)
                pygame.draw.line(surf, self.tema.linea_oro, (12, 1), (ancho - 12, 1), 1)
                w_lim = ancho - 1
                h_lim = alto - 1
                for vx, vy, vdx, vdy in ((0, 0, 1, 1), (w_lim, 0, -1, 1),
                                         (0, h_lim, 1, -1), (w_lim, h_lim, -1, -1)):
                    pygame.draw.line(surf, HUD_ORO, (vx + 4 * vdx, vy),
                                     (vx + 18 * vdx, vy), 2)
                    pygame.draw.line(surf, HUD_ORO, (vx, vy + 4 * vdy),
                                     (vx, vy + 16 * vdy), 2)
                try:
                    surf = surf.convert_alpha()
                except Exception:
                    pass
            self._paneles_cache[clave] = surf
        return surf

    # --- Iconos dibujados con pygame.draw (sin assets) ---
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
    def dibujar(
        self,
        surface: pygame.Surface,
        modelo: HudModel,
        mensajes: MensajeHUD = None,
        reducir_movimiento: bool = False,
        dt: float = 0.0,
        modo_hud: int = None,
        timer_inmersivo: float = 0.0,
    ) -> None:
        self.tiempo = getattr(self, "tiempo", 0.0) + dt
        if modo_hud is not None:
            self.modo_hud = modo_hud
        else:
            self.modo_hud = getattr(self, "modo_hud", 0)

        # Modo Inmersivo puro: oculta los paneles periféricos salvo en combate de jefe, timer activo o avisos
        if self.modo_hud == 2 and not modelo.jefe_vivo and timer_inmersivo <= 0:
            tiene_mensaje = (mensajes and mensajes.esta_visible()) or (
                getattr(modelo, "mensaje_texto", None) and getattr(modelo, "mensaje_alpha", 0) > 0
            )
            if not tiene_mensaje:
                return

        layout = HudLayout.construir(surface.get_width(), surface.get_height())
        alfa_global = 155 if self.modo_hud == 1 else 235
        if self.modo_hud == 2 and timer_inmersivo > 0 and not modelo.jefe_vivo:
            alfa_global = int(min(255, max(0, min(1.0, timer_inmersivo / 0.4) * 255)))

        # 1. RELICARIO SUPERIOR IZQUIERDO (Cálices de Sangre + Cuerda del Rosario)
        self._dibujar_relicario_izquierdo(surface, layout.zona_izq, modelo, alfa_global)

        # 2. CARTELA SUPERIOR CENTRAL (Respaldo de obsidiana translúcido que protege el título del techo)
        self._dibujar_cartela_central_transparente(surface, layout.zona_centro, modelo, alfa_global)

        # 3. MEDALLONES SUPERIORES DERECHOS (Diales circulares con iconos de Dash y Arma + Urna de Almas)
        self._dibujar_medallones_derechos(surface, layout.zona_der, modelo, alfa_global)

        # 4. BARRA DE SALUD DEL JEFE / MINI-JEFE EN LA ZONA SUPERIOR CENTRAL (Cero obstrucción del suelo)
        if modelo.jefe_vivo:
            self._dibujar_barra_jefe_catedral(surface, modelo)

        # 5. CANAL DE MENSAJES LITÚRGICOS (Pergamino de obsidiana y bronce)
        if mensajes and mensajes.esta_visible() and mensajes.alpha() > 0:
            self._dibujar_mensajes(surface, modelo, mensajes, reducir_movimiento, dt)

    def _dibujar_relicario_izquierdo(self, surface: pygame.Surface, rect: pygame.Rect, modelo: HudModel, alfa: int) -> None:
        """Medallón heráldico compacto con Cálices de Rubí arriba, Rosario de 10 cuentas debajo y estado de bendición."""
        vidas_max = max(getattr(modelo, "vidas_maximas", getattr(modelo, "vidas_max", 5)), 5)
        w_vis = max(224, 68 + vidas_max * 28)
        h_vis = rect.height - 8
        clave_izq = ("relicario_izq", w_vis, h_vis, alfa)
        panel = self._paneles_cache.get(clave_izq)
        if panel is None:
            panel = pygame.Surface((w_vis, h_vis), pygame.SRCALPHA)
            pts_fondo = [
                (0, 0), (w_vis - 20, 0), (w_vis - 2, h_vis // 2),
                (w_vis - 26, h_vis - 1), (0, h_vis - 1)
            ]
            pygame.draw.polygon(panel, (12, 10, 18, int(alfa * 0.90)), pts_fondo)
            pygame.draw.polygon(panel, (218, 178, 86, alfa), pts_fondo, 2)
            pygame.draw.line(panel, (104, 82, 52, int(alfa * 0.85)), (42, h_vis // 2 + 2), (w_vis - 24, h_vis // 2 + 2), 1)
            self._paneles_cache[clave_izq] = panel
        surface.blit(panel, (rect.x, rect.y + 4))

        # Emblema izquierdo de Manto / Filo de Ánima / Corazón
        emblema_cx, emblema_cy = rect.x + 22, rect.centery
        pygame.draw.circle(surface, (18, 14, 26), (emblema_cx, emblema_cy), 14)
        tiene_manto = getattr(modelo, "escudo_farol", False)
        tiene_filo = getattr(modelo, "filo_anima", False)
        color_aro = (92, 220, 200) if tiene_manto else ((255, 215, 100) if tiene_filo else (218, 178, 86))
        pygame.draw.circle(surface, color_aro, (emblema_cx, emblema_cy), 14, 2)
        if tiene_manto:
            pygame.draw.polygon(surface, (140, 235, 255), [
                (emblema_cx, emblema_cy - 8), (emblema_cx + 7, emblema_cy),
                (emblema_cx, emblema_cy + 8), (emblema_cx - 7, emblema_cy)
            ])
        elif tiene_filo:
            pygame.draw.circle(surface, (255, 215, 100), (emblema_cx, emblema_cy), 6)
        else:
            pygame.draw.circle(surface, (210, 28, 50), (emblema_cx, emblema_cy), 5)

        # Cálices de Sangre (Vidas)
        x_caliz = rect.x + 50
        y_caliz = rect.y + 20
        for i in range(vidas_max):
            cx = x_caliz + i * 26
            lleno = i < modelo.vidas
            pts_gema = [(cx, y_caliz - 8), (cx + 8, y_caliz), (cx, y_caliz + 9), (cx - 8, y_caliz)]
            pygame.draw.polygon(surface, (24, 18, 28), pts_gema)
            if lleno:
                col_rubi = (235, 45, 68) if (modelo.vidas == 1 and int(getattr(self, "tiempo", 0.0) * 8) % 2 == 0) else (210, 28, 50)
                pygame.draw.polygon(surface, col_rubi, [(cx, y_caliz - 6), (cx + 6, y_caliz), (cx, y_caliz + 7), (cx - 6, y_caliz)])
                pygame.draw.circle(surface, (255, 210, 215), (cx - 2, y_caliz - 2), 2)
            pygame.draw.polygon(surface, (218, 178, 86) if lleno else (95, 82, 68), pts_gema, 1)

        # Cuerda del Rosario de 10 cuentas debajo (progreso hacia +1 Vida)
        y_rosario = rect.y + 50
        x_rosario_ini = rect.x + 50
        pygame.draw.line(surface, (140, 115, 65), (x_rosario_ini, y_rosario), (x_rosario_ini + 9 * 14, y_rosario), 1)
        cuentas_activas = getattr(modelo, "almas_para_vida", modelo.almas % 10)
        for c_idx in range(10):
            bx = x_rosario_ini + c_idx * 14
            encendida = c_idx < cuentas_activas
            if encendida:
                pygame.draw.circle(surface, (92, 220, 200), (bx, y_rosario), 4)
                pygame.draw.circle(surface, (235, 255, 255), (bx, y_rosario), 1)
            else:
                pygame.draw.circle(surface, (28, 24, 34), (bx, y_rosario), 3)
                pygame.draw.circle(surface, (110, 95, 70), (bx, y_rosario), 3, 1)

    def _dibujar_cartela_central_transparente(self, surface: pygame.Surface, rect: pygame.Rect, modelo: HudModel, alfa: int = 235) -> None:
        """Cartela central compacta con respaldo de obsidiana translúcido para evitar colisión visual con el techo."""
        cx = rect.centerx
        nom = getattr(modelo, "nombre_nivel", "") or getattr(modelo, "nivel_nombre", "")
        titulo = nom.upper() if nom else "EL UMBRAL"
        jefe_activo = getattr(modelo, "jefe_vivo", False)
        tam_fuente = 11 if jefe_activo else 13
        img_txt = self._texto(titulo, tam_fuente, (228, 224, 210), sombra=True)

        w_cartela = max(220 if jefe_activo else 236, img_txt.get_width() + 44)
        h_cartela = 24 if jefe_activo else 34
        x_cartela = cx - w_cartela // 2
        y_cartela = rect.y + (0 if jefe_activo else 4)

        clave_c = ("cartela_centro", w_cartela, h_cartela, alfa)
        panel_c = self._paneles_cache.get(clave_c)
        if panel_c is None:
            panel_c = pygame.Surface((w_cartela, h_cartela), pygame.SRCALPHA)
            pts_c = [
                (10, 0), (w_cartela - 10, 0), (w_cartela - 1, h_cartela // 2),
                (w_cartela - 10, h_cartela - 1), (10, h_cartela - 1), (1, h_cartela // 2)
            ]
            pygame.draw.polygon(panel_c, (10, 8, 16, int(alfa * 0.86)), pts_c)
            pygame.draw.polygon(panel_c, (218, 178, 86, int(alfa * 0.85)), pts_c, 1)
            # Filigranas laterales internas
            pygame.draw.circle(panel_c, (218, 178, 86, alfa), (9, h_cartela // 2), 2)
            pygame.draw.circle(panel_c, (218, 178, 86, alfa), (w_cartela - 9, h_cartela // 2), 2)
            self._paneles_cache[clave_c] = panel_c

        surface.blit(panel_c, (x_cartela, y_cartela))
        surface.blit(img_txt, (cx - img_txt.get_width() // 2, y_cartela + (h_cartela - img_txt.get_height()) // 2))

    def _dibujar_medallones_derechos(self, surface: pygame.Surface, rect: pygame.Rect, modelo: HudModel, alfa: int) -> None:
        """Dos medallones circulares biselados con iconos reales (Dash y Pala/Guadaña) + Urna de Almas y Reloj."""
        cy_med = rect.centery - 4
        # Medallón 1: Dash Espectral con icono de ala y arco radial de recarga
        cx_dash = rect.x + 36
        dash_listo = getattr(modelo, "dash_listo", modelo.dash_cooldown <= 0 and (modelo.en_suelo or modelo.dash_usos_aire > 0))
        prog_dash = 1.0 if dash_listo else max(0.0, 1.0 - min(1.0, modelo.dash_cooldown / max(0.01, DASH_COOLDOWN)))
        self._dibujar_dial_circular(
            surface, cx_dash, cy_med, 20,
            desbloqueado=modelo.tiene_dash,
            progreso=prog_dash,
            color_activo=(92, 220, 200),
            etiqueta="[SHIFT]" if modelo.tiene_dash else "DASH",
            tipo_icono="dash",
        )

        # Medallón 2: Pala / Guadaña Consagrada con icono real
        cx_arma = rect.x + 90
        es_guadana = getattr(modelo, "rango_mejorado", getattr(modelo, "rango_ataque_mejorado", False))
        prog_arma = 1.0 if modelo.ataque_cooldown <= 0 else max(0.0, 1.0 - min(1.0, modelo.ataque_cooldown / max(0.01, ATAQUE_COOLDOWN)))
        self._dibujar_dial_circular(
            surface, cx_arma, cy_med, 20,
            desbloqueado=modelo.tiene_pala,
            progreso=prog_arma,
            color_activo=(195, 85, 250) if es_guadana else (218, 178, 86),
            etiqueta="[J] GUADAÑA" if (modelo.tiene_pala and es_guadana) else ("[J] PALA" if modelo.tiene_pala else "PALA"),
            tipo_icono="guadana" if es_guadana else "pala",
        )

        # Urna de Almas y Reloj a la derecha (compacta y con total de almas + reloj)
        urna_rect = pygame.Rect(rect.x + 128, rect.y + 6, rect.width - 132, rect.height - 12)
        clave_u = ("urna_der", urna_rect.width, urna_rect.height, alfa)
        panel_u = self._paneles_cache.get(clave_u)
        if panel_u is None:
            panel_u = pygame.Surface((urna_rect.width, urna_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(panel_u, (12, 10, 18, int(alfa * 0.90)), (0, 0, urna_rect.width, urna_rect.height), border_radius=8)
            pygame.draw.rect(panel_u, (218, 178, 86, alfa), (0, 0, urna_rect.width, urna_rect.height), 2, border_radius=8)
            pygame.draw.line(panel_u, (104, 82, 52, int(alfa * 0.8)), (10, urna_rect.height // 2 + 4), (urna_rect.width - 10, urna_rect.height // 2 + 4), 1)
            self._paneles_cache[clave_u] = panel_u
        surface.blit(panel_u, urna_rect.topleft)

        # Fila superior de la urna: Orbe de ánima + contador almas de total (+volátiles)
        orb_x, orb_y = urna_rect.x + 18, urna_rect.y + 18
        pygame.draw.circle(surface, (92, 220, 200), (orb_x, orb_y), 6)
        pygame.draw.circle(surface, (235, 255, 255), (orb_x, orb_y), 2)
        if modelo.almas_total > 0:
            txt_almas = f"{modelo.almas:02d} de {modelo.almas_total:02d}"
        else:
            txt_almas = f"{modelo.almas:02d}"
        if getattr(modelo, "almas_volatiles", 0) > 0:
            txt_almas += f" (+{modelo.almas_volatiles})"
        img_n = self._texto(txt_almas, 14, (228, 224, 210), sombra=True)
        surface.blit(img_n, (orb_x + 12, orb_y - img_n.get_height() // 2))

        # Fila inferior de la urna: Reloj del nivel
        rel_x, rel_y = urna_rect.x + 10, urna_rect.y + 36
        self._icono_reloj(surface, rel_x, rel_y, (198, 156, 62))
        txt_t = fmt_tiempo(getattr(modelo, "tiempo", 0.0))
        img_t = self._texto(txt_t, 12, (190, 178, 156), sombra=True)
        surface.blit(img_t, (rel_x + 20, rel_y + 8 - img_t.get_height() // 2))

    def _dibujar_dial_circular(
        self, surface: pygame.Surface, cx: int, cy: int, radio: int,
        desbloqueado: bool, progreso: float, color_activo: tuple, etiqueta: str,
        tipo_icono: str = "dash",
    ) -> None:
        pygame.draw.circle(surface, (12, 10, 18), (cx, cy), radio)
        if not desbloqueado:
            color_apagado = (72, 64, 78)
            pygame.draw.circle(surface, color_apagado, (cx, cy), radio, 2)
            if tipo_icono == "dash":
                self._icono_ala_dash(surface, cx - 8, cy - 8, color_apagado)
            else:
                self._icono_pala(surface, cx - 8, cy - 8, tipo_icono == "guadana", color_apagado)
            # Pequeño candado de hierro en el borde inferior del medallón
            pygame.draw.rect(surface, (36, 30, 42), (cx - 4, cy + radio - 5, 8, 6), border_radius=1)
            pygame.draw.rect(surface, (120, 108, 92), (cx - 4, cy + radio - 5, 8, 6), 1, border_radius=1)
            img_t = self._texto(etiqueta, 9, (120, 110, 100), sombra=True)
            surface.blit(img_t, (cx - img_t.get_width() // 2, cy + radio + 2))
            return

        if progreso >= 0.99:
            pygame.draw.circle(surface, color_activo, (cx, cy), radio, 2)
        else:
            pygame.draw.circle(surface, (75, 68, 58), (cx, cy), radio, 2)
            rect_arc = pygame.Rect(cx - radio, cy - radio, radio * 2, radio * 2)
            pygame.draw.arc(surface, color_activo, rect_arc, math.pi / 2, math.pi / 2 + math.tau * progreso, 3)

        color_ic = color_activo if progreso >= 0.99 else (130, 122, 112)
        if tipo_icono == "dash":
            self._icono_ala_dash(surface, cx - 8, cy - 8, color_ic)
        else:
            self._icono_pala(surface, cx - 8, cy - 8, tipo_icono == "guadana", color_ic)

        img_t = self._texto(etiqueta, 9, (218, 178, 86), sombra=True)
        surface.blit(img_t, (cx - img_t.get_width() // 2, cy + radio + 2))

    def _dibujar_barra_jefe_catedral(self, surface: pygame.Surface, modelo: HudModel) -> None:
        """Barra gótica de jefe integrada en la zona superior central (y = 58..76), dejando 100% libre el suelo."""
        sw = surface.get_width()
        bw, bh = 460, 16
        bx = (sw - bw) // 2
        by = 60
        tiempo = getattr(self, "tiempo", 0.0)
        temblor_x = int(math.sin(tiempo * 45.0) * 2) if getattr(modelo, "jefe_fase", 1) >= 2 else 0
        bx += temblor_x

        # Nombre litúrgico del Jefe arriba de la barra (dentro de zona_centro, y = 42)
        nombre_jefe = getattr(modelo, "jefe_nombre", "EL CUSTODIO DEL OSARIO").upper()
        if getattr(modelo, "jefe_fase", 1) >= 2:
            nombre_jefe += " · FASE II"
        img_j = self._texto(nombre_jefe, 12, (218, 178, 86), sombra=True)
        surface.blit(img_j, (sw // 2 - img_j.get_width() // 2, by - 18))

        # Marco de obsidiana y filigrana de oro/hueso
        pygame.draw.rect(surface, (8, 6, 12), (bx - 3, by - 3, bw + 6, bh + 6), border_radius=4)
        pygame.draw.rect(surface, (218, 178, 86), (bx - 3, by - 3, bw + 6, bh + 6), 2, border_radius=4)

        vida_max = max(1, modelo.jefe_vida_max)
        proporcion = max(0.0, min(1.0, modelo.jefe_vida / float(vida_max)))
        ancho_lleno = int(bw * proporcion)
        if ancho_lleno > 0:
            col_barra = (210, 28, 50) if getattr(modelo, "jefe_fase", 1) >= 2 else (168, 32, 46)
            pygame.draw.rect(surface, col_barra, (bx, by, ancho_lleno, bh), border_radius=2)
            pygame.draw.line(surface, (255, 150, 160), (bx + 2, by + 2), (bx + max(2, ancho_lleno - 2), by + 2), 2)

        # Separadores de hueso por punto de vida
        seg_w = bw / float(vida_max)
        for s_idx in range(1, vida_max):
            sx = int(bx + s_idx * seg_w)
            pygame.draw.line(surface, (6, 5, 10), (sx, by), (sx, by + bh), 2)
            pygame.draw.line(surface, (228, 224, 210), (sx + 1, by + 2), (sx + 1, by + bh - 2), 1)

        # Aviso de Fase II del Jefe debajo de la barra superior (sin tocar jamás el suelo)
        if getattr(modelo, "aviso_jefe", 0.0) > 0:
            aviso_txt = "¡FASE II! LA PALA REBOTA — SOLO EL PISOTÓN DESDE ARRIBA LO DAÑA"
            img_av = self._texto(aviso_txt, 12, (255, 110, 120), sombra=True)
            av_w = img_av.get_width() + 16
            av_x = sw // 2 - av_w // 2
            av_y = by + bh + 6
            pygame.draw.rect(surface, (10, 8, 14), (av_x, av_y, av_w, img_av.get_height() + 4), border_radius=4)
            pygame.draw.rect(surface, (210, 45, 65), (av_x, av_y, av_w, img_av.get_height() + 4), 1, border_radius=4)
            surface.blit(img_av, (sw // 2 - img_av.get_width() // 2, av_y + 2))

    # --- Canal de mensajes con Lápida de Obsidiana y Keycaps Físicos ---
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
        caja.fill((0, 0, 0, 0))

        # 1. Fondo de Lápida de Obsidiana Grabada (opacidad base uniforme; el fade se aplica una sola vez con set_alpha)
        pygame.draw.rect(caja, (*self.tema.panel_bg[:3], 235),
                         caja.get_rect(), border_radius=10)
        pygame.draw.rect(caja, (*self.tema.panel_border, self.tema.panel_border_alpha),
                         caja.get_rect(), 1, border_radius=10)
        pygame.draw.rect(caja, (218, 178, 86, 200),
                         (2, 2, m.w - 4, m.h - 4), 1, border_radius=8)
        pygame.draw.rect(caja, (*self.tema.oro, 255), (0, 0, 4, m.h), border_radius=2)

        # 2. Medallón circular a la izquierda con icono
        med_cx, med_cy = 18, m.h // 2
        pygame.draw.circle(caja, (24, 20, 28, 255), (med_cx, med_cy), 11)
        pygame.draw.circle(caja, (218, 178, 86, 255), (med_cx, med_cy), 11, 1)

        color_icono = self.tema.rojo if mensajes.prioridad >= 3 else self.tema.oro
        if mensajes.prioridad >= 3:
            self._icono_calavera(caja, med_cx - 8, med_cy - 8, color_icono)
        else:
            self._icono_reloj(caja, med_cx - 8, med_cy - 8, color_icono)

        # 3. Detección opcional de Keycap Físico Biselado (solo cuando se indica una tecla real entre corchetes)
        texto_crudo = mensajes.texto.strip()
        keycap_tag = None
        texto_resto = texto_crudo
        if texto_crudo.startswith("[") and "]" in texto_crudo:
            idx_fin = texto_crudo.find("]")
            keycap_tag = texto_crudo[1:idx_fin].strip()
            texto_resto = texto_crudo[idx_fin + 1:].strip()
            if texto_resto.startswith("·") or texto_resto.startswith(":"):
                texto_resto = texto_resto[1:].strip()

        texto_x = 38
        if keycap_tag:
            fuente_kc = self._fuente(11)
            kw, kh = fuente_kc.size(keycap_tag)
            kc_w = kw + 12
            kc_h = 20
            kc_x = texto_x
            kc_y = (m.h - kc_h) // 2

            # Botón marfil / oro con bisel físico
            pygame.draw.rect(caja, (150, 115, 45, 255), (kc_x, kc_y + 2, kc_w, kc_h - 2), border_radius=4)
            pygame.draw.rect(caja, (228, 195, 110, 255), (kc_x, kc_y, kc_w, kc_h - 2), border_radius=4)
            pygame.draw.rect(caja, (24, 20, 16, 255), (kc_x, kc_y, kc_w, kc_h), 1, border_radius=4)

            img_kc = self._texto(keycap_tag, 11, (24, 18, 20), sombra=False)
            caja.blit(img_kc, (kc_x + (kc_w - kw) // 2, kc_y + 2))

            texto_x = kc_x + kc_w + 8

        ancho_util = m.w - texto_x - 12
        fuente = self._fuente(self.tema.fuente_contador)
        lineas = envolver(texto_resto, fuente, ancho_util, max_lineas=2)
        alto_bloque = len(lineas) * 18
        texto_y = max(4, (m.h - alto_bloque) // 2)

        for i, linea in enumerate(lineas):
            img = self._texto(linea, self.tema.fuente_contador, self.tema.texto, sombra=True)
            caja.blit(img, (texto_x, texto_y + i * 18))

        if alpha < 255:
            caja.set_alpha(alpha)
        pantalla.blit(caja, (m.x, m.y + mensajes.offset_y()))


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
        self.modo_hud = 0
        self.timer_inmersivo = 0.0

    def actualizar(self, dt):
        self.mensajes.actualizar(dt)
        if self.timer_inmersivo > 0:
            self.timer_inmersivo = max(0.0, self.timer_inmersivo - dt)

    def armar_modelo(self, juego):
        j = juego.jugador
        n = juego.nivel
        jefe = juego.jefe

        self.modo_hud = getattr(juego, "config_hud_idx", 0)

        # Despertar HUD en modo inmersivo ante eventos clave (3 segundos)
        nueva_vida = j.vidas if j else VIDAS_MAXIMAS
        nuevas_almas = j.almas if j else 0
        nuevo_dash = getattr(j, "tiene_dash", False) if j else False
        nueva_pala = j.tiene_pala if j else False
        nuevo_manto = getattr(j, "escudo_farol", False) if j else False

        if self.modelo.vidas_prev > 0:
            if (nueva_vida < self.modelo.vidas or
                nuevas_almas > self.modelo.almas or
                (nuevo_dash and not self.modelo.tiene_dash) or
                (nueva_pala and not self.modelo.tiene_pala) or
                (nuevo_manto and not self.modelo.escudo_farol)):
                self.timer_inmersivo = 3.0

        self.modelo.vidas = nueva_vida
        self.modelo.vidas_max = VIDAS_MAXIMAS
        self.modelo.almas = nuevas_almas
        self.modelo.almas_total = n.total_almas if n else 0
        self.modelo.almas_volatiles = max(0, nuevas_almas - getattr(juego, "almas_consagradas", 0))
        self.modelo.almas_para_vida = j.almas_para_vida if j else 0
        self.modelo.dash_cooldown = j.dash_cooldown if j else 0.0
        self.modelo.dash_usos_aire = j.dash_usos_aire if j else DASH_USOS_AIRE
        self.modelo.tiene_dash = nuevo_dash
        self.modelo.en_suelo = j.en_suelo if j else True
        self.modelo.ataque_cooldown = j.ataque_cooldown if j else 0.0
        self.modelo.tiene_pala = nueva_pala
        self.modelo.rango_ataque_mejorado = getattr(j, "rango_ataque_mejorado", False) if j else False
        self.modelo.escudo_farol = nuevo_manto
        self.modelo.filo_anima = getattr(j, "filo_anima", False) if j else False

        jefe_cerca = False
        if jefe is not None and getattr(jefe, "vivo", False):
            if hasattr(jefe, "rect") and j is not None and hasattr(j, "rect"):
                mismo_piso = (j.rect.centery // (18 * 32)) == (jefe.rect.centery // (18 * 32))
                dist_x = abs(j.rect.centerx - jefe.rect.centerx)
                jefe_cerca = mismo_piso and (
                    dist_x < 36 * 32
                    or getattr(juego, "aviso_jefe", 0.0) > 0
                    or getattr(jefe, "vida", JEFE_VIDA) < JEFE_VIDA
                )
            else:
                jefe_cerca = True

        minijefe_activo = None
        if n and hasattr(n, "minijefes") and not jefe_cerca:
            for mj in n.minijefes:
                if mj.vivo and mj.estado != "muerto":
                    if j is not None and hasattr(j, "rect") and hasattr(mj, "rect"):
                        mismo_piso_mj = (j.rect.centery // (18 * 32)) == (mj.rect.centery // (18 * 32))
                        dist = abs(j.rect.centerx - mj.rect.centerx)
                        if mismo_piso_mj and (
                            dist < 520
                            or mj.estado in ("ataque", "telegrafo", "recuperacion", "cansado")
                            or getattr(mj, "vida", 3) < 3
                        ):
                            minijefe_activo = mj
                            break
                    else:
                        minijefe_activo = mj
                        break

        if jefe_cerca:
            self.modelo.jefe_vivo = True
            self.modelo.jefe_vida = jefe.vida
            self.modelo.jefe_vida_max = JEFE_VIDA
            self.modelo.jefe_fase = jefe.fase
            self.modelo.jefe_nombre = "EL CUSTODIO DEL OSARIO"
        elif minijefe_activo is not None:
            self.modelo.jefe_vivo = True
            self.modelo.jefe_vida = minijefe_activo.vida
            self.modelo.jefe_vida_max = 3
            self.modelo.jefe_fase = 1
            self.modelo.jefe_nombre = "EL CARCELERO DEL OSARIO"
        else:
            self.modelo.jefe_vivo = False
            self.modelo.jefe_vida = 0
            self.modelo.jefe_vida_max = JEFE_VIDA
            self.modelo.jefe_fase = 1
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
        self.modelo.snapshot_prev()

    def dibujar(self, pantalla, juego, dt):
        self.armar_modelo(juego)
        self.renderer.dibujar(pantalla, self.modelo, self.mensajes,
                              self.reducir_movimiento, dt,
                              modo_hud=self.modo_hud,
                              timer_inmersivo=self.timer_inmersivo)

    def mostrar_mensaje(self, texto, prioridad, hold, forzar=False):
        self.mensajes.mostrar(texto, prioridad, hold, forzar=forzar)
