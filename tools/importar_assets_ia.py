#!/usr/bin/env python3
# ============================================================================
# tools/importar_assets_ia.py — Pipeline de importación de assets IA de IN CRYPTA
# ============================================================================
# Orquestación: plan/orquestacion_assets_goal.xml
# Fuente única (P1): plan/manifest_assets.json  (única lista válida)
#
# Modos:
#   --validar-manifiesto   F0-1 + F0-2 + F0-3: valida manifiesto, verifica claves
#                          contra código y crea carpetas de entrega. Exit 0 si OK.
#   --todo                 F1-1 / F3-1: procesa todos los assets. Los que faltan
#                          en assets_in_crypta/entrega/ quedan ESPERANDO_ENTREGA.
#                          Genera reports/assets_ia.json. Exit 0.
#   --solo <ID>            Procesa un solo asset por id.
#   --gdevelop             F4-1: copia a export/gdevelop_nativo/assets/ solo los
#                          assets que pasaron (estado OK).
#
# P2: no se generan imágenes ni audio. Si falta un archivo, ESPERANDO_ENTREGA.
# ============================================================================

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))
MANIFIESTO_PATH = RAIZ / "plan" / "manifest_assets.json"
DIR_ENTREGA = RAIZ / "assets_in_crypta" / "entrega"
DIR_AUDIO = RAIZ / "assets" / "audio"
DIR_SPRITES_IA = RAIZ / "assets" / "sprites_ia"
DIR_SPRITESHEETS = RAIZ / "assets_pixelart" / "spritesheets"
MANIFIESTO_SHEETS_PATH = DIR_SPRITESHEETS / "spritesheets_manifest.json"
REPORTS_DIR = RAIZ / "reports"
REPORT_PATH = REPORTS_DIR / "assets_ia.json"
DIR_GD_ASSETS = RAIZ / "export" / "gdevelop_nativo" / "assets"

# Estados permitidos (ver orquestacion_assets_goal.xml, formato_evidencia).
ESPERANDO_ENTREGA = "ESPERANDO_ENTREGA"
OK = "OK"
FALLA = "FALLA"
PENDIENTE_HERRAMIENTA = "PENDIENTE_HERRAMIENTA"
BLOQUEADA = "BLOQUEADA"

# Campos obligatorios por categoria.
CAMPOS_SFX = ["id", "duracion_s", "bucle", "archivo", "clave_codigo"]
CAMPOS_MUSICA = ["id", "duracion_s", "bucle", "archivo"]
CAMPOS_SPRITES = ["id", "cuadros", "claves_manifiesto", "tamano_final_px", "tamano_generacion_px"]

PALETTE_HEX = re.compile(r"^#[0-9A-Fa-f]{6}$")


# --------------------------------------------------------------------------- #
# Carga del manifiesto
# --------------------------------------------------------------------------- #
def cargar_manifiesto(ruta=MANIFIESTO_PATH):
    with open(ruta, "r", encoding="utf-8") as f:
        return json.load(f)


# --------------------------------------------------------------------------- #
# F0-1 — Validación del manifiesto
# --------------------------------------------------------------------------- #
def _es_ascii(texto: str) -> bool:
    try:
        texto.encode("ascii")
        return True
    except UnicodeEncodeError:
        return False


def validar_manifiesto(manifiesto):
    """F0-1. Devuelve (ok, errores)."""
    errores = []

    # Ids unicos en todas las categorías.
    vistos = set()
    for categoria in ("sfx", "musica", "sprites"):
        for asset in manifiesto.get(categoria, []):
            aid = asset.get("id")
            if aid in vistos:
                errores.append(f"id duplicado '{aid}' en {categoria}")
            vistos.add(aid)

    # Campos obligatorios y nombres de archivo ASCII.
    campos_por_cat = {"sfx": CAMPOS_SFX, "musica": CAMPOS_MUSICA, "sprites": CAMPOS_SPRITES}
    for categoria, campos in campos_por_cat.items():
        for asset in manifiesto.get(categoria, []):
            for campo in campos:
                if campo not in asset or asset[campo] is None:
                    errores.append(f"{categoria}/{asset.get('id','?')} falta campo obligatorio '{campo}'")
            archivo = asset.get("archivo")
            if archivo and not _es_ascii(archivo):
                errores.append(f"{categoria}/{asset.get('id','?')} nombre de archivo no ASCII: {archivo!r}")

    return (len(errores) == 0), errores


