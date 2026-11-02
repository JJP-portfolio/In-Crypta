# Guía de Python y pygame — Salto Pixel

> Esta guía explica el proyecto desde cero. No hace falta saber pygame antes:
> empezamos por el loop, seguimos por las estructuras de Python y terminamos en la
> física y el código archivo por archivo.
>
> Código: `~/unahur/TallerDeProgramacion1/plataformero_pygame/`.
> Ejercicios: `EJERCICIOS.md`.

---

## 1. Qué vas a aprender

Al terminar de leer y tocar este proyecto vas a poder:

- Crear una ventana y un loop a 60 FPS con `pygame`.
- Usar `Surface`, `Rect`, `draw`, `font`, `event` y `key`.
- Mover algo con delta time, sin depender de los FPS.
- Implementar gravedad, salto, coyote time y jump buffer.
- Detectar colisiones AABB y resolverlas por ejes.
- Leer datos de un mapa ASCII y convertirlos en objetos.
- Separar el código en módulos y clases con una responsabilidad cada uno.
- Escribir tests de lógica que corran sin abrir una ventana.

La progresión sigue el material de Taller de Programación I:

| Unidad | Dónde aparece |
|---|---|
| C1: datos, variables, listas, strings | `config.py`, mapas ASCII, HUD |
| C2: `for`, `range`, acumuladores | parser de niveles, monedas, dibujo |
| C3: `if/elif/else`, operadores | física, colisiones, estados |
| C4: funciones, parámetros, `return` | todo el proyecto |
| C5: `while`, flags, `break` | loop principal, estados |
| Clean Code | nombres, constantes, funciones chicas, tests |

---

## 2. Instalación y ejecución

Desde la carpeta del proyecto:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

Si ya existe `.venv` (como en esta máquina):

```bash
source .venv/bin/activate
python main.py
```

Para salir: `ESC` o cerrar la ventana.

### Tests

```bash
PYTHONPATH=. SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy \
  .venv/bin/python tests/test_logica.py
```

`SDL_VIDEODRIVER=dummy` hace que pygame no abra una ventana real. Es lo mismo que usan
los smokes de PsicoWorld.

---

## 3. Mapa del proyecto

```
main.py       → crea Juego y llama run()
juego.py      → loop, eventos, estados, HUD, fondo y overlays
config.py     → constantes: pantalla, física, colores
niveles.py    → mapas ASCII
nivel.py      → parser + dibujo de plataformas, monedas y meta
entidades.py  → Jugador, Enemigo, Moneda
camara.py     → seguimiento y transformación mundo → pantalla
tests/        → pruebas de lógica y del juego headless
```

La dirección de las dependencias es:

```text
main.py
  └── juego.py
       ├── nivel.py ── entidades.py ── config.py
       ├── camara.py ── config.py
       └── niveles.py
```

`config.py` no importa nada del juego. `entidades.py` no conoce `Juego` ni `Nivel`.
Eso permite probar cada pieza por separado.

---

## 4. El game loop

El corazón de cualquier juego es un ciclo:

```python
while corriendo:
    dt = reloj.tick(FPS) / 1000
    procesar_eventos()
    actualizar(dt)
    dibujar()
    pygame.display.flip()
```

En `juego.py`:

```python
def run(self):
    while self.corriendo:
        dt = min(self.reloj.tick(FPS) / 1000, MAX_DT)
        self.procesar_eventos()
        self.actualizar(dt)
        self.dibujar()
        pygame.display.flip()
```

### `pygame.time.Clock`

`reloj.tick(FPS)` hace dos cosas:

1. Espera lo necesario para no superar `FPS`.
2. Devuelve cuántos milisegundos pasaron desde el tick anterior.

Dividir por 1000 da segundos. Ese valor es `dt` (delta time).

### Por qué `dt`

Si moves un rectángulo `4 px` por frame:

- a 60 FPS recorre `240 px/s`;
- a 30 FPS recorre `120 px/s`.

En cambio, si haces:

```python
rect.x += velocidad * dt
```

recorre `velocidad` píxeles por segundo sin importar los FPS.

