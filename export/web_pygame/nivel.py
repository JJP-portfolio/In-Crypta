# ============================================================
# nivel.py — Lectura del mapa ASCII y construcción del nivel
# ============================================================
# Esta clase convierte texto en objetos que pygame entiende:
# rectángulos sólidos, almas, moradores, decoraciones y peligros.
# ============================================================

import math

import pygame

from config import (
    AMARILLO,
    BLANCO,
    CARMESÍ_SANGRE,
    ENEMIGO_ALTO,
    ENEMIGO_ANCHO,
    FAROL_CÁLIDO,
    HUESO,
    HUESO_MARFIL,
    INCENSARIO_ALTO,
    INCENSARIO_ANCHO,
    JEFE_ALTO,
    JEFE_ANCHO,
    MARRON,
    MARRON_OSCURO,
    MINIJEFE_ALTO,
    MINIJEFE_ANCHO,
    MUSGO,
    NEGRO,
    NEGRO_NOCHE,
    NARANJA,
    ORO,
    ORO_LITÚRGICO,
    PASTO,
    PIEDRA,
    PIEDRA_FRIA,
    PIEDRA_OSCURA,
    ROJO,
    SALITRE_CRIPTA,
    SANGRE,
    TILE,
    TURQUESA_ÁNIMA,
    VERDE_OSCURO,
    VIOLETA_POE,
)

# Paleta Grabado Xilográfico Gótico & Vitral
MARFIL_XILOGRAFICO = (228, 224, 210)
TINTA_ABISMO = (6, 5, 10)
from entidades import (
    Alma,
    Araña,
    Cuervo,
    Custodio,
    DashPowerUp,
    Enemigo,
    EnemigoMelee,
    FarolCheckpoint,
    IncensarioRebote,
    LosaQuebradiza,
    MiniJefe,
    PalaRecogible,
    Polilla,
    RangoPowerUp,
    TotemProyectil,
)


DECORACIONES = {"t", "c", "r", "b", "s", "j", "g", "u"}

_HALO_VELA = None
_HALO_META = None
_HALO_BRASERO_ESPECTRAL = None


def _obtener_halo_brasero() -> pygame.Surface:
    """Halo espectral cian/turquesa cacheado para braseros 'b' (CPU BLEND_RGB_ADD)."""
    global _HALO_BRASERO_ESPECTRAL
    if _HALO_BRASERO_ESPECTRAL is None:
        diam = 96
        _HALO_BRASERO_ESPECTRAL = pygame.Surface((diam, diam), pygame.SRCALPHA)
        _HALO_BRASERO_ESPECTRAL.fill((0, 0, 0, 0))
        cx, cy = diam // 2, diam // 2
        for r in range(cx, 2, -2):
            norm = r / float(cx)
            factor = (1.0 - norm * norm) ** 2.0
            rgb = (
                int(75 * factor * 0.28),
                int(220 * factor * 0.28),
                int(205 * factor * 0.28),
            )
            pygame.draw.circle(_HALO_BRASERO_ESPECTRAL, rgb, (cx, cy), r)
        _HALO_BRASERO_ESPECTRAL = _HALO_BRASERO_ESPECTRAL.convert_alpha()
    return _HALO_BRASERO_ESPECTRAL


def _obtener_halo_vela() -> pygame.Surface:
    """Halo translúcido cálido con desvanecimiento suave para iluminación litúrgica de velas."""
    global _HALO_VELA
    if _HALO_VELA is None:
        _HALO_VELA = pygame.Surface((40, 40), pygame.SRCALPHA)
        _HALO_VELA.fill((0, 0, 0, 0))
        for r in range(18, 1, -2):
            norm = r / 18.0
            alfa = int(32 * (1.0 - norm * norm))
            pygame.draw.circle(_HALO_VELA, (255, 185, 65, alfa), (20, 20), r)
        _HALO_VELA = _HALO_VELA.convert_alpha()
    return _HALO_VELA


def _obtener_halo_meta() -> pygame.Surface:
    """Halo translúcido suave para el portal/portón de meta."""
    global _HALO_META
    if _HALO_META is None:
        _HALO_META = pygame.Surface((64, 64), pygame.SRCALPHA)
        _HALO_META.fill((0, 0, 0, 0))
        for r in range(30, 2, -2):
            norm = r / 30.0
            alfa = int(35 * (1.0 - norm * norm))
            pygame.draw.circle(_HALO_META, (255, 205, 95, alfa), (32, 32), r)
        _HALO_META = _HALO_META.convert_alpha()
    return _HALO_META


# --- Clase PlataformaMovil --- #
class PlataformaMovil:
    """Plataforma cinemática que oscila alrededor de su posición inicial."""

    def __init__(self, rect, eje, amplitud, velocidad, fase):
        self.inicial_rect = pygame.Rect(rect)
        self.rect = pygame.Rect(rect)
        self.eje = eje
        self.amplitud = amplitud
        self.velocidad = velocidad
        self.fase = fase
        self.tiempo = 0.0
        self.dx = 0
        self.dy = 0

    # --- Función reiniciar --- #
    def reiniciar(self):
        self.rect = pygame.Rect(self.inicial_rect)
        self.tiempo = 0.0
        self.dx = 0
        self.dy = 0

    # --- Función actualizar --- #
    def actualizar(self, dt):
        anterior = self.rect.copy()
        self.tiempo += dt
        desplazamiento = math.sin(self.tiempo * self.velocidad + self.fase) * self.amplitud
        if self.eje == "h":
            self.rect.x = round(self.inicial_rect.x + desplazamiento)
        else:
            self.rect.y = round(self.inicial_rect.y + desplazamiento)
        self.dx = self.rect.x - anterior.x
        self.dy = self.rect.y - anterior.y