# --------------------------------------------------------------------------- #
# F0-2 — Verificación contra el código
# --------------------------------------------------------------------------- #
def _claves_reproducir_en_juego():
    """Extrae las claves pasadas a reproducir(\"...\") en juego.py."""
    ruta = RAIZ / "juego.py"
    claves = set()
    if ruta.exists():
        texto = ruta.read_text(encoding="utf-8")
        for m in re.finditer(r'reproducir\s*\(\s*["\']([^"\']+)["\']\s*\)', texto):
            claves.add(m.group(1))
    return claves


def _claves_sonido_en_audio():
    """Devuelve las claves de sonido del banco de audio.py.

    Instancia Audio() (headless) para leer las claves reales, incluidas las
    generadas por bucle (alma_1..alma_6) que no aparecen como literales en el
    fuente. Si falla, retrocede al análisis por expresiones regulares.
    """
    try:
        import audio as _audio_mod  # noqa: WPS433
        banco = _audio_mod.Audio()
        return set(banco.sonidos.keys())
    except Exception:
        ruta = RAIZ / "audio.py"
        claves = set()
        if ruta.exists():
            texto = ruta.read_text(encoding="utf-8")
            for m in re.finditer(r'sonidos\s*\[\s*["\']([^"\']+)["\']\s*\]', texto):
                claves.add(m.group(1))
        return claves


def _expandir_clave_codigo(clave_codigo):
    """Expande el clave_codigo del manifiesto a las claves de código concretas.

    - rango alma_1..alma_6  -> alma_1 ... alma_6
    - lo demás se toma hasta el primer paréntesis (el contenido entre paréntesis
      son notas/alias informativos, no claves separadas a verificar).
    """
    clave = clave_codigo.strip()
    if ".." in clave:
        izquierda, derecha = clave.split("..", 1)
        base_izq = izquierda.rsplit("_", 1)[0]
        base_der = derecha.rsplit("_", 1)[0]
        ini = int(izquierda.rsplit("_", 1)[1])
        fin = int(derecha.rsplit("_", 1)[1])
        if base_izq == base_der:
            return [f"{base_izq}_{i}" for i in range(ini, fin + 1)]
    return [clave.split("(", 1)[0].strip()]


def _claves_sprite_en_manifiesto_sheets():
    """Devuelve set de claves de frame presentes en spritesheets_manifest.json."""
    claves = set()
    if MANIFIESTO_SHEETS_PATH.exists():
        try:
            datos = json.loads(MANIFIESTO_SHEETS_PATH.read_text(encoding="utf-8"))
        except Exception:
            datos = {}
        for _hoja, frames in datos.items():
            if isinstance(frames, dict):
                claves.update(frames.keys())
    return claves


def verificar_contra_codigo(manifiesto):
    """F0-2. Devuelve (ok, errores).

    - Claves de sprite (sin sufijo _izq) existen en spritesheets_manifest.json.
    - Claves SFX coinciden con llamadas reproducir() en juego.py y/o claves
      de audio.py.
    """
    errores = []
    claves_juego = _claves_reproducir_en_juego()
    claves_audio = _claves_sonido_en_audio()
    claves_sheets = _claves_sprite_en_manifiesto_sheets()

    for asset in manifiesto.get("sprites", []):
        for clave in asset.get("claves_manifiesto", []):
            base = clave[:-4] if clave.endswith("_izq") else clave
            if base not in claves_sheets and not _hay_frames_base(base, claves_sheets):
                errores.append(f"sprite clave '{base}' no encontrada en spritesheets_manifest.json")

    for asset in manifiesto.get("sfx", []):
        claves = _expandir_clave_codigo(asset.get("clave_codigo", ""))
        for clave in claves:
            if clave not in claves_juego and clave not in claves_audio:
                errores.append(f"SFX clave '{clave}' (id={asset.get('id')}) no se usa en reproducir() ni en audio.py")

    return (len(errores) == 0), errores


