# Exportador a GDevelop — paridad con el juego Pygame

> Objetivo: **el mismo juego**. El proyecto GDevelop tiene que reproducir el
> juego de Pygame escena por escena: misma geometría, mismos sprites en el
> mismo lugar, mismas colisiones, mismo comportamiento de plataformas y
> enemigos. El exportador es la herramienta; el juego es la fuente de verdad.

Todo lo que está en este documento se investigó sobre el proyecto real
(GDevelop 5.6.285 flatpak + el juego en Pygame) y se comprobó con
`tools/verificar_paridad.py`.

---

## 1. Qué estaba roto (la investigación)

El export anterior (`tools/generar_proyecto_nativo.py`, 2839 líneas) generaba un
proyecto que **se veía distinto al juego**. Las causas, con la evidencia:

### 1.1 La cámara mostraba menos mundo del que se juega

| | Pygame | Export anterior |
|---|---|---|
| Resolución de pantalla | 1280×720 (`config.py`) | 1920×1080 |
| Zoom de cámara | 1 (1 px = 1 px) | **2** |
| Mundo visible | 1280×720 | **960×540** |

Con zoom 2 en una ventana de 1920 de ancho se veían 960 px de mundo, pero el
juego muestra 1280. Consecuencias:

* La cámara se limitaba con `nivel.ancho - 1280` (suponiendo 1280 px visibles),
  pero en realidad sólo se veían 960 → **el final del nivel era inalcanzable**
  para la cámara (hasta 320 px de nivel nunca se veían).
* El HUD está diseñado sobre 1280×720 (`GAME_W`/`GAME_H`) y la capa "UI" tenía
  zoom 2 → **la barra inferior y el texto de pista quedaban fuera de pantalla**.

**Arreglo**: el zoom se deriva de la resolución —
`GAME_ZOOM = CAMARA_ZOOM = 1.25` → el mundo visible es exactamente
1280×720, igual que en Pygame, y el HUD entra entero.

### 1.2 Las plataformas no se movían

Las instancias de `PlataformaMovil` tenían sus variables (`origen_x`,
`origen_y`, `amplitud`, `velocidad`, `fase`, `eje`) pero **no existía ningún
evento que las moviera**: en GDevelop eran cajas estáticas, y el nivel 1 tiene
3 plataformas que en el juego oscilan. Era el síntoma más visible de
"los movimientos de las plataformas están corridos".

**Arreglo**: regla genérica (`tools/exportador/reglas.py`) que reproduce la
fórmula del juego (`nivel.py::PlataformaMovil.actualizar`):

```
desplazamiento = sin(tiempo * velocidad + fase) * amplitud
x = round(origen_x + desplazamiento)      # eje horizontal
y = round(origen_y + desplazamiento)      # eje vertical
```

En GDevelop la posición se pone con la acción `SetXY` (objeto, x, y,
relativo=0) y las expresiones `Sine(...)` y `TimeFromStart()`. Las dos
coordenadas van como valores absolutos: la que no se mueve es la de origen y
la otra es la fórmula del juego.

### 1.3 Los sprites se deformaban

La textura y la caja de la instancia no tenían la misma proporción:

| Sprite | Textura | Caja | Proporción |
|---|---|---|---|
| Enemy | 52×64 (26×32 a 2×) | 26×26 | 0,81 vs 1,00 → aplastado |
| PlataformaMovil | 192×64 (96×32 a 2×) | 160×32 | 3,00 vs 5,00 → estirado |

La causa: las texturas se dibujaban a mano con un tamaño fijo, pero las
instancias usaban el tamaño real de la entidad.

**Arreglo**: las texturas se generan con el **código de dibujo del propio
juego** (`tools/exportador/sprites.py`) y con el **tamaño exacto** del rect de
la entidad; para las plataformas hay una textura por ancho
(`PlataformaMovil_160x32`, …) y un objeto por plataforma (su recorrido es
propio).

### 1.4 El jugador aparecía corrido

El export lo ponía en `(spawn.x - 4, spawn.y - 1)`; el juego lo crea
exactamente en `nivel.spawn`.

**Arreglo**: la instancia usa `nivel.spawn` sin ajustes.