# --- Clase Nivel --- #
class Nivel:
    """Representación jugable de un mapa ASCII."""

    def __init__(self, datos, nombre="Nivel", pista="", tema="camposanto"):
        self.nombre = nombre
        self.pista = pista
        self.tema = tema
        filas = datos.strip("\n").splitlines()
        if not filas:
            raise ValueError("El nivel no tiene filas")

        self.columnas = max(len(fila) for fila in filas)
        self.num_filas = len(filas)
        # Rellenamos con puntos para que todas las filas midan lo mismo.
        self.filas = [fila.ljust(self.columnas, ".") for fila in filas]

        self.ancho = self.columnas * TILE
        self.alto = self.num_filas * TILE

        self.spawn = self._buscar_spawn()
        self.meta = self._buscar_meta()
        self.solidos = self._crear_solidos()
        self.almas = self._crear_almas()
        self.enemigos = self._crear_enemigos()
        self.enemigos_melee = self._crear_enemigos_melee()
        self.totems = self._crear_totems()
        self.decoraciones = self._crear_decoraciones()
        self.peligros = self._crear_peligros()
        self.palas = self._crear_palas()
        self.power_ups_dash = self._crear_power_ups_dash()
        self.power_ups_rango = self._crear_power_ups_rango()
        self.checkpoints = self._crear_checkpoints()
        self.plataformas = self._crear_plataformas()
        self.losas_quebradizas = self._crear_losas_quebradizas()
        self.incensarios = self._crear_incensarios()
        self.jefes = self._crear_jefes()
        self.minijefes = self._crear_minijefes()
        self.cuervos = self._crear_cuervos()
        self.polillas = self._crear_polillas()
        self.aranias = self._crear_aranias()
        self.total_almas = len(self.almas)

        if self.spawn is None:
            raise ValueError("Falta la P de spawn en el nivel")
        if self.meta is None:
            raise ValueError("Falta la G de meta en el nivel")

    # --- Función _buscar_spawn --- #
    def _buscar_spawn(self):
        for fila, texto in enumerate(self.filas):
            for columna, simbolo in enumerate(texto):
                if simbolo == "P":
                    # El jugador mide 30 px; +2 lo deja apoyado en el tile.
                    return (columna * TILE + 4, fila * TILE + 2)
        return None

    # --- Función _buscar_meta --- #
    def _buscar_meta(self):
        for fila, texto in enumerate(self.filas):
            for columna, simbolo in enumerate(texto):
                if simbolo == "G":
                    return pygame.Rect(
                        columna * TILE + 6,
                        fila * TILE + 2,
                        20,
                        30,
                    )
        return None

    # --- Función _crear_solidos --- #
    def _crear_solidos(self):
        """Une bloques consecutivos de una fila en un solo rectángulo."""
        solidos = []
        for fila, texto in enumerate(self.filas):
            columna = 0
            while columna < self.columnas:
                if texto[columna] != "#":
                    columna += 1
                    continue

                inicio = columna
                while columna < self.columnas and texto[columna] == "#":
                    columna += 1

                solidos.append(pygame.Rect(
                    inicio * TILE,
                    fila * TILE,
                    (columna - inicio) * TILE,
                    TILE,
                ))
        return solidos

    # --- Función _crear_almas --- #
    def _crear_almas(self):
        almas = []
        for fila, texto in enumerate(self.filas):
            for columna, simbolo in enumerate(texto):
                if simbolo == "o":
                    almas.append(Alma(pygame.Rect(
                        columna * TILE + 8,
                        fila * TILE + 8,
                        16,
                        16,
                    )))
        return almas

    # --- Función _crear_enemigos --- #
    def _crear_enemigos(self):
        enemigos = []
        for fila, texto in enumerate(self.filas):
            for columna, simbolo in enumerate(texto):
                if simbolo != "E":
                    continue

                rect = pygame.Rect(
                    columna * TILE + (TILE - ENEMIGO_ANCHO) // 2,
                    fila * TILE + (TILE - ENEMIGO_ALTO),
                    ENEMIGO_ANCHO,
                    ENEMIGO_ALTO,
                )
                minimo_x, maximo_x = self._limites_patrulla(columna, fila)
                enemigos.append(Enemigo(rect, minimo_x, maximo_x))
        return enemigos

    # --- Función _crear_decoraciones --- #
    def _crear_decoraciones(self):
        decoraciones = []
        for fila, texto in enumerate(self.filas):
            for columna, simbolo in enumerate(texto):
                if simbolo not in DECORACIONES:
                    continue
                decoraciones.append({
                    "tipo": simbolo,
                    "rect": pygame.Rect(
                        columna * TILE,
                        fila * TILE,
                        TILE,
                        TILE,
                    ),
                })
        return decoraciones

    # --- Función _crear_palas --- #
    def _crear_palas(self):
        palas = []
        for fila, texto in enumerate(self.filas):
            for columna, simbolo in enumerate(texto):
                if simbolo != "W":
                    continue
                palas.append(PalaRecogible(pygame.Rect(
                    columna * TILE + 6,
                    fila * TILE + 2,
                    20,
                    30,
                )))
        return palas

    # --- Función _crear_power_ups_dash --- #
    def _crear_power_ups_dash(self):
        power_ups = []
        for fila, texto in enumerate(self.filas):
            for columna, simbolo in enumerate(texto):
                if simbolo != "D":
                    continue
                power_ups.append(DashPowerUp(pygame.Rect(
                    columna * TILE + 6,
                    fila * TILE + 2,
                    20,
                    30,
                )))
        return power_ups

    # --- Función _crear_power_ups_rango --- #
    def _crear_power_ups_rango(self):
        power_ups = []
        for fila, texto in enumerate(self.filas):
            for columna, simbolo in enumerate(texto):
                if simbolo != "X":
                    continue
                power_ups.append(RangoPowerUp(pygame.Rect(
                    columna * TILE + 6,
                    fila * TILE + 2,
                    20,
                    30,
                )))
        return power_ups

    # --- Función _crear_checkpoints --- #
    def _crear_checkpoints(self):
        checkpoints = []
        for fila, texto in enumerate(self.filas):
            for columna, simbolo in enumerate(texto):
                if simbolo != "F":
                    continue
                checkpoints.append(FarolCheckpoint(pygame.Rect(
                    columna * TILE + 6,
                    fila * TILE + 2,
                    20,
                    30,
                )))
        return checkpoints

    # --- Función _crear_losas_quebradizas --- #
    def _crear_losas_quebradizas(self):
        losas = []
        for fila, texto in enumerate(self.filas):
            for columna, simbolo in enumerate(texto):
                if simbolo == "~":
                    losas.append(LosaQuebradiza(pygame.Rect(
                        columna * TILE,
                        fila * TILE,
                        TILE,
                        TILE,
                    )))
        return losas

    # --- Función _crear_incensarios --- #
    def _crear_incensarios(self):
        incensarios = []
        for fila, texto in enumerate(self.filas):
            for columna, simbolo in enumerate(texto):
                if simbolo == "I":
                    incensarios.append(IncensarioRebote(pygame.Rect(
                        columna * TILE + (TILE - INCENSARIO_ANCHO) // 2,
                        fila * TILE + (TILE - INCENSARIO_ALTO) // 2,
                        INCENSARIO_ANCHO,
                        INCENSARIO_ALTO,
                    )))
        return incensarios

    # --- Función _crear_cuervos --- #
    def _crear_cuervos(self):
        cuervos = []
        for fila, texto in enumerate(self.filas):
            for columna, simbolo in enumerate(texto):
                if simbolo != "C":
                    continue
                rect = pygame.Rect(
                    columna * TILE + 4,
                    fila * TILE + 4,
                    24,
                    24,
                )
                cuervos.append(Cuervo(
                    rect,
                    centro_x=columna * TILE + TILE // 2,
                    centro_y=fila * TILE + TILE // 2,
                    radio=3 * TILE,
                    velocidad=1.5,
                ))
        return cuervos

    # --- Función _crear_polillas --- #
    def _crear_polillas(self):
        polillas = []
        for fila, texto in enumerate(self.filas):
            for columna, simbolo in enumerate(texto):
                if simbolo != "m":
                    continue
                rect = pygame.Rect(
                    columna * TILE + (TILE - ENEMIGO_ANCHO) // 2,
                    fila * TILE + (TILE - ENEMIGO_ALTO),
                    ENEMIGO_ANCHO,
                    ENEMIGO_ALTO,
                )
                minimo_x, maximo_x = self._limites_patrulla(columna, fila)
                polillas.append(Polilla(rect, minimo_x, maximo_x))
        return polillas

    # --- Función _crear_aranias --- #
    def _crear_aranias(self):
        aranias = []
        for fila, texto in enumerate(self.filas):
            for columna, simbolo in enumerate(texto):
                if simbolo != "A":
                    continue
                rect = pygame.Rect(
                    columna * TILE + (TILE - ENEMIGO_ANCHO) // 2,
                    fila * TILE + (TILE - ENEMIGO_ALTO),
                    ENEMIGO_ANCHO,
                    ENEMIGO_ALTO,
                )
                minimo_x, maximo_x = self._limites_patrulla(columna, fila)
                aranias.append(Araña(rect, minimo_x, maximo_x))
        return aranias

    # --- Función _crear_jefes --- #
    def _crear_jefes(self):
        jefes = []
        for fila, texto in enumerate(self.filas):
            for columna, simbolo in enumerate(texto):
                if simbolo != "B":
                    continue
                rect = pygame.Rect(
                    columna * TILE - (JEFE_ANCHO - TILE) // 2,
                    (fila + 1) * TILE - JEFE_ALTO,
                    JEFE_ANCHO,
                    JEFE_ALTO,
                )
                minimo_x = max(0, (columna - 20) * TILE)
                maximo_x = min(self.ancho - JEFE_ANCHO, (columna + 20) * TILE)
                jefes.append(Custodio(rect, minimo_x, maximo_x))
        return jefes

    # --- Función _crear_minijefes --- #
    def _crear_minijefes(self):
        minijefes = []
        for fila, texto in enumerate(self.filas):
            for columna, simbolo in enumerate(texto):
                if simbolo != "K":
                    continue
                rect = pygame.Rect(
                    columna * TILE - (MINIJEFE_ANCHO - TILE) // 2,
                    (fila + 1) * TILE - MINIJEFE_ALTO,
                    MINIJEFE_ANCHO,
                    MINIJEFE_ALTO,
                )
                minimo_x = max(0, (columna - 12) * TILE)
                maximo_x = min(self.ancho - MINIJEFE_ANCHO, (columna + 12) * TILE)
                minijefes.append(MiniJefe(rect, minimo_x, maximo_x))
        return minijefes
    def _crear_plataformas(self):
        plataformas = []
        for fila, texto in enumerate(self.filas):
            columna = 0
            while columna < self.columnas:
                simbolo = texto[columna]
                if simbolo not in ("M", "V"):
                    columna += 1
                    continue

                inicio = columna
                while columna < self.columnas and texto[columna] == simbolo:
                    columna += 1

                plataformas.append(PlataformaMovil(
                    pygame.Rect(
                        inicio * TILE,
                        fila * TILE,
                        (columna - inicio) * TILE,
                        TILE,
                    ),
                    "h" if simbolo == "M" else "v",
                    3 * TILE if simbolo == "M" else 2 * TILE,
                    1.35,
                    (inicio * 0.37 + fila * 0.21) % math.tau,
                ))
        return plataformas

    # --- Función _crear_enemigos_melee --- #
    def _crear_enemigos_melee(self):
        enemigos_melee = []
        for fila, texto in enumerate(self.filas):
            for columna, simbolo in enumerate(texto):
                if simbolo != "L":  # L = EnemigoMelee
                    continue

                rect = pygame.Rect(
                    columna * TILE + (TILE - ENEMIGO_ANCHO) // 2,
                    fila * TILE + (TILE - ENEMIGO_ALTO),
                    ENEMIGO_ANCHO,
                    ENEMIGO_ALTO,
                )
                minimo_x, maximo_x = self._limites_patrulla(columna, fila)
                enemigos_melee.append(EnemigoMelee(rect, minimo_x, maximo_x))
        return enemigos_melee

    # --- Función _crear_totems --- #
    def _crear_totems(self):
        totems = []
        for fila, texto in enumerate(self.filas):
            for columna, simbolo in enumerate(texto):
                if simbolo != "O":  # O = TotemProyectil
                    continue

                x = columna * TILE + TILE // 2
                y = fila * TILE + TILE * 3
                totems.append(TotemProyectil(x, y))
        return totems

    # --- Función _crear_peligros --- #
    def _crear_peligros(self):
        peligros = []
        for fila, texto in enumerate(self.filas):
            for columna, simbolo in enumerate(texto):
                if simbolo != "^":
                    continue
                peligros.append(pygame.Rect(
                    columna * TILE + 4,
                    fila * TILE + 12,
                    TILE - 8,
                    TILE - 12,
                ))
        return peligros

    # --- Función _limites_patrulla --- #
    def _limites_patrulla(self, columna, fila):
        """El enemigo patrulla solo sobre la plataforma que tiene debajo.

        Además recorta el tramo para que no pise pinchos ni atraviese muros
        que estén en su misma fila: el enemigo gira antes de tocarlos.
        """
        fila_piso = fila + 1
        if fila_piso >= self.num_filas:
            return (columna * TILE - TILE, (columna + 1) * TILE + TILE)

        piso = self.filas[fila_piso]
        if piso[columna] != "#":
            return (columna * TILE - TILE, (columna + 1) * TILE + TILE)

        izquierda = columna
        while izquierda > 0 and piso[izquierda - 1] == "#":
            izquierda -= 1

        derecha = columna
        while derecha + 1 < self.columnas and piso[derecha + 1] == "#":
            derecha += 1

        fila_enemigo = self.filas[fila]
        libre_izquierda = columna
        while (
            libre_izquierda > izquierda
            and fila_enemigo[libre_izquierda - 1] not in ("^", "#")
        ):
            libre_izquierda -= 1

        libre_derecha = columna
        while (
            libre_derecha < derecha
            and fila_enemigo[libre_derecha + 1] not in ("^", "#")
        ):
            libre_derecha += 1

        return (
            max(izquierda, libre_izquierda) * TILE,
            (min(derecha, libre_derecha) + 1) * TILE,
        )

    # --- Función actualizar --- #
    def actualizar(self, dt):
        for plataforma in self.plataformas:
            plataforma.actualizar(dt)
        for losa in getattr(self, "losas_quebradizas", []):
            losa.actualizar(dt)
        for incensario in getattr(self, "incensarios", []):
            incensario.actualizar(dt)

    # --- Función solidos_actuales --- #
    def solidos_actuales(self):
        return (
            self.solidos
            + [plataforma.rect for plataforma in self.plataformas]
            + [losa.rect for losa in getattr(self, "losas_quebradizas", []) if losa.activa]
        )

    # --- Función reiniciar --- #
    def reiniciar(self):
        """Devuelve el nivel a su estado inicial."""
        for alma in self.almas:
            alma.reiniciar()
        for enemigo in self.enemigos:
            enemigo.reiniciar()
        for enemigo_melee in self.enemigos_melee:
            enemigo_melee.reiniciar()
        for totem in self.totems:
            totem.reiniciar()
        for pala in self.palas:
            pala.reiniciar()
        for power_up in self.power_ups_dash:
            power_up.reiniciar()
        for power_up in self.power_ups_rango:
            power_up.reiniciar()
        for checkpoint in self.checkpoints:
            checkpoint.reiniciar()
        for cuervo in self.cuervos:
            cuervo.reiniciar()
        for polilla in self.polillas:
            polilla.reiniciar()
        for araña in self.aranias:
            araña.reiniciar()
        for plataforma in self.plataformas:
            plataforma.reiniciar()
        for minijefe in self.minijefes:
            minijefe.reiniciar()
        for jefe in self.jefes:
            jefe.reiniciar()
        for losa in getattr(self, "losas_quebradizas", []):
            losa.reiniciar()
        for incensario in getattr(self, "incensarios", []):
            incensario.reiniciar()

    # --- Función dibujar --- #
    def dibujar(self, surface, camara):
        self.dibujar_solidos(surface, camara)
        self.dibujar_plataformas(surface, camara)
        self.dibujar_decoraciones(surface, camara)
        self.dibujar_peligros(surface, camara)

        tiempo = pygame.time.get_ticks() / 1000
        for losa in getattr(self, "losas_quebradizas", []):
            losa.dibujar(surface, camara, tiempo)
        for incensario in getattr(self, "incensarios", []):
            incensario.dibujar(surface, camara, tiempo)
        for alma in self.almas:
            alma.dibujar(surface, camara, tiempo)
        for pala in self.palas:
            pala.dibujar(surface, camara, tiempo)
        for power_up in self.power_ups_dash:
            power_up.dibujar(surface, camara, tiempo)
        for power_up in self.power_ups_rango:
            power_up.dibujar(surface, camara, tiempo)
        for checkpoint in self.checkpoints:
            checkpoint.dibujar(surface, camara, tiempo)
        for minijefe in self.minijefes:
            minijefe.dibujar(surface, camara, tiempo)
        for enemigo_melee in self.enemigos_melee:
            enemigo_melee.dibujar(surface, camara, tiempo)
        for totem in self.totems:
            totem.dibujar(surface, camara, tiempo)
        for cuervo in self.cuervos:
            cuervo.dibujar(surface, camara, tiempo)
        for polilla in self.polillas:
            polilla.dibujar(surface, camara, tiempo)
        for araña in self.aranias:
            araña.dibujar(surface, camara, tiempo)

        self.dibujar_meta(surface, camara)

    # --- Función dibujar_plataformas --- #
    def dibujar_plataformas(self, surface, camara):
        tema = getattr(self, "tema", "camposanto")
        tiempo = pygame.time.get_ticks() / 1000.0
        for plataforma in self.plataformas:
            if not camara.is_on_screen(plataforma.rect):
                continue
            rect = camara.aplicar_rect(plataforma.rect)
            init_rect = camara.aplicar_rect(plataforma.inicial_rect)
            fila_plat = plataforma.rect.y // TILE
            tema_efectivo = "cripta" if (fila_plat >= 18 and tema == "camposanto") else tema

            # Riel mecánico / cadena tensa según el eje real de oscilación ("h" o "v")
            amp = int(getattr(plataforma, "amplitud", 0))
            eje = getattr(plataforma, "eje", "h")
            if amp > 0:
                if eje in ("h", "x"):
                    x_min = init_rect.x - amp + 6
                    x_max = init_rect.right + amp - 6
                    ry = rect.centery
                    # Riel de hierro forjado en segundo plano con eslabones
                    pygame.draw.line(surface, (22, 20, 28), (x_min, ry), (x_max, ry), 4)
                    pygame.draw.line(surface, (58, 56, 70), (x_min, ry - 1), (x_max, ry - 1), 1)
                    for ex in range(x_min, x_max + 1, 12):
                        pygame.draw.circle(surface, (86, 82, 98), (ex, ry), 2, 1)
                    # Rosetones de anclaje en los extremos del recorrido
                    for ext_x in (x_min, x_max):
                        pygame.draw.circle(surface, (28, 24, 34), (ext_x, ry), 5)
                        pygame.draw.circle(surface, (132, 118, 88), (ext_x, ry), 4, 1)
                        pygame.draw.circle(surface, TURQUESA_ÁNIMA, (ext_x, ry), 1)
                else:
                    y_min = init_rect.centery - amp - 18
                    y_max = init_rect.centery + amp + 10
                    for ancla_x in (rect.x + 10, rect.right - 10):
                        for cy in range(y_min, y_max, 8):
                            pygame.draw.rect(surface, (18, 16, 22), (ancla_x - 3, cy, 6, 7), border_radius=2)
                            pygame.draw.rect(surface, (78, 74, 90), (ancla_x - 2, cy + 1, 4, 5), 1, border_radius=1)
                        pygame.draw.circle(surface, (30, 26, 38), (ancla_x, y_min), 5)
                        pygame.draw.circle(surface, (132, 118, 88), (ancla_x, y_min), 4, 1)

            # Sombra proyectada y brasero de ánima inferior
            pygame.draw.rect(
                surface,
                NEGRO_NOCHE,
                (rect.x + 2, rect.bottom, rect.width - 4, 4),
                border_radius=2,
            )
            if rect.width >= 40:
                cx_b = rect.centerx
                pulso_b = 0.5 + 0.5 * math.sin(tiempo * 5.0 + init_rect.x * 0.05)
                pygame.draw.polygon(
                    surface,
                    (36, 32, 44),
                    [(cx_b - 10, rect.bottom - 1), (cx_b + 10, rect.bottom - 1), (cx_b + 5, rect.bottom + 5), (cx_b - 5, rect.bottom + 5)],
                )
                c_nucleo = (int(70 + 30 * pulso_b), int(185 + 40 * pulso_b), int(170 + 35 * pulso_b))
                pygame.draw.circle(surface, c_nucleo, (cx_b, rect.bottom + 2), 2)

            # Tapa de sarcófago férreo labrada según tema efectivo
            if tema_efectivo == "osario":
                color_losa = (60, 46, 48)
                color_marco = (28, 20, 22)
            elif tema_efectivo == "cripta":
                color_losa = (50, 54, 68)
                color_marco = (22, 24, 34)
            else:
                color_losa = (56, 50, 62)
                color_marco = (24, 20, 28)

            pygame.draw.rect(surface, color_losa, rect, border_radius=3)
            pygame.draw.rect(surface, color_marco, rect, 2, border_radius=3)

            # Cornisa superior en Marfil Xilográfico (3px) con muescas de cincel
            pygame.draw.line(surface, MARFIL_XILOGRAFICO, (rect.x + 2, rect.y + 1), (rect.right - 2, rect.y + 1), 3)
            for cx_cincel in range(rect.x + 8, rect.right - 4, 16):
                pygame.draw.line(surface, TINTA_ABISMO, (cx_cincel, rect.y), (cx_cincel, rect.y + 3), 1)
            pygame.draw.line(surface, TINTA_ABISMO, (rect.x + 2, rect.y + 4), (rect.right - 2, rect.y + 4), 2)
            for ax in range(rect.x + 6, rect.right - 6, 8):
                pygame.draw.line(surface, (18, 16, 24), (ax, rect.y + 6), (ax, rect.y + 11), 1)

            # Relieve central de bronce litúrgico
            if rect.width >= 48:
                cx = rect.centerx
                pygame.draw.line(surface, color_marco, (cx, rect.y + 4), (cx, rect.bottom - 3), 3)
                pygame.draw.line(surface, color_marco, (cx - 10, rect.y + 9), (cx + 10, rect.y + 9), 3)
                pygame.draw.line(surface, ORO_LITÚRGICO, (cx, rect.y + 5), (cx, rect.bottom - 4), 1)
                pygame.draw.line(surface, ORO_LITÚRGICO, (cx - 9, rect.y + 9), (cx + 9, rect.y + 9), 1)
            elif rect.width >= 32:
                pygame.draw.line(
                    surface,
                    ORO_LITÚRGICO,
                    (rect.x + 8, rect.y + 9),
                    (rect.right - 8, rect.y + 9),
                    1,
                )

            # Engranajes laterales de bronce que giran con el desplazamiento de la plataforma
            giro = (plataforma.rect.x + plataforma.rect.y) * 0.12
            for eng_x in (rect.x + 5, rect.right - 6):
                eng_y = rect.centery + 1
                pygame.draw.circle(surface, (32, 26, 36), (eng_x, eng_y), 4)
                pygame.draw.circle(surface, (168, 134, 72), (eng_x, eng_y), 3, 1)
                dx_g = int(math.cos(giro) * 3)
                dy_g = int(math.sin(giro) * 3)
                pygame.draw.line(surface, (198, 162, 92), (eng_x - dx_g, eng_y - dy_g), (eng_x + dx_g, eng_y + dy_g), 1)

    # --- Función dibujar_solidos --- #
    def dibujar_solidos(self, surface, camara):
        tema = getattr(self, "tema", "camposanto")
        import config
        estilo = config.resolver_estilo(getattr(config, "ESTILO_MUNDO", "AUTO"))
        c_corte = (10, 8, 14)

        for solido in self.solidos:
            if not camara.is_on_screen(solido):
                continue

            rect = camara.aplicar_rect(solido)
            fila = solido.y // TILE
            col_inicio = solido.x // TILE
            num_cols = solido.width // TILE
            fila_rel = fila % 18
            es_piso_nivel = fila_rel >= 15

            # Tema contextual por piso en niveles verticales (ej: catacumbas bajo tierra)
            tema_efectivo = "cripta" if (fila >= 18 and tema == "camposanto") else tema

            if tema_efectivo == "cripta":
                c_bisel_top = (180, 198, 222)
                color_piso = (44, 48, 58)
                color_piso_profundo = (26, 28, 36)
                color_borde = (18, 20, 26)
                color_arriba = (55, 78, 68)
                color_brizna = (82, 118, 102)
                color_cuerpo = (52, 56, 68)
                color_marco = (24, 26, 34)
            elif tema_efectivo == "osario":
                c_bisel_top = (218, 208, 186)
                color_piso = (62, 45, 43)
                color_piso_profundo = (38, 26, 26)
                color_borde = (26, 18, 20)
                color_arriba = (96, 58, 52)
                color_brizna = (136, 86, 78)
                color_cuerpo = (74, 52, 50)
                color_marco = (36, 22, 24)
            else:
                c_bisel_top = (165, 185, 160)
                color_piso = (68, 52, 42)
                color_piso_profundo = (44, 32, 26)
                color_borde = (28, 20, 16)
                color_arriba = (48, 76, 44)
                color_brizna = (76, 114, 68)
                color_cuerpo = (64, 62, 70)
                color_marco = (26, 24, 30)

            if estilo == "NES":
                for c_idx in range(num_cols):
                    col = col_inicio + c_idx
                    tx = rect.x + c_idx * TILE
                    t_rect = pygame.Rect(tx, rect.y, TILE, TILE)
                    tiene_arriba = (
                        fila > 0
                        and fila - 1 < len(self.filas)
                        and col < len(self.filas[fila - 1])
                        and self.filas[fila - 1][col] == "#"
                    )
                    c_fill = color_piso_profundo if tiene_arriba else color_piso
                    pygame.draw.rect(surface, c_fill, t_rect)
                    pygame.draw.rect(surface, c_corte, t_rect, 1)
                    if not tiene_arriba:
                        pygame.draw.rect(surface, c_bisel_top, (tx, rect.y, TILE, 3))
                        pygame.draw.rect(surface, c_corte, (tx, rect.y + 3, TILE, 2))
                continue

            if estilo == "SNES":
                desplazamiento = (TILE // 2) if fila % 2 == 1 else 0
                c_ladrillo = (
                    (58, 56, 70)
                    if tema_efectivo == "cripta"
                    else ((68, 54, 52) if tema_efectivo == "osario" else (62, 58, 50))
                )
                for c_idx in range(num_cols):
                    col = col_inicio + c_idx
                    tx = rect.x + c_idx * TILE
                    t_rect = pygame.Rect(tx, rect.y, TILE, TILE)
                    tiene_arriba = (
                        fila > 0
                        and fila - 1 < len(self.filas)
                        and col < len(self.filas[fila - 1])
                        and self.filas[fila - 1][col] == "#"
                    )
                    pygame.draw.rect(surface, c_ladrillo, t_rect)
                    pygame.draw.rect(surface, c_corte, t_rect, 1)
                    start_y = rect.y + 7 if not tiene_arriba else rect.y
                    gx = tx + desplazamiento
                    if gx < tx + TILE:
                        pygame.draw.line(surface, c_corte, (gx, start_y), (gx, rect.bottom), 1)
                        pygame.draw.line(surface, (84, 82, 98), (gx + 1, start_y), (gx + 1, rect.bottom), 1)
                    if not tiene_arriba:
                        pygame.draw.rect(surface, c_bisel_top, (tx, rect.y, TILE, 3))
                        c_bisel_sub = (
                            max(0, c_bisel_top[0] - 30),
                            max(0, c_bisel_top[1] - 30),
                            max(0, c_bisel_top[2] - 30),
                        )
                        pygame.draw.rect(surface, c_bisel_sub, (tx, rect.y + 3, TILE, 2))
                        pygame.draw.rect(surface, c_corte, (tx, rect.y + 5, TILE, 2))
                continue

            # MODELO B3: PROC (Procedural Gótico con Autotiling Ortogonal y Estalactitas Orgánicas)
            for c_idx in range(num_cols):
                col = col_inicio + c_idx
                tx = rect.x + c_idx * TILE
                t_rect = pygame.Rect(tx, rect.y, TILE, TILE)

                tiene_arriba = (
                    fila > 0
                    and fila - 1 < len(self.filas)
                    and col < len(self.filas[fila - 1])
                    and self.filas[fila - 1][col] == "#"
                )
                tiene_abajo = (
                    fila + 1 < len(self.filas)
                    and col < len(self.filas[fila + 1])
                    and self.filas[fila + 1][col] == "#"
                )
                tiene_izq = (
                    col > 0
                    and self.filas[fila][col - 1] == "#"
                )
                tiene_der = (
                    col + 1 < len(self.filas[fila])
                    and self.filas[fila][col + 1] == "#"
                )

                if es_piso_nivel:
                    c_fill = color_piso_profundo if tiene_arriba else color_piso
                    pygame.draw.rect(surface, c_fill, t_rect)
                    if not tiene_arriba:
                        if tema_efectivo == "camposanto":
                            pygame.draw.rect(surface, color_arriba, (tx, rect.y, TILE, 4))
                            for bx in range(tx + 3, tx + TILE - 2, 6):
                                alt = 2 + ((bx * 11) % 5)
                                pygame.draw.line(surface, color_brizna, (bx, rect.y), (bx, rect.y - alt), 1)
                        pygame.draw.line(surface, MARFIL_XILOGRAFICO, (tx, rect.y + 1), (tx + TILE, rect.y + 1), 3)
                        for cx in (tx + 8, tx + 24):
                            pygame.draw.line(surface, TINTA_ABISMO, (cx, rect.y), (cx, rect.y + 3), 1)
                        pygame.draw.line(surface, TINTA_ABISMO, (tx, rect.y + 4), (tx + TILE, rect.y + 4), 2)
                        for hx in (tx + 4, tx + 12, tx + 20, tx + 28):
                            pygame.draw.line(surface, (20, 18, 26), (hx, rect.y + 6), (hx, rect.y + 12), 1)
                    else:
                        # Textura de sillares subterráneos en el suelo profundo
                        if (fila + col) % 2 == 0:
                            pygame.draw.rect(surface, color_borde, (tx + 3, rect.y + 4, TILE - 6, TILE - 8), 1, border_radius=2)
                    if not tiene_abajo:
                        pygame.draw.line(surface, color_borde, (tx, rect.bottom - 1), (tx + TILE, rect.bottom - 1), 1)
                    if not tiene_izq:
                        pygame.draw.line(surface, color_borde, (tx, rect.y), (tx, rect.bottom), 1)
                    if not tiene_der:
                        pygame.draw.line(surface, color_borde, (tx + TILE - 1, rect.y), (tx + TILE - 1, rect.bottom), 1)
                else:
                    # Formaciones de techo cavernoso (estalactitas orgánicas en filas 1..3 de cada piso)
                    es_formacion_techo = tiene_arriba and not tiene_abajo and (1 <= fila_rel <= 3)

                    if es_formacion_techo and not tiene_izq and not tiene_der:
                        # Punta cónica de estalactita tallada en roca
                        c_sombra = color_marco
                        c_roca_oscura = (max(0, color_cuerpo[0] - 12), max(0, color_cuerpo[1] - 12), max(0, color_cuerpo[2] - 10))
                        jit = ((col * 7 + fila * 3) % 5) - 2
                        punta_x = tx + TILE // 2 + jit
                        punta_y = rect.bottom - 1
                        pts_cono = [
                            (tx + 1, rect.y),
                            (tx + TILE - 1, rect.y),
                            (tx + TILE - 5, rect.y + 11),
                            (punta_x + 3, rect.y + 23),
                            (punta_x, punta_y),
                            (punta_x - 3, rect.y + 23),
                            (tx + 5, rect.y + 11),
                        ]
                        pygame.draw.polygon(surface, color_cuerpo, pts_cono)
                        # Faceta derecha en sombra para volumen 3D
                        pts_sombra = [
                            (tx + TILE // 2, rect.y),
                            (tx + TILE - 1, rect.y),
                            (tx + TILE - 5, rect.y + 11),
                            (punta_x, punta_y),
                        ]
                        pygame.draw.polygon(surface, c_roca_oscura, pts_sombra)
                        pygame.draw.polygon(surface, c_sombra, pts_cono, 2)
                        # Arista mineral iluminada y gota de salitre en la punta
                        pygame.draw.line(surface, SALITRE_CRIPTA, (tx + 5, rect.y + 2), (punta_x - 1, punta_y - 3), 1)
                        pygame.draw.circle(surface, SALITRE_CRIPTA, (punta_x, punta_y + 2), 1)
                        continue

                    if es_formacion_techo and (not tiene_izq or not tiene_der):
                        # Hombros inclinados de estalactita ancha (ej. '###' sobre '.#.')
                        c_roca_oscura = (max(0, color_cuerpo[0] - 10), max(0, color_cuerpo[1] - 10), max(0, color_cuerpo[2] - 8))
                        if not tiene_izq and tiene_der:
                            pts_hombro = [
                                (tx + 2, rect.y),
                                (tx + TILE, rect.y),
                                (tx + TILE, rect.bottom),
                                (tx + TILE - 10, rect.bottom - 4),
                                (tx + 8, rect.y + 14),
                            ]
                            pygame.draw.polygon(surface, color_cuerpo, pts_hombro)
                            pygame.draw.lines(surface, color_marco, False, [(tx + 2, rect.y), (tx + 8, rect.y + 14), (tx + TILE - 10, rect.bottom - 4), (tx + TILE, rect.bottom)], 2)
                            pygame.draw.line(surface, SALITRE_CRIPTA, (tx + 5, rect.y + 3), (tx + 12, rect.y + 16), 1)
                            continue
                        if tiene_izq and not tiene_der:
                            pts_hombro = [
                                (tx, rect.y),
                                (tx + TILE - 2, rect.y),
                                (tx + TILE - 8, rect.y + 14),
                                (tx + 10, rect.bottom - 4),
                                (tx, rect.bottom),
                            ]
                            pygame.draw.polygon(surface, c_roca_oscura, pts_hombro)
                            pygame.draw.lines(surface, color_marco, False, [(tx + TILE - 2, rect.y), (tx + TILE - 8, rect.y + 14), (tx + 10, rect.bottom - 4), (tx, rect.bottom)], 2)
                            continue

                    pygame.draw.rect(surface, color_cuerpo, t_rect)

                    # Borde superior expuesto al aire (Walkable Edge Cue)
                    if not tiene_arriba:
                        pygame.draw.line(surface, MARFIL_XILOGRAFICO, (tx, rect.y), (tx + TILE, rect.y), 3)
                        for cx in (tx + 8, tx + 24):
                            pygame.draw.line(surface, TINTA_ABISMO, (cx, rect.y), (cx, rect.y + 3), 1)
                        pygame.draw.line(surface, TINTA_ABISMO, (tx, rect.y + 3), (tx + TILE, rect.y + 3), 3)
                        for hx in (tx + 6, tx + 14, tx + 22):
                            pygame.draw.line(surface, (20, 18, 26), (hx, rect.y + 6), (hx, rect.y + 11), 1)

                    # Borde inferior expuesto (techo o losa flotante)
                    if not tiene_abajo:
                        pygame.draw.line(surface, color_marco, (tx, rect.bottom - 1), (tx + TILE, rect.bottom - 1), 2)
                        # Solo colgar pequeños picos de roca/salitre cuando el bloque pertenece al techo (tiene_arriba),
                        # evitando que peldaños de 1 tile de grosor tengan estalactitas colgando.
                        if tema_efectivo == "cripta" and tiene_arriba and fila_rel > 0:
                            salt_alt = 3 + (((col * 11) + fila) % 5)
                            pts_pico = [
                                (tx + 11, rect.bottom - 1),
                                (tx + 21, rect.bottom - 1),
                                (tx + 16, rect.bottom + salt_alt),
                            ]
                            pygame.draw.polygon(surface, color_cuerpo, pts_pico)
                            pygame.draw.polygon(surface, color_marco, pts_pico, 1)

                    # Caras laterales expuestas
                    if not tiene_izq:
                        pygame.draw.line(surface, color_marco, (tx, rect.y), (tx, rect.bottom), 2)
                    if not tiene_der:
                        pygame.draw.line(surface, color_marco, (tx + TILE - 1, rect.y), (tx + TILE - 1, rect.bottom), 2)

                    # Mortaja vertical sutil si hay ladrillos contiguos
                    if tiene_der:
                        pygame.draw.line(surface, color_marco, (tx + TILE - 1, rect.y + 2), (tx + TILE - 1, rect.bottom - 2), 1)

    # --- Función dibujar_decoraciones --- #
    def dibujar_decoraciones(self, surface, camara):
        tiempo = pygame.time.get_ticks() / 1000.0
        for decoracion in self.decoraciones:
            if not camara.is_on_screen(decoracion["rect"]):
                continue
            rect = camara.aplicar_rect(decoracion["rect"])
            tipo = decoracion["tipo"]

            if tipo == "t":
                self._dibujar_tumba(surface, rect)
            elif tipo == "c":
                self._dibujar_vela(surface, rect)
            elif tipo == "r":
                self._dibujar_raiz(surface, rect)
            elif tipo == "b":
                self._dibujar_brasero_y_osamenta(surface, rect, tiempo)
            elif tipo == "s":
                self._dibujar_estatua(surface, rect)
            elif tipo == "j":
                self._dibujar_cadena_colgante(surface, rect, tiempo)
            elif tipo == "g":
                self._dibujar_gargola(surface, rect)
            elif tipo == "u":
                self._dibujar_urna_cineraria(surface, rect)

    def _dibujar_tumba(self, surface, rect):
        base = rect.bottom - 2
        pygame.draw.rect(
            surface,
            PIEDRA,
            (rect.x + 8, rect.y + 8, 16, 22),
            border_radius=5,
        )
        pygame.draw.rect(
            surface,
            PIEDRA_OSCURA,
            (rect.x + 8, rect.y + 8, 16, 22),
            2,
            border_radius=5,
        )
        pygame.draw.line(
            surface,
            MUSGO,
            (rect.x + 9, rect.y + 25),
            (rect.x + 23, rect.y + 25),
            3,
        )
        pygame.draw.line(surface, PIEDRA_OSCURA, (rect.x + 16, rect.y + 12), (rect.x + 16, rect.y + 22), 2)
        pygame.draw.line(surface, PIEDRA_OSCURA, (rect.x + 12, rect.y + 16), (rect.x + 20, rect.y + 16), 2)
        pygame.draw.line(surface, (36, 38, 46), (rect.x + 10, base), (rect.x + 22, base), 2)

    def _dibujar_vela(self, surface, rect):
        x = rect.centerx
        import config
        estilo = config.resolver_estilo(getattr(config, "ESTILO_MUNDO", "AUTO"))
        if estilo != "NES":
            surface.blit(_obtener_halo_vela(), (x - 20, rect.y + 12 - 20))
        pygame.draw.rect(surface, (198, 188, 158), (x - 3, rect.y + 14, 6, 14), border_radius=2)
        pygame.draw.line(surface, NEGRO, (x, rect.y + 13), (x, rect.y + 9), 1)
        pygame.draw.polygon(
            surface,
            AMARILLO,
            [
                (x, rect.y + 2),
                (x + 4, rect.y + 9),
                (x, rect.y + 13),
                (x - 4, rect.y + 9),
            ],
        )
        pygame.draw.circle(surface, NARANJA, (x, rect.y + 10), 2)

    def _dibujar_raiz(self, surface, rect):
        x = rect.centerx
        pygame.draw.line(surface, MARRON_OSCURO, (x, rect.y), (x + 4, rect.y + 16), 4)
        pygame.draw.line(surface, MARRON_OSCURO, (x + 4, rect.y + 16), (x - 4, rect.y + 28), 3)
        pygame.draw.line(surface, MARRON_OSCURO, (x + 2, rect.y + 11), (x + 13, rect.y + 19), 2)
        pygame.draw.line(surface, MARRON_OSCURO, (x + 5, rect.y + 22), (x + 14, rect.y + 29), 2)

    def _dibujar_estatua(self, surface, rect):
        x = rect.centerx
        pygame.draw.rect(surface, PIEDRA, (x - 7, rect.y + 8, 14, 24), border_radius=4)
        pygame.draw.rect(surface, PIEDRA_OSCURA, (x - 7, rect.y + 8, 14, 24), 2, border_radius=4)
        pygame.draw.circle(surface, PIEDRA, (x, rect.y + 7), 6)
        pygame.draw.rect(surface, PIEDRA_OSCURA, (x - 10, rect.bottom - 4, 20, 4))
        pygame.draw.line(surface, MUSGO, (x - 5, rect.y + 12), (x + 4, rect.y + 26), 2)

    def _dibujar_cadena_colgante(self, surface, rect, tiempo):
        """'j': Cadena de hierro forjado colgante con oscilación pendular sutil."""
        x_base = rect.centerx
        balanceo = int(math.sin(tiempo * 1.8 + rect.x * 0.05) * 2)
        for idx, y_off in enumerate(range(0, TILE, 7)):
            cx = x_base + int((idx / 4.0) * balanceo)
            cy = rect.y + y_off
            # Sombra de eslabón
            pygame.draw.rect(surface, TINTA_ABISMO, (cx - 3, cy, 6, 8), border_radius=2)
            # Cuerpo de hierro forjado
            pygame.draw.rect(surface, (88, 86, 102), (cx - 2, cy + 1, 4, 6), 1, border_radius=2)
            # Brillo especular xilográfico
            if idx % 2 == 0:
                pygame.draw.line(surface, MARFIL_XILOGRAFICO, (cx - 1, cy + 2), (cx - 1, cy + 5), 1)
        # Gancho o grillete inferior si la celda de abajo está libre
        fila_abajo = (rect.y // TILE) + 1
        pygame.draw.circle(surface, (120, 118, 134), (x_base + balanceo, rect.bottom - 2), 3, 1)

    def _dibujar_gargola(self, surface, rect):
        """'g': Gárgola ornamental esculpida en piedra grabada con recorte cenital marfil."""
        cx = rect.centerx
        base_y = rect.bottom
        # Pedestal / ménsula de cornisa
        pygame.draw.rect(surface, TINTA_ABISMO, (cx - 11, base_y - 6, 22, 6))
        pygame.draw.rect(surface, (52, 50, 64), (cx - 10, base_y - 5, 20, 4))
        pygame.draw.line(surface, MARFIL_XILOGRAFICO, (cx - 10, base_y - 5), (cx + 10, base_y - 5), 1)

        # Alas plegadas en ángulo gótico
        pts_alas = [
            (cx - 12, base_y - 22),
            (cx - 4, base_y - 28),
            (cx, base_y - 18),
            (cx + 4, base_y - 28),
            (cx + 12, base_y - 22),
            (cx + 8, base_y - 6),
            (cx - 8, base_y - 6),
        ]
        pygame.draw.polygon(surface, TINTA_ABISMO, pts_alas)
        pygame.draw.polygon(surface, (44, 42, 54), pts_alas[1:-1])
        pygame.draw.lines(surface, MARFIL_XILOGRAFICO, False, [pts_alas[0], pts_alas[1], pts_alas[2], pts_alas[3], pts_alas[4]], 1)

        # Torso encorvado y cráneo cornudo
        pygame.draw.ellipse(surface, (58, 56, 70), (cx - 7, base_y - 20, 14, 14))
        pygame.draw.circle(surface, (68, 66, 82), (cx, base_y - 21), 5)
        pygame.draw.arc(surface, MARFIL_XILOGRAFICO, (cx - 5, base_y - 26, 10, 8), 0.2, math.pi - 0.2, 2)
        # Ojos rubí vigilantes
        pygame.draw.circle(surface, (210, 28, 50), (cx - 2, base_y - 21), 1)
        pygame.draw.circle(surface, (210, 28, 50), (cx + 2, base_y - 21), 1)

    def _dibujar_urna_cineraria(self, surface, rect):
        """'u': Urna funeraria tallada en piedra y bronce relicario sobre el suelo."""
        cx = rect.centerx
        base_y = rect.bottom - 1
        # Pie de la urna
        pygame.draw.rect(surface, TINTA_ABISMO, (cx - 6, base_y - 4, 12, 4))
        pygame.draw.line(surface, (218, 178, 86), (cx - 5, base_y - 3), (cx + 5, base_y - 3), 1)
        # Cuerpo bulboso con achurado
        cuerpo_rect = pygame.Rect(cx - 8, base_y - 18, 16, 14)
        pygame.draw.ellipse(surface, (44, 42, 54), cuerpo_rect)
        pygame.draw.ellipse(surface, TINTA_ABISMO, cuerpo_rect, 2)
        for hx in range(cx - 4, cx + 5, 3):
            pygame.draw.line(surface, TINTA_ABISMO, (hx, base_y - 15), (hx, base_y - 7), 1)
        # Franja heráldica dorada y cuello
        pygame.draw.line(surface, (218, 178, 86), (cx - 7, base_y - 12), (cx + 7, base_y - 12), 2)
        pygame.draw.rect(surface, (58, 56, 70), (cx - 5, base_y - 22, 10, 4))
        pygame.draw.line(surface, MARFIL_XILOGRAFICO, (cx - 6, base_y - 22), (cx + 6, base_y - 22), 2)
        # Tapa cónica con remate
        pygame.draw.polygon(surface, (218, 178, 86), [(cx - 5, base_y - 22), (cx + 5, base_y - 22), (cx, base_y - 27)])

    def _dibujar_brasero_y_osamenta(self, surface, rect, tiempo):
        """'b': Brasero espectral de pared con halo aditivo cian y restos óseos al pie."""
        cx = rect.centerx
        base_y = rect.bottom - 2
        import config
        estilo = config.resolver_estilo(getattr(config, "ESTILO_MUNDO", "AUTO"))

        # 1. Osamenta cruzada al pie con recorte marfil
        pygame.draw.line(surface, TINTA_ABISMO, (cx - 9, base_y - 4), (cx + 9, base_y + 1), 4)
        pygame.draw.line(surface, MARFIL_XILOGRAFICO, (cx - 8, base_y - 4), (cx + 8, base_y), 2)
        pygame.draw.line(surface, MARFIL_XILOGRAFICO, (cx + 8, base_y - 4), (cx - 8, base_y), 2)

        # 2. Cazoleta de hierro forjado a media altura
        py_copa = rect.y + 15
        pygame.draw.polygon(surface, TINTA_ABISMO, [(cx - 8, py_copa), (cx + 8, py_copa), (cx + 5, py_copa + 6), (cx - 5, py_copa + 6)])
        pygame.draw.line(surface, (218, 178, 86), (cx - 8, py_copa), (cx + 8, py_copa), 2)

        # 3. Llama espectral bioluminiscente (TURQUESA_ESPIRITU) + Halo BLEND_RGB_ADD
        pulso = int(math.sin(tiempo * 8.0 + rect.x * 0.1) * 2)
        pts_llama = [
            (cx, rect.y + 4 + pulso),
            (cx + 5, py_copa - 1),
            (cx, py_copa + 1),
            (cx - 5, py_copa - 1),
        ]
        pygame.draw.polygon(surface, (92, 220, 200), pts_llama)
        pygame.draw.circle(surface, (235, 255, 255), (cx, py_copa - 3), 2)

        if estilo != "NES":
            halo = _obtener_halo_brasero()
            surface.blit(halo, (cx - 48, py_copa - 52), special_flags=pygame.BLEND_RGB_ADD)

    # --- Función dibujar_peligros --- #
    def dibujar_peligros(self, surface, camara):
        tiempo = pygame.time.get_ticks() / 1000.0
        for peligro in self.peligros:
            if not camara.is_on_screen(peligro):
                continue
            rect = camara.aplicar_rect(peligro)
            cantidad = 3
            ancho = max(1, rect.width // cantidad)

            # Hoja de péndulo oscilante de Poe suspendida sobre fosos de pinchos
            if rect.width >= 32 and rect.y > 60:
                angulo = math.sin(tiempo * 2.2 + rect.x * 0.04) * 0.42
                pivote_x = rect.centerx
                pivote_y = max(-20, rect.top - 62)
                longitud = 52
                extremo_x = int(pivote_x + math.sin(angulo) * longitud)
                extremo_y = int(pivote_y + math.cos(angulo) * longitud)

                # Varilla de hierro forjado
                pygame.draw.line(surface, (42, 38, 48), (pivote_x, pivote_y), (extremo_x, extremo_y), 2)
                # Hoja curva de media luna afilada
                pygame.draw.arc(
                    surface,
                    (160, 165, 180),
                    (extremo_x - 13, extremo_y - 6, 26, 14),
                    3.14,
                    0.0,
                    2,
                )
                pygame.draw.arc(
                    surface,
                    (225, 230, 240),
                    (extremo_x - 11, extremo_y - 5, 22, 12),
                    3.14,
                    0.0,
                    1,
                )
                pygame.draw.circle(surface, CARMESÍ_SANGRE, (extremo_x, extremo_y + 3), 2)

            # Base de piedra oscura corroída
            pygame.draw.rect(
                surface,
                (38, 32, 36),
                (rect.x, rect.bottom - 5, rect.width, 5),
                border_radius=2,
            )
            # Mancha de sangre seca coagulada
            pygame.draw.ellipse(
                surface,
                CARMESÍ_SANGRE,
                (rect.x + rect.width // 2 - 8, rect.bottom - 3, 16, 4),
            )

            for i in range(cantidad):
                x = rect.x + i * ancho
                cx = x + ancho // 2

                # Puntas de hierro forjado: silueta oscura
                pygame.draw.polygon(
                    surface,
                    (48, 40, 38),
                    [
                        (x + 2, rect.bottom - 4),
                        (cx + 1, rect.top + 2),
                        (x + ancho - 1, rect.bottom - 4),
                    ],
                )
                # Triángulo metálico con herrumbre
                pygame.draw.polygon(
                    surface,
                    (112, 66, 50),
                    [
                        (x + 1, rect.bottom - 4),
                        (cx, rect.top + 1),
                        (x + ancho - 2, rect.bottom - 4),
                    ],
                )
                # Filo cortante de acero frío
                pygame.draw.line(
                    surface,
                    (190, 185, 200),
                    (cx, rect.top + 2),
                    (cx - 1, rect.bottom - 6),
                    1,
                )
                # Manchas de sangre seca en la punta
                pygame.draw.line(
                    surface,
                    CARMESÍ_SANGRE,
                    (cx, rect.top + 2),
                    (cx, rect.top + 6),
                    1,
                )
                pygame.draw.circle(
                    surface,
                    CARMESÍ_SANGRE,
                    (cx, rect.bottom - 5),
                    2,
                )

    # --- Función dibujar_meta --- #
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
