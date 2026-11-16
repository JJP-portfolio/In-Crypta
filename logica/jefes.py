#---- Importamos librerias y configuracion ----#
import pygame

from config import (
    AMARILLO,
    BLANCO,
    CARMESÍ_SANGRE,
    CREMA,
    DASH_USOS_AIRE,
    HUESO,
    JEFE_ONDA_VELOCIDAD,
    ORO,
    ORO_LITÚRGICO,
    PIEDRA_FRIA,
    REBOTE_ENEMIGO,
    SALITRE_CRIPTA,
    TILE,
)
from entidades import OndaCustodio
from escena.constantes import ALMAS_MINIJEFE


#---- Mixin de jefes y minijefes ----#
class JefesMixin:
    """Metodos de logica del Custodio, fases de jefe y minijefes Carcelero."""

    def _golpear_minijefes(self, golpe):
        """Resuelve el choque del golpe frontal contra el blindaje del Carcelero."""
        for mj in getattr(self.nivel, "minijefes", []):
            if not mj.vivo or not golpe.colliderect(mj.rect):
                continue
            if hasattr(mj, "tiempo_flash"):
                mj.tiempo_flash = 0.04
            inter = golpe.clip(mj.rect)
            self.particulas.hit_spark(inter.centerx, inter.centery, self.jugador.direccion, self.jugador.rango_ataque_mejorado)
            self.jugador.ataque_golpeado = True
            if mj.recibir_golpe_pala():
                self.jugador.dash_usos_aire = DASH_USOS_AIRE
                self.jugador.dash_cooldown = 0.0
                self.audio.reproducir("pala")
                self.particulas.pala(mj.rect.centerx, mj.rect.centery)
                self.camara.sacudir(6.0, 0.14, dir_x=self.jugador.direccion, dir_y=0.0)
                self.hitstop = 0.08
                self.flash = 0.06
                self.flash_color = AMARILLO
                self._comprobar_muerte_minijefe(mj)
            else:
                self._rebote_minijefe_guardia(mj)
                self.jugador.vx = -self.jugador.direccion * 150.0
                self.hud.mostrar_mensaje("¡BLINDAJE FRONTAL! Usa las campanas y véncelo rebotando desde arriba", 2, 2.6)
            return True
        return False

    def _anunciar_cambio_fase3(self, jefe):
        """Activa el clímax visual, musical y de aviso al entrar a Fase III (Sepulcro)."""
        jefe.cambio_fase3_recien = False
        self.audio.reproducir("jefe_fase")
        self.audio.reproducir_musica("custodio_f3", bucle=True, fade_ms=350)
        self.camara.sacudir(13.0, 0.30, dir_x=0.0, dir_y=1.0)
        self.aviso_jefe = 3.2
        self.particulas.emitir(
            jefe.rect.centerx, jefe.rect.centery, 28,
            ((165, 70, 235), CARMESÍ_SANGRE, ORO, BLANCO), 250, 0.85, 5, 320,
        )
        self.hud.mostrar_mensaje(
            "¡FASE III · EL SEPULCRO! · Esquiva su salto y golpéalo al aterrizar [J/Z] para hundir el piso",
            5, 4.5,
        )

    def _procesar_victoria_jefe(self, jefe):
        """Abre las compuertas y celebra la caída definitiva del Custodio (una sola vez)."""
        if getattr(self, "_jefe_victoria_procesada", False):
            return
        self._jefe_victoria_procesada = True
        for compuerta in getattr(self.nivel, "compuertas_arena", []):
            compuerta.abrir()
        if getattr(self.nivel, "compuertas_arena", None):
            self.audio.reproducir("compuerta")
        self.audio.detener_dron()
        self.audio.reproducir("meta")
        self.particulas.meta(jefe.rect.centerx, jefe.rect.centery)
        self.ondas_jefe = []
        self.aviso_jefe = 3.2
        self.flash = 0.22
        self.hud.mostrar_mensaje("¡EL CUSTODIO CAYÓ EN SU PROPIA TUMBA! · Las compuertas se abren", 5, 4.2)

    def _cerrar_compuertas_arena_jefe(self, jefe):
        compuertas = getattr(self.nivel, "compuertas_arena", [])
        if not (jefe.vivo and compuertas and not all(c.cerrada for c in compuertas)):
            return
        arena_izq = min(c.rect.right for c in compuertas)
        arena_der = max(c.rect.left for c in compuertas)
        en_rango_x = (arena_izq + 14) <= self.jugador.rect.centerx <= (arena_der - 14)
        en_rango_y = abs(self.jugador.rect.centery - jefe.rect.centery) < 6 * TILE
        if not (en_rango_x and en_rango_y):
            return
        for comp in compuertas:
            comp.cerrar()
        self.audio.reproducir("compuerta")
        self.camara.sacudir(6.0, 0.16, dir_x=0.0, dir_y=1.0)
        self.audio.reproducir_musica("custodio_f1", bucle=True, fade_ms=600)
        self.hud.mostrar_mensaje("¡LAS COMPUERTAS SE CIERRAN!", 3, 2.8)

    def _procesar_embate_jefe(self, jefe, cerca_jefe):
        # Silencia temporalmente las campanas sobre el Custodio para evitar campeo aereo.
        zona_silencio = pygame.Rect(
            jefe.rect.centerx - 48,
            jefe.rect.top - int(4.5 * TILE),
            96,
            int(5.0 * TILE),
        )
        for inc in getattr(self.nivel, "incensarios", []):
            if zona_silencio.colliderect(inc.rect):
                inc.cooldown = max(inc.cooldown, 1.2)
                inc.tiempo_repique = max(inc.tiempo_repique, 0.45)
        if cerca_jefe:
            self.audio.reproducir("onda")
            self.camara.sacudir(7.5, 0.18, dir_x=0.0, dir_y=-1.0)
            self.particulas.emitir(
                jefe.rect.centerx, jefe.rect.top, 18, (ORO, HUESO, CREMA, BLANCO), 240, 0.50, 4, -180
            )

    def _emitir_eventos_jefe(self, jefe, cerca_jefe):
        if getattr(jefe, "cambio_fase3_recien", False):
            self._anunciar_cambio_fase3(jefe)
        if getattr(jefe, "aplasto_suelo_recien", False):
            self._romper_criptas_bajo_jefe(jefe)
        if getattr(jefe, "en_abismo_recien", False):
            self.audio.reproducir("jefe_caida")
            self.camara.sacudir(7.0, 0.25)
        if jefe.aviso_recien and cerca_jefe:
            self.audio.reproducir("jefe_aviso")
            self.camara.sacudir(3.0, 0.12)
        if getattr(jefe, "embate_recien", False):
            self._procesar_embate_jefe(jefe, cerca_jefe)

    def _generar_ondas_jefe(self, jefe, cerca_jefe):
        velocidad = JEFE_ONDA_VELOCIDAD + (jefe.fase - 1) * 45
        y_onda = (
            (int(jefe.y_suelo) + jefe.rect.height) if jefe.fase >= 3 else jefe.rect.bottom
        )
        for direccion in (-1, 1):
            self.ondas_jefe.append(
                OndaCustodio(jefe.rect.centerx + direccion * 24, y_onda, direccion, velocidad)
            )
        if jefe.fase >= 2:
            for direccion in (-1, 1):
                self.ondas_jefe.append(
                    OndaCustodio(
                        jefe.rect.centerx + direccion * 48,
                        y_onda,
                        direccion,
                        velocidad * 1.35,
                    )
                )
        if cerca_jefe:
            self.audio.reproducir("onda")
            self.camara.sacudir(8.0, 0.20)
            self.particulas.emitir(
                jefe.rect.centerx,
                jefe.rect.bottom - 4,
                16,
                (HUESO, CREMA, (126, 100, 68)),
                190,
                0.55,
                5,
                620,
            )

    def _actualizar_ondas_jefe(self, dt):
        for onda in self.ondas_jefe:
            onda.actualizar(dt)
            if (
                onda.viva
                and self.jugador.invulnerable <= 0
                and onda.rect.colliderect(self.jugador.rect)
            ):
                self.perder_vida(causa="Onda de choque del Custodio")
                return True
        self.ondas_jefe = [onda for onda in self.ondas_jefe if onda.viva]
        return False

    def _resolver_contacto_jefe(self, jefe, dt):
        tol_jefe = max(32, self._tolerancia_pisoton_frame(dt) + 12)
        if not self.jugador.rect.colliderect(jefe.rect):
            return False
        viene_desde_arriba = (
            self.jugador.vy > 0 and self.jugador.rect.bottom <= jefe.rect.top + tol_jefe
        )
        if viene_desde_arriba:
            self.jugador.rect.bottom = jefe.rect.top
            self.jugador.y = float(self.jugador.rect.y)
            self.jugador.en_suelo = False
            self.jugador.invulnerable = 0.40
            self.dañar_jefe_pisaton()
            return False
        if self.jugador.invulnerable <= 0:
            self.perder_vida(causa="Poder abrumador del Custodio")
            return True
        return False

    def _activar_checkpoint_antesala_jefe(self, jefe):
        if self.punto_reintento is not None:
            return
        if abs(self.jugador.rect.centery - jefe.rect.centery) >= 5 * TILE:
            return
        limite = jefe.minimo_x - 3 * TILE
        en_umbral = (
            self.jugador.rect.right > limite
            and abs(self.jugador.rect.centerx - jefe.rect.centerx) < 26 * TILE
        )
        if not en_umbral:
            return
        y_piso_jefe = jefe.rect.bottom - self.jugador.rect.height
        self.punto_reintento = (limite, y_piso_jefe)
        self.texto_ayuda = "PUNTO DE CONTROL · LA ANTESALA DEL CUSTODIO"
        self.mostrar_ayuda = 4.5
        self.hud.mostrar_mensaje("PUNTO DE CONTROL · La antesala del Custodio del Osario", 1, 3.5)
        self.audio.reproducir("ui")
        self.audio.reproducir_musica("custodio_f1", bucle=True, fade_ms=600)

    def actualizar_jefe(self, dt):
        """Actualiza al Custodio, sus ataques de fase y la colision con el jugador."""
        if self.jefe is None:
            return False
        jefe = self.jefe
        solidos_cripta = self.nivel.solidos + [
            b.rect for b in getattr(self.nivel, "bloques_cripta", []) if not b.roto
        ]
        jefe.actualizar(dt, self.jugador, solidos_cripta=solidos_cripta)
        self._cerrar_compuertas_arena_jefe(jefe)
        cerca_jefe = (
            abs(self.jugador.rect.centerx - jefe.rect.centerx) < 22 * TILE
            and abs(self.jugador.rect.centery - jefe.rect.centery) < 10 * TILE
        )
        self._emitir_eventos_jefe(jefe, cerca_jefe)

        rect_emb = jefe.rect_embate() if hasattr(jefe, "rect_embate") else None
        if (
            rect_emb is not None
            and self.jugador.invulnerable <= 0
            and rect_emb.colliderect(self.jugador.rect)
        ):
            self.perder_vida(causa="Embate ascendente del Custodio")
            return True

        if jefe.ondas_recien:
            self._generar_ondas_jefe(jefe, cerca_jefe)
        if self._actualizar_ondas_jefe(dt):
            return True
        if not jefe.vivo:
            self._procesar_victoria_jefe(jefe)
            return False
        if self._resolver_contacto_jefe(jefe, dt):
            return True
        self._activar_checkpoint_antesala_jefe(jefe)
        return False

    def _rebotar_jefe_coraza(self):
        self.jugador.vx = -self.jugador.direccion * 240
        self.jugador.vy = -180
        self.jugador.retroceso_tiempo = 0.20
        self.jugador.invulnerable = 0.25
        self.camara.sacudir(5.0, 0.12, dir_x=-self.jugador.direccion, dir_y=0.0)
        self.flash = 0.08
        self.flash_color = (200, 50, 50)
        self.audio.reproducir("rebote_pala")
        self.particulas.chispas_rebote(
            self.jefe.rect.centerx - self.jugador.direccion * 16,
            self.jefe.rect.centery,
            -self.jugador.direccion,
        )

    def _evaluar_soporte_f3_jefe(self, jefe):
        franja_central = jefe.rect_soporte_central_f3()
        soportes_restantes = [
            b.rect
            for b in getattr(self.nivel, "bloques_cripta", [])
            if not b.roto and franja_central.colliderect(b.rect)
        ] + [s for s in getattr(self.nivel, "solidos", []) if franja_central.colliderect(s)]
        if soportes_restantes:
            nuevo_top = min(s.top for s in soportes_restantes)
            jefe.y = float(nuevo_top - jefe.rect.height)
            jefe.rect.y = round(jefe.y)
            if getattr(jefe, "quiebre_sismico_recien", False):
                self.hud.mostrar_mensaje(
                    "¡QUIEBRE SÍSMICO! · ¡Hundiste una capa más del sepulcro bajo el Custodio!",
                    4,
                    2.8,
                    forzar=True,
                )
            return
        jefe.estado = "cayendo_abismo"
        jefe.en_abismo_recien = True
        jefe.vy = max(jefe.vy, 280.0)
        if getattr(jefe, "quiebre_sismico_recien", False):
            self.hud.mostrar_mensaje(
                "¡QUIEBRE SÍSMICO DEFINITIVO! · ¡El sepulcro se abre bajo el Custodio!",
                5,
                3.5,
                forzar=True,
            )

    def _romper_criptas_bajo_jefe(self, jefe):
        """Rompe 1 capa de cripta ('=') bajo el Custodio y desciende al siguiente nivel."""
        area_aplast = jefe.rect_aplastamiento()
        rotos = 0
        for bloque in getattr(self.nivel, "bloques_cripta", []):
            if not bloque.roto and bloque.rect.colliderect(area_aplast) and bloque.romper():
                rotos += 1
                self.particulas.emitir(
                    bloque.rect.centerx,
                    bloque.rect.centery,
                    10,
                    (PIEDRA_FRIA, SALITRE_CRIPTA, HUESO, (145, 75, 175)),
                    170,
                    0.48,
                    4,
                    480,
                )
        if rotos > 0:
            self.audio.reproducir("cripta_romper")
            self.camara.sacudir(9.5, 0.22, dir_x=0.0, dir_y=1.0)
        self._evaluar_soporte_f3_jefe(jefe)
        return rotos

    def dañar_jefe_pala(self):
        """Golpe de pala/guadaña: daña en Fase 1 y Fase 2 (en recuperación); en Fase 3 provoca Quiebre Sísmico al aterrizar."""
        if self.jefe is None or not self.jefe.vivo:
            return False
        rango_mejorado = getattr(self.jugador, "rango_ataque_mejorado", False)
        if self.jefe.fase >= 3:
            if self.jefe.recibir_quiebre_sismico_f3(rango_mejorado=rango_mejorado):
                self._romper_criptas_bajo_jefe(self.jefe)
                self.jugador.dash_usos_aire = DASH_USOS_AIRE
                self.jugador.dash_cooldown = 0.0
                self.audio.reproducir("pala")
                self.particulas.pala(self.jefe.rect.centerx, self.jefe.rect.centery)
                dir_empuje = 1 if self.jugador.rect.centerx >= self.jefe.rect.centerx else -1
                self.jugador.vx = dir_empuje * 240.0
                self.jugador.retroceso_tiempo = 0.16
                self.hitstop = 0.08
                self.flash = 0.10
                self.flash_color = (185, 95, 255)
                return True
            self._rebotar_jefe_coraza()
            self.hud.mostrar_mensaje("¡GUARDIA SÍSMICA! · Esquiva su salto y golpéalo al aterrizar [J/Z] para hundir el piso", 4, 2.5, forzar=True)
            return False
        if self.jefe.fase == 2 and not rango_mejorado:
            self._rebotar_jefe_coraza()
            self.hud.mostrar_mensaje("¡CORAZA ESPECTRAL! · Necesitas la Guadaña Consagrada del piso superior", 4, 2.5, forzar=True)
            return False
        if not self.jefe.recibir_golpe_pala(rango_mejorado=rango_mejorado):
            self._rebotar_jefe_coraza()
            if self.jefe.fase == 2:
                self.hud.mostrar_mensaje("¡GUARDIA CERRADA! · Espera a que termine su ataque y golpéalo con tu Guadaña [J/Z]", 4, 2.5, forzar=True)
            return False
        res = self._aplicar_golpe_jefe()
        # Ráfaga de rechazo al dañar con pala frontal
        dir_empuje = 1 if self.jugador.rect.centerx >= self.jefe.rect.centerx else -1
        self.jugador.vx = dir_empuje * 220.0
        self.jugador.retroceso_tiempo = 0.16
        return res

    def _impulsar_rebote_lateral_jefe(self, dir_empuje, vy=-220.0, recargar_dash=True):
        self.jugador.vx = dir_empuje * 280.0
        self.jugador.vy = vy
        self.jugador.retroceso_tiempo = 0.22
        if recargar_dash:
            self.jugador.dash_usos_aire = DASH_USOS_AIRE
            self.jugador.dash_cooldown = 0.0

    def _rebotar_pisoton_sin_dano(
        self, dir_empuje, fuerza_sacudida, mensaje=None, recargar_dash=False
    ):
        self._impulsar_rebote_lateral_jefe(dir_empuje, recargar_dash=recargar_dash)
        self.audio.reproducir("rebote_pala")
        self.particulas.chispas_rebote(self.jefe.rect.centerx, self.jefe.rect.top, dir_empuje)
        self.camara.sacudir(fuerza_sacudida, 0.12 if fuerza_sacudida >= 5 else 0.10, dir_x=dir_empuje, dir_y=0.0)
        if mensaje:
            self.hud.mostrar_mensaje(mensaje, 4, 2.5, forzar=True)

    def _pisoton_fase3_jefe(self, dir_empuje, rango_mejorado):
        self._impulsar_rebote_lateral_jefe(dir_empuje, vy=-240.0, recargar_dash=True)
        if self.jefe.recibir_quiebre_sismico_f3(rango_mejorado=rango_mejorado):
            self._romper_criptas_bajo_jefe(self.jefe)
            self.audio.reproducir("stomp")
            self.particulas.stomp(self.jefe.rect.centerx, self.jefe.rect.top)
            self.hitstop = 0.08
            self.flash = 0.10
            self.flash_color = (185, 95, 255)
            return True
        self._rebotar_pisoton_sin_dano(
            dir_empuje,
            5.0,
            "¡GUARDIA SÍSMICA! · Esquiva su salto y golpéalo al aterrizar [J/Z] para hundir el piso",
            recargar_dash=True,
        )
        return False

    def dañar_jefe_pisaton(self):
        """Pisotón: daña en Fase 1 y Fase 2; en Fase 3 provoca Quiebre Sísmico al aterrizar."""
        if self.jefe is None or not self.jefe.vivo:
            return False
        dir_empuje = 1 if self.jugador.rect.centerx >= self.jefe.rect.centerx else -1
        rango_mejorado = getattr(self.jugador, "rango_ataque_mejorado", False)
        if self.jefe.fase >= 3:
            return self._pisoton_fase3_jefe(dir_empuje, rango_mejorado)
        if self.jefe.fase == 2 and not rango_mejorado:
            self._rebotar_pisoton_sin_dano(
                dir_empuje,
                5.0,
                "¡CORAZA ESPECTRAL! · Necesitas la Guadaña Consagrada del piso superior",
                recargar_dash=True,
            )
            return False
        if not self.jefe.recibir_pisaton(rango_mejorado=rango_mejorado):
            msg = (
                "¡GUARDIA CERRADA! · Espera a que termine su ataque y golpéalo con tu Guadaña [J/Z]"
                if self.jefe.fase == 2
                else None
            )
            self._rebotar_pisoton_sin_dano(dir_empuje, 4.0, msg)
            return False

        res = self._aplicar_golpe_jefe()
        self.audio.reproducir("stomp")
        self.particulas.stomp(self.jefe.rect.centerx, self.jefe.rect.top)
        colores_rep = (CARMESÍ_SANGRE, ORO_LITÚRGICO, BLANCO)
        self.particulas.emitir(
            self.jefe.rect.centerx, self.jefe.rect.top, 16, colores_rep, 200, 0.4, 3.5, 350
        )
        self.jugador.vx = dir_empuje * 340.0
        self.jugador.vy = -260.0
        self.jugador.retroceso_tiempo = 0.25
        self.camara.sacudir(9.0, 0.20, dir_x=dir_empuje, dir_y=0.5)
        return res

    def _anunciar_cambio_fase2(self):
        self.audio.reproducir("jefe_fase")
        self.audio.reproducir_musica("custodio_f2", bucle=True, fade_ms=400)
        self.camara.sacudir(11.0, 0.26, dir_x=0.0, dir_y=1.0)
        self.particulas.emitir(
            self.jefe.rect.centerx,
            self.jefe.rect.centery,
            24,
            (ORO, AMARILLO, HUESO),
            230,
            0.8,
            5,
            280,
        )
        self.aviso_jefe = 2.0
        if getattr(self.jugador, "rango_ataque_mejorado", False):
            msg = (
                "¡FASE II · CORAZA CARMESÍ! · Espera a que termine su ataque y golpéalo "
                "con tu Guadaña [J/Z] o Pisotón"
            )
        else:
            msg = (
                "¡FASE II · CORAZA CARMESÍ! · Sin la Guadaña Consagrada del piso superior "
                "no podrás herirlo"
            )
        self.hud.mostrar_mensaje(msg, 4, 4.5)

    def _aplicar_golpe_jefe(self):
        self.jugador.dash_usos_aire = DASH_USOS_AIRE
        self.jugador.dash_cooldown = 0.0
        self.audio.reproducir("pala")
        self.particulas.pala(self.jefe.rect.centerx, self.jefe.rect.centery)
        self.camara.sacudir(8.0, 0.18, dir_x=self.jugador.direccion, dir_y=0.0)
        self.hitstop = 0.08
        self.flash = 0.10
        self.flash_color = AMARILLO

        if not self.jefe.vivo:
            self._procesar_victoria_jefe(self.jefe)
        elif getattr(self.jefe, "estado", "") == "cambio_f3":
            self._anunciar_cambio_fase3(self.jefe)
        elif self.jefe.estado == "cambio":
            self._anunciar_cambio_fase2()
        return True

    def _preparar_muros_minijefe(self, muros_mj):
        if muros_mj and all(getattr(m, "usado_ciclo", False) for m in muros_mj):
            for m in muros_mj:
                m.usado_ciclo = False
                m.enfriamiento = min(getattr(m, "enfriamiento", 0.0), 0.5)
        for muro in muros_mj:
            if getattr(muro, "recien_armado", False) and abs(muro.x - self.jugador.rect.centerx) < 520:
                self.audio.reproducir("compuerta")
                self.camara.sacudir(2.5, 0.08)

    def _activar_muro_telegrafia_mj(self, mj, muros_mj):
        self.audio.reproducir("jefe_aviso")
        if not muros_mj:
            return
        disponibles = [m for m in muros_mj if getattr(m, "puede_activarse", lambda: True)()]
        if not disponibles:
            for m in muros_mj:
                m.usado_ciclo = False
                m.enfriamiento = 0.0
            disponibles = [m for m in muros_mj if m.estado == "oculto"]

        frente = [
            m
            for m in disponibles
            if 64 <= (m.x + m.ancho // 2 - mj.rect.centerx) * mj.direccion <= 460
        ]
        if not frente:
            opuestos = [
                m
                for m in disponibles
                if 64 <= (m.x + m.ancho // 2 - mj.rect.centerx) * (-mj.direccion) <= 460
            ]
            if opuestos:
                mj.direccion = -mj.direccion
                frente = opuestos
        if not frente:
            return
        frente.sort(key=lambda m: abs(m.x + m.ancho // 2 - mj.rect.centerx))
        elegido = frente[0]
        for m in muros_mj:
            if m is not elegido and m.estado in ("aviso", "armado"):
                m.retraer()
        elegido.activar(duracion_aviso=0.16, duracion_armado=1.5)

    def _resolver_contacto_minijefe(self, mj):
        if self.jugador.tiene_pala and self._viene_desde_arriba(mj.rect):
            if mj.recibir_pisaton():
                self._rebote_pisoton(mj.rect, fuerza_sacudida=7.0)
                self._comprobar_muerte_minijefe(mj)
            else:
                self.jugador.rect.bottom = mj.rect.top
                self.jugador.y = float(self.jugador.rect.y)
                self.jugador.vy = -REBOTE_ENEMIGO * 0.85
                self.jugador.en_suelo = False
                self.jugador.dash_usos_aire = DASH_USOS_AIRE
                self.jugador.dash_cooldown = 0.0
                self._rebote_minijefe_guardia(mj)
            return False
        if self.jugador.invulnerable <= 0:
            self.perder_vida(causa="Ataque del Carcelero del Osario")
            return True
        return False

    def actualizar_minijefes(self, dt):
        """Actualiza Carceleros del Osario, muros telegrafiados y contacto con el jugador."""
        muros_mj = getattr(self.nivel, "muros_minijefe", [])
        self._preparar_muros_minijefe(muros_mj)
        for mj in getattr(self.nivel, "minijefes", []):
            mj.actualizar(dt, self.jugador, muros=muros_mj if muros_mj else None)
            if not mj.vivo:
                continue
            if getattr(mj, "activado", False) and abs(mj.rect.centerx - self.jugador.rect.centerx) < 480:
                self.audio.reproducir_musica("carcelero", bucle=True, fade_ms=600)
            if mj.estado in ("cansado", "recuperacion") and muros_mj:
                for m in muros_mj:
                    if m.estado == "armado":
                        m.retraer()
            if mj.aviso_recien:
                self._activar_muro_telegrafia_mj(mj, muros_mj)
            if getattr(mj, "choque_recien", False) and abs(mj.rect.centerx - self.jugador.rect.centerx) < 520:
                self.audio.reproducir("compuerta")
                self.audio.reproducir("stomp")
                self.camara.sacudir(6.5, 0.16)
                self.hitstop = max(self.hitstop, 0.05)
                px_ch, py_ch = getattr(mj, "punto_choque", None) or (
                    mj.rect.centerx + mj.direccion * 16,
                    mj.rect.bottom - 12,
                )
                self.particulas.chispas_rebote(px_ch, py_ch, -mj.direccion)
            if self.jugador.rect.colliderect(mj.rect) and self._resolver_contacto_minijefe(mj):
                return

    def _rebote_minijefe_guardia(self, mj):
        """Feedback discernible: golpe fuera de la ventana vulnerable del Carcelero."""
        self.audio.reproducir("rebote_pala")
        self.particulas.chispas_rebote(mj.rect.centerx, mj.rect.centery, -self.jugador.direccion)
        self.camara.sacudir(3.0, 0.08)

    def _comprobar_muerte_minijefe(self, mj):
        if mj.vivo or mj.almas_otorgadas:
            return
        mj.almas_otorgadas = True
        self.jugador.almas += ALMAS_MINIJEFE
        self._sumar_almas_para_vida(ALMAS_MINIJEFE)
        self.audio.reproducir("meta")
        self.particulas.meta(mj.rect.centerx, mj.rect.centery)
        self.particulas.disolucion_enemigo(mj.rect.centerx, mj.rect.centery, 36, 48)
        self.camara.sacudir(9.0, 0.22)
        self.hud.mostrar_mensaje(
            f"¡EL CARCELERO HA CAÍDO! · El altar de la Guadaña se abre (+{ALMAS_MINIJEFE} Almas)", 2, 4.0
        )
        for muro in getattr(self.nivel, "muros_minijefe", []):
            muro.retraer()
        self.audio.reproducir_musica(self.nivel.tema, bucle=True, fade_ms=800)
