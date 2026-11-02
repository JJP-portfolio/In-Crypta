# Optimización web de IN CRYPTA

## Resumen

La versión web funciona, pero es pesada y lenta por tres razones de fondo: el navegador ejecuta el mismo perfil gráfico que la PC, el paquete publicado incluye audio sin comprimir y duplicado, y el arranque sintetiza sonidos en Python. El parche `optimizacion_web.patch` ataca las tres. Cambiar de servicio de hosting no vuelve más rápido el juego: la lentitud ocurre en el navegador. El hosting solo define costos y límites de tráfico.

Este reporte distingue lo que medí de lo que quedó pendiente de medir en tu máquina.

---

## 1. Diagnóstico

### 1.1 El navegador usa el perfil más pesado

El juego no detecta que corre en web. Arranca con `config_shader_idx = 0` y `config_calidad_idx = 0`, es decir, bloom, scanlines CRT, penumbra completa y halos al 100 %. Es el mismo perfil de PC, ejecutado por CPython compilado a WebAssembly, que es más lento que el nativo.

### 1.2 Pasadas de pantalla completa en cada frame

En `juego.py`, método `dibujar()` (líneas 2773 a 2842), cada frame hace estas operaciones sobre la pantalla completa:

| Operación | Línea | Costo |
|---|---|---|
| Bloom: `smoothscale` de bajada a un cuarto y de subida a tamaño completo | 597–598, llamado en 2831 | El más caro |
| Escalado del mundo 1024×576 → 1280×720 | 2820 | Obligatorio |
| `fill` con `BLEND_RGBA_MAX` | 2823 | Una pasada completa |
| Scanlines CRT (blit con alfa) | 2837 | Una pasada completa |
| Viñeta (blit con alfa, en todos los frames) | 2842 | Una pasada completa |
| Máscara de penumbra: fill + 2 blits | 2773–2794 | Pasadas a 1024×576 |

Además, `entidades.py` crea 11 superficies `SRCALPHA` dentro de métodos `dibujar()`, es decir, por frame y por entidad. **Esto no lo cambié en este parche.** Es el siguiente candidato si la medición lo justifica.

### 1.3 El paquete pesa más de lo necesario

El exportador copiaba todos los `.wav` de `sfx/`, y `audio.py` ya prefiere el `.ogg` hermano. Eso dejaba archivos que nunca se usan. Además, los WAV sueltos viajaban sin comprimir.

Medido con un tono de prueba de 0,25 s:

- WAV de 44 178 bytes → OGG de 5 697 bytes (≈ 7,7× menos).

Con música real el ahorro es menor, porque los tonos sintéticos comprimen mucho más. Por eso el script reporta el tamaño real de cada build en vez de asumir un número.

### 1.4 El arranque sintetiza sonidos en Python

`audio.py` genera en Python, muestra por muestra con `math.sin`, todo SFX que no encuentre como archivo. Medido en CPython nativo, en el peor caso (ningún archivo en disco):

- Banco completo: **855 ms**, 30 sonidos (incluye el dron de 4 s, que tarda 256 ms).

En el navegador será más lento, porque WebAssembly ejecuta Python más despacio. No lo cambié en este parche: la solución correcta es pre-renderizar esos sonidos en el build o cargarlos de forma diferida, y requiere probar el juego real.

---

## 2. Cambios del parche

| Archivo | Cambio |
|---|---|
| `config.py` | Agrega `ES_WEB = sys.platform == "emscripten"` y el perfil web: `PERFIL_WEB_SHADER = 2` (Puro) y `PERFIL_WEB_CALIDAD = 1` (Media). |
| `juego.py` | Al arrancar aplica el perfil web solo si `ES_WEB` es verdadero. En PC, los valores quedan iguales a antes (0, 0, factor de partículas 1.0). |
| `tools/exportar_web_pygame.py` | No copia WAV con OGG hermano. Recodifica el audio a OGG Vorbis con ffmpeg y conserva la versión nueva solo si pesa menos. Vacía la carpeta de audio antes de copiar, para no arrastrar archivos viejos. Imprime el peso de la build y avisa si un archivo supera 25 MiB. Nueva opción `--sin-optimizar-audio`. |
| `tools/medir_web.py` (nuevo) | Mide la build en Chromium real con Playwright: tiempo hasta el botón, tiempo del click hasta el canvas 1280×720, FPS medio, bytes por dominio y errores. |

