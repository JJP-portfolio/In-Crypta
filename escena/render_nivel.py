#---- Importamos librerias y configuracion ----#
import math

import pygame

import config
from config import (
    AMARILLO,
    CARMESÍ_SANGRE,
    MARFIL_XILOGRAFICO,
    NEGRO,
    NEGRO_NOCHE,
    ORO,
    ORO_LITÚRGICO,
    PIEDRA_OSCURA,
    SALITRE_CRIPTA,
    SANGRE,
    TILE,
    TINTA_ABISMO,
    TURQUESA_ÁNIMA,
)
from escena.decoraciones import (
    DecoracionesNivelMixin,
    _construir_halo_radial,
    _obtener_halo_brasero,
    _obtener_halo_vela,
)


_HALO_META = None
_PALETAS_SOLIDOS = {
    "cripta": {
        "bisel_top": (180, 198, 222),
        "piso": (44, 48, 58),
        "piso_profundo": (26, 28, 36),
        "borde": (18, 20, 26),
        "arriba": (55, 78, 68),
        "brizna": (82, 118, 102),
        "cuerpo": (52, 56, 68),
        "marco": (24, 26, 34),
        "ladrillo": (58, 56, 70),
    },
    "osario": {
        "bisel_top": (218, 208, 186),
        "piso": (62, 45, 43),
        "piso_profundo": (38, 26, 26),
        "borde": (26, 18, 20),
        "arriba": (96, 58, 52),
        "brizna": (136, 86, 78),
        "cuerpo": (74, 52, 50),
        "marco": (36, 22, 24),
        "ladrillo": (68, 54, 52),
    },
    "camposanto": {
        "bisel_top": (165, 185, 160),
        "piso": (68, 52, 42),
        "piso_profundo": (44, 32, 26),
        "borde": (28, 20, 16),
        "arriba": (48, 76, 44),
        "brizna": (76, 114, 68),
        "cuerpo": (64, 62, 70),
        "marco": (26, 24, 30),
        "ladrillo": (62, 58, 50),
    },
}



def _obtener_halo_meta():
    """Halo translucido suave para el portal/porton de meta."""
    global _HALO_META
    if _HALO_META is None:
        _HALO_META = _construir_halo_radial(64, 30, (255, 205, 95), 35)
    return _HALO_META


#---- Mixin de renderizado de nivel y decoraciones ----#
class RenderNivelMixin:
    """Metodos de renderizado procedural de solidos, plataformas, trampas y decoracion."""