`MAX_DT = 1/30` evita que un tirón grande (por ejemplo, arrastrar la ventana) teletransporte
al jugador a través de una pared.

### Eventos vs estado del teclado

Hay dos formas de leer input y no son intercambiables:

| Uso | Herramienta | Por qué |
|---|---|---|
| Saltar, pausar, confirmar | `pygame.event.get()` + `KEYDOWN` | Querés una acción por pulsación |
| Caminar, mantener dirección | `pygame.key.get_pressed()` | Querés saber si la tecla sigue apretada |

En el proyecto:

- `ESPACIO` se detecta con `KEYDOWN` para llamar `pedir_salto()`.
- `A/D/flechas` se leen con `get_pressed()` dentro de `Jugador.actualizar`.
- `KEYUP` de `ESPACIO` llama `soltar_salto()` para el salto variable.

Si usás `get_pressed()` para saltar, el personaje salta todos los frames mientras
mantenés la tecla. Si usás `KEYDOWN` para caminar, solo te movés un paso por pulsación.

---

## 5. Coordenadas, Surface y Rect

### Sistema de coordenadas

Pygame usa:

```text
(0, 0) ─────────────► x
  │
  │
  ▼
  y
```

- `x` crece hacia la derecha.
- `y` crece hacia abajo.
- Un `Rect(x, y, ancho, alto)` tiene su esquina superior izquierda en `(x, y)`.
- `rect.center`, `rect.centerx`, `rect.bottom` son atajos de lectura/escritura.

### Surface

Una `Surface` es una imagen o lienzo en memoria. La ventana también es una `Surface`.

Operaciones básicas:

```python
superficie = pygame.Surface((ANCHO, ALTO))       # crear
superficie.fill((30, 30, 40))                     # pintar todo
superficie.blit(imagen, (x, y))                   # pegar otra surface
pygame.display.flip()                             # mostrar el frame
```

`SRCALPHA` permite transparencia:

```python
overlay = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
overlay.fill((0, 0, 0, 190))
```

El cuarto valor (190) es el alpha: 0 invisible, 255 opaco.

### Rect

`Rect` no dibuja: representa un rectángulo y sabe compararse con otros.

| Atributo/método | Qué hace |
|---|---|
| `rect.x`, `rect.y` | Esquina superior izquierda |
| `rect.left`, `rect.right` | Bordes horizontales |
| `rect.top`, `rect.bottom` | Bordes verticales |
| `rect.centerx`, `rect.centery` | Centro |
| `rect.width`, `rect.height` | Tamaño |
| `rect.colliderect(otro)` | `True` si se superponen |
| `rect.collidelist(lista)` | Índice del primer rect que toca, o `-1` |
| `rect.move(dx, dy)` | Devuelve una copia movida |
| `rect.move_ip(dx, dy)` | Mueve el rect en el lugar |
| `rect.clamp_ip(otro)` | Lo mete dentro de otro rect |
| `rect.inflate(dw, dh)` | Copia más grande/chica |
| `rect.copy()` | Copia independiente |

En el proyecto se usa `colliderect` para jugador/plataforma, jugador/moneda y
jugador/enemigo.

---

## 6. Funciones de pygame usadas

### Inicialización y ventana

| Función | Para qué |
|---|---|
| `pygame.init()` | Inicializa módulos (video, fuentes, etc.) |
| `pygame.display.set_mode((ancho, alto))` | Crea la ventana y devuelve su Surface |
| `pygame.display.set_caption(texto)` | Título de la ventana |
| `pygame.display.flip()` | Muestra el frame dibujado |
| `pygame.quit()` | Cierra pygame |

### Tiempo

| Función | Para qué |
|---|---|
| `pygame.time.Clock()` | Crear reloj |
| `reloj.tick(FPS)` | Limitar FPS y devolver milisegundos |
| `pygame.time.get_ticks()` | Milisegundos desde `pygame.init()` |

### Dibujo