### 1.5 El export quedó viejo (y el juego cambió)

El juego se sigue editando (`niveles.py`): los niveles pasaron a 120×12,
96×12 y 90×12 columnas. El export anterior seguía con los mapas anteriores:
**119 tiles de colisión diferentes en el nivel 2 y 202 en el nivel 3**, y las
plataformas con la fase y el origen viejos.

**Arreglo**: el export lee el modelo del juego **en el momento de generarlo**,
y `tools/verificar_paridad.py` compara el JSON exportado contra el modelo vivo
y falla si no coinciden.

### 1.6 Faltaban tipos de entidad

El export no conocía `EnemigoMelee` (L), `TotemProyectil` (O), `Cuervo` (C),
`Polilla` (m), `Araña` (A) ni del power-up de rango (X): no había objeto,
instancia ni sprite. Los mapas actuales ya no los usan, pero el exportador
debe poder exportarlos.

**Arreglo**: cada tipo de entidad tiene un adaptador (fila en una tabla) con su
objeto, su textura, su z, sus variables y su regla.

### 1.7 El exportador era "cosa por cosa"

2.839 líneas con decisiones enterradas en el código:

* `pala_inicial = indice == 3`, `siguiente = "Victoria" if indice == total`,
  `pista.replace("J","A") if numero == 2`, `SALAS_PRUEBA[:3]`,
  `for indice in range(1, 4)`.
* `eventos_nivel` era un bloque de 690 líneas; `eventos_jefe` 237;
  `escena_sala` 213.
* La geometría estaba **reimplementada** (los sólidos, el spawn, la puerta se
  volvían a calcular) en vez de leerse del juego.

**Arreglo**: la arquitectura nueva (sección 2).

---

### 1.8 La cámara no tenía suavizado ni sacudida

El Pygame (`camara.py::Camara.actualizar`) interpola la cámara hacia el
jugador (`CAMARA_SUAVIZADO = 7.0`, suavizado exponencial) y la sacude cuando
pasa algo (dash, pala, daño, jefe). El export pegaba la cámara al jugador y
no tenía sacudida: se notaba en el juego y no era "el mismo juego".

**Arreglo**: variables globales `cam_x`, `cam_y`, `sacudida_f`, `sacudida_t`;
un evento por frame que interpola la cámara y le suma un offset aleatorio
que cae linealmente durante la duración de la sacudida; y los mismos
disparadores que en el Pygame:

| Evento | Fuerza | Duración |
| --- | --- | --- |
| Dash | 3.5 | 0.10 |
| La pala mata a un morador | 5.0 | 0.12 |
| Daño al jugador | 9.0 | 0.22 |
| El jefe dispara sus ondas | 8.0 | 0.20 |
| El jefe cambia de fase | 11.0 | 0.26 |
| El jefe muere | 8.0 | 0.18 |

---

### 1.9 Los eventos no coincidían con la API de GDevelop 5.6

El export usaba formatos de evento de GDevelop 4 (y algunos inventados), así
que el IDE los marcaba en rojo ("parámetros inválidos") y no ejecutaba nada:
la cámara no seguía al jugador, las plataformas no se movían y el HUD no
aparecía.

**Arreglo**: los formatos salen de las declaraciones reales de la extensión
(`AddAction` / `AddCondition` del código fuente de GDevelop 5.6):

| Acción / condición | Parámetros |
| --- | --- |
| `SetXY` | objeto, signo, x, signo, y |
| `SetX` / `ChangeAnimation` | objeto, signo, valor |
| `CameraCenterX` / `CameraCenterY` | signo, valor, capa, cámara |
| `ZoomCamera` | zoom, capa, cámara |
| `CollisionNP` | objeto 1, objeto 2, invertir |
| `Delete` | objeto |
| `Create` | objeto, x, y, capa |
| `Scene` | nombre de escena, reiniciar |
| `PlaySound` | sonido, repetir, volumen, pitch |
| `KeyFromTextJustPressed` | tecla |
| `PlatformBehavior::Gravity` | objeto, comportamiento, signo, valor |

Además:

* El `seno` de GDevelop se escribe `sin(...)`, no `Sine(...)`.
* La acción de cámara se llama `CameraCenterX`/`CameraCenterY` (las
  `SetCameraCenterX` son alias viejos).
