# Próxima sesión — IN CRYPTA: levels, room tests y referencia Castlevania

> Pegar este bloque (desde "## Contexto") como primer mensaje de la sesión nueva.

---

## Contexto

Proyecto: `/home/sanodesu/unahur/PlataformeroMDA` — IN CRYPTA, plataformero gótico 2D
(equipo 6, MDA / Programación 1 UNLP). Prototipo en pygame + export para **GDevelop 5**
(`export/gdevelop_nativo/IN_CRYPTA_NATIVO.json`) y export web/JS (`export/gdevelop/`).

Referencias de diseño: **Blasphemous**, **Castlevania** (PS1) y **Ender Lilies**.

## Qué hay que hacer, en este orden

### 1. Investigar diseño de niveles de los 3 juegos de referencia (OBLIGATORIO, primero)

Buscar **ejemplos concretos de diseño de niveles** en los 3 juegos de referencia, con
énfasis especial en **Castlevania de PlayStation 1** (Symphony of the Night y/o
Chronicles of the Moon). Objetivo: extraer patrones reutilizables, no cop layouts.

Para cada juego, documentar:

- **Estructura de salas**: cómo encadenan las salas (vertical scroll, horizontal scroll,
  combo de ambos), cuántas salas por área, dónde están los checkpoints/save rooms.
- **Ritmo de dificultad**: cómo sube la dificultad dentro de un área (intro segura →
  primera amenaza →rooms de mecánica → prueba → jefe) y entre áreas.
- **Diseño de plataformas**: densidad, altura máxima de salto, anchos de hueco que
  castigan, uso de paredes y ángulos, si se usan "one-way platforms", si las hay.
- **Ubicación del checkpoint y de la salida**: a qué distancia del inicio/fin de sala,
  relación con la dificultad.
- **Integración de enemigos**: si se mezclan con plataformas, si hay salas dedicated.
- **Hitos clave** (ejemplos concretos y citables): el nombre de la sala/área y qué la
  hace memorable o difícil (el inicio de cada área, los rooms con plataformas
  imposibles, el tramo pre-jefe, las salas de jefe).

Fuentes: wikis de Castlevania (Castlevania Wiki / GameFAQs), Maps/guides de
"Castlevania: Symphony of the Night" (el "Rings of Power"/mapas de la wiki), videos y
mapas de referencia de las áreas, y lo mismo para Blasphemous y Ender Lilies.
Guardar el resultado en `docs/referencias/diseno_niveles_referencia.md` con URLs y
fechas de consulta.

### 2. Arreglar los room tests (están ROTOS)

`niveles_rediseñados.py` es un módulo **generado por loops**, no diseñado a mano: produce
patrones degenerados tipo `#####...#####...` repetidos, con:

- huecos de 3 tiles en una fila que **están tapados por la fila sólida de abajo**
  ("un hueco tapado con tiles"),
- **dos spawns `P`** y **dos portones `G`** por mapa,
- plataformas repetidas cada 7/12 tiles ("plataformas repartidas por todos lados"),
- filas de distinta longitud (el parser las rellena, pero el mapa queda feo/roto).

Los 3 niveles principales (`niveles.py`) **sí están bien**: validados tile por tile contra
el export, con todas las almas alcanzables y los 3 completables por simulador.

Opciones (elegir una y justificarla):
- **(a)** Rediseñar los 3 room tests **a mano**, tomando el diseño documentado en
  `docs/niveles_rediseñados.txt` y `docs/ROOM_TESTS.md` (que son mejores que el módulo
  generado) y adaptándolos a la física nueva.
- **(b)** Reemplazar los room tests por **salas de práctica deliberadas** derivadas del
  análisis de los juegos de referencia del punto 1.
- **(c)** Si no dan tiempo: **borrar los 3 room tests v2** del selector y del export
  (quedan solo las 3 `SALA_PRUEBA_1/2/3` a mano) hasta poder hacerlos bien.

Regla dura para cualquier room test: una sola mecánica por sala, sin tiles que tapan
huecos, un solo `P` y un solo `G`, y validación con el simulador antes de exportar.

### 3. Revalidar las 3 salas de prueba a mano con la física nueva