| Función | Para qué |
|---|---|
| `pygame.draw.rect(surface, color, rect, width=0)` | Rectángulo lleno o borde |
| `pygame.draw.ellipse(surface, color, rect, width=0)` | Elipse |
| `pygame.draw.circle(surface, color, centro, radio, width=0)` | Círculo |
| `pygame.draw.line(surface, color, inicio, fin, width)` | Línea |
| `pygame.draw.polygon(surface, color, puntos)` | Polígono |
| `surface.blit(otra, (x, y))` | Pegar una Surface |

`width=0` significa “relleno”; un número mayor que 0 dibuja solo el borde.

### Texto

```python
fuente = pygame.font.Font(None, 28)        # fuente por defecto, tamaño 28
imagen = fuente.render("Hola", True, BLANCO)
pantalla.blit(imagen, (10, 10))
```

- `render(texto, antialias, color)` devuelve una Surface.
- `imagen.get_rect()` permite centrar:
  ```python
  rect = imagen.get_rect(center=(ANCHO // 2, 100))
  pantalla.blit(imagen, rect)
  ```

### Imágenes (referencia)

Aunque este proyecto no usa archivos de imagen, en pygame se hace así:

```python
imagen = pygame.image.load("ruta.png").convert_alpha()
rect = imagen.get_rect(topleft=(x, y))
pantalla.blit(imagen, rect)

# Recortar un frame de un spritesheet
frame = imagen.subsurface(pygame.Rect(x, y, 32, 32))
```

`convert_alpha()` acelera el dibujo y conserva transparencia.

### Transformaciones

```python
pygame.transform.flip(surface, True, False)  # espejo horizontal
pygame.transform.scale(surface, (w, h))
pygame.transform.rotate(surface, angulo)
```

### Eventos y teclado

```python
for evento in pygame.event.get():
    if evento.type == pygame.QUIT:
        corriendo = False
    elif evento.type == pygame.KEYDOWN:
        if evento.key == pygame.K_SPACE:
            saltar()
    elif evento.type == pygame.KEYUP:
        if evento.key == pygame.K_SPACE:
            soltar_salto()

teclas = pygame.key.get_pressed()
if teclas[pygame.K_a]:
    mover_izquierda()
```

Constantes útiles: `K_a`, `K_d`, `K_w`, `K_s`, `K_LEFT`, `K_RIGHT`, `K_SPACE`,
`K_RETURN`, `K_p`, `K_r`, `K_ESCAPE`.

---

## 7. Python necesario, explicado

### 7.1 Variables y tipos

```python
nombre = "Ana"       # str
edad = 20            # int
altura = 1.65        # float
vivo = True          # bool
nada = None          # ausencia de valor
```

Python infiere el tipo; no se declara. `type(x)` lo consulta.

Conversiones:

```python
int("20")       # 20
float("1.5")    # 1.5
str(20)         # "20"
```

### 7.2 Operadores

| Operador | Significado |
|---|---|
| `+ - * /` | Suma, resta, multiplicación, división |
| `//` | División entera |
| `%` | Resto |
| `**` | Potencia |
| `== != < > <= >=` | Comparaciones |
| `and or not` | Lógica |
| `in` | Pertenencia |
| `is` | Identidad (no usar para comparar números) |

En juegos se usa mucho `//` para pasar de píxeles a tiles:

```python
columna = x // TILE
fila = y // TILE
```

### 7.3 Listas

Una lista es una colección ordenada y mutable:

```python
monedas = [10, 20, 30]
monedas.append(40)       # agregar al final
monedas[0]               # 10
monedas[-1]              # 40
len(monedas)             # 4
for moneda in monedas:   # recorrer
    print(moneda)
```

En el proyecto, `nivel.solidos` y `nivel.monedas` son listas.

### 7.4 Tuplas

Una tupla es ordenada pero inmutable:

```python
punto = (100, 200)
x, y = punto
```

Se usan para coordenadas y colores `(r, g, b)`.

### 7.5 Diccionarios

Un diccionario asocia claves con valores:

```python
nivel = {
    "nombre": "Bosque",
    "mapa": NIVEL_1,
}
print(nivel["nombre"])
nivel["pista"] = "..."
```

