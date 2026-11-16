#---- Importamos librerias y entidades ----#
from collections import defaultdict
import math

import pygame

from config import (
    ARANA_ALTO,
    ENEMIGO_ALTO,
    ENEMIGO_ANCHO,
    INCENSARIO_ALTO,
    INCENSARIO_ANCHO,
    JEFE_ALTO,
    JEFE_ANCHO,
    MINIJEFE_ALTO,
    MINIJEFE_ANCHO,
    TILE,
)
from entidades import (
    Alma,
    Araña,
    BloqueCripta,
    CompuertaArena,
    Cuervo,
    Custodio,
    DashPowerUp,
    Enemigo,
    EnemigoMelee,
    FarolCheckpoint,
    IncensarioRebote,
    LosaQuebradiza,
    MiniJefe,
    MuroMovilCompuerta,
    PalaRecogible,
    Polilla,
    RangoPowerUp,
)
from escena.render_nivel import (
    RenderNivelMixin,
    _PALETAS_SOLIDOS,
    _obtener_halo_brasero,
    _obtener_halo_meta,
    _obtener_halo_vela,
)


DECORACIONES = {"t", "c", "r", "b", "s", "j", "g", "u"}


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

    def reiniciar(self):
        self.rect = pygame.Rect(self.inicial_rect)
        self.tiempo = 0.0
        self.dx = 0
        self.dy = 0

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


