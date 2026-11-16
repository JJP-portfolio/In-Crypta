#---- Importamos configuracion y entidades ----#
from config import (
    AMARILLO,
    BLANCO,
    DASH_USOS_AIRE,
    HUESO,
    ORO,
    PIEDRA_FRIA,
    REBOTE_ENEMIGO,
    SALITRE_CRIPTA,
    TURQUESA_ÁNIMA,
)
from entidades import Cuervo
from escena.constantes import TOLERANCIA_PISOTON


#---- Mixin de combate cuerpo a cuerpo y enemigos ----#
class CombateMixin:
    """Metodos de ataque, pisoton, feedback de dano y enemigos comunes."""

    def intentar_ataque(self):
        """Ataque frontal con pala (J / Z / C / click). Requiere tiene_pala."""
        if not self.jugador.pedir_ataque():
            return False
        self.audio.reproducir("ataque")
        self.particulas.ataque(
            self.jugador.rect.centerx,
            self.jugador.rect.centery,
            self.jugador.direccion,
            mejorado=self.jugador.rango_ataque_mejorado,
        )
        return True

    def _tolerancia_pisoton_frame(self, dt=None):
        """Calcula tolerancia vertical dinámica para evitar túneles a velocidad terminal."""
        dt_eff = max(float(dt if dt is not None else getattr(self, "_dt_actual", 0.016)), 0.016)
        vy_abs = abs(getattr(self.jugador, "vy", 0.0)) if self.jugador else 0.0
        return max(TOLERANCIA_PISOTON, int(vy_abs * dt_eff) + 6)

    def procesar_feedback_jugador(self):
        if self.jugador.salto_recien:
            self.audio.reproducir("salto")
            self.particulas.salto(self.jugador.rect.centerx, self.jugador.rect.bottom)

        if getattr(self.jugador, "aterrizaje_recien", False):
            # 4 partículas de polvo suave al aterrizar en pies
            pies_x = self.jugador.rect.centerx
            pies_y = self.jugador.rect.bottom
            self.particulas.emitir(
                pies_x,
                pies_y,
                4,
                (SALITRE_CRIPTA, PIEDRA_FRIA, HUESO, BLANCO),
                48,
                0.24,
                2.5,
                320,
            )

        if self.jugador.dash_recien:
            self.jugador.dash_recien = False
            self.audio.reproducir("dash")
            self.camara.sacudir(3.5, 0.10, dir_x=self.jugador.direccion, dir_y=0.0)

        if self.jugador.dash_tiempo > 0:
            self.particulas.dash(
                self.jugador.rect.centerx,
                self.jugador.rect.centery,
                self.jugador.dash_direccion,
            )

    def _golpear_incensarios(self, golpe):
        """Resuelve el rebote sobre campanas/incensarios golpeados; retorna True si impactó."""
        for incensario in getattr(self.nivel, "incensarios", []):
            if not (incensario.puede_rebotar() and golpe.colliderect(incensario.rect)):
                continue
            self._aplicar_rebote_campana(incensario, por_ataque=True)
            return True
        return False

    def _golpear_enemigos_comunes(self, golpe):
        """Abate al primer enemigo común alcanzado por el golpe frontal."""
        for grupo in (
            self.nivel.enemigos,
            self.nivel.cuervos,
            self.nivel.polillas,
            self.nivel.aranias,
            self.nivel.enemigos_melee,
        ):
            for entidad in grupo:
                if not entidad.vivo or not golpe.colliderect(entidad.rect):
                    continue
                entidad.tiempo_flash = 0.06
                inter = golpe.clip(entidad.rect)
                self.particulas.hit_spark(
                    inter.centerx, inter.centery, self.jugador.direccion, self.jugador.rango_ataque_mejorado
                )
                entidad.vivo = False
                self.particulas.disolucion_enemigo(entidad.rect.centerx, entidad.rect.centery)
                if isinstance(entidad, Cuervo):
                    for _ in range(4):
                        self.particulas.pluma_cuervo(entidad.rect.centerx, entidad.rect.centery)
                self.jugador.ataque_golpeado = True
                self.jugador.dash_usos_aire = DASH_USOS_AIRE
                self.jugador.dash_cooldown = 0.0
                self.audio.reproducir("pala")
                self.particulas.pala(entidad.rect.centerx, entidad.rect.centery)
                self.camara.sacudir(5.0, 0.12, dir_x=self.jugador.direccion, dir_y=0.0)
                self.hitstop = 0.08
                self.flash = 0.06
                self.flash_color = AMARILLO
                return True
        return False

    def actualizar_ataque(self):
        if self.jugador.ataque_tiempo <= 0 or self.jugador.ataque_golpeado:
            return

        golpe = self.jugador.rect_ataque()

        if getattr(self.jugador, "filo_anima", False):
            self.particulas.emitir(
                golpe.centerx,
                golpe.centery,
                2,
                (ORO, TURQUESA_ÁNIMA, BLANCO),
                120,
                0.25,
                3,
            )

        if self._golpear_incensarios(golpe):
            return
        if self._golpear_enemigos_comunes(golpe):
            return
        if self._golpear_minijefes(golpe):
            return

        if (
            self.jefe is not None
            and self.jefe.vivo
            and self.jefe.rect.colliderect(golpe)
        ):
            self.jugador.ataque_golpeado = True
            inter = golpe.clip(self.jefe.rect)
            self.particulas.hit_spark(inter.centerx, inter.centery, self.jugador.direccion, self.jugador.rango_ataque_mejorado)
            if hasattr(self.jefe, "tiempo_flash"):
                self.jefe.tiempo_flash = 0.06
            self.dañar_jefe_pala()

    def actualizar_enemigos(self, dt):
        # Regla de diseño: el pisotón (stomp) solo mata si el jugador tiene la pala.
        # Cada pisotón rebota y recarga el dash aéreo → "trampolines dinámicos"
        # para encadenar Salto -> Dash -> Pisotón -> Rebote -> Nuevo Dash.
        for enemigo in self.nivel.enemigos:
            enemigo.actualizar(dt)
            if self._resolver_contacto(enemigo, "Contacto con un Morador de la cripta"):
                return

        for enemigo_melee in self.nivel.enemigos_melee:
            enemigo_melee.actualizar(dt, self.jugador)
            if self._resolver_contacto(enemigo_melee, "Embestida del Guardia de la cripta"):
                return
            espada = enemigo_melee.rect_espada() if hasattr(enemigo_melee, "rect_espada") else None
            if (
                espada is not None
                and self.jugador.invulnerable <= 0
                and espada.colliderect(self.jugador.rect)
            ):
                self.perder_vida(causa="Estocada del Guardia de la cripta")
                return

        # Cuervos: vuelo circular. Pisables con pala (trampolín aéreo).
        for cuervo in self.nivel.cuervos:
            cuervo.actualizar(dt)
            if self._resolver_contacto(cuervo, "Ataque aéreo de Cuervo espectral"):
                return

        # Polillas: vuelo zigzag. Pisables con pala (trampolín aéreo).
        for polilla in self.nivel.polillas:
            polilla.actualizar(dt)
            if self._resolver_contacto(polilla, "Polvo letal de Polilla sombría"):
                return

        # Arañas: patrullaje horizontal. Pisables con pala.
        for araña in self.nivel.aranias:
            araña.actualizar(dt)
            if self._resolver_contacto(araña, "Picadura de Araña espectral"):
                return

    def _viene_desde_arriba(self, rect):
        """Pisotón válido: cayendo y dentro de la tolerancia dinámica por frame."""
        return (
            self.jugador.vy > 0
            and self.jugador.rect.bottom <= rect.top + self._tolerancia_pisoton_frame()
        )

    def _rebote_pisoton(self, rect, fuerza_sacudida=6.0):
        """Rebote + recarga instantánea del dash aéreo tras un pisotón exitoso."""
        self.jugador.rect.bottom = min(self.jugador.rect.bottom, rect.top)
        self.jugador.y = float(self.jugador.rect.y)
        self.jugador.vy = -REBOTE_ENEMIGO
        self.jugador.en_suelo = False
        self.jugador.dash_usos_aire = DASH_USOS_AIRE
        self.jugador.dash_cooldown = 0.0
        self.audio.reproducir("stomp")
        self.particulas.stomp(rect.centerx, rect.top)
        self.camara.sacudir(fuerza_sacudida, 0.14, dir_x=0.0, dir_y=1.0)
        self.hitstop = 0.08

    def _resolver_contacto(self, enemigo, causa):
        """Resuelve el contacto jugador-enemigo. Devuelve True si el jugador perdió una vida."""
        if not enemigo.vivo or not self.jugador.rect.colliderect(enemigo.rect):
            return False
        if self.jugador.tiene_pala and self._viene_desde_arriba(enemigo.rect):
            enemigo.vivo = False
            self.particulas.disolucion_enemigo(enemigo.rect.centerx, enemigo.rect.centery)
            self._rebote_pisoton(enemigo.rect)
            return False
        if self.jugador.invulnerable > 0:
            return False
        self.perder_vida(causa=causa)
        return True
