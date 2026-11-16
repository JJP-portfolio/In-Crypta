#---- Importamos librerias y configuracion ----#
from collections import OrderedDict
import math

import pygame

import config
from config import ATAQUE_COOLDOWN, DASH_COOLDOWN
from ui.animacion import TextoCache, envolver, fmt_tiempo
from ui.modelos import HudLayout, HudModel, HudTheme, MensajeHUD, _RUTA_FUENTE



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
        self.modo_hud = modo_hud if modo_hud is not None else getattr(self, "modo_hud", 0)
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

        self._dibujar_relicario_izquierdo(surface, layout.zona_izq, modelo, alfa_global)
        if modelo.jefe_vivo:
            self._dibujar_barra_jefe_catedral(surface, modelo)
        else:
            self._dibujar_cartela_central_transparente(surface, layout.zona_centro, modelo, alfa_global)
        self._dibujar_medallones_derechos(surface, layout.zona_der, modelo, alfa_global)
        if mensajes and mensajes.esta_visible() and mensajes.alpha() > 0:
            self._dibujar_mensajes(surface, modelo, mensajes, reducir_movimiento, dt)

    def _dibujar_panel_relicario(self, surface, rect, w_vis, h_vis, alfa_q):
        clave_izq = ("relicario_izq_v3", w_vis, h_vis, alfa_q)
        panel = self._obtener_panel_cache(clave_izq)
        if panel is None:
            panel = pygame.Surface((w_vis, h_vis), pygame.SRCALPHA)
            pts_ext = [
                (0, 0), (w_vis - 18, 0), (w_vis - 1, h_vis // 2),
                (w_vis - 22, h_vis - 1), (0, h_vis - 1),
            ]
            pts_int = [
                (2, 2), (w_vis - 19, 2), (w_vis - 3, h_vis // 2),
                (w_vis - 23, h_vis - 3), (2, h_vis - 3),
            ]
            pygame.draw.polygon(panel, (10, 8, 16, int(alfa_q * 0.94)), pts_ext)
            pygame.draw.polygon(panel, (4, 3, 8, alfa_q), pts_ext, 1)
            pygame.draw.polygon(panel, (198, 162, 82, int(alfa_q * 0.92)), pts_int, 1)
            pygame.draw.line(
                panel, (92, 74, 48, int(alfa_q * 0.65)), (46, h_vis // 2 + 2), (w_vis - 26, h_vis // 2 + 2), 1
            )
            self._guardar_panel_cache(clave_izq, panel)
        surface.blit(panel, (rect.x, rect.y + 3))

    def _dibujar_emblema_y_calices(self, surface, rect, modelo, vidas_max):
        emblema_cx, emblema_cy = rect.x + 24, rect.centery
        pygame.draw.circle(surface, (16, 12, 24), (emblema_cx, emblema_cy), 14)
        tiene_manto = getattr(modelo, "escudo_farol", False)
        tiene_filo = getattr(modelo, "filo_anima", False)
        color_aro = (
            (92, 220, 200) if tiene_manto else ((255, 215, 100) if tiene_filo else (198, 162, 82))
        )
        pygame.draw.circle(surface, (4, 3, 8), (emblema_cx, emblema_cy), 15, 1)
        pygame.draw.circle(surface, color_aro, (emblema_cx, emblema_cy), 14, 1)
        if tiene_manto:
            pygame.draw.polygon(
                surface,
                (140, 235, 255),
                [
                    (emblema_cx, emblema_cy - 8), (emblema_cx + 7, emblema_cy),
                    (emblema_cx, emblema_cy + 8), (emblema_cx - 7, emblema_cy),
                ],
            )
        elif tiene_filo:
            pygame.draw.circle(surface, (255, 215, 100), (emblema_cx, emblema_cy), 6)
        else:
            pygame.draw.circle(surface, (210, 28, 50), (emblema_cx, emblema_cy), 5)

        x_caliz, y_caliz = rect.x + 54, rect.y + 20
        parpadeo = int(getattr(self, "tiempo", 0.0) * 8) % 2 == 0
        for i in range(vidas_max):
            cx = x_caliz + i * 26
            lleno = i < modelo.vidas
            pts_gema = [(cx, y_caliz - 8), (cx + 8, y_caliz), (cx, y_caliz + 9), (cx - 8, y_caliz)]
            pygame.draw.polygon(surface, (20, 14, 24), pts_gema)
            if lleno:
                col_rubi = (235, 45, 68) if (modelo.vidas == 1 and parpadeo) else (210, 28, 50)
                pts_rubi = [(cx, y_caliz - 6), (cx + 6, y_caliz), (cx, y_caliz + 7), (cx - 6, y_caliz)]
                pygame.draw.polygon(surface, col_rubi, pts_rubi)
                pygame.draw.circle(surface, (255, 215, 220), (cx - 2, y_caliz - 2), 2)
            pygame.draw.polygon(surface, (218, 178, 86) if lleno else (88, 76, 64), pts_gema, 1)

    def _dibujar_relicario_izquierdo(
        self, surface: pygame.Surface, rect: pygame.Rect, modelo: HudModel, alfa: int
    ) -> None:
        """Medallón heráldico compacto con Cálices de Rubí arriba y Rosario debajo."""
        vidas_max = max(getattr(modelo, "vidas_max", 5), 5)
        w_vis = max(230, 74 + vidas_max * 28)
        alfa_q = max(0, min(255, (int(alfa) // 8) * 8))
        self._dibujar_panel_relicario(surface, rect, w_vis, rect.height - 6, alfa_q)
        self._dibujar_emblema_y_calices(surface, rect, modelo, vidas_max)

        y_rosario = rect.y + 50
        x_rosario_ini = rect.x + 54
        pygame.draw.line(
            surface, (130, 106, 60), (x_rosario_ini, y_rosario), (x_rosario_ini + 9 * 14, y_rosario), 1
        )
        cuentas_activas = getattr(modelo, "almas_para_vida", modelo.almas % 10)
        for c_idx in range(10):
            bx = x_rosario_ini + c_idx * 14
            if c_idx < cuentas_activas:
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

    def _dibujar_urna_derecha(self, surface, rect, modelo, alfa):
        urna_rect = pygame.Rect(rect.x + 128, rect.y + 4, rect.width - 130, rect.height - 8)
        alfa_q = max(0, min(255, (int(alfa) // 8) * 8))
        clave_u = ("urna_der_v3", urna_rect.width, urna_rect.height, alfa_q)
        panel_u = self._obtener_panel_cache(clave_u)
        if panel_u is None:
            panel_u = pygame.Surface((urna_rect.width, urna_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(
                panel_u, (10, 8, 16, int(alfa_q * 0.94)), (0, 0, urna_rect.width, urna_rect.height), border_radius=8
            )
            pygame.draw.rect(
                panel_u, (4, 3, 8, alfa_q), (0, 0, urna_rect.width, urna_rect.height), 1, border_radius=8
            )
            pygame.draw.rect(
                panel_u,
                (198, 162, 82, int(alfa_q * 0.92)),
                (2, 2, urna_rect.width - 4, urna_rect.height - 4),
                1,
                border_radius=7,
            )
            pygame.draw.line(
                panel_u,
                (92, 74, 48, int(alfa_q * 0.65)),
                (12, urna_rect.height // 2 + 2),
                (urna_rect.width - 12, urna_rect.height // 2 + 2),
                1,
            )
            self._guardar_panel_cache(clave_u, panel_u)
        surface.blit(panel_u, urna_rect.topleft)

        orb_x, orb_y = urna_rect.x + 18, urna_rect.y + 18
        pygame.draw.circle(surface, (92, 220, 200), (orb_x, orb_y), 6)
        pygame.draw.circle(surface, (235, 255, 255), (orb_x, orb_y), 2)
        txt_almas = (
            f"{modelo.almas:02d} de {modelo.almas_total:02d}"
            if modelo.almas_total > 0
            else f"{modelo.almas:02d}"
        )
        if getattr(modelo, "almas_volatiles", 0) > 0:
            txt_almas += f" (+{modelo.almas_volatiles})"
        img_n = self._texto(txt_almas, 15, (242, 236, 222), sombra=True)
        surface.blit(img_n, (orb_x + 12, orb_y - img_n.get_height() // 2))

        rel_x, rel_y = urna_rect.x + 10, urna_rect.y + 37
        self._icono_reloj(surface, rel_x, rel_y, (212, 172, 76))
        img_t = self._texto(fmt_tiempo(getattr(modelo, "tiempo", 0.0)), 13, (214, 200, 174), sombra=True)
        surface.blit(img_t, (rel_x + 20, rel_y + 8 - img_t.get_height() // 2))

    def _dibujar_medallones_derechos(
        self, surface: pygame.Surface, rect: pygame.Rect, modelo: HudModel, alfa: int
    ) -> None:
        """Dos medallones circulares biselados + Urna de Almas y Reloj."""
        cy_med = rect.centery - 6
        dash_listo = getattr(
            modelo,
            "dash_listo",
            modelo.dash_cooldown <= 0 and (modelo.en_suelo or modelo.dash_usos_aire > 0),
        )
        prog_dash = (
            1.0
            if dash_listo
            else max(0.0, 1.0 - min(1.0, modelo.dash_cooldown / max(0.01, DASH_COOLDOWN)))
        )
        self._dibujar_dial_circular(
            surface,
            rect.x + 34,
            cy_med,
            19,
            desbloqueado=modelo.tiene_dash,
            progreso=prog_dash,
            color_activo=(92, 220, 200),
            etiqueta="[SHIFT]" if modelo.tiene_dash else "DASH",
            tipo_icono="dash",
        )

        es_guadana = getattr(
            modelo, "rango_mejorado", getattr(modelo, "rango_ataque_mejorado", False)
        )
        prog_arma = (
            1.0
            if modelo.ataque_cooldown <= 0
            else max(0.0, 1.0 - min(1.0, modelo.ataque_cooldown / max(0.01, ATAQUE_COOLDOWN)))
        )
        etiq_arma = (
            "[J] HOJA"
            if (modelo.tiene_pala and es_guadana)
            else ("[J] PALA" if modelo.tiene_pala else "PALA")
        )
        self._dibujar_dial_circular(
            surface,
            rect.x + 90,
            cy_med,
            19,
            desbloqueado=modelo.tiene_pala,
            progreso=prog_arma,
            color_activo=(195, 85, 250) if es_guadana else (218, 178, 86),
            etiqueta=etiq_arma,
            tipo_icono="guadana" if es_guadana else "pala",
        )
        self._dibujar_urna_derecha(surface, rect, modelo, alfa)

    def _dibujar_etiqueta_dial(self, surface, cx, cy, radio, etiqueta, color_txt, con_borde):
        img_t = self._texto(etiqueta, 11, color_txt, sombra=True)
        pw, ph = img_t.get_width() + 8, img_t.get_height() + 2
        pygame.draw.rect(
            surface, (10, 8, 16), (cx - pw // 2, cy + radio + 2, pw, ph), border_radius=3
        )
        if con_borde:
            pygame.draw.rect(
                surface, (110, 90, 52), (cx - pw // 2, cy + radio + 2, pw, ph), 1, border_radius=3
            )
        surface.blit(img_t, (cx - img_t.get_width() // 2, cy + radio + 3))

    def _dibujar_dial_circular(
        self,
        surface: pygame.Surface,
        cx: int,
        cy: int,
        radio: int,
        desbloqueado: bool,
        progreso: float,
        color_activo: tuple,
        etiqueta: str,
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
            pygame.draw.rect(surface, (36, 30, 42), (cx - 4, cy + radio - 5, 8, 6), border_radius=1)
            pygame.draw.rect(surface, (120, 108, 92), (cx - 4, cy + radio - 5, 8, 6), 1, border_radius=1)
            self._dibujar_etiqueta_dial(surface, cx, cy, radio, etiqueta, (140, 130, 118), False)
            return

        if progreso >= 0.99:
            pygame.draw.circle(surface, color_activo, (cx, cy), radio, 2)
        else:
            pygame.draw.circle(surface, (75, 68, 58), (cx, cy), radio, 1)
            rect_arc = pygame.Rect(cx - radio, cy - radio, radio * 2, radio * 2)
            pygame.draw.arc(
                surface, color_activo, rect_arc, math.pi / 2, math.pi / 2 + math.tau * progreso, 3
            )
        color_ic = color_activo if progreso >= 0.99 else (140, 132, 122)
        if tipo_icono == "dash":
            self._icono_ala_dash(surface, cx - 8, cy - 8, color_ic)
        else:
            self._icono_pala(surface, cx - 8, cy - 8, tipo_icono == "guadana", color_ic)
        self._dibujar_etiqueta_dial(surface, cx, cy, radio, etiqueta, (236, 206, 126), True)

    def _dibujar_aviso_fase_jefe(self, surface, sw, placa_y, placa_h, fase):
        if fase >= 3:
            aviso_txt = "¡FASE III! ES INVULNERABLE — HAZ QUE ROMPA LAS CRIPTAS DEL SUELO"
            borde_av, color_av = (165, 92, 235), (232, 188, 255)
        else:
            aviso_txt = "¡FASE II! LA PALA REBOTA — USA LA GUADAÑA CONSAGRADA (X)"
            borde_av, color_av = (210, 45, 65), (255, 120, 130)
        img_av = self._texto(aviso_txt, 12, color_av, sombra=True)
        av_w = img_av.get_width() + 18
        av_x = sw // 2 - av_w // 2
        av_y = placa_y + placa_h + 4
        pygame.draw.rect(
            surface, (10, 8, 16), (av_x, av_y, av_w, img_av.get_height() + 4), border_radius=4
        )
        pygame.draw.rect(
            surface, borde_av, (av_x, av_y, av_w, img_av.get_height() + 4), 1, border_radius=4
        )
        surface.blit(img_av, (sw // 2 - img_av.get_width() // 2, av_y + 2))

    def _dibujar_barra_jefe_catedral(self, surface: pygame.Surface, modelo: HudModel) -> None:
        """Barra gótica de jefe en el centro del riel superior."""
        sw = surface.get_width()
        bw, bh = 440, 14
        fase = getattr(modelo, "jefe_fase", 1)
        temblor_x = int(math.sin(getattr(self, "tiempo", 0.0) * 45.0) * 2) if fase >= 2 else 0
        bx = (sw - bw) // 2 + temblor_x

        nombre_jefe = getattr(modelo, "jefe_nombre", "EL CUSTODIO DEL OSARIO").upper()
        if fase >= 3:
            nombre_jefe = "EL CUSTODIO · FASE III · SEPULCRO"
        elif fase == 2:
            nombre_jefe = "EL CUSTODIO · FASE II"
        img_j = self._texto(nombre_jefe, 13, (242, 224, 168), sombra=True)

        placa_w = max(bw + 32, img_j.get_width() + 36)
        placa_h = max(56, img_j.get_height() + bh + 22)
        placa_x, placa_y = (sw - placa_w) // 2, 16
        by = placa_y + img_j.get_height() + 9
        pygame.draw.rect(surface, (10, 8, 16), (placa_x, placa_y, placa_w, placa_h), border_radius=6)
        pygame.draw.rect(surface, (4, 3, 8), (placa_x, placa_y, placa_w, placa_h), 1, border_radius=6)
        pygame.draw.rect(
            surface, (198, 162, 82), (placa_x + 2, placa_y + 2, placa_w - 4, placa_h - 4), 1, border_radius=5
        )
        surface.blit(img_j, (sw // 2 - img_j.get_width() // 2, placa_y + 5))

        pygame.draw.rect(surface, (6, 4, 10), (bx - 2, by - 2, bw + 4, bh + 4), border_radius=3)
        pygame.draw.rect(surface, (186, 150, 74), (bx - 2, by - 2, bw + 4, bh + 4), 1, border_radius=3)

        vida_max = max(1, modelo.jefe_vida_max)
        ancho_lleno = int(bw * max(0.0, min(1.0, modelo.jefe_vida / float(vida_max))))
        if ancho_lleno > 0:
            colores = {
                3: ((145, 58, 210), (225, 175, 255)),
                2: ((210, 28, 50), (255, 150, 160)),
            }
            col_barra, col_brillo = colores.get(
                3 if fase >= 3 else fase, ((172, 34, 48), (255, 150, 160))
            )
            pygame.draw.rect(surface, col_barra, (bx, by, ancho_lleno, bh), border_radius=2)
            pygame.draw.line(
                surface, col_brillo, (bx + 2, by + 2), (bx + max(2, ancho_lleno - 2), by + 2), 2
            )

        seg_w = bw / float(vida_max)
        for s_idx in range(1, vida_max):
            sx = int(bx + s_idx * seg_w)
            pygame.draw.line(surface, (6, 5, 10), (sx, by), (sx, by + bh), 2)
            pygame.draw.line(surface, (228, 224, 210), (sx + 1, by + 2), (sx + 1, by + bh - 2), 1)

        if getattr(modelo, "aviso_jefe", 0.0) > 0 and fase >= 2:
            self._dibujar_aviso_fase_jefe(surface, sw, placa_y, placa_h, fase)

    #---- Canal de mensajes ----#
    def _extraer_tecla_mensaje(self, texto_crudo):
        if texto_crudo.startswith("[") and "]" in texto_crudo:
            idx_fin = texto_crudo.find("]")
            tag = texto_crudo[1:idx_fin].strip()
            resto = texto_crudo[idx_fin + 1 :].strip()
            if resto.startswith(("·", ":")):
                resto = resto[1:].strip()
            return tag, resto
        return None, texto_crudo

    def _preparar_caja_mensaje(self, ancho, alto_caja, prioridad):
        caja = pygame.Surface((ancho, alto_caja), pygame.SRCALPHA)
        caja.fill((0, 0, 0, 0))
        pygame.draw.rect(caja, (*self.tema.panel_bg[:3], 235), caja.get_rect(), border_radius=10)
        pygame.draw.rect(
            caja,
            (*self.tema.panel_border, self.tema.panel_border_alpha),
            caja.get_rect(),
            1,
            border_radius=10,
        )
        pygame.draw.rect(caja, (218, 178, 86, 200), (2, 2, ancho - 4, alto_caja - 4), 1, border_radius=8)
        pygame.draw.rect(caja, (*self.tema.oro, 255), (0, 0, 4, alto_caja), border_radius=2)

        med_cx, med_cy = 18, alto_caja // 2
        pygame.draw.circle(caja, (24, 20, 28, 255), (med_cx, med_cy), 11)
        pygame.draw.circle(caja, (218, 178, 86, 255), (med_cx, med_cy), 11, 1)
        color_icono = self.tema.rojo if prioridad >= 3 else self.tema.oro
        if prioridad >= 3:
            self._icono_calavera(caja, med_cx - 8, med_cy - 8, color_icono)
        else:
            self._icono_reloj(caja, med_cx - 8, med_cy - 8, color_icono)
        return caja

    def _dibujar_keycap_mensaje(self, caja, texto_x, alto_caja, kc_w, kc_h, keycap_tag):
        kc_x = texto_x
        kc_y = (alto_caja - kc_h) // 2
        pygame.draw.rect(caja, (150, 115, 45, 255), (kc_x, kc_y + 2, kc_w, kc_h - 2), border_radius=4)
        pygame.draw.rect(caja, (228, 195, 110, 255), (kc_x, kc_y, kc_w, kc_h - 2), border_radius=4)
        pygame.draw.rect(caja, (24, 20, 16, 255), (kc_x, kc_y, kc_w, kc_h), 1, border_radius=4)
        img_kc = self._texto(keycap_tag, 11, (24, 18, 20), sombra=False)
        caja.blit(
            img_kc, (kc_x + (kc_w - img_kc.get_width()) // 2, kc_y + (kc_h - img_kc.get_height()) // 2)
        )
        return kc_x + kc_w + 8

    def _dibujar_mensajes(self, pantalla, modelo, mensajes, reducir_movimiento, dt):
        if modelo.estado != "jugando" or not mensajes.esta_visible():
            return
        alpha = mensajes.alpha()
        if alpha <= 0:
            return
        m = self.layout.canal_mensajes
        keycap_tag, texto_resto = self._extraer_tecla_mensaje(mensajes.texto.strip())

        texto_x = 38
        fuente_kc = self._fuente(11) if keycap_tag else None
        kc_w = kc_h = 0
        if keycap_tag and fuente_kc is not None:
            kw, _ = fuente_kc.size(keycap_tag)
            kc_w = kw + 12
            kc_h = max(20, fuente_kc.get_height() + 4)

        ancho_util = m.w - (texto_x + (kc_w + 8 if keycap_tag else 0)) - 12
        fuente = self._fuente(self.tema.fuente_contador)
        lineas = envolver(texto_resto, fuente, ancho_util, max_lineas=2)
        linea_h = max(18, fuente.get_height() + 2)
        alto_bloque = len(lineas) * linea_h
        alto_caja = max(m.h, alto_bloque + 12)

        caja = self._preparar_caja_mensaje(m.w, alto_caja, mensajes.prioridad)
        if keycap_tag and fuente_kc is not None:
            texto_x = self._dibujar_keycap_mensaje(caja, texto_x, alto_caja, kc_w, kc_h, keycap_tag)

        texto_y = max(4, (alto_caja - alto_bloque) // 2)
        for i, linea in enumerate(lineas):
            img = self._texto(linea, self.tema.fuente_contador, self.tema.texto, sombra=True)
            caja.blit(img, (texto_x, texto_y + i * linea_h))

        if alpha < 255:
            caja.set_alpha(alpha)
        jefe_av = (
            modelo.jefe_vivo
            and getattr(modelo, "jefe_fase", 1) >= 2
            and getattr(modelo, "aviso_jefe", 0.0) > 0
        )
        desp_jefe = 34 if jefe_av else (16 if modelo.jefe_vivo else 0)
        pantalla.blit(caja, (m.x, m.y + desp_jefe + mensajes.offset_y()))