`NIVELES` es una lista de diccionarios. `self.fuentes` en `Juego` es un diccionario
`tamaño -> fuente`.

### 7.6 Strings

```python
texto = "hola"
texto.upper()          # "HOLA"
texto.strip()          # saca espacios de los bordes
texto.split("|")       # separa por |
"-".join(["a", "b"])    # "a-b"
```

Los strings son inmutables: `texto[0] = "H"` falla. Se crea otro string.

### 7.7 f-strings

```python
vidas = 3
print(f"Vidas: {vidas}")
print(f"Tiempo: {tiempo:04.1f}s")
```

`04.1f` significa: ancho 4, un decimal, rellenar con 0.

### 7.8 Condicionales

```python
if vida <= 0:
    estado = "derrota"
elif vida == 1:
    estado = "peligro"
else:
    estado = "jugando"
```

La primera condición verdadera gana. El orden importa.

### 7.9 `for`

```python
for i in range(3):
    print(i)          # 0, 1, 2

for solido in nivel.solidos:
    if jugador.rect.colliderect(solido):
        choque = True
```

`range(inicio, fin, paso)` no incluye el fin. `enumerate(lista)` da índice y valor.

### 7.10 `while`

```python
while corriendo:
    ...
```

Sirve cuando no sabés cuántas iteraciones habrá. En el loop principal, `corriendo` es
la bandera que lo mantiene vivo.

`break` corta el loop; `continue` salta a la siguiente vuelta.

### 7.11 Funciones

```python
def calcular_danio(ataque, defensa):
    danio = ataque - defensa
    if danio < 0:
        danio = 0
    return danio
```

- `def` define.
- Los nombres entre paréntesis son parámetros.
- `return` devuelve un valor y termina la función.
- Sin `return`, la función devuelve `None`.

Parámetros por defecto:

```python
def saludar(nombre, saludo="Hola"):
    return f"{saludo}, {nombre}"

saludar("Ana")                 # "Hola, Ana"
saludar("Ana", saludo="Ey")    # "Ey, Ana"
```

Los parámetros con default van después de los obligatorios.

### 7.12 Scope

Una variable creada dentro de una función es local:

```python
def f():
    x = 10   # local

f()
print(x)    # NameError
```

Si una función necesita modificar una lista recibida, puede hacerlo porque la lista
es mutable. Si necesita modificar una variable global, se usa `global`, pero en este
proyecto se evita: se pasan datos como parámetros.

### 7.13 Clases y objetos

Una clase agrupa datos y funciones:

```python
class Jugador:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vidas = 3

    def perder_vida(self):
        self.vidas -= 1

ana = Jugador(100, 200)
ana.perder_vida()
```

- `class` define el molde.
- `__init__` se ejecuta al crear el objeto.
- `self` es el objeto actual; siempre es el primer parámetro de los métodos.
- `self.x` es un atributo del objeto.
- `Jugador(100, 200)` crea una instancia.

En el proyecto: `Jugador`, `Enemigo`, `Moneda`, `Nivel`, `Camara` y `Juego` son clases.

### 7.14 Imports

```python
import pygame                 # módulo completo
from config import GRAVEDAD   # nombre específico
from entidades import Jugador
```

Si un archivo se ejecuta directamente, `__name__ == "__main__"`. Si se importa, no.

### 7.15 Excepciones y asserts

```python
raise ValueError("El nivel no tiene spawn")
assert jugador.en_suelo, "El jugador debería estar en el suelo"
```

`assert` es una verificación para tests y desarrollo. Si falla, el programa corta con
`AssertionError`.

### 7.16 Palabras reservadas de Python

No se pueden usar como nombres de variables:

```text
False  None  True  and  as  assert  async  await  break  class  continue
def  del  elif  else  except  finally  for  from  global  if  import
in  is  lambda  nonlocal  not  or  pass  raise  return  try  while
with  yield
```

Tampoco conviene pisar builtins como `list`, `dict`, `str`, `int`, `print`, `len`,
`range`, `type`, `min`, `max`, `sum`.

### 7.17 Nombres y Clean Code