class Nivel(RenderNivelMixin):
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
        self._posiciones = self._indexar_simbolos()

        self.spawn = self._buscar_spawn()
        self.meta = self._buscar_meta()
        if self.spawn is None:
            raise ValueError("Falta la P de spawn en el nivel")
        if self.meta is None:
            raise ValueError("Falta la G de meta en el nivel")
        self._poblar_nivel()

    def _poblar_nivel(self):
        self.solidos = self._crear_solidos()
        self.almas = self._crear_almas()
        self.enemigos = self._crear_enemigos()
        self.enemigos_melee = self._crear_enemigos_melee()
        self.decoraciones = self._crear_decoraciones()
        self.peligros = self._crear_peligros()
        self.palas = self._crear_palas()
        self.power_ups_dash = self._crear_power_ups_dash()
        self.power_ups_rango = self._crear_power_ups_rango()
        self.checkpoints = self._crear_checkpoints()
        self.plataformas = self._crear_plataformas()
        self.losas_quebradizas = self._crear_losas_quebradizas()
        self.bloques_cripta = self._crear_bloques_cripta()
        self.compuertas_arena = self._crear_compuertas_arena()
        self.incensarios = self._crear_incensarios()
        self.jefes = self._crear_jefes()
        self.minijefes = self._crear_minijefes()
        self.muros_minijefe = self._crear_muros_minijefe()
        self.cuervos = self._crear_cuervos()
        self.polillas = self._crear_polillas()
        self.aranias = self._crear_aranias()
        self.total_almas = len(self.almas)

    def _indexar_simbolos(self):
        """Indexa en una sola pasada las coordenadas (columna, fila) de cada simbolo."""
        indice = defaultdict(list)
        for fila, texto in enumerate(self.filas):
            for columna, simbolo in enumerate(texto):
                if simbolo != ".":
                    indice[simbolo].append((columna, fila))
        return indice

    def _buscar_spawn(self):
        for columna, fila in self._posiciones.get("P", ()):
            # El jugador mide 30 px; +2 lo deja apoyado en el tile.
            return (columna * TILE + 4, fila * TILE + 2)
        return None

    def _buscar_meta(self):
        for columna, fila in self._posiciones.get("G", ()):
            return pygame.Rect(columna * TILE + 6, fila * TILE + 2, 20, 30)
        return None

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

    def _crear_almas(self):
        return [
            Alma(pygame.Rect(col * TILE + 8, fila * TILE + 8, 16, 16))
            for col, fila in self._posiciones.get("o", ())
        ]

    def _crear_entidades_patrulleras(self, simbolo, clase_entidad, ancho=ENEMIGO_ANCHO, alto=ENEMIGO_ALTO):
        """Instancia entidades patrulleras estándar y calcula sus limites de plataforma."""
        entidades = []
        for columna, fila in self._posiciones.get(simbolo, ()):
            rect = pygame.Rect(
                columna * TILE + (TILE - ancho) // 2,
                fila * TILE + (TILE - alto),
                ancho,
                alto,
            )
            minimo_x, maximo_x = self._limites_patrulla(columna, fila)
            entidades.append(clase_entidad(rect, minimo_x, maximo_x))
        return entidades

    def _crear_altares_genericos(self, simbolo, clase_entidad, offset_x=6, offset_y=2, ancho=20, alto=30):
        """Instancia altares y objetos recogibles de 20x30 en la grilla."""
        return [
            clase_entidad(pygame.Rect(
                columna * TILE + offset_x,
                fila * TILE + offset_y,
                ancho,
                alto,
            ))
            for columna, fila in self._posiciones.get(simbolo, ())
        ]

    def _crear_enemigos(self):
        return self._crear_entidades_patrulleras("E", Enemigo)

    def _crear_decoraciones(self):
        decoraciones = []
        for fila, texto in enumerate(self.filas):
            for columna, simbolo in enumerate(texto):
                if simbolo in DECORACIONES:
                    decoraciones.append({
                        "tipo": simbolo,
                        "rect": pygame.Rect(columna * TILE, fila * TILE, TILE, TILE),
                    })
        return decoraciones

    def _crear_palas(self):
        return self._crear_altares_genericos("W", PalaRecogible)

    def _crear_power_ups_dash(self):
        return self._crear_altares_genericos("D", DashPowerUp)

    def _crear_power_ups_rango(self):
        return self._crear_altares_genericos("X", RangoPowerUp)

    def _crear_checkpoints(self):
        return self._crear_altares_genericos("F", FarolCheckpoint)

    def _crear_losas_quebradizas(self):
        return [
            LosaQuebradiza(pygame.Rect(col * TILE, fila * TILE, TILE, TILE))
            for col, fila in self._posiciones.get("~", ())
        ]

    def _crear_incensarios(self):
        return [
            IncensarioRebote(pygame.Rect(
                col * TILE + (TILE - INCENSARIO_ANCHO) // 2,
                fila * TILE + (TILE - INCENSARIO_ALTO) // 2,
                INCENSARIO_ANCHO,
                INCENSARIO_ALTO,
            ))
            for col, fila in self._posiciones.get("I", ())
        ]

    def _crear_cuervos(self):
        cuervos = []
        for columna, fila in self._posiciones.get("C", ()):
            rect = pygame.Rect(columna * TILE + 4, fila * TILE + 4, 24, 24)
            cuervos.append(Cuervo(
                rect,
                centro_x=columna * TILE + TILE // 2,
                centro_y=fila * TILE + TILE // 2,
                radio=3 * TILE,
                velocidad=1.5,
            ))
        return cuervos

    def _crear_polillas(self):
        polillas = []
        for columna, fila in self._posiciones.get("m", ()):
            texto = self.filas[fila]
            rect = pygame.Rect(
                columna * TILE + (TILE - ENEMIGO_ANCHO) // 2,
                fila * TILE + (TILE - ENEMIGO_ALTO),
                ENEMIGO_ANCHO,
                ENEMIGO_ALTO,
            )
            minimo_x, maximo_x = self._limites_patrulla(columna, fila)
            if maximo_x - minimo_x <= 3 * TILE:
                izq = columna
                while izq > max(1, columna - 4) and texto[izq - 1] not in ("#", "^"):
                    izq -= 1
                der = columna
                while der < min(self.columnas - 2, columna + 4) and texto[der + 1] not in ("#", "^"):
                    der += 1
                minimo_x = izq * TILE
                maximo_x = (der + 1) * TILE
            polillas.append(Polilla(rect, minimo_x, maximo_x))
        return polillas

    def _crear_bloques_cripta(self):
        return [
            BloqueCripta(pygame.Rect(col * TILE, fila * TILE, TILE, TILE))
            for col, fila in self._posiciones.get("=", ())
        ]

    def _crear_compuertas_arena(self):
        """Agrupa columnas contiguas de '|' en compuertas verticales de arena."""
        por_col = defaultdict(list)
        for col, fila in self._posiciones.get("|", ()):
            por_col[col].append(fila)
        compuertas = []
        for col, filas in sorted(por_col.items()):
            filas.sort()
            ini = prev = filas[0]
            for f in filas[1:]:
                if f == prev + 1:
                    prev = f
                else:
                    compuertas.append(CompuertaArena(pygame.Rect(col * TILE, ini * TILE, TILE, (prev - ini + 1) * TILE)))
                    ini = prev = f
            compuertas.append(CompuertaArena(pygame.Rect(col * TILE, ini * TILE, TILE, (prev - ini + 1) * TILE)))
        return compuertas

    def _crear_aranias(self):
        aranias = []
        for columna, fila in self._posiciones.get("A", ()):
            rect = pygame.Rect(
                columna * TILE + (TILE - ENEMIGO_ANCHO) // 2,
                fila * TILE + (TILE - ARANA_ALTO),
                ENEMIGO_ANCHO,
                ARANA_ALTO,
            )
            lim_izq, lim_der = self._limites_patrulla(columna, fila)
            minimo_x = max(lim_izq + 8, (columna - 6) * TILE)
            maximo_x = min(lim_der - 8, (columna + 7) * TILE)
            if maximo_x - minimo_x < 2 * TILE:
                minimo_x, maximo_x = lim_izq, lim_der
            aranias.append(Araña(rect, minimo_x, maximo_x))
        return aranias

    def _crear_jefes(self):
        jefes = []
        for columna, fila in self._posiciones.get("B", ()):
            rect = pygame.Rect(
                columna * TILE - (JEFE_ANCHO - TILE) // 2,
                (fila + 1) * TILE - JEFE_ALTO,
                JEFE_ANCHO,
                JEFE_ALTO,
            )
            fila_txt = self.filas[fila]
            c_izq = columna
            while c_izq > max(0, columna - 20) and fila_txt[c_izq - 1] not in ("#", "|"):
                c_izq -= 1
            c_der = columna + 1
            while c_der < min(self.columnas, columna + 21) and fila_txt[c_der] not in ("#", "|"):
                c_der += 1
            minimo_x = max(0, c_izq * TILE + 2)
            maximo_x = min(self.ancho - JEFE_ANCHO, c_der * TILE - JEFE_ANCHO - 2)
            if maximo_x <= minimo_x:
                minimo_x = max(0, (columna - 20) * TILE)
                maximo_x = min(self.ancho - JEFE_ANCHO, (columna + 20) * TILE)
            jefes.append(Custodio(rect, minimo_x, maximo_x))
        return jefes

    def _crear_minijefes(self):
        minijefes = []
        for columna, fila in self._posiciones.get("K", ()):
            rect = pygame.Rect(
                columna * TILE - (MINIJEFE_ANCHO - TILE) // 2,
                (fila + 1) * TILE - MINIJEFE_ALTO,
                MINIJEFE_ANCHO,
                MINIJEFE_ALTO,
            )
            lim_izq, lim_der = self._limites_patrulla(columna, fila)
            if lim_der - lim_izq >= 4 * TILE:
                minimo_x = lim_izq + 8
                maximo_x = max(minimo_x + TILE, lim_der - MINIJEFE_ANCHO - 8)
            else:
                minimo_x = max(0, (columna - 10) * TILE)
                maximo_x = min(self.ancho - MINIJEFE_ANCHO, (columna + 10) * TILE)
            minijefes.append(MiniJefe(rect, minimo_x, maximo_x))
        return minijefes

    def _crear_muros_minijefe(self):
        """Crea los 3 muros compuerta emergentes de abajo hacia arriba distribuidos en la arena del Mini-Boss."""
        muros = []
        for columna, fila in self._posiciones.get("K", ()):
            lim_izq, lim_der = self._limites_patrulla(columna, fila)
            if lim_der - lim_izq >= 16 * TILE:
                base_y = (fila + 1) * TILE
                centro_col = (lim_izq + lim_der) // (2 * TILE)
                for offset_col in (-8, 0, 8):
                    col_m = max((lim_izq // TILE) + 5, min((lim_der // TILE) - 6, centro_col + offset_col))
                    muros.append(MuroMovilCompuerta(col_m * TILE, base_y, ancho=TILE, alto_max=3 * TILE))
        return muros

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

    def _crear_enemigos_melee(self):
        return self._crear_entidades_patrulleras("L", EnemigoMelee)

    def _crear_peligros(self):
        return [
            pygame.Rect(col * TILE + 4, fila * TILE + 12, TILE - 8, TILE - 12)
            for col, fila in self._posiciones.get("^", ())
        ]

    def _limites_patrulla(self, columna, fila):
        """Recorta la patrulla al tramo de suelo sin pinchos ni muros laterales."""
        fila_piso = fila + 1
        if fila_piso >= self.num_filas or self.filas[fila_piso][columna] != "#":
            return (columna * TILE - TILE, (columna + 1) * TILE + TILE)

        piso = self.filas[fila_piso]
        izq = columna
        while izq > 0 and piso[izq - 1] == "#":
            izq -= 1
        der = columna
        while der + 1 < self.columnas and piso[der + 1] == "#":
            der += 1

        fila_enemigo = self.filas[fila]
        libre_izq = columna
        while libre_izq > izq and fila_enemigo[libre_izq - 1] not in ("^", "#"):
            libre_izq -= 1
        libre_der = columna
        while libre_der < der and fila_enemigo[libre_der + 1] not in ("^", "#"):
            libre_der += 1

        return max(izq, libre_izq) * TILE, (min(der, libre_der) + 1) * TILE

    def actualizar(self, dt):
        for plataforma in self.plataformas:
            plataforma.actualizar(dt)
        for losa in getattr(self, "losas_quebradizas", []):
            losa.actualizar(dt)
        for incensario in getattr(self, "incensarios", []):
            incensario.actualizar(dt)
        for cp in self.checkpoints:
            if hasattr(cp, "actualizar_dt"):
                cp.actualizar_dt(dt)
        for compuerta in getattr(self, "compuertas_arena", []):
            compuerta.actualizar(dt)
        for muro in getattr(self, "muros_minijefe", []):
            muro.actualizar(dt)

    def solidos_actuales(self):
        return (
            self.solidos
            + [plataforma.rect for plataforma in self.plataformas]
            + [losa.rect for losa in getattr(self, "losas_quebradizas", []) if losa.activa]
            + [bloque.rect for bloque in getattr(self, "bloques_cripta", []) if not bloque.roto]
            + [compuerta.rect for compuerta in getattr(self, "compuertas_arena", []) if compuerta.cerrada]
            + [muro.rect for muro in getattr(self, "muros_minijefe", []) if muro.es_solido()]
        )

    def _tema_efectivo(self, fila):
        """Aplica el subtema de cripta en pisos subterraneos de nivel vertical."""
        tema = getattr(self, "tema", "camposanto")
        return "cripta" if (fila >= 18 and tema == "camposanto") else tema

    def _tiene_solido(self, fila, col):
        return (
            0 <= fila < len(self.filas)
            and 0 <= col < len(self.filas[fila])
            and self.filas[fila][col] == "#"
        )

    def reiniciar(self):
        """Devuelve todas las entidades y obstaculos del nivel a su estado inicial."""
        grupos = (
            self.almas,
            self.enemigos,
            self.enemigos_melee,
            self.palas,
            self.power_ups_dash,
            self.power_ups_rango,
            self.checkpoints,
            self.cuervos,
            self.polillas,
            self.aranias,
            self.plataformas,
            self.minijefes,
            self.jefes,
            getattr(self, "losas_quebradizas", ()),
            getattr(self, "bloques_cripta", ()),
            getattr(self, "compuertas_arena", ()),
            getattr(self, "muros_minijefe", ()),
            getattr(self, "incensarios", ()),
        )
        for grupo in grupos:
            for item in grupo:
                item.reiniciar()
