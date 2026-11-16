#---- Importamos librerias y configuracion ----#
import math
from collections import OrderedDict
from dataclasses import dataclass, field
from pathlib import Path

import pygame

import config
from config import (
    ANCHO,
    ALTO,
    ATAQUE_COOLDOWN,
    DASH_COOLDOWN,
    DASH_USOS_AIRE,
    HUD_BORDE,
    HUD_TEXTO,
    HUD_VERDE,
    JEFE_VIDA,
    MINIJEFE_VIDA,
    VIDAS_MAXIMAS,
)

try:
    from niveles import NIVELES
except ImportError:
    NIVELES = []

#---- Constantes de diseno del HUD ----#
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

# Ruta absoluta de la fuente gotica legible (trazos firmes sin astas ultrafinas)
_RAIZ_HUD = Path(__file__).resolve().parent
_RUTA_FUENTE = _RAIZ_HUD / getattr(config, "RUTA_FUENTE_GOTICA", "assets/NotoSerif-Bold.ttf")


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


#---- Tema visual del HUD ----#
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


#---- Distribucion espacial ----#
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


#---- Modelo de estado del HUD ----#
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
    # Nivel y tiempo
    nivel_indice: int = 0
    nivel_total: int = 1
    nivel_nombre: str = "CAMPOSANTO"
    tiempo: float = 0.0
    # Estado y mensajes
    estado: str = "jugando"
    pista: str = ""
    aviso_jefe: float = 0.0
    # Instantanea previa para activar el modo inmersivo sin acoplar el gameplay
    vidas_prev: int = field(init=False, default=0)

    def snapshot_prev(self):
        self.vidas_prev = self.vidas

    @property
    def dash_listo(self) -> bool:
        return self.tiene_dash and self.dash_cooldown <= 0 and (self.en_suelo or self.dash_usos_aire > 0)

    @property
    def rango_mejorado(self) -> bool:
        return getattr(self, "rango_ataque_mejorado", False)

    @property
    def nombre_nivel(self) -> str:
        return getattr(self, "nivel_nombre", "CAMPOSANTO")


#---- MensajeHUD ----#
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