- Variables y funciones: `snake_case`.
- Constantes: `MAYUSCULAS_CON_GUIONES`.
- Funciones que devuelven `bool`: `es_` / `tiene_`.
- Una función = una tarea.
- Evitar números mágicos: usar `config.py`.
- Comentarios que expliquen el **por qué**, no repetir el **qué**.

---

## 8. Física del plataformero

### 8.1 Gravedad

```text
velocidad_y += GRAVEDAD * dt
posición_y += velocidad_y * dt
```

Con `GRAVEDAD = 1500`, la velocidad de caída aumenta 1500 px/s cada segundo. Se limita
con `MAX_CAIDA` para que no crezca sin control.

### 8.2 Salto

```text
velocidad_y = SALTO
```

`SALTO = -540`. El signo negativo es hacia arriba porque `y` crece hacia abajo.

Altura aproximada:

```text
altura = SALTO² / (2 * GRAVEDAD)
       = 540² / 3000
       ≈ 97 px
       ≈ 3 tiles
```

### 8.3 Salto variable

Al soltar `ESPACIO` antes del punto más alto:

```python
if self.vy < 0:
    self.vy *= CORTE_SALTO
```

Se conserva el 45% del impulso. Así un toque corto salta menos que mantener la tecla.

### 8.4 Coyote time

Es el pequeño margen para saltar después de dejar una plataforma. Sin coyote, el
jugador siente que el salto “no responde” en el borde.

```text
si estaba en el suelo: coyote = 0.10
si no: coyote -= dt
puede_saltar = en_suelo or coyote > 0
```

### 8.5 Jump buffer

Es el margen para pedir salto un poco antes de aterrizar:

```text
al presionar ESPACIO: buffer = 0.12
cada frame: buffer -= dt
si buffer > 0 y (en_suelo o coyote > 0): saltar
```

Hace que el juego se sienta más receptivo.

### 8.6 Colisión AABB por ejes

AABB significa *Axis-Aligned Bounding Box*: rectángulos alineados a los ejes, sin
rotación.

El jugador se mueve primero en X y después en Y:

1. Se suma `dx` a `x`.
2. Si el rect toca un sólido, se corrige el borde y se cancela `vx`.
3. Se suma `dy` a `y`.
4. Si toca un sólido, se corrige el borde y se cancela `vy`.

Separar los ejes permite deslizarse contra una pared sin quedar trabado, y aterrizar
sin atravesar el piso.

### 8.7 Detección de suelo estable

Pygame considera colisión solo si hay superposición, no si dos rects se tocan en el
borde. Por eso, cuando el jugador queda justo apoyado, se usa una sonda de 1 px hacia
abajo:

```python
sonda = self.rect.move(0, 1)
if sonda.colliderect(solido):
    self.en_suelo = True
```

### 8.8 Stomp

Si el jugador cae sobre un enemigo:

```python
viene_desde_arriba = (
    jugador.vy > 0
    and jugador.rect.bottom - enemigo.rect.top <= 18
)
```

Si es verdadero, el enemigo muere y el jugador rebota. Si no, pierde una vida.

### 8.9 Cámara

```text
objetivo_x = jugador.centerx - ANCHO // 2
objetivo_y = jugador.centery - ALTO // 2
```

Luego se interpola:

```text
camara.x += (objetivo_x - camara.x) * min(1, SUAVIZADO * dt)
```

Y se limita para no mostrar fuera del nivel:

```text
0 <= camara.x <= nivel.ancho - ANCHO
```

El HUD se dibuja sin cámara; el mundo se dibuja con `camara.aplicar_rect`.

### 8.10 Parallax

Las colinas se mueven a `camara.x * 0.25` y las nubes a `camara.x * 0.45`. Cuanto menor
el factor, más lejos parece el objeto. Es una técnica barata y muy visible.

---

## 9. Cómo se lee un nivel

`niveles.py` guarda mapas como strings:

```text
.  vacío
#  bloque
P  spawn
G  meta
o  moneda
E  enemigo
```

`Nivel.__init__`:

