#---- Importamos librerias y configuracion ----#
import random

import config
from config import (
    ALMAS_FILO_ANIMA,
    ALMAS_MANTO_FAROL,
    ALMAS_POR_VIDA,
    AMARILLO,
    ATAQUE_ALCANCE_MEJORADO,
    BLANCO,
    DASH_USOS_AIRE,
    HUESO,
    INVULNERABILIDAD,
    ORO,
    PIEDRA_FRIA,
    REBOTE_ENEMIGO,
    ROJO,
    SALITRE_CRIPTA,
    TILE,
    TURQUESA_ÁNIMA,
    VIDAS_INICIALES,
    VIDAS_MAXIMAS,
)


#---- Mixin de mundo, checkpoints y progresion ----#
class MundoMixin:
    """Metodos de plataformas, losas, recogibles, checkpoints y vida."""

    def actualizar_plataformas(self, dt):
        soporte = None
        if self.jugador.en_suelo or self.jugador.vy >= 0:
            for plataforma in self.nivel.plataformas:
                rect = plataforma.rect
                if (
                    abs(self.jugador.rect.bottom - rect.top) <= 3
                    and self.jugador.rect.right > rect.left
                    and self.jugador.rect.left < rect.right
                ):
                    soporte = plataforma
                    break

        self.nivel.actualizar(dt)

        if soporte is not None:
            self.jugador.x += soporte.dx
            self.jugador.rect.x = round(self.jugador.x)
            self.jugador.rect.bottom = soporte.rect.top
            self.jugador.y = float(self.jugador.rect.y)
            self.jugador.en_suelo = True
            self.jugador.vy = 0.0
        elif self.jugador.vy >= 0:
            # Si una plataforma vertical sube hacia los pies del jugador, apoyarlo arriba antes de mover_x
            for plataforma in self.nivel.plataformas:
                rect = plataforma.rect
                if (
                    plataforma.dy < 0
                    and 0 < (self.jugador.rect.bottom - rect.top) <= abs(plataforma.dy) + 4
                    and self.jugador.rect.right > rect.left
                    and self.jugador.rect.left < rect.right
                ):
                    self.jugador.rect.bottom = rect.top
                    self.jugador.y = float(self.jugador.rect.y)
                    self.jugador.en_suelo = True
                    self.jugador.vy = 0.0
                    break

    def actualizar_losas(self, dt):
        for losa in getattr(self.nivel, "losas_quebradizas", []):
            if (
                self.jugador.en_suelo
                and abs(self.jugador.rect.bottom - losa.rect.top) <= 2
                and self.jugador.rect.right > losa.rect.left
                and self.jugador.rect.left < losa.rect.right
            ):
                losa.pisar()

            # Mientras tiembla (0.40s): caen piedritas y polvo hacia abajo
            if getattr(losa, "activa", False) and getattr(losa, "pisada", False) and getattr(losa, "tiempo_quiebre", 0.0) > 0:
                if random.random() < 0.45:
                    self.particulas.emitir(
                        losa.rect.left + random.uniform(2, losa.rect.width - 2),
                        losa.rect.bottom - 2,
                        1,
                        (SALITRE_CRIPTA, PIEDRA_FRIA, HUESO),
                        50,
                        0.35,
                        2.0,
                        480,
                    )

            if losa.recien_quebrada:
                self.audio.reproducir("losa_romper")
                self.particulas.losa_romper(losa.rect.centerx, losa.rect.centery, w=losa.rect.width)
                self.camara.sacudir(3.5, 0.12)
            elif losa.recien_reconstruida:
                self.particulas.emitir(
                    losa.rect.centerx,
                    losa.rect.centery,
                    12,
                    (TURQUESA_ÁNIMA, BLANCO),
                    100,
                    0.35,
                    2,
                )

    def _aplicar_rebote_campana(self, incensario, por_ataque=False):
        """Aplica el rebote del jugador sobre un incensario/campana con escala ascendente."""
        incensario.activar_rebote()
        if por_ataque:
            self.jugador.ataque_golpeado = True
            self.jugador.dash_tiempo = 0.0
        self.jugador.rect.bottom = min(self.jugador.rect.bottom, incensario.rect.top)
        self.jugador.y = float(self.jugador.rect.y)
        self.jugador.vy = -REBOTE_ENEMIGO
        self.jugador.en_suelo = False
        self.jugador.dash_usos_aire = DASH_USOS_AIRE
        self.jugador.dash_cooldown = 0.0

        if self.campanas_combo_timer > 0:
            self.campanas_combo_count = min(6, self.campanas_combo_count + 1)
        else:
            self.campanas_combo_count = 1
        self.campanas_combo_timer = 1.05
        self.audio.reproducir(f"campana_{self.campanas_combo_count}")

        self.particulas.campana_repique(incensario.rect.centerx, incensario.rect.centery)
        if por_ataque:
            self.camara.sacudir(6.0, 0.14, dir_x=self.jugador.direccion, dir_y=-0.5)
            self.flash = 0.08
            self.flash_color = TURQUESA_ÁNIMA
        else:
            self.camara.sacudir(5.0, 0.12, dir_x=0.0, dir_y=1.0)
        self.hitstop = 0.08

    def actualizar_incensarios(self, dt):
        tol = self._tolerancia_pisoton_frame(dt)
        for incensario in getattr(self.nivel, "incensarios", []):
            if not incensario.puede_rebotar():
                continue

            # Pisotón / contacto cayendo desde arriba (funciona sin pala incluso en Nivel 1)
            if (
                self.jugador.vy > 0
                and self.jugador.rect.colliderect(incensario.rect)
                and self.jugador.rect.bottom <= incensario.rect.top + tol
            ):
                self._aplicar_rebote_campana(incensario, por_ataque=False)

    def limitar_jugador(self):
        minimo = 0
        maximo = self.nivel.ancho - self.jugador.rect.width
        if self.jugador.rect.x < minimo:
            self.jugador.rect.x = minimo
            self.jugador.x = float(minimo)
            self.jugador.vx = 0.0
        elif self.jugador.rect.x > maximo:
            self.jugador.rect.x = maximo
            self.jugador.x = float(maximo)
            self.jugador.vx = 0.0

    def actualizar_peligros(self):
        if self.jugador.invulnerable > 0:
            return False
        for peligro in self.nivel.peligros:
            if self.jugador.rect.colliderect(peligro):
                self.perder_vida(causa="Pinchos ancestrales del camposanto")
                return True
        return False

    def _sumar_almas_para_vida(self, cantidad):
        """Loop positivo 'Rosario de Vida': cada ALMAS_POR_VIDA almas → +1 vida (tope VIDAS_MAXIMAS)."""
        self.jugador.almas_para_vida += cantidad
        while self.jugador.almas_para_vida >= ALMAS_POR_VIDA:
            self.jugador.almas_para_vida -= ALMAS_POR_VIDA
            if self.jugador.vidas < VIDAS_MAXIMAS:
                self.jugador.vidas += 1
                self.audio.reproducir("vida_extra")
                self.flash = 0.12
                self.flash_color = AMARILLO
                self.hud.mostrar_mensaje("¡VIDA EXTRA · 10 ALMAS CONSAGRADAS!", 2, 3.0)

    def actualizar_almas(self):
        for alma in self.nivel.almas:
            if alma.actualizar(self.jugador):
                self.almas_combo_timer = 2.2
                self.almas_combo_count = min(6, self.almas_combo_count + 1)
                sonido_alma = (
                    f"alma_{self.almas_combo_count}"
                    if f"alma_{self.almas_combo_count}" in self.audio.sonidos
                    else "alma"
                )
                self.audio.reproducir(sonido_alma)
                self.particulas.alma(alma.rect.centerx, alma.rect.centery)
                if self.almas_combo_count == 6:
                    self.particulas.emitir(
                        alma.rect.centerx,
                        alma.rect.centery,
                        8,
                        (ORO, TURQUESA_ÁNIMA, BLANCO),
                        140,
                        0.4,
                        3,
                    )
                self._sumar_almas_para_vida(1)

    def actualizar_palas(self):
        for pala in self.nivel.palas:
            if pala.actualizar(self.jugador):
                self.audio.reproducir("pala_recoger")
                self.particulas.alma(pala.rect.centerx, pala.rect.centery)
                self.texto_ayuda = "¡HIERRO DEL SEPULTURERO! · J / Z: EXORCIZAR LAS SOMBRAS"
                self.mostrar_ayuda = 4.0
                self.hud.mostrar_mensaje("¡HIERRO SAGRADO RECLAMADO! · J / Z: Castigar el abismo · Caída: pisotón purificador", 2, 4.0)

    def actualizar_power_ups_dash(self):
        for power_up in self.nivel.power_ups_dash:
            if power_up.actualizar(self.jugador):
                self.audio.reproducir("dash_recoger")
                self.particulas.emitir(
                    power_up.rect.centerx,
                    power_up.rect.centery,
                    28,
                    ((80, 220, 255), (180, 250, 255), BLANCO, (40, 150, 240)),
                    240,
                    0.7,
                    5,
                    200,
                )
                self.camara.sacudir(6.0, 0.16)
                self.flash = 0.14
                self.flash_color = (60, 200, 255)
                self.texto_ayuda = "¡MANTO DE SOMBRAS! · SHIFT / X: DESGARRAR EL VELO"
                self.mostrar_ayuda = 4.0
                self.hud.mostrar_mensaje("¡AMULETO DEL VELO! · SHIFT / X: Desgarrar el velo de la cripta en pleno vuelo", 2, 4.0)

    def _inscripcion_farol(self, checkpoint):
        """Obtiene la inscripción críptica estilo MK1 Arcade correspondiente al farol."""
        inscripciones = getattr(config, "INSCRIPCIONES_FAROLES", {})
        clave = 0 if getattr(self, "es_tutorial", False) else getattr(self, "nivel_indice", 0) + 1
        lista = inscripciones.get(clave, ())
        if not lista or not self.nivel:
            return "EN ALGÚN MOMENTO HAY QUE CREER."
        col_cp = checkpoint.rect.centerx // TILE
        if clave == 3 and checkpoint.rect.centery < 18 * TILE and 290 <= col_cp <= 312:
            return "NO BUSQUES PUENTE: EN ALGÚN MOMENTO HAY QUE CREER."
        if clave == 3 and checkpoint.rect.centery >= 18 * TILE and 138 <= col_cp <= 165:
            return "LAS COMPUERTAS SE CIERRAN. ÉL MISMO CAVARÁ SU TUMBA."
        try:
            idx = self.nivel.checkpoints.index(checkpoint)
        except ValueError:
            idx = 0
        return lista[idx % len(lista)]

    def _actualizar_duda_salto_de_fe(self, dt):
        """Susurra la pista oculta cuando el jugador duda ante el abismo del Salto de Fe."""
        if getattr(self, "es_tutorial", False) or getattr(self, "nivel_indice", 0) != 2 or not self.jugador:
            return
        col = self.jugador.rect.centerx // TILE
        fila = self.jugador.rect.centery // TILE
        if 296 <= col <= 311 and fila <= 16 and self.jugador.en_suelo:
            if abs(self.jugador.vx) < 25.0:
                self.tiempo_en_borde_fe += dt
            else:
                self.tiempo_en_borde_fe = max(0.0, self.tiempo_en_borde_fe - dt * 0.5)
            if self.tiempo_en_borde_fe >= 2.0 and not self.pista_fe_mostrada:
                self.pista_fe_mostrada = True
                pista = getattr(config, "PISTA_SALTO_DE_FE_DUDA", "LO INVISIBLE SOSTIENE AL QUE CAMINA SIN VER.")
                self.hud.mostrar_mensaje(f"VOZ DEL FAROL · {pista}", 3, 5.0, forzar=True)
        else:
            self.tiempo_en_borde_fe = 0.0

    def actualizar_checkpoints(self):
        for checkpoint in self.nivel.checkpoints:
            if checkpoint.actualizar(self.jugador):
                self.punto_reintento = (checkpoint.rect.x, checkpoint.rect.y - 4)
                self.audio.reproducir("checkpoint")
                self.particulas.emitir(
                    checkpoint.rect.centerx,
                    checkpoint.rect.bottom - 20,
                    18,
                    ((120, 220, 255), (200, 245, 255), BLANCO),
                    180,
                    0.6,
                    3,
                    120,
                )

                # Curación y Consagración de Almas: El Pacto del Farol (3 Grados)
                almas_tramo = self.jugador.almas - getattr(self, "almas_consagradas", 0)
                if almas_tramo >= ALMAS_FILO_ANIMA:
                    checkpoint.tier = 3
                    self.jugador.escudo_farol = True
                    self.jugador.filo_anima = True
                    self.destello_manto = 0.45
                    grado_txt = "Grado III"
                elif almas_tramo >= ALMAS_MANTO_FAROL:
                    checkpoint.tier = 2
                    self.jugador.escudo_farol = True
                    self.destello_manto = 0.40
                    grado_txt = "Grado II"
                elif almas_tramo >= 1:
                    checkpoint.tier = 1
                    grado_txt = "Grado I"
                else:
                    checkpoint.tier = 0
                    grado_txt = ""

                if checkpoint.tier > 0:
                    self.particulas.consagracion_farol(checkpoint.rect.centerx, checkpoint.rect.bottom, checkpoint.tier)
                    if checkpoint.tier == 1:
                        self.audio.reproducir("farol_tier_1")
                    elif checkpoint.tier == 2:
                        self.audio.reproducir("farol_tier_2")
                    elif checkpoint.tier >= 3:
                        self.audio.reproducir("farol_tier_3")

                vida_txt = ""
                if self.jugador.vidas < VIDAS_INICIALES:
                    self.jugador.vidas += 1
                    vida_txt = " (+1 Vida)"

                inscripcion = self._inscripcion_farol(checkpoint)
                encabezado = f"FARO{' · ' + grado_txt if grado_txt else ''}{vida_txt}"
                self.almas_consagradas = self.jugador.almas
                self.almas_vida_consagradas = self.jugador.almas_para_vida
                self.hud.mostrar_mensaje(f"{encabezado} · {inscripcion}", 2, 4.8)

    def actualizar_tutorial_contextual(self):
        """Muestra solo indicaciones breves al primer contacto real sin saturar de texto."""
        col = self.jugador.rect.x // TILE
        piso = self.jugador.rect.centery // (18 * TILE)

        zona = None
        msg = None
        if piso == 0:
            if 6 <= col < 22:
                zona = 1
                msg = "[ESPACIO] · Salto breve o alto según duración"
            elif 60 <= col < 76:
                zona = 2
                msg = "Brinca sobre el bronce y encadena"
        elif piso > 0 and 12 <= col < 30:
            zona = 3
            msg = "Atraviesa el Portón Sacro"

        if zona is not None and getattr(self, "tutorial_zona_actual", None) != zona:
            self.tutorial_zona_actual = zona
            self.hud.mostrar_mensaje(msg, 2, 3.6, forzar=True)

    def actualizar_power_ups_rango(self):
        carcelero_vivo = any(mj.vivo for mj in getattr(self.nivel, "minijefes", []))
        for power_up in self.nivel.power_ups_rango:
            power_up.sellado = carcelero_vivo
            if (
                power_up.sellado
                and not power_up.recogida
                and power_up.rect.colliderect(self.jugador.rect)
                and self.hud_aviso_altar <= 0
            ):
                self.hud_aviso_altar = 3.0
                self.hud.mostrar_mensaje("ALTAR SELLADO · Derrota al Carcelero del Osario para disipar el cerrojo sacrílego", 2, 3.0)
            if power_up.actualizar(self.jugador):
                self.audio.reproducir("alma")
                self.particulas.emitir(
                    power_up.rect.centerx,
                    power_up.rect.centery,
                    28,
                    ((215, 80, 255), (255, 200, 255), BLANCO, (160, 50, 220)),
                    240,
                    0.7,
                    5,
                    200,
                )
                self.camara.sacudir(6.0, 0.16)
                self.flash = 0.14
                self.flash_color = (190, 60, 255)
                self.texto_ayuda = "¡GUADAÑA CONSAGRADA! · EL HIERRO ESPECTRAL QUIEBRA LA CORAZA DEL CUSTODIO"
                self.mostrar_ayuda = 4.0
                self.hud.mostrar_mensaje(
                    f"¡GUADAÑA CONSAGRADA! · Alcance espectral {ATAQUE_ALCANCE_MEJORADO}px · Quiebra la vil coraza del Custodio",
                    3,
                    4.0,
                )

    def perder_vida(self, ignorar_invulnerabilidad=False, causa="Peligros de la cripta"):
        if self.jugador.invulnerable > 0 and not ignorar_invulnerabilidad:
            return

        # Si el jugador posee el Manto del Farol, absorbe el golpe letal
        if getattr(self.jugador, "escudo_farol", False):
            self.jugador.escudo_farol = False
            self.jugador.invulnerable = INVULNERABILIDAD
            self.audio.reproducir("rebote_pala")
            self.particulas.emitir(
                self.jugador.rect.centerx,
                self.jugador.rect.centery,
                24,
                ((120, 220, 255), (200, 245, 255), BLANCO),
                220,
                0.7,
                4,
            )
            self.flash = 0.15
            self.flash_color = (120, 220, 255)
            self.destello_manto = 0.38
            self.hud.mostrar_mensaje("¡MANTO DEL FAROL CONSUMIDO! · Daño absorbido", 2, 2.5)
            return

        self.jugador.vidas -= 1
        self.jugador.filo_anima = False
        self.audio.reproducir("daño")
        self.particulas.daño(self.jugador.rect.centerx, self.jugador.rect.centery)
        self.camara.sacudir(9.0, 0.22, dir_x=-self.jugador.direccion, dir_y=-0.5)
        self.flash = 0.16
        self.flash_color = ROJO
        self.almas_combo_count = 0
        self.almas_combo_timer = 0.0

        if self.jugador.vidas <= 0:
            self.muertes_totales += 1
            self.causa_muerte = causa
            self.derrota_opcion = 0
            self.estado = "derrota"
            self.audio.detener_dron()
            self.audio.reproducir("muerte")
            self.audio.reproducir_musica("derrota", bucle=False, fade_ms=400)
            return

        self.hitstop = 0.08

        if self.punto_reintento is not None:
            self._reaparecer_en_checkpoint(reiniciar_enemigos=False)
        else:
            self.jugador.almas = 0
            self.jugador.almas_para_vida = 0
            for alma in self.nivel.almas:
                alma.reiniciar()
            tenia_pala = self.jugador.tiene_pala
            tenia_dash = self.jugador.tiene_dash
            self.jugador.respawn(*self.nivel.spawn)
            self.jugador.tiene_pala = tenia_pala
            self.jugador.tiene_dash = tenia_dash
            for pup in self.nivel.power_ups_rango:
                pup.reiniciar()
            for pup in self.nivel.power_ups_dash:
                pup.reiniciar()
            self._reiniciar_arena_y_mecanismos()

        self.camara.actualizar(self.jugador, self.nivel, 1.0)

    def _reiniciar_arena_y_mecanismos(self):
        """Restaura el estado del jefe, carceleros activos y obstáculos mecánicos."""
        if self.jefe is not None and self.jefe.vivo:
            self.jefe.reiniciar()
            self.ondas_jefe = []
        for mj in getattr(self.nivel, "minijefes", []):
            # Un Carcelero ya derrotado no resucita: el altar sigue libre.
            if mj.vivo:
                mj.reiniciar()
        for losa in getattr(self.nivel, "losas_quebradizas", []):
            losa.reiniciar()
        for inc in getattr(self.nivel, "incensarios", []):
            inc.reiniciar()
        for bloque in getattr(self.nivel, "bloques_cripta", []):
            bloque.reiniciar()
        for compuerta in getattr(self.nivel, "compuertas_arena", []):
            compuerta.reiniciar()
        for muro in getattr(self.nivel, "muros_minijefe", []):
            muro.reiniciar()
        self._jefe_victoria_procesada = False

    def _reaparecer_en_checkpoint(self, reiniciar_enemigos=False):
        """Restaura al jugador en el último farol consagrado conservando reliquias."""
        self.jugador.almas = getattr(self, "almas_consagradas", 0)
        checkpoint_x, checkpoint_y = self.punto_reintento[0], self.punto_reintento[1]
        for alma in self.nivel.almas:
            if alma.rect.x >= checkpoint_x and self._es_mismo_piso(alma.rect, checkpoint_y):
                alma.reiniciar()
        if reiniciar_enemigos:
            for grupo in (self.nivel.enemigos, self.nivel.enemigos_melee):
                for enemigo in grupo:
                    if enemigo.rect.x >= checkpoint_x - TILE * 2 and self._es_mismo_piso(enemigo.rect, checkpoint_y):
                        enemigo.reiniciar()
        self._reiniciar_arena_y_mecanismos()
        tenia_guadana = self.jugador.rango_ataque_mejorado
        tenia_pala = self.jugador.tiene_pala
        tenia_dash = self.jugador.tiene_dash
        self.jugador.respawn(*self.punto_reintento)
        # respawn() limpia el contador del Rosario: restaurar lo consagrado en el farol.
        self.jugador.almas_para_vida = getattr(self, "almas_vida_consagradas", 0)
        self.jugador.rango_ataque_mejorado = tenia_guadana
        self.jugador.tiene_pala = tenia_pala
        self.jugador.tiene_dash = tenia_dash
        if self.nivel and getattr(self.nivel, "tema", None):
            if getattr(self.audio, "musica_actual", None) != self.nivel.tema or not getattr(self.audio, "musica_bucle", True):
                self.audio.reproducir_musica(self.nivel.tema, bucle=True, fade_ms=500)

    def reintentar_nivel(self):
        """Reinicia desde el último Farol activado o desde el inicio del nivel con vidas iniciales."""
        if self.punto_reintento is not None:
            self.jugador.vidas = VIDAS_INICIALES
            self._reaparecer_en_checkpoint(reiniciar_enemigos=True)
            self.camara.actualizar(self.jugador, self.nivel, 1.0)
            self.audio.iniciar_dron()
            if self.nivel and getattr(self.nivel, "tema", None):
                self.audio.reproducir_musica(self.nivel.tema, bucle=True, fade_ms=500)
        else:
            self.cargar_nivel(self.nivel_indice, vidas=VIDAS_INICIALES)