* La capa UI lleva su propia cámara con zoom 1 (el HUD se dibuja en pixels de
  pantalla) y la capa base con zoom 1.25 (1280×720 de mundo visible).
* El HUD necesita **instancias**: los objetos de texto y las barras existían
  pero no tenían instancia, así que no se veían.
* Los sprites usan ancla explícita en la esquina (`centerPoint` con
  `automatic: false`): en GDevelop 5 el ancla por defecto es el centro, y
  eso corría todas las instancias media imagen.

Para que esto no vuelva a pasar, `tools/validar_eventos_gd.py` contrasta
cada evento del export con la tabla de declaraciones de GDevelop 5.6 y
verifica que cada objeto usado exista en la escena:

```bash
.venv/bin/python tools/validar_eventos_gd.py   # -> EVENTOS_OK
```

---

## 2. La arquitectura nueva

```
tools/exportador/
├── manifiesto.py   # QUÉ escenas existen y con qué reglas (datos puros)
├── modelo.py       # el modelo real del juego (nivel.py) leído como datos
├── adaptadores.py  # CÓMO se traduce cada tipo de entidad a GDevelop
├── sprites.py      # las texturas, dibujadas con el código del juego
├── reglas.py       # el comportamiento que sale de los datos (plataformas)
├── pipeline.py     # modelo + adaptadores → objetos e instancias
└── gdevelop.py     # primitivas del formato de proyecto (uid, escena, ...)

tools/generar_proyecto_nativo.py   # CLI delgado: manifiesto → proyecto + assets
tools/verificar_paridad.py         # criterio de aceptación: export == juego
```

El flujo completo es:

```
manifiesto (datos)  →  modelo (nivel.py)  →  adaptadores  →  objetos/instancias
                                    ↓
                          reglas (eventos)
                                    ↓
                    proyecto GDevelop  →  verificar_paridad.py
```

### 2.1 Manifiesto (`manifiesto.py`)

Declara las escenas. **No hay `if indice == 3`**: el encadenado de la campaña se
deriva del orden de la lista y el resto son datos.

```python
@dataclass(frozen=True)
class EscenaSpec:
    clave: str            # "nivel_1" / "sala_2"
    nombre: str           # "Nivel 1" (nombre de la escena en GDevelop)
    mapa: str
    nombre_juego: str
    pista: str
    tema: str
    titulo: str           # texto del HUD
    hud: str              # ayuda de teclas inicial
    hud_sin_pala: str
    fondo: str            # recurso de fondo ("FondoNivel1" / "FondoSala1")
    pala_inicial: bool
    siguiente: str | None # escena siguiente (None = victoria)
    destino_muerte: str
    reiniciar_vidas: bool
    es_sala: bool
```

Agregar un nivel nuevo = agregar una entrada en `niveles.py` (el manifiesto lo
recoge solo). Agregar una sala = ampliar `SALAS_PRUEBA`.

### 2.2 Modelo (`modelo.py`)

Lee el juego y devuelve un modelo uniforme: `Entidad(kind, rect, variables)`.
Cada tipo de entidad tiene un extractor (`_almas`, `_enemigos`, `_plataformas`,
…) y una tabla `EXTRACTORES`. **La geometría no se recalcula: se pide al
juego.**

### 2.3 Adaptadores (`adaptadores.py`)

Una fila por tipo de entidad:

```python
"enemigo": Adaptador(
    "enemigo", "Enemy", "Enemy", z=5,
    comportamiento="enemigo", regla="patrulla",
    variables=("dir", "min_x", "max_x"),
    sprite=(ENEMIGO_ANCHO, ENEMIGO_ALTO),
),
```

Dice: qué objeto de GDevelop es, qué textura usa, en qué capa y con qué z,
qué variables se exportan, cómo se ancla (esquina/centro) y qué regla lo
mueve. **Agregar un tipo de entidad = agregar una fila** (y su extractor en
`modelo.py` y su renderer en `sprites.py`).

### 2.4 Sprites (`sprites.py`)