Calidad de audio configurable en `tools/exportar_web_pygame.py`: `CALIDAD_VORBIS_MUSICA = 3` y `CALIDAD_VORBIS_SFX = 5`.

### Qué verifiqué y qué no

Verificado en este entorno:

- `config.py`, `juego.py`, `tools/exportar_web_pygame.py` y `tools/medir_web.py` compilan.
- El parche aplica limpio con `git apply` sobre el repo original.
- Exportador, con fixtures de audio y ffmpeg real: descarta el WAV con OGG hermano, convierte WAV sueltos, reemplaza `tema1.ogg` por una versión más liviana, conserva el OGG que agrandaría si se recodificara, excluye los `-pygbag` y el dron WAV, borra copias viejas, funciona sin ffmpeg (con aviso) y advierte sobre archivos de más de 25 MiB.
- `medir_web.py` contra una página de prueba en Chromium real: detecta el botón, el click, el canvas 1280×720, FPS (~60), separa los bytes por host y registra los 404.

**No verificado** (faltan pygame, la build de Pygbag y la red en este entorno):

- La build real con Pygbag.
- El FPS del juego real. Las mejoras se basan en el análisis del código y en las mediciones de audio. El FPS real lo mide `medir_web.py` en tu máquina.
- Los 35 tests de `pytest tests/`. No pude correrlos porque pygame no está instalado aquí. Corrélos antes de publicar.

---

## 3. Despliegue local (primero)

```bash
# 1. Dependencias (una vez)
pip install -r requirements.txt
pip install playwright
playwright install chromium
# ffmpeg: descargalo de https://ffmpeg.org o usá: sudo apt install ffmpeg / winget install ffmpeg

# 2. Línea base: medir la versión que está publicada hoy (antes de cambiar nada)
python tools/medir_web.py https://jjp-portfolio.github.io/In-Crypta/ --segundos 10 --salida verificacion/base_github_pages

# 3. Aplicar el parche y compilar
git apply optimizacion_web.patch
python tools/exportar_web_pygame.py --build

# 4. Servir la build local
python -m http.server 8000 --directory export/web_pygame/build/web
# Abrí http://localhost:8000/ y jugá un rato: botón, audio, niveles.

# 5. Medir la build local y comparar con la línea base
python tools/medir_web.py http://localhost:8000/ --segundos 10 --salida verificacion/local
```

El reporte de `--build` muestra el peso total y los archivos más pesados. El que más importa es `web_pygame.apk`. Cloudflare Pages rechaza archivos de más de 25 MiB, así que si aparece el aviso hay que bajar la calidad del audio o quitar material.

### Cómo decidir los ajustes con los números

- **FPS medio por debajo de 50 en local:** en `config.py` poné `PERFIL_WEB_CALIDAD = 2`. Quita penumbra, halos y partículas extra. Es el perfil "Baja" que ya trae el juego.
- **FPS bien arriba de 55 y ganas de más efectos:** podés probar `PERFIL_WEB_CALIDAD = 0`, con todo activado, y volver a medir.
- **El build pesa demasiado:** bajá `CALIDAD_VORBIS_MUSICA` de 3 a 2. Es la palanca de mayor impacto, porque la música suele ser lo más pesado.
- **Tarda en mostrar el botón:** mirá `bytes_por_dominio_mib` en `resumen.json`. Si la mayor parte viene de `pygame-web.github.io`, el cuello de botella es el runtime de Pygbag y no tu código.

---