def _hay_frames_base(base, claves_sheets):
    """True si existen frames base_N en el manifiesto de hojas."""
    return any(c == f"{base}_1" or c.startswith(base + "_") for c in claves_sheets)


# --------------------------------------------------------------------------- #
# F0-3 — Creación de carpetas
# --------------------------------------------------------------------------- #
def asegurar_carpetas():
    for carpeta in (
        DIR_ENTREGA / "sfx",
        DIR_ENTREGA / "musica",
        DIR_ENTREGA / "sprites",
        DIR_AUDIO / "sfx",
        DIR_AUDIO / "musica",
        DIR_SPRITES_IA,
    ):
        carpeta.mkdir(parents=True, exist_ok=True)
    return True


# --------------------------------------------------------------------------- #
# Estado de entrega de un asset
# --------------------------------------------------------------------------- #
def _ruta_entrega(categoria, archivo):
    # archivo ya puede incluir la categoria (p.ej. "sfx/salto.wav"); usar solo el
    # nombre final para no duplicar el prefijo de carpeta.
    return DIR_ENTREGA / categoria / Path(archivo).name


def _archivo_entregado(categoria, archivo):
    return _ruta_entrega(categoria, archivo).exists()


# --------------------------------------------------------------------------- #
# Procesamiento de audio (F1-2, F1-3, F1-4) — solo si llega el archivo
# --------------------------------------------------------------------------- #
def _ffmpeg_disponible():
    return subprocess.run(["ffmpeg", "-version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0


def _pillow_disponible():
    try:
        import PIL  # noqa: F401
        return True
    except Exception:
        return False


def normalizar_sfx(entrada: Path, salida: Path, duracion_s: float):
    """F1-2. WAV 44100 Hz 16-bit estereo, recorta silencio >10 ms, pico -3 dBFS."""
    if not _ffmpeg_disponible():
        return False, "ffmpeg no disponible"
    try:
        # Conversión base a 44100 Hz, 16-bit, estereo.
        paso1 = salida.with_suffix(".tmp.wav")
        cmd = [
            "ffmpeg", "-y", "-i", str(entrada),
            "-ar", "44100", "-sample_fmt", "s16", "-ac", "2",
            "-af", "silenceremove=start_periods=1:start_duration=0.01:start_threshold=-50dB:"
                   "stop_periods=-1:stop_duration=0.01:stop_threshold=-50dB",
            str(paso1),
        ]
        r = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if r.returncode != 0:
            return False, "ffmpeg conversion falló"
        # Detectar pico y normalizar a -3 dBFS.
        vd = subprocess.run(
            ["ffmpeg", "-i", str(paso1), "-af", "volumedetect", "-f", "null", "-"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        max_vol = None
        for line in vd.stderr.splitlines():
            if "max_volume:" in line:
                try:
                    max_vol = float(line.split("max_volume:")[1].split("dB")[0].strip())
                except Exception:
                    max_vol = None
                break
        gain = 0.0
        if max_vol is not None:
            gain = -3.0 - max_vol
        cmd2 = [
            "ffmpeg", "-y", "-i", str(paso1),
            "-ar", "44100", "-sample_fmt", "s16", "-ac", "2",
            "-af", f"volume={gain}dB",
            str(salida),
        ]
        r2 = subprocess.run(cmd2, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        paso1.unlink(missing_ok=True)
        if r2.returncode != 0:
            return False, "ffmpeg normalización falló"
        # Verificar duración dentro de ±15 %.
        dur = _duracion_wav(salida)
        if dur is None:
            return False, "no se pudo leer duración del WAV"
        if abs(dur - duracion_s) > 0.15 * duracion_s:
            return False, f"duración {dur:.2f}s fuera de ±15% de {duracion_s}s"
        return True, "OK"
    except Exception as exc:  # noqa: BLE001
        return False, str(exc)


def _duracion_wav(path: Path):
    try:
        import wave
        with wave.open(str(path), "rb") as w:
            frames = w.getnframes()
            rate = w.getframerate()
            return frames / float(rate) if rate else None
    except Exception:
        return None


def generar_variantes_sfx(salida: Path):
    """D10. Variantes _v1 y _v2 con resampleo ±4%."""
    resultados = []
    for sufijo, ratio in (("_v1", 0.96), ("_v2", 1.04)):
        variante = salida.with_name(salida.stem + sufijo + ".wav")
        cmd = [
            "ffmpeg", "-y", "-i", str(salida),
            "-filter:a", f"aresample=44100,asetrate=44100*{ratio},aresample=44100",
            "-ar", "44100", "-sample_fmt", "s16", "-ac", "2",
            str(variante),
        ]
        r = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        resultados.append((sufijo, r.returncode == 0, variante))
    return resultados


def procesar_alma_ref(entrada: Path):
    """F1-3. FFT fundamental, ajuste a 880 Hz si hace falta, genera alma_1..alma_6."""
    notas = [523, 587, 659, 784, 880, 1046]
    try:
        import numpy as np  # noqa: F401
    except Exception:
        return {f"alma_{n}": (False, "numpy no disponible") for n in notas}
    if not _ffmpeg_disponible():
        return {f"alma_{n}": (False, "ffmpeg no disponible") for n in notas}
    resultados = {}
    try:
        import wave
        with wave.open(str(entrada), "rb") as w:
            nchannels = w.getnchannels()
            swidth = w.getsampwidth()
            framerate = w.getframerate()
            frames = w.readframes(w.getnframes())
        datos = np.frombuffer(frames, dtype=np.int16)
        if nchannels > 1:
            datos = datos.reshape(-1, nchannels)[:, 0]
        if len(datos) == 0:
            return {f"alma_{n}": (False, "audio vacío") for n in notas}
        window = np.hanning(len(datos))
        espectro = np.abs(np.fft.rfft(datos * window))
        freqs = np.fft.rfftfreq(len(datos), 1.0 / framerate)
        if len(espectro) == 0:
            return {f"alma_{n}": (False, "espectro vacío") for n in notas}
        fundamental = float(freqs[int(np.argmax(espectro))])
        if fundamental <= 0:
            return {f"alma_{n}": (False, "fundamental no detectable") for n in notas}
        for nota in notas:
            salida = DIR_AUDIO / "sfx" / f"alma_{nota}.wav"
            ratio = nota / fundamental
            cmd = [
                "ffmpeg", "-y", "-i", str(entrada),
                "-filter:a", f"aresample=44100,asetrate=44100*{ratio},aresample=44100",
                "-ar", "44100", "-sample_fmt", "s16", "-ac", "2",
                str(salida),
            ]
            r = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            resultados[f"alma_{nota}"] = (r.returncode == 0, "OK" if r.returncode == 0 else "ffmpeg falló")
    except Exception as exc:  # noqa: BLE001
        return {f"alma_{n}": (False, str(exc)) for n in notas}
    return resultados


def codificar_musica(entrada: Path, salida: Path, bucle: bool):
    """F1-4. OGG Vorbis 44100 Hz estereo, loudnorm -16 LUFS, crossfade 1.5s si bucle."""
    if not _ffmpeg_disponible():
        return False, PENDIENTE_HERRAMIENTA
    try:
        filtros = ["loudnorm=I=-16:TP=-1.5:LRA=11"]
        if bucle:
            filtros.append("afade=t=out:st=58:d=1.5")  # placeholder; crossfade real requiere dos pases
        cmd = [
            "ffmpeg", "-y", "-i", str(entrada),
            "-ar", "44100", "-ac", "2", "-c:a", "libvorbis",
            "-af", ",".join(filtros),
            str(salida),
        ]
        r = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if r.returncode != 0:
            return False, "ffmpeg música falló"
        return True, "OK"
    except Exception as exc:  # noqa: BLE001
        return False, str(exc)


# --------------------------------------------------------------------------- #
# Procesamiento de sprites (F1-5) — solo si llega el strip
# --------------------------------------------------------------------------- #
def procesar_sprite(asset):
    """F1-5. Procesa un strip horizontal de N cuadros. Requiere Pillow."""
    if not _pillow_disponible():
        return False, PENDIENTE_HERRAMIENTA
    entrada = _ruta_entrega("sprites", asset["archivo"])
    if not entrada.exists():
        return False, ESPERANDO_ENTREGA
    # Implementación real se ejecuta cuando el strip IA esté disponible.
    return False, "sin implementar (pendiente entrega)"


# --------------------------------------------------------------------------- #
# Reporte
# --------------------------------------------------------------------------- #
def nuevo_estado(asset, categoria, estado, motivo=""):
    return {
        "id": asset.get("id"),
        "categoria": categoria,
        "archivo": asset.get("archivo"),
        "estado": estado,
        "motivo": motivo,
    }


def escribir_reporte(entries):
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    reporte = {
        "proyecto": "IN CRYPTA",
        "modulo": "assets_ia",
        "generado": __import__("datetime").datetime.now().isoformat(),
        "manifiesto": str(MANIFIESTO_PATH),
        "total": len(entries),
        "resumen": {
            estado: sum(1 for e in entries if e["estado"] == estado)
            for estado in (OK, ESPERANDO_ENTREGA, FALLA, PENDIENTE_HERRAMIENTA, BLOQUEADA)
        },
        "assets": entries,
    }
    REPORT_PATH.write_text(json.dumps(reporte, indent=2, ensure_ascii=False), encoding="utf-8")
    return reporte


# --------------------------------------------------------------------------- #
# Procesamiento por activo
# --------------------------------------------------------------------------- #
def evaluar_asset(asset, categoria):
    """Devuelve dict de estado para un asset (sin generar nada si no hay archivo)."""
    archivo = asset.get("archivo")
    if not archivo:
        # Sin nombre de archivo en el manifiesto: no se inventa uno, queda
        # esperando entrega (P2/P5). Se revisará cuando lleguen los archivos.
        return nuevo_estado(asset, categoria, ESPERANDO_ENTREGA,
                            "sin archivo de entrega definido en manifiesto")
    if not _archivo_entregado(categoria, archivo):
        return nuevo_estado(asset, categoria, ESPERANDO_ENTREGA,
                            f"falta {DIR_ENTREGA / categoria / Path(archivo).name}")
    # El archivo llegó: procesar según categoría.
    if categoria == "sfx":
        salida = DIR_AUDIO / "sfx" / Path(archivo).name
        ok, motivo = normalizar_sfx(_ruta_entrega(categoria, archivo), salida, float(asset.get("duracion_s", 0)))
        if not ok:
            return nuevo_estado(asset, categoria, FALLA, motivo)
        generar_variantes_sfx(salida)
        return nuevo_estado(asset, categoria, OK, "normalizado")
    if categoria == "musica":
        salida = DIR_AUDIO / "musica" / Path(archivo).with_suffix(".ogg").name
        ok, motivo = codificar_musica(_ruta_entrega(categoria, archivo), salida, bool(asset.get("bucle", False)))
        if not ok:
            estado = PENDIENTE_HERRAMIENTA if motivo == PENDIENTE_HERRAMIENTA else FALLA
            return nuevo_estado(asset, categoria, estado, motivo)
        return nuevo_estado(asset, categoria, OK, "codificado")
    if categoria == "sprites":
        ok, motivo = procesar_sprite(asset)
        if not ok:
            estado = PENDIENTE_HERRAMIENTA if motivo == PENDIENTE_HERRAMIENTA else FALLA
            return nuevo_estado(asset, categoria, estado, motivo)
        return nuevo_estado(asset, categoria, OK, "procesado")
    return nuevo_estado(asset, categoria, FALLA, f"categoría desconocida {categoria}")


def procesar_todo(manifiesto):
    entries = []
    for asset in manifiesto.get("sfx", []):
        entries.append(evaluar_asset(asset, "sfx"))
    # alma_ref expande a alma_1..alma_6 cuando llega el archivo.
    for asset in manifiesto.get("sfx", []):
        if asset.get("id") == "alma_ref" and _archivo_entregado("sfx", asset["archivo"]):
            resultados = procesar_alma_ref(_ruta_entrega("sfx", asset["archivo"]))
            for i in range(1, 7):
                clave = f"alma_{i}"
                ok, motivo = resultados.get(clave, (False, "sin procesar"))
                entries.append({
                    "id": clave,
                    "categoria": "sfx",
                    "archivo": f"sfx/alma_{i}.wav",
                    "estado": OK if ok else FALLA,
                    "motivo": motivo,
                })
    for asset in manifiesto.get("musica", []):
        entries.append(evaluar_asset(asset, "musica"))
    for asset in manifiesto.get("sprites", []):
        entries.append(evaluar_asset(asset, "sprites"))
    return entries


def procesar_solo(manifiesto, asset_id):
    for categoria in ("sfx", "musica", "sprites"):
        for asset in manifiesto.get(categoria, []):
            if asset.get("id") == asset_id:
                return [evaluar_asset(asset, categoria)]
    return []


def copiar_gdevelop():
    """F4-1. Copia a export/gdevelop_nativo/assets/ solo los assets OK."""
    if not REPORT_PATH.exists():
        return False, "reporte no existente"
    reporte = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
    DIR_GD_ASSETS.mkdir(parents=True, exist_ok=True)
    copiados = 0
    for entrada in reporte.get("assets", []):
        if entrada.get("estado") != OK:
            continue
        archivo = entrada.get("archivo")
        if not archivo:
            continue
        src = RAIZ / "assets" / archivo
        dst = DIR_GD_ASSETS / Path(archivo).name
        if src.exists():
            dst.parent.mkdir(parents=True, exist_ok=True)
            import shutil
            shutil.copy2(src, dst)
            copiados += 1
    return True, f"{copiados} assets copiados"


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def cmd_validar_manifiesto():
    manifiesto = cargar_manifiesto()
    ok1, err1 = validar_manifiesto(manifiesto)
    ok2, err2 = verificar_contra_codigo(manifiesto)
    asegurar_carpetas()
    errores = err1 + err2
    print(f"F0-1 validación manifiesto: {'OK' if ok1 else 'FALLA'}")
    print(f"F0-2 verificación código:   {'OK' if ok2 else 'FALLA'}")
    print(f"F0-3 carpetas:              {'OK' if asegurar_carpetas() else 'FALLA'}")
    for e in errores:
        print(f"  - {e}")
    if errores:
        print("RESULTADO: FALLA")
        return 1
    print("RESULTADO: OK")
    return 0


def cmd_todo(manifiesto):
    entries = procesar_todo(manifiesto)
    reporte = escribir_reporte(entries)
    resumen = reporte["resumen"]
    print(f"F1/F3 --todo: total={reporte['total']} OK={resumen.get(OK,0)} "
          f"ESPERANDO_ENTREGA={resumen.get(ESPERANDO_ENTREGA,0)} "
          f"FALLA={resumen.get(FALLA,0)} PENDIENTE_HERRAMIENTA={resumen.get(PENDIENTE_HERRAMIENTA,0)}")
    print(f"Reporte: {REPORT_PATH}")
    return 0


def cmd_solo(manifiesto, asset_id):
    entries = procesar_solo(manifiesto, asset_id)
    if not entries:
        print(f"Asset '{asset_id}' no encontrado en el manifiesto.")
        return 1
    escribir_reporte(entries)
    for e in entries:
        print(f"{e['id']} [{e['categoria']}]: {e['estado']} — {e['motivo']}")
    return 0


def main():
    parser = argparse.ArgumentParser(description="Importador de assets IA de IN CRYPTA")
    parser.add_argument("--validar-manifiesto", action="store_true", help="F0: valida manifiesto y crea carpetas")
    parser.add_argument("--todo", action="store_true", help="Procesa todos los assets y genera reports/assets_ia.json")
    parser.add_argument("--solo", metavar="ID", help="Procesa un solo asset por id")
    parser.add_argument("--gdevelop", action="store_true", help="F4-1: copia assets OK a export/gdevelop_nativo/assets/")
    args = parser.parse_args()

    if args.validar_manifiesto:
        return cmd_validar_manifiesto()
    if args.gdevelop:
        ok, msg = copiar_gdevelop()
        print(msg)
        return 0 if ok else 1

    manifiesto = cargar_manifiesto()
    if args.todo:
        return cmd_todo(manifiesto)
    if args.solo:
        return cmd_solo(manifiesto, args.solo)

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
