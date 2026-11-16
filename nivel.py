#---- Importamos librerias y clases ----#

from collections import defaultdict
import math

import pygame

import config
from config import (
    AMARILLO,
    ARANA_ALTO,
    CARMESÍ_SANGRE,
    ENEMIGO_ALTO,
    ENEMIGO_ANCHO,
    INCENSARIO_ALTO,
    INCENSARIO_ANCHO,
    JEFE_ALTO,
    JEFE_ANCHO,
    MARFIL_XILOGRAFICO,
    MARRON_OSCURO,
    MINIJEFE_ALTO,
    MINIJEFE_ANCHO,
    MUSGO,
    NEGRO,
    NEGRO_NOCHE,
    NARANJA,
    ORO,
    ORO_LITÚRGICO,
    PIEDRA,
    PIEDRA_OSCURA,
    SALITRE_CRIPTA,
    SANGRE,
    TILE,
    TINTA_ABISMO,
    TURQUESA_ÁNIMA,
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


DECORACIONES = {"t", "c", "r", "b", "s", "j", "g", "u"}

_HALO_VELA = None
_HALO_META = None
_HALO_BRASERO_ESPECTRAL = None

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


def _construir_halo_radial(diametro, radio_max, color_rgb, alpha_max):
    """Genera una superficie circular con caida cuadratica de opacidad."""
    halo = pygame.Surface((diametro, diametro), pygame.SRCALPHA)
    centro = diametro // 2
    for r in range(radio_max, 1, -2):
        norm = r / float(radio_max)
        alfa = int(alpha_max * (1.0 - norm * norm))
        pygame.draw.circle(halo, (*color_rgb, alfa), (centro, centro), r)
    return halo.convert_alpha()


def _obtener_halo_brasero():
    """Halo cálido y tenue para braseros 'b' en segundo plano (similar a velas)."""
    global _HALO_BRASERO_ESPECTRAL
    if _HALO_BRASERO_ESPECTRAL is None:
        _HALO_BRASERO_ESPECTRAL = _construir_halo_radial(36, 15, (235, 145, 58), 14)
    return _HALO_BRASERO_ESPECTRAL


def _obtener_halo_vela():
    """Halo translucido calido atenuado para velas decorativas de fondo."""
    global _HALO_VELA
    if _HALO_VELA is None:
        _HALO_VELA = _construir_halo_radial(36, 15, (255, 185, 65), 16)
    return _HALO_VELA


def _obtener_halo_meta():
    """Halo translucido suave para el portal/porton de meta."""
    global _HALO_META
    if _HALO_META is None:
        _HALO_META = _construir_halo_radial(64, 30, (255, 205, 95), 35)
    return _HALO_META


#---- Clase PlataformaMovil ----#
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


#---- Clase Nivel ----#
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
        self._posiciones = self._indexar_simbolos()

        self.spawn = self._buscar_spawn()
        self.meta = self._buscar_meta()
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

        if self.spawn is None:
            raise ValueError("Falta la P de spawn en el nivel")
        if self.meta is None:
            raise ValueError("Falta la G de meta en el nivel")

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

    def _dibujar_cuerpo_plataforma(self, surface, rect, init_rect, plataforma, tema_efectivo, tiempo):
        """Renderiza la tapa del sarcofago ferreo, cornisa superior y engranajes."""
        pygame.draw.rect(surface, NEGRO_NOCHE, (rect.x + 2, rect.bottom, rect.width - 4, 4), border_radius=2)
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

        colores_losa = {
            "osario": ((60, 46, 48), (28, 20, 22)),
            "cripta": ((50, 54, 68), (22, 24, 34)),
        }
        color_losa, color_marco = colores_losa.get(tema_efectivo, ((56, 50, 62), (24, 20, 28)))
        pygame.draw.rect(surface, color_losa, rect, border_radius=3)
        pygame.draw.rect(surface, color_marco, rect, 2, border_radius=3)

        pygame.draw.line(surface, MARFIL_XILOGRAFICO, (rect.x + 2, rect.y + 1), (rect.right - 2, rect.y + 1), 3)
        for cx_cincel in range(rect.x + 8, rect.right - 4, 16):
            pygame.draw.line(surface, TINTA_ABISMO, (cx_cincel, rect.y), (cx_cincel, rect.y + 3), 1)
        pygame.draw.line(surface, TINTA_ABISMO, (rect.x + 2, rect.y + 4), (rect.right - 2, rect.y + 4), 2)
        for ax in range(rect.x + 6, rect.right - 6, 8):
            pygame.draw.line(surface, (18, 16, 24), (ax, rect.y + 6), (ax, rect.y + 11), 1)

        if rect.width >= 48:
            cx = rect.centerx
            pygame.draw.line(surface, color_marco, (cx, rect.y + 4), (cx, rect.bottom - 3), 3)
            pygame.draw.line(surface, color_marco, (cx - 10, rect.y + 9), (cx + 10, rect.y + 9), 3)
            pygame.draw.line(surface, ORO_LITÚRGICO, (cx, rect.y + 5), (cx, rect.bottom - 4), 1)
            pygame.draw.line(surface, ORO_LITÚRGICO, (cx - 9, rect.y + 9), (cx + 9, rect.y + 9), 1)
        elif rect.width >= 32:
            pygame.draw.line(surface, ORO_LITÚRGICO, (rect.x + 8, rect.y + 9), (rect.right - 8, rect.y + 9), 1)

        giro = (plataforma.rect.x + plataforma.rect.y) * 0.12
        for eng_x in (rect.x + 5, rect.right - 6):
            eng_y = rect.centery + 1
            pygame.draw.circle(surface, (32, 26, 36), (eng_x, eng_y), 4)
            pygame.draw.circle(surface, (168, 134, 72), (eng_x, eng_y), 3, 1)
            dx_g, dy_g = int(math.cos(giro) * 3), int(math.sin(giro) * 3)
            pygame.draw.line(surface, (198, 162, 92), (eng_x - dx_g, eng_y - dy_g), (eng_x + dx_g, eng_y + dy_g), 1)

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

    def _dibujar_formacion_techo(self, surface, rect, tx, fila, col, tiene_izq, tiene_der, paleta):
        """Dibuja estalactitas y hombros inclinados en formaciones de techo."""
        color_cuerpo = paleta["cuerpo"]
        color_marco = paleta["marco"]
        if not tiene_izq and not tiene_der:
            c_roca_oscura = (max(0, color_cuerpo[0] - 12), max(0, color_cuerpo[1] - 12), max(0, color_cuerpo[2] - 10))
            jit = ((col * 7 + fila * 3) % 5) - 2
            punta_x, punta_y = tx + TILE // 2 + jit, rect.bottom - 1
            pts_cono = [
                (tx + 1, rect.y), (tx + TILE - 1, rect.y), (tx + TILE - 5, rect.y + 11),
                (punta_x + 3, rect.y + 23), (punta_x, punta_y), (punta_x - 3, rect.y + 23), (tx + 5, rect.y + 11),
            ]
            pts_sombra = [(tx + TILE // 2, rect.y), (tx + TILE - 1, rect.y), (tx + TILE - 5, rect.y + 11), (punta_x, punta_y)]
            pygame.draw.polygon(surface, color_cuerpo, pts_cono)
            pygame.draw.polygon(surface, c_roca_oscura, pts_sombra)
            pygame.draw.polygon(surface, color_marco, pts_cono, 2)
            pygame.draw.line(surface, SALITRE_CRIPTA, (tx + 5, rect.y + 2), (punta_x - 1, punta_y - 3), 1)
            pygame.draw.circle(surface, SALITRE_CRIPTA, (punta_x, punta_y + 2), 1)
            return True

        c_roca_oscura = (max(0, color_cuerpo[0] - 10), max(0, color_cuerpo[1] - 10), max(0, color_cuerpo[2] - 8))
        if not tiene_izq and tiene_der:
            pts_hombro = [(tx + 2, rect.y), (tx + TILE, rect.y), (tx + TILE, rect.bottom), (tx + TILE - 10, rect.bottom - 4), (tx + 8, rect.y + 14)]
            pygame.draw.polygon(surface, color_cuerpo, pts_hombro)
            pygame.draw.lines(surface, color_marco, False, [(tx + 2, rect.y), (tx + 8, rect.y + 14), (tx + TILE - 10, rect.bottom - 4), (tx + TILE, rect.bottom)], 2)
            pygame.draw.line(surface, SALITRE_CRIPTA, (tx + 5, rect.y + 3), (tx + 12, rect.y + 16), 1)
            return True
        if tiene_izq and not tiene_der:
            pts_hombro = [(tx, rect.y), (tx + TILE - 2, rect.y), (tx + TILE - 8, rect.y + 14), (tx + 10, rect.bottom - 4), (tx, rect.bottom)]
            pygame.draw.polygon(surface, c_roca_oscura, pts_hombro)
            pygame.draw.lines(surface, color_marco, False, [(tx + TILE - 2, rect.y), (tx + TILE - 8, rect.y + 14), (tx + 10, rect.bottom - 4), (tx, rect.bottom)], 2)
            return True
        return False

    def _dibujar_solido_proc(self, surface, rect, fila, col_inicio, num_cols, tema_efectivo, paleta):
        fila_rel = fila % 18
        es_piso_nivel = fila_rel >= 15
        for c_idx in range(num_cols):
            col = col_inicio + c_idx
            tx = rect.x + c_idx * TILE
            t_rect = pygame.Rect(tx, rect.y, TILE, TILE)
            tiene_arriba = self._tiene_solido(fila - 1, col)
            tiene_abajo = self._tiene_solido(fila + 1, col)
            tiene_izq = self._tiene_solido(fila, col - 1)
            tiene_der = self._tiene_solido(fila, col + 1)

            if es_piso_nivel:
                c_fill = paleta["piso_profundo"] if tiene_arriba else paleta["piso"]
                pygame.draw.rect(surface, c_fill, t_rect)
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
                    pygame.draw.rect(surface, paleta["borde"], (tx + 3, rect.y + 4, TILE - 6, TILE - 8), 1, border_radius=2)
                if not tiene_abajo:
                    pygame.draw.line(surface, paleta["borde"], (tx, rect.bottom - 1), (tx + TILE, rect.bottom - 1), 1)
                if not tiene_izq:
                    pygame.draw.line(surface, paleta["borde"], (tx, rect.y), (tx, rect.bottom), 1)
                if not tiene_der:
                    pygame.draw.line(surface, paleta["borde"], (tx + TILE - 1, rect.y), (tx + TILE - 1, rect.bottom), 1)
                continue

            if tiene_arriba and not tiene_abajo and (1 <= fila_rel <= 3):
                if self._dibujar_formacion_techo(surface, rect, tx, fila, col, tiene_izq, tiene_der, paleta):
                    continue

            color_cuerpo, color_marco = paleta["cuerpo"], paleta["marco"]
            pygame.draw.rect(surface, color_cuerpo, t_rect)
            if not tiene_arriba:
                pygame.draw.line(surface, MARFIL_XILOGRAFICO, (tx, rect.y), (tx + TILE, rect.y), 3)
                for cx in (tx + 8, tx + 24):
                    pygame.draw.line(surface, TINTA_ABISMO, (cx, rect.y), (cx, rect.y + 3), 1)
                pygame.draw.line(surface, TINTA_ABISMO, (tx, rect.y + 3), (tx + TILE, rect.y + 3), 3)
                for hx in (tx + 6, tx + 14, tx + 22):
                    pygame.draw.line(surface, (20, 18, 26), (hx, rect.y + 6), (hx, rect.y + 11), 1)
            if not tiene_abajo:
                pygame.draw.line(surface, color_marco, (tx, rect.bottom - 1), (tx + TILE, rect.bottom - 1), 2)
                if tema_efectivo == "cripta" and tiene_arriba and fila_rel > 0:
                    salt_alt = 3 + (((col * 11) + fila) % 5)
                    pts_pico = [(tx + 11, rect.bottom - 1), (tx + 21, rect.bottom - 1), (tx + 16, rect.bottom + salt_alt)]
                    pygame.draw.polygon(surface, color_cuerpo, pts_pico)
                    pygame.draw.polygon(surface, color_marco, pts_pico, 1)
            if not tiene_izq:
                pygame.draw.line(surface, color_marco, (tx, rect.y), (tx, rect.bottom), 2)
            if not tiene_der:
                pygame.draw.line(surface, color_marco, (tx + TILE - 1, rect.y), (tx + TILE - 1, rect.bottom), 2)
            else:
                pygame.draw.line(surface, color_marco, (tx + TILE - 1, rect.y + 2), (tx + TILE - 1, rect.bottom - 2), 1)

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
        # Gancho o grillete inferior
        pygame.draw.circle(surface, (120, 118, 134), (x_base + balanceo, rect.bottom - 2), 3, 1)

    def _dibujar_gargola(self, surface, rect):
        """'g': Acrotera / gárgola arquitectónica de piedra erosionada en segundo plano (sin rasgos de enemigo)."""
        cx = rect.centerx
        base_y = rect.bottom
        # Zócalo escalonado de piedra pizarra oscura
        pygame.draw.rect(surface, (16, 18, 24), (cx - 11, base_y - 7, 22, 7))
        pygame.draw.rect(surface, (30, 32, 42), (cx - 9, base_y - 6, 18, 5))
        pygame.draw.line(surface, (44, 48, 60), (cx - 9, base_y - 6), (cx + 9, base_y - 6), 1)
        # Musgo húmedo en la junta del pedestal
        pygame.draw.line(surface, (38, 54, 44), (cx - 7, base_y - 2), (cx + 5, base_y - 2), 2)

        # Contrafuerte alado tallado en bajorrelieve pétreo (bajo contraste, fundido al fondo)
        pts_piedra = [
            (cx - 10, base_y - 19),
            (cx - 6, base_y - 25),
            (cx, base_y - 22),
            (cx + 6, base_y - 25),
            (cx + 10, base_y - 19),
            (cx + 7, base_y - 7),
            (cx - 7, base_y - 7),
        ]
        pygame.draw.polygon(surface, (18, 20, 28), pts_piedra)
        pygame.draw.polygon(surface, (28, 30, 40), pts_piedra[1:-1])
        pygame.draw.lines(surface, (42, 46, 58), False, [pts_piedra[0], pts_piedra[1], pts_piedra[2], pts_piedra[3], pts_piedra[4]], 1)

        # Busto pétreo erosionado y grietas verticales de cantería (sin ojos ni brillos)
        pygame.draw.rect(surface, (24, 26, 36), (cx - 5, base_y - 21, 10, 14), border_radius=3)
        pygame.draw.line(surface, (16, 18, 24), (cx, base_y - 20), (cx, base_y - 9), 1)
        pygame.draw.line(surface, (38, 54, 44), (cx - 4, base_y - 14), (cx - 1, base_y - 12), 1)

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
        """'b': Brasero y fogata tenue de fondo con tonos apagados para no competir con faroles."""
        cx = rect.centerx
        base_y = rect.bottom - 2
        estilo = config.resolver_estilo(getattr(config, "ESTILO_MUNDO", "AUTO"))

        # 1. Osamenta discreta al pie en piedra/ceniza de bajo contraste
        pygame.draw.line(surface, (18, 16, 22), (cx - 8, base_y - 4), (cx + 8, base_y), 3)
        pygame.draw.line(surface, (78, 72, 78), (cx - 7, base_y - 4), (cx + 7, base_y), 2)
        pygame.draw.line(surface, (78, 72, 78), (cx + 7, base_y - 4), (cx - 7, base_y), 2)

        # 2. Cazoleta de hierro envejecido a media altura
        py_copa = rect.y + 16
        pygame.draw.polygon(surface, (20, 18, 26), [(cx - 7, py_copa), (cx + 7, py_copa), (cx + 4, py_copa + 6), (cx - 4, py_copa + 6)])
        pygame.draw.line(surface, (108, 84, 58), (cx - 7, py_copa), (cx + 7, py_copa), 1)

        # 3. Llama cálida tipo vela de fondo (sin cian intenso ni blanco brillante)
        pulso = int(math.sin(tiempo * 7.0 + rect.x * 0.1) * 1.5)
        if estilo != "NES":
            surface.blit(_obtener_halo_brasero(), (cx - 18, py_copa - 22))
        pts_llama = [
            (cx, rect.y + 7 + pulso),
            (cx + 4, py_copa - 2),
            (cx, py_copa + 1),
            (cx - 4, py_copa - 2),
        ]
        pygame.draw.polygon(surface, (205, 130, 56), pts_llama)
        pygame.draw.circle(surface, (238, 182, 92), (cx, py_copa - 3), 2)

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