1. `datos.strip("\n").splitlines()` convierte el texto en filas.
2. Calcula el ancho máximo y rellena con `.` para que todas midan igual.
3. Busca `P` y `G`.
4. `_crear_solidos()` recorre cada fila y une `#` consecutivos en un `Rect`.
5. `_crear_monedas()` crea un `Moneda` por cada `o`.
6. `_crear_enemigos()` crea un `Enemigo` por cada `E` y calcula su patrulla.

Unir bloques consecutivos reduce la cantidad de rectángulos. En vez de 10 rects de
32×32, se crea uno de 320×32. Es una optimización simple y didáctica.

### Cómo agregar un nivel

1. Copiá un mapa en `niveles.py`.
2. Mantené las filas del mismo ancho.
3. Asegurate de tener una `P` y una `G`.
4. Agregá el diccionario a `NIVELES`.
5. Corré `tests/test_logica.py`.

### Cómo agregar un símbolo nuevo

Ejemplo: pinches `^`.

1. Elegí el símbolo en el mapa.
2. En `Nivel`, creá una lista `pinches` y un rect por cada `^`.
3. En `Juego.actualizar`, comprobá colisión con el jugador.
4. Llamá `perder_vida`.
5. Agregá un test.

---

## 10. Recorrido del código

### `config.py`

Constantes. Si querés cambiar la sensación del juego, empezá acá:

- `GRAVEDAD`: más alta = caída más pesada.
- `SALTO`: más negativo = salto más alto.
- `VELOCIDAD`: más alto = personaje más rápido.
- `COYOTE_TIME`, `JUMP_BUFFER`: tolerancia del control.
- `CORTE_SALTO`: cuánto se conserva al soltar.
- `REBOTE_ENEMIGO`: impulso al pisar.

### `niveles.py`

Datos puros. No importa pygame. Es el archivo que más vas a editar cuando quieras
diseñar.

### `nivel.py`

`Nivel` convierte texto en objetos y dibuja el escenario. Métodos:

| Método | Qué hace |
|---|---|
| `_buscar_spawn` | Encuentra `P` |
| `_buscar_meta` | Encuentra `G` |
| `_crear_solidos` | Une `#` en rects |
| `_crear_monedas` | Crea monedas |
| `_crear_enemigos` | Crea enemigos y límites de patrulla |
| `_limites_patrulla` | Busca el tramo de piso debajo del enemigo |
| `reiniciar` | Reinicia monedas y enemigos |
| `dibujar` | Dibuja sólidos, monedas y meta |
| `dibujar_meta` | Dibuja la bandera |

### `entidades.py`

`Jugador`:

| Método | Qué hace |
|---|---|
| `pedir_salto` | Activa el buffer |
| `soltar_salto` | Corta el salto |
| `actualizar` | Input, timers, gravedad y colisiones |
| `actualizar_horizontal` | Lee A/D/flechas |
| `actualizar_temporizadores` | Buffer y coyote |
| `mover_x` / `mover_y` | Colisión por eje |
| `respawn` | Vuelve al spawn |
| `dibujar` | Dibuja el personaje |

`Enemigo`: patrulla, invierte en los límites, se dibuja como slime y `reiniciar`
lo devuelve a su posición inicial.
`Moneda`: flota, se recoge una vez, suma al contador y `reiniciar` la vuelve a poner.

### `camara.py`

`Camara.actualizar` sigue al jugador y limita al mapa. `aplicar_rect` traduce mundo a
pantalla. `is_on_screen` permite no dibujar lo que está lejos (culling).

### `juego.py`

`Juego` es el coordinador:

- `__init__`: pygame, ventana, reloj, fondo y primer nivel.
- `cargar_nivel`: crea `Nivel`, `Jugador` y cámara.
- `procesar_eventos`: QUIT, teclas, pausa, reinicio, salto.
- `actualizar`: jugador, enemigos, monedas, cámara y meta.
- `perder_vida`: descuenta vida o pasa a derrota.
- `dibujar_fondo`: cielo, colinas y nubes con parallax.
- `dibujar_hud`: nivel, monedas, vidas y tiempo.
- `dibujar_overlay`: pausa, nivel completado, victoria y derrota.
- `run`: loop principal.