## 4. Despliegue en Render (después)

Los pasos son los mismos de antes, con la build liviana:

1. Hacé commit y push de los cambios a `main`. El workflow `deploy-pages.yml` compila y publica en `gh-pages`. Verificá en la pestaña Actions que termine en verde. En el log, la línea `⚠ ffmpeg no está instalado` significa que el audio no se optimizó.
2. En Render: **New → Static Site**, conectá `jjp-portfolio/In-Crypta`.
3. **Branch:** `gh-pages`. **Build Command:** `exit 0`. **Publish Directory:** `.`
4. Create Static Site. Desde ese momento, cada push a `gh-pages` se redespliega solo.
5. Medí la URL pública: `python tools/medir_web.py https://TU-SITIO.onrender.com/ --segundos 10`.

El `render.yaml` del repo hace lo mismo como Blueprint, si preferís versionarlo.

---

## 5. Hosting: qué servicio conviene

Los límites cambian, así que verificalos antes de decidir. Lo que sigue está tomado de fuentes consultadas en noviembre de 2026.

| Servicio | Plan gratis | Límite que importa | Fuente |
|---|---|---|---|
| **Render** (Static Site) | Workspace Hobby | **5 GB/mes de egreso por workspace** desde el 23/04/2026. Excedente a $0,15/GB. Pro: 25 GB/mes por $25/mes. | Documentación oficial de Render (`outbound-bandwidth` y `new-workspace-plans`) |
| **Cloudflare Pages** | Free | Tráfico de estáticos sin límite declarado. 500 builds/mes. 20 000 archivos por sitio. **25 MiB por archivo.** | Documentación oficial de Cloudflare Pages |
| **GitHub Pages** | Gratis | 1 GB por sitio. 100 GB/mes de tráfico (límite blando). 10 builds por hora. | Fuentes secundarias de 2026; confirmalo en la documentación de GitHub |

**Nota sobre Render:** muchos artículos y foros todavía citan 100 GB gratis. Son anteriores al cambio de abril de 2026. Manda la documentación oficial.

**Cuánto consume el juego:** Render solo cuenta lo que él mismo sirve: `index.html`, el `.apk` y el audio. Según la configuración por defecto de Pygbag, el runtime de CPython y el wheel de `pygame-ce` vienen de `pygame-web.github.io`, así que no consumen tu cuota. Por eso el peso del build define cuántas cargas completas entran en los 5 GB. Con un build de 20 MB son unas 250 cargas al mes antes de empezar a pagar excedente. Si el build pesa 10 MB, son unas 500. Para una cifra exacta usá el peso de `web_pygame.apk` que imprime `--build`.

### Mi recomendación

1. **Render ahora**, como pediste. Para un portfolio con tráfico moderado alcanza. Si pasa el límite, Render te cobra el excedente; no te corta el servicio.
2. **Cloudflare Pages si el tráfico crece.** Su plan gratis no tiene límite de tráfico para estáticos, y el build es la misma carpeta `export/web_pygame/build/web`. Se sube con `npx wrangler pages deploy export/web_pygame/build/web --project-name in-crypta` (requiere cuenta y `npx wrangler login`).
3. **GitHub Pages como respaldo.** Ya funciona y no hace falta tocarlo.

Ningún host hace el juego más rápido en el navegador. Para eso sirven el perfil web, el peso del build y, si hace falta, los pasos pendientes de la sección 6.

---

## 6. Pendientes con mejor relación costo/beneficio

Si después de medir sigue lento, en este orden:

1. **Pre-renderizar el audio sintetizado** en el build (o cargarlo de forma diferida). Elimina los ~855 ms de arranque en el peor caso.
2. **Cachear las superficies `SRCALPHA` de `entidades.py`** (11 creaciones por frame en `dibujar()`).
3. **Reemplazar el `smoothscale` del bloom por un escalado más barato** cuando el perfil use bloom. Cambia el look, por eso va último y con medición antes y después.