Cada textura se dibuja con el **método `dibujar` del juego** sobre una
superficie del tamaño exacto del rect. Por eso el sprite y la caja coinciden y
GDevelop no deforma nada.

```python
def render_enemigo(ancho, alto):
    surface = _superficie(ancho, alto)
    Enemigo(pygame.Rect(0, 0, ancho, alto), 0, 0).dibujar(surface, _camara(), 0.0)
    return surface
```

### 2.5 Reglas (`reglas.py`)

El comportamiento que depende de los datos (hoy: las plataformas). Se generan
desde la entidad y sus variables, así que tampoco hay nada escrito para un
nivel concreto.

---

## 3. Verificación

```bash
.venv/bin/python tools/generar_proyecto_nativo.py   # genera el proyecto
.venv/bin/python tools/verificar_paridad.py         # compara contra el juego
.venv/bin/python tests/test_logica.py               # suite del juego
node tests/test_runtime_gdevelop.js                 # suite del export web
```

Además hay una previsualización **headless** del export en el runtime real de
GDevelop (GDJS), sin abrir el IDE:

```bash
.venv/bin/python tools/previsualizar_nativo.py --escena "Nivel 1" --salida /tmp/x.png
```

La herramienta arma una carpeta con el runtime de GDJS + los assets + el
proyecto como `data.js`, la sirve por HTTP y la abre en Chromium con
chromedriver: imprime la consola del navegador y saca una captura. Sirve para
ver la escena (geometría, sprites, posiciones) y para que cualquier error de
GDevelop aparezca en la consola.

**Límite**: el runtime ejecuta la lógica de la escena desde el código que
genera el IDE (`<Escena>Code` en los `code*.js`), no desde el array `events`
de la escena. Por eso la previsualización **muestra** la escena pero **no
ejecuta** los eventos: para verlos hay que abrir el proyecto en el IDE (o
exportarlo desde ahí). Lo que sí se puede verificar sin IDE son los datos,
los objetos, las instancias y las texturas.

El generador además **borra los assets que el proyecto ya no referencia**
(`limpiar_assets`), así no se acumulan texturas ni sonidos viejos (los que
el generador cambió de nombre o dejó de generar).

`verificar_paridad.py` compara, escena por escena:

* los tiles de colisión contra el mapa,
* la posición y el tamaño del jugador, del portón, de las almas, los pinchos,
  las palas, los enemigos y el jefe,
* las plataformas (posición + variables + que exista la regla de movimiento),
* la proporción textura/caja de cada sprite (para detectar deformaciones),
* que no falte ningún tipo de entidad del juego.

Estado actual: **PARIDAD_OK** (0 diferencias; antes: 88).

---

## 4. Reglas para tocar el exportador

1. **No se toca el código del juego.** El exportador lee; si hay que cambiar
   una regla del juego, se cambia en el juego y el exportador lo sigue.
2. Después de cualquier cambio en `niveles.py` o en el exportador:
   regenerar (`generar_proyecto_nativo.py`) y verificar
   (`verificar_paridad.py`). El juego cambia seguido: un export viejo es
   silenciosamente incorrecto.
3. **El IDE tiene el proyecto viejo en memoria**: hay que reabrir
   `export/gdevelop_nativo/IN_CRYPTA_NATIVO.json` antes de previsualizar (un
   Ctrl+S del IDE pisa el archivo regenerado).
4. Las constantes de física del export salen de `config.py`; no volver a
   escribirlas a mano (ya no queda ningún `620`/`1500`/`900` hardcodeado en los
   comportamientos).

---

## 5. Pendientes

* **Reglas de comportamiento que faltan**: las entidades que no están en los
  mapas actuales (`EnemigoMelee`, `Polilla`, `Araña`, `Cuervo`, `Totem`,
  power-up de rango) se exportan **visualmente** en cuanto aparecen en un
  mapa, pero todavía no tienen su regla de eventos (volar, orbitar, disparar).
  Sus adaptadores ya están listos (`regla="patrulla"` / `"orbita"` / `"totem"`).
* **Caja de colisión del jugador**: el Pygame usa 24×30 y el export 32×32
  (la caja del sprite). Se puede ajustar con una máscara de colisión
  personalizada.
