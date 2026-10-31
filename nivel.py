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
    ENEMIGO_ALTO,
    ENEMIGO_ANCHO,
    HUESO,
    JEFE_ALTO,
    JEFE_ANCHO,
    MARRON,
    MARRON_OSCURO,
    MUSGO,
    NEGRO,
    NARANJA,
    ORO,
    PASTO,
    PIEDRA,
    PIEDRA_FRIA,
    PIEDRA_OSCURA,
    ROJO,
    SANGRE,
    TILE,
    VERDE_OSCURO,
)
from entidades import (
    Alma,
    Araña,
    Cuervo,
    Custodio,
    Enemigo,
    EnemigoMelee,
    PalaRecogible,
    Polilla,
    RangoPowerUp,
    TotemProyectil,
)


DECORACIONES = {"t", "c", "r", "b", "s"}


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
        self.power_ups_rango = self._crear_power_ups_rango()
        self.plataformas = self._crear_plataformas()
        self.jefes = self._crear_jefes()
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

    # --- Función solidos_actuales --- #
    def solidos_actuales(self):
        return self.solidos + [plataforma.rect for plataforma in self.plataformas]

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
        for power_up in self.power_ups_rango:
            power_up.reiniciar()
        for cuervo in self.cuervos:
            cuervo.reiniciar()
        for polilla in self.polillas:
            polilla.reiniciar()
        for araña in self.aranias:
            araña.reiniciar()
        for plataforma in self.plataformas:
            plataforma.reiniciar()
        for jefe in self.jefes:
            jefe.reiniciar()

    # --- Función dibujar --- #
    def dibujar(self, surface, camara):
        self.dibujar_solidos(surface, camara)
        self.dibujar_plataformas(surface, camara)
        self.dibujar_decoraciones(surface, camara)
        self.dibujar_peligros(surface, camara)

        tiempo = pygame.time.get_ticks() / 1000
        for alma in self.almas:
            alma.dibujar(surface, camara, tiempo)
        for pala in self.palas:
            pala.dibujar(surface, camara, tiempo)
        for power_up in self.power_ups_rango:
            power_up.dibujar(surface, camara, tiempo)
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
        for plataforma in self.plataformas:
            if not camara.is_on_screen(plataforma.rect):
                continue
            rect = camara.aplicar_rect(plataforma.rect)
            pygame.draw.rect(surface, (63, 57, 68), rect, border_radius=3)
            pygame.draw.rect(surface, (28, 24, 32), rect, 2, border_radius=3)
            pygame.draw.line(
                surface,
                ORO,
                (rect.x + 5, rect.y + 3),
                (rect.right - 5, rect.y + 3),
                2,
            )
            pygame.draw.line(
                surface,
                (115, 105, 122),
                (rect.x + 8, rect.bottom - 6),
                (rect.right - 8, rect.bottom - 6),
                1,
            )

    # --- Función dibujar_solidos --- #
    def dibujar_solidos(self, surface, camara):
        if self.tema == "cripta":
            color_piso = PIEDRA_FRIA
            color_borde = (28, 30, 38)
            color_arriba = MUSGO
        elif self.tema == "osario":
            color_piso = (62, 45, 43)
            color_borde = (32, 22, 24)
            color_arriba = (96, 60, 54)
        else:
            color_piso = MARRON
            color_borde = MARRON_OSCURO
            color_arriba = PASTO

        for solido in self.solidos:
            if not camara.is_on_screen(solido):
                continue

            rect = camara.aplicar_rect(solido)
            es_piso = solido.y >= (self.num_filas - 2) * TILE

            if es_piso:
                pygame.draw.rect(surface, color_piso, rect)
                pygame.draw.rect(surface, color_borde, rect, 2)
                pygame.draw.rect(surface, color_arriba, (rect.x, rect.y, rect.width, 6))
                pygame.draw.rect(
                    surface,
                    color_borde,
                    (rect.x, rect.y + 8, rect.width, 2),
                )
                # Juntas de piedra.
                for x in range(rect.x + TILE, rect.right, TILE):
                    pygame.draw.line(
                        surface,
                        color_borde,
                        (x, rect.y + 12),
                        (x, rect.bottom - 1),
                        1,
                    )
            else:
                pygame.draw.rect(surface, PIEDRA, rect)
                pygame.draw.rect(surface, PIEDRA_OSCURA, rect, 2)
                pygame.draw.rect(
                    surface,
                    (92, 95, 105),
                    (rect.x + 2, rect.y + 2, rect.width - 4, 5),
                )
                if rect.width >= TILE:
                    pygame.draw.line(
                        surface,
                        PIEDRA_OSCURA,
                        (rect.x + 3, rect.bottom - 4),
                        (rect.right - 4, rect.bottom - 4),
                        1,
                    )

    # --- Función dibujar_decoraciones --- #
    def dibujar_decoraciones(self, surface, camara):
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
                self._dibujar_huesos(surface, rect)
            elif tipo == "s":
                self._dibujar_estatua(surface, rect)

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
        pygame.draw.circle(surface, (78, 52, 20), (x, rect.y + 12), 10)
        pygame.draw.circle(surface, (150, 100, 36), (x, rect.y + 12), 5)
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

    def _dibujar_huesos(self, surface, rect):
        x = rect.centerx
        y = rect.bottom - 6
        pygame.draw.line(surface, HUESO, (x - 8, y - 4), (x + 8, y + 2), 3)
        pygame.draw.line(surface, HUESO, (x + 8, y - 4), (x - 8, y + 2), 3)
        pygame.draw.circle(surface, HUESO, (x - 10, y + 1), 3)
        pygame.draw.circle(surface, HUESO, (x + 10, y - 3), 3)

    def _dibujar_estatua(self, surface, rect):
        x = rect.centerx
        pygame.draw.rect(surface, PIEDRA, (x - 7, rect.y + 8, 14, 24), border_radius=4)
        pygame.draw.rect(surface, PIEDRA_OSCURA, (x - 7, rect.y + 8, 14, 24), 2, border_radius=4)
        pygame.draw.circle(surface, PIEDRA, (x, rect.y + 7), 6)
        pygame.draw.rect(surface, PIEDRA_OSCURA, (x - 10, rect.bottom - 4, 20, 4))
        pygame.draw.line(surface, MUSGO, (x - 5, rect.y + 12), (x + 4, rect.y + 26), 2)

    # --- Función dibujar_peligros --- #
    def dibujar_peligros(self, surface, camara):
        for peligro in self.peligros:
            if not camara.is_on_screen(peligro):
                continue
            rect = camara.aplicar_rect(peligro)
            cantidad = 3
            ancho = max(1, rect.width // cantidad)

            # Base de piedra oscura
            pygame.draw.rect(
                surface,
                (44, 38, 42),
                (rect.x, rect.bottom - 5, rect.width, 5),
                border_radius=2,
            )
            # Mancha de sangre al pie de cada grupo
            pygame.draw.ellipse(
                surface,
                (*SANGRE, 140) if hasattr(SANGRE, '__len__') and len(SANGRE) == 3 else SANGRE,
                (rect.x + rect.width // 2 - 7, rect.bottom - 3, 14, 4),
            )

            for i in range(cantidad):
                x = rect.x + i * ancho
                cx = x + ancho // 2

                # Puntas óseas: triángulo oscuro de base (sombra)
                pygame.draw.polygon(
                    surface,
                    (80, 72, 68),
                    [
                        (x + 2, rect.bottom - 4),
                        (cx + 1, rect.top + 2),
                        (x + ancho - 1, rect.bottom - 4),
                    ],
                )
                # Triángulo principal (gris piedra)
                pygame.draw.polygon(
                    surface,
                    (148, 140, 128),
                    [
                        (x + 1, rect.bottom - 4),
                        (cx, rect.top + 1),
                        (x + ancho - 2, rect.bottom - 4),
                    ],
                )
                # Filo brillante (tono hueso)
                pygame.draw.line(
                    surface,
                    (220, 210, 190),
                    (cx, rect.top + 2),
                    (cx - 1, rect.bottom - 6),
                    1,
                )
                # Mancha de sangre individual (pequeño círculo)
                pygame.draw.circle(
                    surface,
                    SANGRE,
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

        pygame.draw.circle(surface, (42, 34, 22), (x, y + 22), 26)
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