class RenderNivelMixin(DecoracionesNivelMixin):
    def dibujar(self, surface, camara):
        """Dibuja la geometria del nivel, objetos interactivos y enemigos secundarios."""
        self.dibujar_solidos(surface, camara)
        self.dibujar_plataformas(surface, camara)
        self.dibujar_decoraciones(surface, camara)
        self.dibujar_peligros(surface, camara)

        tiempo = pygame.time.get_ticks() / 1000
        grupos_dibujables = (
            getattr(self, "losas_quebradizas", ()),
            getattr(self, "bloques_cripta", ()),
            getattr(self, "compuertas_arena", ()),
            getattr(self, "muros_minijefe", ()),
            getattr(self, "incensarios", ()),
            self.almas,
            self.palas,
            self.power_ups_dash,
            self.power_ups_rango,
            self.checkpoints,
            self.minijefes,
            self.enemigos_melee,
            self.cuervos,
            self.polillas,
            self.aranias,
        )
        for grupo in grupos_dibujables:
            for item in grupo:
                item.dibujar(surface, camara, tiempo)

        self.dibujar_meta(surface, camara)

    def _dibujar_riel_plataforma(self, surface, rect, init_rect, plataforma):
        """Dibuja el riel o cadena guia segun el eje de oscilacion ('h' o 'v')."""
        amp = int(getattr(plataforma, "amplitud", 0))
        if amp <= 0:
            return
        eje = getattr(plataforma, "eje", "h")
        if eje in ("h", "x"):
            x_min = init_rect.x - amp + 6
            x_max = init_rect.right + amp - 6
            ry = rect.centery
            pygame.draw.line(surface, (22, 20, 28), (x_min, ry), (x_max, ry), 4)
            pygame.draw.line(surface, (58, 56, 70), (x_min, ry - 1), (x_max, ry - 1), 1)
            for ex in range(x_min, x_max + 1, 12):
                pygame.draw.circle(surface, (86, 82, 98), (ex, ry), 2, 1)
            for ext_x in (x_min, x_max):
                pygame.draw.circle(surface, (28, 24, 34), (ext_x, ry), 5)
                pygame.draw.circle(surface, (132, 118, 88), (ext_x, ry), 4, 1)
                pygame.draw.circle(surface, TURQUESA_ÁNIMA, (ext_x, ry), 1)
            return

        y_min = init_rect.centery - amp - 18
        y_max = init_rect.centery + amp + 10
        for ancla_x in (rect.x + 10, rect.right - 10):
            for cy in range(y_min, y_max, 8):
                pygame.draw.rect(surface, (18, 16, 22), (ancla_x - 3, cy, 6, 7), border_radius=2)
                pygame.draw.rect(surface, (78, 74, 90), (ancla_x - 2, cy + 1, 4, 5), 1, border_radius=1)
            pygame.draw.circle(surface, (30, 26, 38), (ancla_x, y_min), 5)
            pygame.draw.circle(surface, (132, 118, 88), (ancla_x, y_min), 4, 1)

    def _dibujar_detalles_plataforma(self, surface, rect, color_marco, plataforma):
        pygame.draw.line(
            surface, MARFIL_XILOGRAFICO, (rect.x + 2, rect.y + 1), (rect.right - 2, rect.y + 1), 3
        )
        for cx_cincel in range(rect.x + 8, rect.right - 4, 16):
            pygame.draw.line(surface, TINTA_ABISMO, (cx_cincel, rect.y), (cx_cincel, rect.y + 3), 1)
        pygame.draw.line(
            surface, TINTA_ABISMO, (rect.x + 2, rect.y + 4), (rect.right - 2, rect.y + 4), 2
        )
        for ax in range(rect.x + 6, rect.right - 6, 8):
            pygame.draw.line(surface, (18, 16, 24), (ax, rect.y + 6), (ax, rect.y + 11), 1)

        if rect.width >= 48:
            cx = rect.centerx
            pygame.draw.line(surface, color_marco, (cx, rect.y + 4), (cx, rect.bottom - 3), 3)
            pygame.draw.line(surface, color_marco, (cx - 10, rect.y + 9), (cx + 10, rect.y + 9), 3)
            pygame.draw.line(surface, ORO_LITÚRGICO, (cx, rect.y + 5), (cx, rect.bottom - 4), 1)
            pygame.draw.line(surface, ORO_LITÚRGICO, (cx - 9, rect.y + 9), (cx + 9, rect.y + 9), 1)
        elif rect.width >= 32:
            pygame.draw.line(
                surface, ORO_LITÚRGICO, (rect.x + 8, rect.y + 9), (rect.right - 8, rect.y + 9), 1
            )

        giro = (plataforma.rect.x + plataforma.rect.y) * 0.12
        for eng_x in (rect.x + 5, rect.right - 6):
            eng_y = rect.centery + 1
            pygame.draw.circle(surface, (32, 26, 36), (eng_x, eng_y), 4)
            pygame.draw.circle(surface, (168, 134, 72), (eng_x, eng_y), 3, 1)
            dx_g, dy_g = int(math.cos(giro) * 3), int(math.sin(giro) * 3)
            pygame.draw.line(
                surface, (198, 162, 92), (eng_x - dx_g, eng_y - dy_g), (eng_x + dx_g, eng_y + dy_g), 1
            )

    def _dibujar_cuerpo_plataforma(
        self, surface, rect, init_rect, plataforma, tema_efectivo, tiempo
    ):
        """Renderiza la tapa del sarcofago ferreo, cornisa superior y engranajes."""
        pygame.draw.rect(
            surface, NEGRO_NOCHE, (rect.x + 2, rect.bottom, rect.width - 4, 4), border_radius=2
        )
        if rect.width >= 40:
            cx_b = rect.centerx
            pulso_b = 0.5 + 0.5 * math.sin(tiempo * 5.0 + init_rect.x * 0.05)
            pygame.draw.polygon(
                surface,
                (36, 32, 44),
                [
                    (cx_b - 10, rect.bottom - 1),
                    (cx_b + 10, rect.bottom - 1),
                    (cx_b + 5, rect.bottom + 5),
                    (cx_b - 5, rect.bottom + 5),
                ],
            )
            c_nucleo = (
                int(70 + 30 * pulso_b),
                int(185 + 40 * pulso_b),
                int(170 + 35 * pulso_b),
            )
            pygame.draw.circle(surface, c_nucleo, (cx_b, rect.bottom + 2), 2)

        colores_losa = {
            "osario": ((60, 46, 48), (28, 20, 22)),
            "cripta": ((50, 54, 68), (22, 24, 34)),
        }
        color_losa, color_marco = colores_losa.get(
            tema_efectivo, ((56, 50, 62), (24, 20, 28))
        )
        pygame.draw.rect(surface, color_losa, rect, border_radius=3)
        pygame.draw.rect(surface, color_marco, rect, 2, border_radius=3)
        self._dibujar_detalles_plataforma(surface, rect, color_marco, plataforma)

    def dibujar_plataformas(self, surface, camara):
        tiempo = pygame.time.get_ticks() / 1000.0
        for plataforma in self.plataformas:
            if not camara.is_on_screen(plataforma.rect):
                continue
            rect = camara.aplicar_rect(plataforma.rect)
            init_rect = camara.aplicar_rect(plataforma.inicial_rect)
            tema_efectivo = self._tema_efectivo(plataforma.rect.y // TILE)
            self._dibujar_riel_plataforma(surface, rect, init_rect, plataforma)
            self._dibujar_cuerpo_plataforma(surface, rect, init_rect, plataforma, tema_efectivo, tiempo)

    def _dibujar_solido_nes(self, surface, rect, fila, col_inicio, num_cols, paleta):
        c_corte = (10, 8, 14)
        for c_idx in range(num_cols):
            tx = rect.x + c_idx * TILE
            t_rect = pygame.Rect(tx, rect.y, TILE, TILE)
            tiene_arriba = self._tiene_solido(fila - 1, col_inicio + c_idx)
            c_fill = paleta["piso_profundo"] if tiene_arriba else paleta["piso"]
            pygame.draw.rect(surface, c_fill, t_rect)
            pygame.draw.rect(surface, c_corte, t_rect, 1)
            if not tiene_arriba:
                pygame.draw.rect(surface, paleta["bisel_top"], (tx, rect.y, TILE, 3))
                pygame.draw.rect(surface, c_corte, (tx, rect.y + 3, TILE, 2))

    def _dibujar_solido_snes(self, surface, rect, fila, col_inicio, num_cols, paleta):
        c_corte = (10, 8, 14)
        desplazamiento = (TILE // 2) if fila % 2 == 1 else 0
        c_bisel_top = paleta["bisel_top"]
        c_bisel_sub = tuple(max(0, ch - 30) for ch in c_bisel_top)
        for c_idx in range(num_cols):
            tx = rect.x + c_idx * TILE
            t_rect = pygame.Rect(tx, rect.y, TILE, TILE)
            tiene_arriba = self._tiene_solido(fila - 1, col_inicio + c_idx)
            pygame.draw.rect(surface, paleta["ladrillo"], t_rect)
            pygame.draw.rect(surface, c_corte, t_rect, 1)
            start_y = rect.y + 7 if not tiene_arriba else rect.y
            gx = tx + desplazamiento
            if gx < tx + TILE:
                pygame.draw.line(surface, c_corte, (gx, start_y), (gx, rect.bottom), 1)
                pygame.draw.line(surface, (84, 82, 98), (gx + 1, start_y), (gx + 1, rect.bottom), 1)
            if not tiene_arriba:
                pygame.draw.rect(surface, c_bisel_top, (tx, rect.y, TILE, 3))
                pygame.draw.rect(surface, c_bisel_sub, (tx, rect.y + 3, TILE, 2))
                pygame.draw.rect(surface, c_corte, (tx, rect.y + 5, TILE, 2))

    def _dibujar_estalactita_techo(self, surface, rect, tx, fila, col, color_cuerpo, color_marco):
        c_roca_oscura = (
            max(0, color_cuerpo[0] - 12),
            max(0, color_cuerpo[1] - 12),
            max(0, color_cuerpo[2] - 10),
        )
        jit = ((col * 7 + fila * 3) % 5) - 2
        punta_x, punta_y = tx + TILE // 2 + jit, rect.bottom - 1
        pts_cono = [
            (tx + 1, rect.y),
            (tx + TILE - 1, rect.y),
            (tx + TILE - 5, rect.y + 11),
            (punta_x + 3, rect.y + 23),
            (punta_x, punta_y),
            (punta_x - 3, rect.y + 23),
            (tx + 5, rect.y + 11),
        ]
        pts_sombra = [
            (tx + TILE // 2, rect.y),
            (tx + TILE - 1, rect.y),
            (tx + TILE - 5, rect.y + 11),
            (punta_x, punta_y),
        ]
        pygame.draw.polygon(surface, color_cuerpo, pts_cono)
        pygame.draw.polygon(surface, c_roca_oscura, pts_sombra)
        pygame.draw.polygon(surface, color_marco, pts_cono, 2)
        pygame.draw.line(
            surface, SALITRE_CRIPTA, (tx + 5, rect.y + 2), (punta_x - 1, punta_y - 3), 1
        )
        pygame.draw.circle(surface, SALITRE_CRIPTA, (punta_x, punta_y + 2), 1)

    def _dibujar_hombro_techo(
        self, surface, rect, tx, tiene_izq, tiene_der, color_cuerpo, color_marco
    ):
        c_roca_oscura = (
            max(0, color_cuerpo[0] - 10),
            max(0, color_cuerpo[1] - 10),
            max(0, color_cuerpo[2] - 8),
        )
        if not tiene_izq and tiene_der:
            pts_hombro = [
                (tx + 2, rect.y), (tx + TILE, rect.y), (tx + TILE, rect.bottom),
                (tx + TILE - 10, rect.bottom - 4), (tx + 8, rect.y + 14),
            ]
            borde = [
                (tx + 2, rect.y), (tx + 8, rect.y + 14),
                (tx + TILE - 10, rect.bottom - 4), (tx + TILE, rect.bottom),
            ]
            pygame.draw.polygon(surface, color_cuerpo, pts_hombro)
            pygame.draw.lines(surface, color_marco, False, borde, 2)
            pygame.draw.line(surface, SALITRE_CRIPTA, (tx + 5, rect.y + 3), (tx + 12, rect.y + 16), 1)
            return True
        if tiene_izq and not tiene_der:
            pts_hombro = [
                (tx, rect.y), (tx + TILE - 2, rect.y), (tx + TILE - 8, rect.y + 14),
                (tx + 10, rect.bottom - 4), (tx, rect.bottom),
            ]
            borde = [
                (tx + TILE - 2, rect.y), (tx + TILE - 8, rect.y + 14),
                (tx + 10, rect.bottom - 4), (tx, rect.bottom),
            ]
            pygame.draw.polygon(surface, c_roca_oscura, pts_hombro)
            pygame.draw.lines(surface, color_marco, False, borde, 2)
            return True
        return False

    def _dibujar_formacion_techo(
        self, surface, rect, tx, fila, col, tiene_izq, tiene_der, paleta
    ):
        """Dibuja estalactitas y hombros inclinados en formaciones de techo."""
        color_cuerpo, color_marco = paleta["cuerpo"], paleta["marco"]
        if not tiene_izq and not tiene_der:
            self._dibujar_estalactita_techo(
                surface, rect, tx, fila, col, color_cuerpo, color_marco
            )
            return True
        return self._dibujar_hombro_techo(
            surface, rect, tx, tiene_izq, tiene_der, color_cuerpo, color_marco
        )

    def _dibujar_tile_piso_proc(
        self, surface, rect, tx, fila, col, vecinos, tema_efectivo, paleta
    ):
        tiene_arriba, tiene_abajo, tiene_izq, tiene_der = vecinos
        c_fill = paleta["piso_profundo"] if tiene_arriba else paleta["piso"]
        pygame.draw.rect(surface, c_fill, (tx, rect.y, TILE, TILE))
        if not tiene_arriba:
            if tema_efectivo == "camposanto":
                pygame.draw.rect(surface, paleta["arriba"], (tx, rect.y, TILE, 4))
                for bx in range(tx + 3, tx + TILE - 2, 6):
                    alt = 2 + ((bx * 11) % 5)
                    pygame.draw.line(surface, paleta["brizna"], (bx, rect.y), (bx, rect.y - alt), 1)
            pygame.draw.line(surface, MARFIL_XILOGRAFICO, (tx, rect.y + 1), (tx + TILE, rect.y + 1), 3)
            for cx in (tx + 8, tx + 24):
                pygame.draw.line(surface, TINTA_ABISMO, (cx, rect.y), (cx, rect.y + 3), 1)
            pygame.draw.line(surface, TINTA_ABISMO, (tx, rect.y + 4), (tx + TILE, rect.y + 4), 2)
            for hx in (tx + 4, tx + 12, tx + 20, tx + 28):
                pygame.draw.line(surface, (20, 18, 26), (hx, rect.y + 6), (hx, rect.y + 12), 1)
        elif (fila + col) % 2 == 0:
            pygame.draw.rect(
                surface, paleta["borde"], (tx + 3, rect.y + 4, TILE - 6, TILE - 8), 1, border_radius=2
            )
        if not tiene_abajo:
            pygame.draw.line(
                surface, paleta["borde"], (tx, rect.bottom - 1), (tx + TILE, rect.bottom - 1), 1
            )
        if not tiene_izq:
            pygame.draw.line(surface, paleta["borde"], (tx, rect.y), (tx, rect.bottom), 1)
        if not tiene_der:
            pygame.draw.line(
                surface, paleta["borde"], (tx + TILE - 1, rect.y), (tx + TILE - 1, rect.bottom), 1
            )

    def _dibujar_tile_bloque_proc(
        self, surface, rect, tx, fila, col, fila_rel, vecinos, tema_efectivo, paleta
    ):
        tiene_arriba, tiene_abajo, tiene_izq, tiene_der = vecinos
        color_cuerpo, color_marco = paleta["cuerpo"], paleta["marco"]
        pygame.draw.rect(surface, color_cuerpo, (tx, rect.y, TILE, TILE))
        if not tiene_arriba:
            pygame.draw.line(surface, MARFIL_XILOGRAFICO, (tx, rect.y), (tx + TILE, rect.y), 3)
            for cx in (tx + 8, tx + 24):
                pygame.draw.line(surface, TINTA_ABISMO, (cx, rect.y), (cx, rect.y + 3), 1)
            pygame.draw.line(surface, TINTA_ABISMO, (tx, rect.y + 3), (tx + TILE, rect.y + 3), 3)
            for hx in (tx + 6, tx + 14, tx + 22):
                pygame.draw.line(surface, (20, 18, 26), (hx, rect.y + 6), (hx, rect.y + 11), 1)
        if not tiene_abajo:
            pygame.draw.line(
                surface, color_marco, (tx, rect.bottom - 1), (tx + TILE, rect.bottom - 1), 2
            )
            if tema_efectivo == "cripta" and tiene_arriba and fila_rel > 0:
                salt_alt = 3 + (((col * 11) + fila) % 5)
                pts_pico = [
                    (tx + 11, rect.bottom - 1),
                    (tx + 21, rect.bottom - 1),
                    (tx + 16, rect.bottom + salt_alt),
                ]
                pygame.draw.polygon(surface, color_cuerpo, pts_pico)
                pygame.draw.polygon(surface, color_marco, pts_pico, 1)
        if not tiene_izq:
            pygame.draw.line(surface, color_marco, (tx, rect.y), (tx, rect.bottom), 2)
        if not tiene_der:
            pygame.draw.line(surface, color_marco, (tx + TILE - 1, rect.y), (tx + TILE - 1, rect.bottom), 2)
        else:
            pygame.draw.line(
                surface, color_marco, (tx + TILE - 1, rect.y + 2), (tx + TILE - 1, rect.bottom - 2), 1
            )

    def _dibujar_solido_proc(
        self, surface, rect, fila, col_inicio, num_cols, tema_efectivo, paleta
    ):
        fila_rel = fila % 18
        es_piso_nivel = fila_rel >= 15
        for c_idx in range(num_cols):
            col = col_inicio + c_idx
            tx = rect.x + c_idx * TILE
            vecinos = (
                self._tiene_solido(fila - 1, col),
                self._tiene_solido(fila + 1, col),
                self._tiene_solido(fila, col - 1),
                self._tiene_solido(fila, col + 1),
            )
            if es_piso_nivel:
                self._dibujar_tile_piso_proc(
                    surface, rect, tx, fila, col, vecinos, tema_efectivo, paleta
                )
                continue
            tiene_arriba, tiene_abajo, tiene_izq, tiene_der = vecinos
            if tiene_arriba and not tiene_abajo and (1 <= fila_rel <= 3):
                if self._dibujar_formacion_techo(
                    surface, rect, tx, fila, col, tiene_izq, tiene_der, paleta
                ):
                    continue
            self._dibujar_tile_bloque_proc(
                surface, rect, tx, fila, col, fila_rel, vecinos, tema_efectivo, paleta
            )

    def dibujar_solidos(self, surface, camara):
        estilo = config.resolver_estilo(getattr(config, "ESTILO_MUNDO", "AUTO"))
        for solido in self.solidos:
            if not camara.is_on_screen(solido):
                continue
            rect = camara.aplicar_rect(solido)
            fila = solido.y // TILE
            col_inicio = solido.x // TILE
            num_cols = solido.width // TILE
            tema_efectivo = self._tema_efectivo(fila)
            paleta = _PALETAS_SOLIDOS.get(tema_efectivo, _PALETAS_SOLIDOS["camposanto"])

            if estilo == "NES":
                self._dibujar_solido_nes(surface, rect, fila, col_inicio, num_cols, paleta)
            elif estilo == "SNES":
                self._dibujar_solido_snes(surface, rect, fila, col_inicio, num_cols, paleta)
            else:
                self._dibujar_solido_proc(surface, rect, fila, col_inicio, num_cols, tema_efectivo, paleta)

    def _dibujar_pendulo_poe(self, surface, rect, tiempo):
        angulo = math.sin(tiempo * 2.2 + rect.x * 0.04) * 0.42
        pivote_x = rect.centerx
        pivote_y = max(-20, rect.top - 62)
        extremo_x = int(pivote_x + math.sin(angulo) * 52)
        extremo_y = int(pivote_y + math.cos(angulo) * 52)
        pygame.draw.line(surface, (42, 38, 48), (pivote_x, pivote_y), (extremo_x, extremo_y), 2)
        pygame.draw.arc(
            surface, (160, 165, 180), (extremo_x - 13, extremo_y - 6, 26, 14), 3.14, 0.0, 2
        )
        pygame.draw.arc(
            surface, (225, 230, 240), (extremo_x - 11, extremo_y - 5, 22, 12), 3.14, 0.0, 1
        )
        pygame.draw.circle(surface, CARMESÍ_SANGRE, (extremo_x, extremo_y + 3), 2)

    def _dibujar_punta_pincho(self, surface, rect, x, ancho):
        cx = x + ancho // 2
        pts_sombra = [(x + 2, rect.bottom - 4), (cx + 1, rect.top + 2), (x + ancho - 1, rect.bottom - 4)]
        pts_acero = [(x + 1, rect.bottom - 4), (cx, rect.top + 1), (x + ancho - 2, rect.bottom - 4)]
        pygame.draw.polygon(surface, (48, 40, 38), pts_sombra)
        pygame.draw.polygon(surface, (112, 66, 50), pts_acero)
        pygame.draw.line(surface, (190, 185, 200), (cx, rect.top + 2), (cx - 1, rect.bottom - 6), 1)
        pygame.draw.line(surface, CARMESÍ_SANGRE, (cx, rect.top + 2), (cx, rect.top + 6), 1)
        pygame.draw.circle(surface, CARMESÍ_SANGRE, (cx, rect.bottom - 5), 2)

    def dibujar_peligros(self, surface, camara):
        tiempo = pygame.time.get_ticks() / 1000.0
        for peligro in self.peligros:
            if not camara.is_on_screen(peligro):
                continue
            rect = camara.aplicar_rect(peligro)
            cantidad = 3
            ancho = max(1, rect.width // cantidad)
            if rect.width >= 32 and rect.y > 60:
                self._dibujar_pendulo_poe(surface, rect, tiempo)
            pygame.draw.rect(
                surface, (38, 32, 36), (rect.x, rect.bottom - 5, rect.width, 5), border_radius=2
            )
            pygame.draw.ellipse(
                surface, CARMESÍ_SANGRE, (rect.x + rect.width // 2 - 8, rect.bottom - 3, 16, 4)
            )
            for i in range(cantidad):
                self._dibujar_punta_pincho(surface, rect, rect.x + i * ancho, ancho)

    def dibujar_meta(self, surface, camara):
        rect = camara.aplicar_rect(self.meta)
        x = rect.centerx
        alto = 58
        ancho = 42
        y = rect.bottom - alto

        # Halo místico suave del umbral (iluminación, no disco opaco)
        surface.blit(_obtener_halo_meta(), (x - 32, y + 22 - 32))
        pygame.draw.rect(surface, (7, 6, 10), (x - ancho // 2, y + 14, ancho, alto - 14))
        pygame.draw.circle(surface, (7, 6, 10), (x, y + 14), ancho // 2)

        pygame.draw.rect(surface, PIEDRA_OSCURA, (x - ancho // 2 - 4, y + 14, 4, alto - 14))
        pygame.draw.rect(surface, PIEDRA_OSCURA, (x + ancho // 2, y + 14, 4, alto - 14))
        pygame.draw.arc(
            surface,
            PIEDRA_OSCURA,
            (x - ancho // 2 - 4, y - 4, ancho + 8, 38),
            0.08,
            3.06,
            4,
        )
        pygame.draw.rect(surface, ORO, (x - 3, y + 18, 6, 26))
        pygame.draw.rect(surface, ORO, (x - 10, y + 29, 20, 4))
        pygame.draw.circle(surface, AMARILLO, (x, y + 12), 4)
        pygame.draw.circle(surface, (255, 235, 170), (x, y + 12), 2)
        pygame.draw.rect(surface, SANGRE, (x - ancho // 2, rect.bottom - 3, ancho, 3))