#---- Renderizador del HUD ----#
class HudRenderer:
    """Renderiza los paneles heraldicos, barra de jefe y mensajes del HUD."""

    def __init__(self, layout: HudLayout, tema: HudTheme, texto_cache: TextoCache):
        self.layout = layout
        self.tema = tema
        self.texto_cache = texto_cache
        self._fuentes = {}
        self._paneles_cache: OrderedDict = OrderedDict()
        self.tiempo = 0.0
        self.modo_hud = 0

    def _guardar_panel_cache(self, clave, surf):
        """Guarda en cache acotada con desalojo LRU (maximo 32 superficies)."""
        self._paneles_cache[clave] = surf
        if len(self._paneles_cache) > 32:
            self._paneles_cache.popitem(last=False)

    def _obtener_panel_cache(self, clave):
        """Recupera de cache y mueve al frente (mas recientemente usado)."""
        if clave in self._paneles_cache:
            self._paneles_cache.move_to_end(clave)
            return self._paneles_cache[clave]
        return None

    def _fuente(self, tamano):
        escala = float(getattr(config, "ESCALA_FUENTES_ACTIVA", 1.15))
        tam_eff = max(8, round(tamano * escala))
        if tam_eff not in self._fuentes:
            try:
                self._fuentes[tam_eff] = pygame.font.Font(str(_RUTA_FUENTE), tam_eff)
            except Exception:
                self._fuentes[tam_eff] = pygame.font.Font(None, tam_eff)
        return self._fuentes[tam_eff]

    def limpiar_caches_texto(self):
        """Descarta las superficies de texto cacheadas al cambiar la escala tipográfica."""
        self.texto_cache.cache.clear()
        self._fuentes.clear()
        self._paneles_cache.clear()

    def _texto(self, texto, tamano, color, sombra=False):
        return self.texto_cache.render(texto, tamano, color, sombra)

    #---- Iconos dibujados ----#
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

    #---- Dibujo principal ----#
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

        # 2. ZONA SUPERIOR CENTRAL: Barra Catedralicia del Jefe (cuando está visible) O Cartela del Nivel
        if modelo.jefe_vivo:
            self._dibujar_barra_jefe_catedral(surface, modelo)
        else:
            self._dibujar_cartela_central_transparente(surface, layout.zona_centro, modelo, alfa_global)

        # 3. MEDALLONES SUPERIORES DERECHOS (Diales circulares con iconos de Dash y Arma + Urna de Almas)
        self._dibujar_medallones_derechos(surface, layout.zona_der, modelo, alfa_global)

        # 4. CANAL DE MENSAJES LITÚRGICOS (Pergamino de obsidiana y bronce)
        if mensajes and mensajes.esta_visible() and mensajes.alpha() > 0:
            self._dibujar_mensajes(surface, modelo, mensajes, reducir_movimiento, dt)

    def _dibujar_relicario_izquierdo(self, surface: pygame.Surface, rect: pygame.Rect, modelo: HudModel, alfa: int) -> None:
        """Medallón heráldico compacto con Cálices de Rubí arriba, Rosario de 10 cuentas debajo y bisel de 1px legible."""
        vidas_max = max(getattr(modelo, "vidas_max", 5), 5)
        w_vis = max(230, 74 + vidas_max * 28)
        h_vis = rect.height - 6
        alfa_q = max(0, min(255, (int(alfa) // 8) * 8))
        clave_izq = ("relicario_izq_v3", w_vis, h_vis, alfa_q)
        panel = self._obtener_panel_cache(clave_izq)
        if panel is None:
            panel = pygame.Surface((w_vis, h_vis), pygame.SRCALPHA)
            pts_ext = [
                (0, 0), (w_vis - 18, 0), (w_vis - 1, h_vis // 2),
                (w_vis - 22, h_vis - 1), (0, h_vis - 1)
            ]
            pts_int = [
                (2, 2), (w_vis - 19, 2), (w_vis - 3, h_vis // 2),
                (w_vis - 23, h_vis - 3), (2, h_vis - 3)
            ]
            pygame.draw.polygon(panel, (10, 8, 16, int(alfa_q * 0.94)), pts_ext)
            pygame.draw.polygon(panel, (4, 3, 8, alfa_q), pts_ext, 1)
            pygame.draw.polygon(panel, (198, 162, 82, int(alfa_q * 0.92)), pts_int, 1)
            pygame.draw.line(panel, (92, 74, 48, int(alfa_q * 0.65)), (46, h_vis // 2 + 2), (w_vis - 26, h_vis // 2 + 2), 1)
            self._guardar_panel_cache(clave_izq, panel)
        surface.blit(panel, (rect.x, rect.y + 3))

        # Emblema izquierdo de Manto / Filo de Ánima / Corazón
        emblema_cx, emblema_cy = rect.x + 24, rect.centery
        pygame.draw.circle(surface, (16, 12, 24), (emblema_cx, emblema_cy), 14)
        tiene_manto = getattr(modelo, "escudo_farol", False)
        tiene_filo = getattr(modelo, "filo_anima", False)
        color_aro = (92, 220, 200) if tiene_manto else ((255, 215, 100) if tiene_filo else (198, 162, 82))
        pygame.draw.circle(surface, (4, 3, 8), (emblema_cx, emblema_cy), 15, 1)
        pygame.draw.circle(surface, color_aro, (emblema_cx, emblema_cy), 14, 1)
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
        x_caliz = rect.x + 54
        y_caliz = rect.y + 20
        for i in range(vidas_max):
            cx = x_caliz + i * 26
            lleno = i < modelo.vidas
            pts_gema = [(cx, y_caliz - 8), (cx + 8, y_caliz), (cx, y_caliz + 9), (cx - 8, y_caliz)]
            pygame.draw.polygon(surface, (20, 14, 24), pts_gema)
            if lleno:
                col_rubi = (235, 45, 68) if (modelo.vidas == 1 and int(getattr(self, "tiempo", 0.0) * 8) % 2 == 0) else (210, 28, 50)
                pygame.draw.polygon(surface, col_rubi, [(cx, y_caliz - 6), (cx + 6, y_caliz), (cx, y_caliz + 7), (cx - 6, y_caliz)])
                pygame.draw.circle(surface, (255, 215, 220), (cx - 2, y_caliz - 2), 2)
            pygame.draw.polygon(surface, (218, 178, 86) if lleno else (88, 76, 64), pts_gema, 1)

        # Cuerda del Rosario de 10 cuentas debajo (progreso hacia +1 Vida)
        y_rosario = rect.y + 50
        x_rosario_ini = rect.x + 54
        pygame.draw.line(surface, (130, 106, 60), (x_rosario_ini, y_rosario), (x_rosario_ini + 9 * 14, y_rosario), 1)
        cuentas_activas = getattr(modelo, "almas_para_vida", modelo.almas % 10)
        for c_idx in range(10):
            bx = x_rosario_ini + c_idx * 14
            encendida = c_idx < cuentas_activas
            if encendida:
                pygame.draw.circle(surface, (92, 220, 200), (bx, y_rosario), 4)
                pygame.draw.circle(surface, (235, 255, 255), (bx, y_rosario), 1)
            else:
                pygame.draw.circle(surface, (24, 20, 30), (bx, y_rosario), 3)
                pygame.draw.circle(surface, (104, 88, 66), (bx, y_rosario), 3, 1)

    def _dibujar_cartela_central_transparente(self, surface: pygame.Surface, rect: pygame.Rect, modelo: HudModel, alfa: int = 235) -> None:
        """Cartela central con respaldo de obsidiana de alto contraste y bisel limpio de 1px."""
        cx = rect.centerx
        nom = getattr(modelo, "nombre_nivel", "") or getattr(modelo, "nivel_nombre", "")
        titulo = nom.upper() if nom else "EL UMBRAL"
        img_txt = self._texto(titulo, 14, (238, 232, 218), sombra=True)

        w_cartela = max(244, img_txt.get_width() + 52)
        h_cartela = 36
        x_cartela = cx - w_cartela // 2
        y_cartela = rect.y + 6

        alfa_q = max(0, min(255, (int(alfa) // 8) * 8))
        clave_c = ("cartela_centro_v3", w_cartela, h_cartela, alfa_q)
        panel_c = self._obtener_panel_cache(clave_c)
        if panel_c is None:
            panel_c = pygame.Surface((w_cartela, h_cartela), pygame.SRCALPHA)
            pts_ext = [
                (12, 0), (w_cartela - 12, 0), (w_cartela - 1, h_cartela // 2),
                (w_cartela - 12, h_cartela - 1), (12, h_cartela - 1), (1, h_cartela // 2)
            ]
            pts_int = [
                (13, 2), (w_cartela - 13, 2), (w_cartela - 3, h_cartela // 2),
                (w_cartela - 13, h_cartela - 3), (13, h_cartela - 3), (3, h_cartela // 2)
            ]
            pygame.draw.polygon(panel_c, (10, 8, 16, int(alfa_q * 0.92)), pts_ext)
            pygame.draw.polygon(panel_c, (4, 3, 8, alfa_q), pts_ext, 1)
            pygame.draw.polygon(panel_c, (198, 162, 82, int(alfa_q * 0.90)), pts_int, 1)
            pygame.draw.circle(panel_c, (218, 178, 86, alfa_q), (11, h_cartela // 2), 2)
            pygame.draw.circle(panel_c, (218, 178, 86, alfa_q), (w_cartela - 11, h_cartela // 2), 2)
            self._guardar_panel_cache(clave_c, panel_c)

        surface.blit(panel_c, (x_cartela, y_cartela))
        surface.blit(img_txt, (cx - img_txt.get_width() // 2, y_cartela + (h_cartela - img_txt.get_height()) // 2))

    def _dibujar_medallones_derechos(self, surface: pygame.Surface, rect: pygame.Rect, modelo: HudModel, alfa: int) -> None:
        """Dos medallones circulares biselados con etiquetas de 11px de alta legibilidad + Urna de Almas y Reloj."""
        cy_med = rect.centery - 6
        # Medallón 1: Dash Espectral con icono de ala y arco radial de recarga
        cx_dash = rect.x + 34
        dash_listo = getattr(modelo, "dash_listo", modelo.dash_cooldown <= 0 and (modelo.en_suelo or modelo.dash_usos_aire > 0))
        prog_dash = 1.0 if dash_listo else max(0.0, 1.0 - min(1.0, modelo.dash_cooldown / max(0.01, DASH_COOLDOWN)))
        self._dibujar_dial_circular(
            surface, cx_dash, cy_med, 19,
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
            surface, cx_arma, cy_med, 19,
            desbloqueado=modelo.tiene_pala,
            progreso=prog_arma,
            color_activo=(195, 85, 250) if es_guadana else (218, 178, 86),
            etiqueta="[J] HOJA" if (modelo.tiene_pala and es_guadana) else ("[J] PALA" if modelo.tiene_pala else "PALA"),
            tipo_icono="guadana" if es_guadana else "pala",
        )

        # Urna de Almas y Reloj a la derecha (con bisel limpio de 1px y tipografías ampliadas)
        urna_rect = pygame.Rect(rect.x + 128, rect.y + 4, rect.width - 130, rect.height - 8)
        alfa_q = max(0, min(255, (int(alfa) // 8) * 8))
        clave_u = ("urna_der_v3", urna_rect.width, urna_rect.height, alfa_q)
        panel_u = self._obtener_panel_cache(clave_u)
        if panel_u is None:
            panel_u = pygame.Surface((urna_rect.width, urna_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(panel_u, (10, 8, 16, int(alfa_q * 0.94)), (0, 0, urna_rect.width, urna_rect.height), border_radius=8)
            pygame.draw.rect(panel_u, (4, 3, 8, alfa_q), (0, 0, urna_rect.width, urna_rect.height), 1, border_radius=8)
            pygame.draw.rect(panel_u, (198, 162, 82, int(alfa_q * 0.92)), (2, 2, urna_rect.width - 4, urna_rect.height - 4), 1, border_radius=7)
            pygame.draw.line(panel_u, (92, 74, 48, int(alfa_q * 0.65)), (12, urna_rect.height // 2 + 2), (urna_rect.width - 12, urna_rect.height // 2 + 2), 1)
            self._guardar_panel_cache(clave_u, panel_u)
        surface.blit(panel_u, urna_rect.topleft)

        # Fila superior de la urna: Orbe de ánima + contador almas de total (+volátiles) en 15px
        orb_x, orb_y = urna_rect.x + 18, urna_rect.y + 18
        pygame.draw.circle(surface, (92, 220, 200), (orb_x, orb_y), 6)
        pygame.draw.circle(surface, (235, 255, 255), (orb_x, orb_y), 2)
        if modelo.almas_total > 0:
            txt_almas = f"{modelo.almas:02d} de {modelo.almas_total:02d}"
        else:
            txt_almas = f"{modelo.almas:02d}"
        if getattr(modelo, "almas_volatiles", 0) > 0:
            txt_almas += f" (+{modelo.almas_volatiles})"
        img_n = self._texto(txt_almas, 15, (242, 236, 222), sombra=True)
        surface.blit(img_n, (orb_x + 12, orb_y - img_n.get_height() // 2))

        # Fila inferior de la urna: Reloj del nivel en 13px
        rel_x, rel_y = urna_rect.x + 10, urna_rect.y + 37
        self._icono_reloj(surface, rel_x, rel_y, (212, 172, 76))
        txt_t = fmt_tiempo(getattr(modelo, "tiempo", 0.0))
        img_t = self._texto(txt_t, 13, (214, 200, 174), sombra=True)
        surface.blit(img_t, (rel_x + 20, rel_y + 8 - img_t.get_height() // 2))

    def _dibujar_dial_circular(
        self, surface: pygame.Surface, cx: int, cy: int, radio: int,
        desbloqueado: bool, progreso: float, color_activo: tuple, etiqueta: str,
        tipo_icono: str = "dash",
    ) -> None:
        pygame.draw.circle(surface, (10, 8, 16), (cx, cy), radio + 1)
        pygame.draw.circle(surface, (4, 3, 8), (cx, cy), radio + 1, 1)
        if not desbloqueado:
            color_apagado = (76, 68, 84)
            pygame.draw.circle(surface, color_apagado, (cx, cy), radio, 1)
            if tipo_icono == "dash":
                self._icono_ala_dash(surface, cx - 8, cy - 8, color_apagado)
            else:
                self._icono_pala(surface, cx - 8, cy - 8, tipo_icono == "guadana", color_apagado)
            # Pequeño candado de hierro en el borde inferior del medallón
            pygame.draw.rect(surface, (36, 30, 42), (cx - 4, cy + radio - 5, 8, 6), border_radius=1)
            pygame.draw.rect(surface, (120, 108, 92), (cx - 4, cy + radio - 5, 8, 6), 1, border_radius=1)
            img_t = self._texto(etiqueta, 11, (140, 130, 118), sombra=True)
            pw, ph = img_t.get_width() + 8, img_t.get_height() + 2
            pygame.draw.rect(surface, (10, 8, 16), (cx - pw // 2, cy + radio + 2, pw, ph), border_radius=3)
            surface.blit(img_t, (cx - img_t.get_width() // 2, cy + radio + 3))
            return

        if progreso >= 0.99:
            pygame.draw.circle(surface, color_activo, (cx, cy), radio, 2)
        else:
            pygame.draw.circle(surface, (75, 68, 58), (cx, cy), radio, 1)
            rect_arc = pygame.Rect(cx - radio, cy - radio, radio * 2, radio * 2)
            pygame.draw.arc(surface, color_activo, rect_arc, math.pi / 2, math.pi / 2 + math.tau * progreso, 3)

        color_ic = color_activo if progreso >= 0.99 else (140, 132, 122)
        if tipo_icono == "dash":
            self._icono_ala_dash(surface, cx - 8, cy - 8, color_ic)
        else:
            self._icono_pala(surface, cx - 8, cy - 8, tipo_icono == "guadana", color_ic)

        img_t = self._texto(etiqueta, 11, (236, 206, 126), sombra=True)
        pw, ph = img_t.get_width() + 8, img_t.get_height() + 2
        pygame.draw.rect(surface, (10, 8, 16), (cx - pw // 2, cy + radio + 2, pw, ph), border_radius=3)
        pygame.draw.rect(surface, (110, 90, 52), (cx - pw // 2, cy + radio + 2, pw, ph), 1, border_radius=3)
        surface.blit(img_t, (cx - img_t.get_width() // 2, cy + radio + 3))

    def _dibujar_barra_jefe_catedral(self, surface: pygame.Surface, modelo: HudModel) -> None:
        """Barra gótica de jefe en el centro del riel superior (reemplaza la cartela del nivel sin apilarse)."""
        sw = surface.get_width()
        bw, bh = 440, 14
        bx = (sw - bw) // 2
        by = 46
        tiempo = getattr(self, "tiempo", 0.0)
        fase = getattr(modelo, "jefe_fase", 1)
        temblor_x = int(math.sin(tiempo * 45.0) * 2) if fase >= 2 else 0
        bx += temblor_x

        # Nombre litúrgico del Jefe en marfil/oro escalado (compacto para respetar badges laterales en +25%)
        nombre_jefe = getattr(modelo, "jefe_nombre", "EL CUSTODIO DEL OSARIO").upper()
        if fase >= 3:
            nombre_jefe = "EL CUSTODIO · FASE III · SEPULCRO"
        elif fase == 2:
            nombre_jefe = "EL CUSTODIO · FASE II"
        img_j = self._texto(nombre_jefe, 13, (242, 224, 168), sombra=True)

        # Placa catedralicia adaptable al tamaño tipográfico activo (F2)
        placa_w = max(bw + 32, img_j.get_width() + 36)
        placa_h = max(56, img_j.get_height() + bh + 22)
        placa_x, placa_y = (sw - placa_w) // 2, 16
        by = placa_y + img_j.get_height() + 9
        pygame.draw.rect(surface, (10, 8, 16), (placa_x, placa_y, placa_w, placa_h), border_radius=6)
        pygame.draw.rect(surface, (4, 3, 8), (placa_x, placa_y, placa_w, placa_h), 1, border_radius=6)
        pygame.draw.rect(surface, (198, 162, 82), (placa_x + 2, placa_y + 2, placa_w - 4, placa_h - 4), 1, border_radius=5)

        surface.blit(img_j, (sw // 2 - img_j.get_width() // 2, placa_y + 5))

        # Marco de obsidiana y filigrana de la barra de sangre
        pygame.draw.rect(surface, (6, 4, 10), (bx - 2, by - 2, bw + 4, bh + 4), border_radius=3)
        pygame.draw.rect(surface, (186, 150, 74), (bx - 2, by - 2, bw + 4, bh + 4), 1, border_radius=3)

        vida_max = max(1, modelo.jefe_vida_max)
        proporcion = max(0.0, min(1.0, modelo.jefe_vida / float(vida_max)))
        ancho_lleno = int(bw * proporcion)
        if ancho_lleno > 0:
            if fase >= 3:
                col_barra = (145, 58, 210)
                col_brillo = (225, 175, 255)
            elif fase == 2:
                col_barra = (210, 28, 50)
                col_brillo = (255, 150, 160)
            else:
                col_barra = (172, 34, 48)
                col_brillo = (255, 150, 160)
            pygame.draw.rect(surface, col_barra, (bx, by, ancho_lleno, bh), border_radius=2)
            pygame.draw.line(surface, col_brillo, (bx + 2, by + 2), (bx + max(2, ancho_lleno - 2), by + 2), 2)

        # Separadores de hueso por punto de vida / bloque de cripta
        seg_w = bw / float(vida_max)
        for s_idx in range(1, vida_max):
            sx = int(bx + s_idx * seg_w)
            pygame.draw.line(surface, (6, 5, 10), (sx, by), (sx, by + bh), 2)
            pygame.draw.line(surface, (228, 224, 210), (sx + 1, by + 2), (sx + 1, by + bh - 2), 1)

        # Aviso de Fase II o III del Jefe debajo de la placa superior (sin tocar jamás el suelo)
        if getattr(modelo, "aviso_jefe", 0.0) > 0 and fase >= 2:
            if fase >= 3:
                aviso_txt = "¡FASE III! ES INVULNERABLE — HAZ QUE ROMPA LAS CRIPTAS DEL SUELO"
                borde_av = (165, 92, 235)
                color_av = (232, 188, 255)
            else:
                aviso_txt = "¡FASE II! LA PALA REBOTA — USA LA GUADAÑA CONSAGRADA (X)"
                borde_av = (210, 45, 65)
                color_av = (255, 120, 130)
            img_av = self._texto(aviso_txt, 12, color_av, sombra=True)
            av_w = img_av.get_width() + 18
            av_x = sw // 2 - av_w // 2
            av_y = placa_y + placa_h + 4
            pygame.draw.rect(surface, (10, 8, 16), (av_x, av_y, av_w, img_av.get_height() + 4), border_radius=4)
            pygame.draw.rect(surface, borde_av, (av_x, av_y, av_w, img_av.get_height() + 4), 1, border_radius=4)
            surface.blit(img_av, (sw // 2 - img_av.get_width() // 2, av_y + 2))

    #---- Canal de mensajes ----#
    def _dibujar_mensajes(self, pantalla, modelo, mensajes, reducir_movimiento, dt):
        if modelo.estado != "jugando":
            return
        if not mensajes.esta_visible():
            return
        m = self.layout.canal_mensajes
        alpha = mensajes.alpha()
        if alpha <= 0:
            return

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
        fuente_kc = self._fuente(11) if keycap_tag else None
        kc_w = kc_h = 0
        if keycap_tag and fuente_kc is not None:
            kw, _kh = fuente_kc.size(keycap_tag)
            kc_w = kw + 12
            kc_h = max(20, fuente_kc.get_height() + 4)

        ancho_util = m.w - (texto_x + (kc_w + 8 if keycap_tag else 0)) - 12
        fuente = self._fuente(self.tema.fuente_contador)
        lineas = envolver(texto_resto, fuente, ancho_util, max_lineas=2)
        linea_h = max(18, fuente.get_height() + 2)
        alto_bloque = len(lineas) * linea_h
        alto_caja = max(m.h, alto_bloque + 12)

        caja = pygame.Surface((m.w, alto_caja), pygame.SRCALPHA)
        caja.fill((0, 0, 0, 0))

        # 1. Fondo de Lápida de Obsidiana Grabada (opacidad base uniforme; el fade se aplica una sola vez con set_alpha)
        pygame.draw.rect(caja, (*self.tema.panel_bg[:3], 235),
                         caja.get_rect(), border_radius=10)
        pygame.draw.rect(caja, (*self.tema.panel_border, self.tema.panel_border_alpha),
                         caja.get_rect(), 1, border_radius=10)
        pygame.draw.rect(caja, (218, 178, 86, 200),
                         (2, 2, m.w - 4, alto_caja - 4), 1, border_radius=8)
        pygame.draw.rect(caja, (*self.tema.oro, 255), (0, 0, 4, alto_caja), border_radius=2)

        # 2. Medallón circular a la izquierda con icono
        med_cx, med_cy = 18, alto_caja // 2
        pygame.draw.circle(caja, (24, 20, 28, 255), (med_cx, med_cy), 11)
        pygame.draw.circle(caja, (218, 178, 86, 255), (med_cx, med_cy), 11, 1)

        color_icono = self.tema.rojo if mensajes.prioridad >= 3 else self.tema.oro
        if mensajes.prioridad >= 3:
            self._icono_calavera(caja, med_cx - 8, med_cy - 8, color_icono)
        else:
            self._icono_reloj(caja, med_cx - 8, med_cy - 8, color_icono)

        if keycap_tag and fuente_kc is not None:
            kc_x = texto_x
            kc_y = (alto_caja - kc_h) // 2

            # Botón marfil / oro con bisel físico
            pygame.draw.rect(caja, (150, 115, 45, 255), (kc_x, kc_y + 2, kc_w, kc_h - 2), border_radius=4)
            pygame.draw.rect(caja, (228, 195, 110, 255), (kc_x, kc_y, kc_w, kc_h - 2), border_radius=4)
            pygame.draw.rect(caja, (24, 20, 16, 255), (kc_x, kc_y, kc_w, kc_h), 1, border_radius=4)

            img_kc = self._texto(keycap_tag, 11, (24, 18, 20), sombra=False)
            caja.blit(img_kc, (kc_x + (kc_w - img_kc.get_width()) // 2, kc_y + (kc_h - img_kc.get_height()) // 2))

            texto_x = kc_x + kc_w + 8

        texto_y = max(4, (alto_caja - alto_bloque) // 2)
        for i, linea in enumerate(lineas):
            img = self._texto(linea, self.tema.fuente_contador, self.tema.texto, sombra=True)
            caja.blit(img, (texto_x, texto_y + i * linea_h))

        if alpha < 255:
            caja.set_alpha(alpha)
        jefe_con_aviso = modelo.jefe_vivo and getattr(modelo, "jefe_fase", 1) >= 2 and getattr(modelo, "aviso_jefe", 0.0) > 0
        desp_jefe = 34 if jefe_con_aviso else (16 if modelo.jefe_vivo else 0)
        pantalla.blit(caja, (m.x, m.y + desp_jefe + mensajes.offset_y()))


#---- Orquestador del HUD ----#
class HudOrquestador:
    def __init__(self):
        self.layout = HudLayout.construir()
        self.tema = HudTheme()
        self.texto_cache = TextoCache(lambda t: self.renderer._fuente(t))
        self.renderer = HudRenderer(self.layout, self.tema, self.texto_cache)
        self.mensajes = MensajeHUD(self.layout, self.tema, self.texto_cache)
        self.modelo = HudModel()
        self.reducir_movimiento = False
        self.modo_hud = 0
        self.timer_inmersivo = 0.0

    def limpiar_caches_texto(self):
        """Limpia las cachés tipográficas del HUD al alternar escala."""
        self.renderer.limpiar_caches_texto()

    def actualizar(self, dt):
        self.mensajes.actualizar(dt)
        if self.timer_inmersivo > 0:
            self.timer_inmersivo = max(0.0, self.timer_inmersivo - dt)

    def armar_modelo(self, juego):
        """Sincroniza el estado del HUD a partir de la instancia activa de Juego."""
        jugador = juego.jugador
        nivel = juego.nivel

        self.modo_hud = getattr(juego, "config_hud_idx", 0)
        self._sincronizar_jugador(jugador, nivel, juego)
        self._sincronizar_jefe(juego, jugador, nivel)
        self._sincronizar_nivel(juego, nivel)
        self.modelo.snapshot_prev()

    def _sincronizar_jugador(self, jugador, nivel, juego):
        """Actualiza recursos y capacidades del jugador y despierta el modo inmersivo."""
        nueva_vida = jugador.vidas if jugador else VIDAS_MAXIMAS
        nuevas_almas = jugador.almas if jugador else 0
        nuevo_dash = getattr(jugador, "tiene_dash", False) if jugador else False
        nueva_pala = jugador.tiene_pala if jugador else False
        nuevo_manto = getattr(jugador, "escudo_farol", False) if jugador else False

        if self.modelo.vidas_prev > 0 and (
            nueva_vida < self.modelo.vidas
            or nuevas_almas > self.modelo.almas
            or (nuevo_dash and not self.modelo.tiene_dash)
            or (nueva_pala and not self.modelo.tiene_pala)
            or (nuevo_manto and not self.modelo.escudo_farol)
        ):
            self.timer_inmersivo = 3.0

        self.modelo.vidas = nueva_vida
        self.modelo.vidas_max = VIDAS_MAXIMAS
        self.modelo.almas = nuevas_almas
        self.modelo.almas_total = nivel.total_almas if nivel else 0
        self.modelo.almas_volatiles = max(0, nuevas_almas - getattr(juego, "almas_consagradas", 0))
        self.modelo.almas_para_vida = jugador.almas_para_vida if jugador else 0
        self.modelo.dash_cooldown = jugador.dash_cooldown if jugador else 0.0
        self.modelo.dash_usos_aire = jugador.dash_usos_aire if jugador else DASH_USOS_AIRE
        self.modelo.tiene_dash = nuevo_dash
        self.modelo.en_suelo = jugador.en_suelo if jugador else True
        self.modelo.ataque_cooldown = jugador.ataque_cooldown if jugador else 0.0
        self.modelo.tiene_pala = nueva_pala
        self.modelo.rango_ataque_mejorado = getattr(jugador, "rango_ataque_mejorado", False) if jugador else False
        self.modelo.escudo_farol = nuevo_manto
        self.modelo.filo_anima = getattr(jugador, "filo_anima", False) if jugador else False

    def _entidad_jefe_visible(self, entidad, jugador, juego, margen_x, margen_y, vida_max, dist_herido):
        if not (hasattr(entidad, "rect") and jugador is not None and hasattr(jugador, "rect")):
            return True
        dist_x = abs(jugador.rect.centerx - entidad.rect.centerx)
        dist_y = abs(jugador.rect.centery - entidad.rect.centery)
        camara = getattr(juego, "camara", None)
        en_camara = camara is not None and camara.is_on_screen(entidad.rect)
        return (dist_y <= margen_y) and (
            en_camara
            or dist_x <= margen_x
            or (getattr(entidad, "vida", vida_max) < vida_max and dist_x <= dist_herido)
        )

    def _sincronizar_jefe(self, juego, jugador, nivel):
        """Selecciona la barra activa entre el jefe principal y los carceleros cercanos."""
        jefe = juego.jefe
        jefe_cerca = bool(
            jefe is not None
            and getattr(jefe, "vivo", False)
            and self._entidad_jefe_visible(jefe, jugador, juego, 420, 220, JEFE_VIDA, 680)
        )
        minijefe_activo = None
        if nivel and hasattr(nivel, "minijefes") and not jefe_cerca:
            for mj in nivel.minijefes:
                if mj.vivo and mj.estado != "muerto" and self._entidad_jefe_visible(
                    mj, jugador, juego, 380, 150, MINIJEFE_VIDA, 540
                ):
                    minijefe_activo = mj
                    break

        if jefe_cerca:
            self.modelo.jefe_vivo = True
            if jefe.fase >= 3 and nivel and getattr(nivel, "bloques_cripta", None):
                total_cr = len(nivel.bloques_cripta)
                sanos_cr = sum(1 for b in nivel.bloques_cripta if not getattr(b, "roto", False))
                self.modelo.jefe_vida = sanos_cr
                self.modelo.jefe_vida_max = max(1, total_cr)
            else:
                self.modelo.jefe_vida = jefe.vida
                self.modelo.jefe_vida_max = JEFE_VIDA
            self.modelo.jefe_fase = jefe.fase
            self.modelo.jefe_nombre = "EL CUSTODIO DEL OSARIO"
        elif minijefe_activo is not None:
            self.modelo.jefe_vivo = True
            self.modelo.jefe_vida = minijefe_activo.vida
            self.modelo.jefe_vida_max = MINIJEFE_VIDA
            self.modelo.jefe_fase = 1
            self.modelo.jefe_nombre = "EL CARCELERO DEL OSARIO"
        else:
            self.modelo.jefe_vivo = False
            self.modelo.jefe_vida = 0
            self.modelo.jefe_vida_max = JEFE_VIDA
            self.modelo.jefe_fase = 1
            self.modelo.jefe_nombre = "EL CUSTODIO DEL OSARIO"

    def _sincronizar_nivel(self, juego, nivel):
        if getattr(juego, "es_tutorial", False):
            self.modelo.nivel_indice = -1
            self.modelo.nivel_total = 3
            self.modelo.nivel_nombre = "RITUAL DEL SEPULTURERO"
        else:
            self.modelo.nivel_indice = juego.nivel_indice
            total = len(getattr(juego, "niveles", [])) or (len(NIVELES) if "NIVELES" in globals() and NIVELES else 3)
            self.modelo.nivel_total = total
            self.modelo.nivel_nombre = nivel.nombre.upper() if nivel and hasattr(nivel, "nombre") else "CAMPOSANTO"
        self.modelo.tiempo = juego.tiempo_total
        self.modelo.estado = juego.estado
        self.modelo.pista = getattr(juego, "texto_ayuda", "") or (nivel.pista if nivel and hasattr(nivel, "pista") else "")
        self.modelo.aviso_jefe = juego.aviso_jefe

    def dibujar(self, pantalla, juego, dt):
        self.armar_modelo(juego)
        self.renderer.dibujar(pantalla, self.modelo, self.mensajes,
                              self.reducir_movimiento, dt,
                              modo_hud=self.modo_hud,
                              timer_inmersivo=self.timer_inmersivo)

    def mostrar_mensaje(self, texto, prioridad, hold, forzar=False):
        self.mensajes.mostrar(texto, prioridad, hold, forzar=forzar)