### `tests/test_logica.py`

Pruebas sin ventana real:

- Los dos niveles son coherentes.
- El parser encuentra spawn y meta.
- La gravedad aterriza.
- El salto da velocidad negativa.
- La moneda se recoge una sola vez.
- El enemigo patrulla.
- La cámara respeta los límites.
- La meta cambia de nivel y termina en victoria.
- El stomp elimina al enemigo y el contacto resta una vida.
- Perder una vida respawnea; quedarse sin vidas da derrota.
- `Nivel.reiniciar` restaura monedas y enemigos.
- El juego corre 180 frames headless.

---

## 11. Errores comunes

| Error | Causa | Solución |
|---|---|---|
| La ventana se congela | No se llama `pygame.event.get()` | Procesar eventos en el loop |
| El personaje atraviesa paredes | Se mueve demasiado por frame | Limitar `dt` y resolver por ejes |
| El salto no responde en el borde | Falta coyote time | Revisar `COYOTE_TIME` |
| Saltar mantiene la tecla | Se usa `KEYDOWN` repetido o `get_pressed` | Usar buffer y eventos |
| El personaje tiembla en el suelo | Se aplica gravedad y no se detecta el borde | Usar sonda de 1 px |
| `KeyError` en un diccionario | La clave no existe | Usar `.get(clave, default)` |
| `NoneType` | `get_component` o búsqueda devolvió `None` | Comprobar antes de usar |
| `IndentationError` | Mezcla de tabs/espacios | Usar 4 espacios |
| `ModuleNotFoundError: pygame` | No se activó el venv | `source .venv/bin/activate` |
| El nivel no carga | Falta `P` o `G` | Revisar el mapa |
| Las filas no coinciden | String de distinto largo | El parser rellena, pero es mejor mantenerlas iguales |

---

## 12. Depuración

1. Imprimí valores:
   ```python
   print(jugador.rect, jugador.vy, jugador.en_suelo)
   ```
2. Dibujá rects de debug:
   ```python
   pygame.draw.rect(pantalla, (255, 0, 0), rect, 1)
   ```
3. Corré los tests.
4. Aislá el problema: si es física, probá `Jugador` sin ventana; si es dibujo, revisá
   la cámara y el `blit`.
5. Hacé cambios pequeños y volvé a correr.

---

## 13. Ejercicios y siguiente paso

`EJERCICIOS.md` tiene una progresión desde cambiar colores hasta agregar dash, pinches,
checkpoints y un tercer nivel. La regla es: **cambiá una cosa, corré, mirá, explicá**.

Cuando termines, podés comparar este proyecto con `PsicoWorld`, que usa una
arquitectura más grande (StateMachine, componentes, sistemas, Tiled y assets externos).

---

## 14. Glosario

- **AABB**: colisión entre rectángulos alineados a los ejes.
- **Buffer**: memoria corta de una intención (saltar antes de aterrizar).
- **Coyote time**: margen para saltar después de dejar el borde.
- **Culling**: no dibujar lo que está fuera de pantalla.
- **Delta time (`dt`)**: tiempo entre frames.
- **Frame**: una iteración del loop.
- **FPS**: frames por segundo.
- **Parallax**: capas que se mueven a distinta velocidad para dar profundidad.
- **Rect**: rectángulo de pygame.
- **Respawn**: volver a aparecer.
- **Stomp**: pisar un enemigo desde arriba.
- **Surface**: lienzo/imagen de pygame.
- **Tick**: una vuelta del reloj del juego.
- **Tile**: baldosa del mapa (32×32 en este proyecto).

---

## 15. Fuentes

- Taller de Programación I, UNAHUR: C1–C5, E/P/S, Clean Code.
- `python_extra/enunciados.md`, `teoria/plan-estudio.md`.
- Guía de Código Limpio de la cátedra.
- Principios LADPAE de la skill `didactica`.
- PsicoWorld: `docs/guia-codigo.md` para la versión grande.