`SALA_PRUEBA_1/2/3` (en `niveles.py`) se diseñaron con el salto viejo de 3 tiles. Con el
salto nuevo de 4 tiles, sus huecos de 6 tiles quedaron en zona ambigua (se cruzan sin
dash, aterrizando al borde). Reverificar y ajustar.

### 4. Confirmar visualmente en GDevelop

El usuario reportó que "el juego está roto". La geometría del export principal está
verificada (0 diferencias tile por tile contra los mapas ASCII), pero **nunca se miró el
proyecto abierto en GDevelop**. Hay que:

- abrir `export/gdevelop_nativo/IN_CRYPTA_NATIVO.json` en GDevelop 5 y revisar a ojo
  Nivel 1, 2 y 3: que se vea el piso, que los huecos estén abiertos, que no haya
  plataformas fantasma;
- si algo se ve mal, capturar el síntoma exacto (qué nivel, qué columna, qué fila) antes
  de tocar código;
- descartar también que el usuario haya abierto `IN_CRYPTA_ROOM_TESTS_NATIVO.json` (ese
  está roto, ver punto 2) o el `.autosave` / `.bak` viejos.

## Física actual (ya ajustada, no tocar sin medir)

`config.py`: `SALTO = -620` (4 tiles de alto), `COYOTE_TIME = 0.18`, `JUMP_BUFFER = 0.15`,
`DASH_VELOCIDAD = 560`, `DASH_DURACION = 0.20`, `DASH_COOLDOWN = 0.60`, `GRAVEDAD = 1500`,
`VELOCIDAD = 250`, `TILE = 32`. En el export nativo: `jumpSpeed 620`, `jumpSustainTime 0`
(crítico: con 0.36 el salto nativo era de 9 tiles), coyote 0.18, buffer 0.15,
`acceleration/deceleration 20000` (instantáneo, igual que el prototipo).

Alcances medidos (aterrizando con el cuerpo apoyado): salto puro 206 px (6.4 tiles),
salto+dash 267-311 px, salto+dash desde cornisa 348-380 px. Por eso: hueco de 3-4 tiles
= salto, 5 = salto justo, 7 = dash obligatorio, 10 = solo desde cornisa.

## Herramientas de validación (ya existen, usar siempre)

- `/tmp/valida.py` — validador de niveles (techos, corredores de salto, escalones de 2
  tiles, entidades dentro de bloques).
- `/tmp/sim2.py` — clase `Mundo` con `almas_alcanzables()`: simula trayectorias reales.
- `/tmp/sim.py` — piloto automático: `simulador(mapa, meta_col)` devuelve si se completa.
- `/tmp/build_n1c.py`, `/tmp/build_n23.py` — builders de los niveles validados.
- `/tmp/verificar_export.py` — reconstruye la grilla del JSON exportado y la compara
  tile por tile con los mapas ASCII (debe dar 0 diferencias).

Comandos:

```bash
cd /home/sanodesu/unahur/PlataformeroMDA
python3 tools/generar_proyecto_nativo.py       # export GDevelop
python3 tools/export_gdevelop.py                # export web/JS
.venv/bin/python tests/test_logica.py           # suite python (TESTS_INCRYPTA_OK)
node tests/test_runtime_gdevelop.js             # suite runtime (TESTS_GDEVELOP_OK)
python3 /tmp/verificar_export.py                # export == mapas
```

## Criterios de aceptación

1. `docs/referencias/diseno_niveles_referencia.md` existe con patrones concretos de los 3
   juegos (Castlevania PS1 primero), con URLs.
2. Ningún mapa del juego tiene tiles tapando un hueco, ni spawns duplicados, ni portones
   duplicados. El validador lo reporta en 0 errores.
3. Las 3 salas de prueba a mano revalidadas con la física nueva.
4. `TESTS_INCRYPTA_OK` y `TESTS_GDEVELOP_OK`, y `/tmp/verificar_export.py` sin
   diferencias.
5. El usuario **confirma a ojo en GDevelop** que el juego se ve bien (piso visible,
   huecos abiertos, sin plataformas fantasma) antes de dar por cerrado.

## Avisar al usuario

En español rioplatense, corto. Cuando el export esté regenerado, avisar que ya puede
testear en GDevelop y qué archivo abrir.
