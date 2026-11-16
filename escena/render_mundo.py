#---- Importamos librerias y configuracion ----#
import math

import pygame

from escena.fondos import _obtener_luz_calida, _obtener_luz_perforacion


#---- Mixin de renderizado de mundo y postprocesado ----#
class RenderMundoMixin:
    """Metodos de renderizado del mundo, iluminacion, shaders y debug visual."""

    def _aplicar_bloom(self, origen, destino, intensidad=0.12):
        pw, ph = destino.get_size()
        sw, sh = max(1, pw // 4), max(1, ph // 4)
        mini = pygame.transform.smoothscale(origen, (sw, sh))
        bloom = pygame.transform.smoothscale(mini, (pw, ph))
        bloom.set_alpha(int(255 * intensidad))
        destino.blit(bloom, (0, 0), special_flags=pygame.BLEND_RGB_ADD)

    def _dibujar_penumbra_mundo(self, destino):
        self.mascara_penumbra.fill((8, 7, 12, 38))
        if self.jugador:
            fx = int(self.jugador.rect.centerx + self.jugador.direccion * 11 - self.camara.x)
            fy = int(self.jugador.rect.y + 19 - self.camara.y)
            self.mascara_penumbra.blit(
                _obtener_luz_perforacion(95),
                (fx - 95, fy - 95),
                special_flags=pygame.BLEND_RGBA_SUB,
            )
        for cp in self.nivel.checkpoints:
            if not self.camara.is_on_screen(cp.rect):
                continue
            cpx = int(cp.rect.centerx - self.camara.x)
            cpy = int(cp.rect.centery - self.camara.y)
            radio_cp = 78 if cp.activo else 36
            self.mascara_penumbra.blit(
                _obtener_luz_perforacion(radio_cp),
                (cpx - radio_cp, cpy - radio_cp),
                special_flags=pygame.BLEND_RGBA_SUB,
            )
        destino.blit(self.mascara_penumbra, (0, 0))

    def _dibujar_luces_calidas_mundo(self, destino, calidad):
        if self.jugador:
            fx = int(self.jugador.rect.centerx + self.jugador.direccion * 11 - self.camara.x)
            fy = int(self.jugador.rect.y + 19 - self.camara.y)
            if getattr(self.jugador, "rango_ataque_mejorado", False):
                color_luz = (195, 85, 250)
            elif self.jugador.dash_listo():
                color_luz = (92, 220, 200)
            else:
                color_luz = (240, 196, 90)
            factor_base = 0.12 if getattr(self.jugador, "rango_ataque_mejorado", False) else 0.09
            factor_luz = factor_base if calidad == 0 else factor_base * 0.65
            radio_luz = 90 if calidad == 0 else 70
            luz_add = _obtener_luz_calida(radio_luz, color_luz, factor_luz)
            destino.blit(
                luz_add, (fx - radio_luz, fy - radio_luz), special_flags=pygame.BLEND_RGB_ADD
            )

        for cp in self.nivel.checkpoints:
            if not self.camara.is_on_screen(cp.rect):
                continue
            cpx = int(cp.rect.centerx - self.camara.x)
            cpy = int(cp.rect.centery - self.camara.y)
            if cp.activo:
                colores_tier = {1: (90, 200, 255), 2: (120, 235, 255), 3: (218, 178, 86)}
                col_cp = colores_tier.get(cp.tier, (90, 200, 255))
                radio_add = 80 if calidad == 0 else 64
                factor_add = 0.16 if calidad == 0 else 0.11
                luz = _obtener_luz_calida(radio_add, col_cp, factor_add)
            else:
                radio_add = 40
                luz = _obtener_luz_calida(40, (70, 185, 255), 0.07)
            destino.blit(
                luz, (cpx - radio_add, cpy - radio_add), special_flags=pygame.BLEND_RGB_ADD
            )

    def _dibujar_mundo_y_luz(self, destino):
        """Renderiza nivel, entidades, partículas y máscara de penumbra en el lienzo virtual."""
        tiempo_s = pygame.time.get_ticks() / 1000
        self.dibujar_fondo(destino)
        self.nivel.dibujar(destino, self.camara)

        for enemigo in self.nivel.enemigos:
            enemigo.dibujar(destino, self.camara, tiempo_s)
        for onda in self.ondas_jefe:
            onda.dibujar(destino, self.camara, tiempo_s)
        if self.jefe is not None:
            self.jefe.dibujar(destino, self.camara, tiempo_s)

        self.jugador.dibujar(
            destino,
            self.camara,
            tiempo_s,
            pose=self.jugador.pose_actual(),
            con_pala=self.jugador.tiene_pala,
        )
        self.particulas.dibujar(destino, self.camara)
        for p in getattr(self, "particulas_bioma", []):
            p.dibujar(destino)

        calidad = getattr(self, "config_calidad_idx", 0)
        if calidad != 2:
            self._dibujar_penumbra_mundo(destino)
        if calidad in (0, 1):
            self._dibujar_luces_calidas_mundo(destino, calidad)
        if getattr(self, "debug_colisiones", False):
            self.dibujar_debug_colisiones(destino, self.camara)

    def _dibujar_destello_manto(self, pw, ph):
        alfa_manto = int(min(180, (self.destello_manto / 0.35) * 180))
        if getattr(self, "reducir_movimiento", False):
            alfa_manto = min(40, int(alfa_manto * 0.3))
        destello = getattr(self, "_superficie_destello_manto", None)
        if destello is None or destello.get_size() != (pw, ph):
            self._superficie_destello_manto = pygame.Surface((pw, ph), pygame.SRCALPHA)
        self._superficie_destello_manto.fill((0, 0, 0, 0))
        for step in range(12):
            a_step = int(alfa_manto * (1.0 - step / 12.0))
            pygame.draw.rect(
                self._superficie_destello_manto,
                (110, 215, 255, a_step),
                (step * 2, step * 2, pw - step * 4, ph - step * 4),
                2,
            )
        self.pantalla.blit(
            self._superficie_destello_manto, (0, 0), special_flags=pygame.BLEND_RGBA_ADD
        )

    def _aplicar_postprocesado_pantalla(self, pw, ph):
        """Aplica filtros ópticos de bloom, CRT, viñeta de salud crítica y destello de manto."""
        shader_modo = getattr(self, "config_shader_idx", 0)
        calidad_modo = getattr(self, "config_calidad_idx", 0)

        if shader_modo in (0, 1) and calidad_modo != 2:
            self._aplicar_bloom(self.pantalla, self.pantalla, intensidad=0.12)

        if shader_modo == 0 and calidad_modo != 2:
            if (
                not hasattr(self, "_superficie_scanlines")
                or self._superficie_scanlines.get_size() != (pw, ph)
            ):
                self._superficie_scanlines = self._crear_scanlines_goticas(pw, ph)
            self.pantalla.blit(self._superficie_scanlines, (0, 0))

        if calidad_modo != 2:
            if self.vineta.get_size() != (pw, ph):
                self.vineta = pygame.transform.smoothscale(self.vineta, (pw, ph))
            self.pantalla.blit(self.vineta, (0, 0))

        if (
            calidad_modo != 2
            and self.jugador
            and self.jugador.vidas == 1
            and not self.reducir_movimiento
        ):
            if self.vineta_carmesi.get_size() != (pw, ph):
                self.vineta_carmesi = pygame.transform.smoothscale(
                    self.vineta_carmesi, (pw, ph)
                )
            ciclo = (self.timer_corazon / (1.0 / 1.2)) * math.pi
            self.vineta_carmesi.set_alpha(int(30 + 45 * math.sin(ciclo)))
            self.pantalla.blit(self.vineta_carmesi, (0, 0))

        if getattr(self, "destello_manto", 0.0) > 0:
            self._dibujar_destello_manto(pw, ph)

    def _dibujar_debug_entidades(self, destino, camara):
        col_hurt = (255, 165, 30)
        grupos = (
            self.nivel.enemigos,
            getattr(self.nivel, "enemigos_melee", ()),
            self.nivel.cuervos,
            self.nivel.polillas,
            self.nivel.aranias,
            getattr(self.nivel, "minijefes", ()),
        )
        for grupo in grupos:
            for ent in grupo:
                if getattr(ent, "vivo", True) and camara.is_on_screen(ent.rect):
                    pygame.draw.rect(destino, col_hurt, camara.aplicar_rect(ent.rect), 1)
        if self.jefe and self.jefe.vivo and camara.is_on_screen(self.jefe.rect):
            pygame.draw.rect(destino, col_hurt, camara.aplicar_rect(self.jefe.rect), 2)
        for onda in self.ondas_jefe:
            if getattr(onda, "vivo", True) and camara.is_on_screen(onda.rect):
                pygame.draw.rect(destino, (255, 120, 20), camara.aplicar_rect(onda.rect), 1)

    #---- Visualizador de depuracion F3 ----#
    def dibujar_debug_colisiones(self, destino, camara):
        """Visualizador F3 de Hitbox / Hurtbox / Peligros para inspección en vivo."""
        if self.nivel and hasattr(self.nivel, "peligros"):
            for pel in self.nivel.peligros:
                if camara.is_on_screen(pel):
                    pygame.draw.rect(destino, (200, 80, 255), camara.aplicar_rect(pel), 1)

        if self.nivel:
            self._dibujar_debug_entidades(destino, camara)
            for em in getattr(self.nivel, "enemigos_melee", []):
                esp = em.rect_espada() if hasattr(em, "rect_espada") else None
                if esp is not None and camara.is_on_screen(esp):
                    pygame.draw.rect(destino, (255, 65, 95), camara.aplicar_rect(esp), 2)

        if self.jugador and camara.is_on_screen(self.jugador.rect):
            pygame.draw.rect(
                destino, (40, 255, 120), camara.aplicar_rect(self.jugador.rect), 1
            )
        if self.jefe and self.jefe.vivo and self.jefe.fase >= 3 and camara.is_on_screen(self.jefe.rect):
            rect_aplast = camara.aplicar_rect(self.jefe.rect_aplastamiento())
            pygame.draw.rect(destino, (195, 90, 255), rect_aplast, 1)
        if self.jugador and self.jugador.ataque_tiempo > 0:
            r_atk = camara.aplicar_rect(self.jugador.rect_ataque())
            col_atk = (255, 40, 60)
            pygame.draw.rect(destino, col_atk, r_atk, 2)
            pygame.draw.line(destino, col_atk, r_atk.topleft, r_atk.bottomright, 1)
            pygame.draw.line(destino, col_atk, r_atk.topright, r_atk.bottomleft, 1)