* **Flash de pantalla**: el Pygame pinta un destello blanco al recibir daño,
  al matar con la pala y al phases del jefe (`self.flash`). En GDevelop falta
  (se puede con un objeto rectangular blanco sobre la capa de UI y una
  opacidad animada).
* **Partículas**: el Pygame tiene partículas (salto, pala, daño, jefe). En el
  export no hay: se pueden hacer con el objeto "partículas" de GDevelop o con
  eventos propios.
* **Verificación visual dentro del IDE**: la acción `SetXY` y las expresiones
  `Sine(...)` / `TimeFromStart()` se escribieron con los nombres internos que
  declara la propia extensión de GDevelop 5.6 (sePueden ver en la tabla de
  strings del binario `libGD.wasm` que trae el flatpak), pero falta
  confirmarlos abriendo el preview: la prueba de fuego es que **las
  plataformas se muevan** y que el jugador las monte. Si el IDE muestra la
  acción con los parámetros en rojo, es cuestión de corregir el orden de los
  parámetros en `reglas.py::regla_plataforma`.
* **`tools/generar_proyecto_rediseñado.py`** (room tests) sigue con su propio
  camino hardcodeado y pisa los assets de `export/gdevelop_nativo/assets/`;
  debería usar el mismo pipeline.
* **Export web** (`tools/export_gdevelop.py`, PixiJS): es otra herramienta y
  otro runtime; este documento es sobre el export nativo de GDevelop.

---

## 6. Datos de GDevelop 5.6 verificados (para no volver a buscarlos)

Saquelos del binario del flatpak
(`~/.local/share/flatpak/app/io.gdevelop.ide/current/active/files/GDevelop/resources/GDJS/Runtime`)
y de `libGD.wasm` (la tabla de strings del core):

* **Nombre de las acciones de posición**: `SetXY` (posición), `SetCenterX` /
  `SetCenterY` (centro), `SetAngle`, `SetScale`, `SetZOrder`, `SetXOffset` /
  `SetYOffset`. **No existen** `SetX` / `SetY` / `ChangeX` / `ChangeY`.
* **Expresiones**: `Sine`, `Cosine`, `TimeFromStart()` (el tiempo de la
  escena), `Object::X` / `Object::Y`, `GlobalVariable(nombre)`.
* **Comportamiento de plataforma**: `PlatformBehavior` (la plataforma),
  `PlatformBehavior::PlatformerObjectBehavior` (el jugador), con acciones
  `PlatformBehavior::SimulateLeftKey/RightKey/JumpKey`,
  `PlatformBehavior::PlatformerObjectBehavior::AbortJump`,
  `PlatformBehavior::Gravity`, `PlatformBehavior::ChangePlatformType`.
* **`jumpSustainTime`** es el tiempo durante el cual la velocidad vertical se
  mantiene **mientras se mantiene la tecla**; al soltarla empieza la caída
  (no hay corte duro de salto). Para el corte de salto del Pygame
  (`CORTE_SALTO`) hay que usar `AbortJump` con `KeyFromTextReleased`.
* **`ignoreDefaultControls: true`** en el `PlatformerObjectBehavior` hace que
  el objeto no obedezca al teclado: el movimiento tiene que simularse con
  `SimulateLeftKey` / `SimulateRightKey` / `SimulateJumpKey`.
* **La hitbox por defecto** de un sprite es su rectángulo (aunque el PNG sea
  casi transparente) y la de un tiled sprite es el rectángulo del objeto.
* **La cámara**: el zoom multiplica; el mundo visible es
  `ventana / zoom`. El `PlatformBehavior` detecta que se movió la plataforma
  comparando la posición del objeto con la del frame anterior
  (`platformruntimebehavior.ts`), así que cambiar la posición del objeto la
  mueve de verdad.
* **Ciclo de la escena**: las funciones de eventos de una escena son
  `onFirstSceneLoaded`, `onSceneLoaded`, `onScenePreEvents` (cada frame, antes
  de la hoja de eventos) y `onScenePostEvents` (cada frame, después). La hoja
  de eventos de la escena (`layout.events`) es lo que corre cada frame; el
  runtime la ejecuta a través del código generado por el IDE
  (`<Escena>Code`).
