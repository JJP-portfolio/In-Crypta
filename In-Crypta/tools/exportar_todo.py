# ============================================================
# tools/exportar_todo.py — Pipeline de exportación integral
# ============================================================
# Ejecuta la cadena completa de exportación:
#   1. Exporta proyecto nativo GDevelop 5.6 (IN_CRYPTA_NATIVO.json y assets/)
#   2. Exporta proyecto nativo de salas de prueba (IN_CRYPTA_ROOM_TESTS_NATIVO.json)
#   3. Exporta datos del juego ligero (game_data.json)
#   4. Sincroniza build web nativo (data.js y assets)
#   5. Ejecuta auditorías de paridad, eventos y tests headless
#   6. Empaqueta el archivo ZIP final de distribución
# ============================================================

import json
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
EXPORT = RAIZ / "export"
GD_DIR = EXPORT / "gdevelop"
NATIVO_DIR = EXPORT / "gdevelop_nativo"
ASSETS_DIR = NATIVO_DIR / "assets"
BUILD_DIR = NATIVO_DIR / "build"
PYTHON = sys.executable

def ejecutar(cmd, descripcion):
    print(f"\n[+] {descripcion}...")
    res = subprocess.run(cmd, cwd=str(RAIZ), capture_output=True, text=True)
    if res.stdout:
        print(res.stdout.strip())
    if res.returncode != 0:
        if res.stderr:
            print(res.stderr.strip(), file=sys.stderr)
        raise RuntimeError(f"Fallo en: {descripcion} (código {res.returncode})")
    return res.stdout

def sincronizar_build():
    print("\n[+] Sincronizando export/gdevelop_nativo/build/ ...")
    if not BUILD_DIR.exists():
        BUILD_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Copiar assets actualizados (PNG, WAV, TTF) a build/
    if ASSETS_DIR.exists():
        for archivo in ASSETS_DIR.iterdir():
            if archivo.is_file():
                try:
                    shutil.copy2(archivo, BUILD_DIR / archivo.name)
                except PermissionError:
                    pass
        print(f"  -> {len(list(ASSETS_DIR.iterdir()))} assets copiados a build/")

    # 2. Generar data.js desde IN_CRYPTA_NATIVO.json
    json_nativo = NATIVO_DIR / "IN_CRYPTA_NATIVO.json"
    if json_nativo.exists():
        contenido = json_nativo.read_text(encoding="utf-8")
        data_js = f"gdjs.projectData = {contenido};\n"
        (BUILD_DIR / "data.js").write_text(data_js, encoding="utf-8")
        print(f"  -> build/data.js actualizado ({len(data_js)} bytes)")

def empaquetar_zip():
    print("\n[+] Empaquetando archivo ZIP de exportación...")
    zip_path = EXPORT / "IN_CRYPTA_GDEVELOP_EXPORT.zip"
    
    # Archivos a incluir
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        # 1. gdevelop (Web / JS Standalone)
        for archivo in GD_DIR.rglob("*"):
            if archivo.is_file():
                arcname = str(Path("gdevelop") / archivo.relative_to(GD_DIR))
                zf.write(archivo, arcname)

        # 2. gdevelop_nativo (Proyecto GDevelop 5.6)
        for archivo in NATIVO_DIR.rglob("*"):
            if archivo.is_file() and not archivo.name.endswith(".bak") and not archivo.name.endswith(".autosave"):
                arcname = str(Path("gdevelop_nativo") / archivo.relative_to(NATIVO_DIR))
                zf.write(archivo, arcname)

        # 3. Lanzadores convenientes
        for lanzador in ["jugar_web.bat", "jugar_pygame.bat"]:
            p = RAIZ / lanzador
            if p.exists():
                zf.write(p, lanzador)

    print(f"  -> ZIP generado exitosamente: {zip_path} ({zip_path.stat().st_size // 1024} KB)")
    return zip_path

def main():
    print("=" * 60)
    print("  IN CRYPTA — PIPELINE DE EXPORTACIÓN TOTAL (GDEVELOP 5.6 / JS)")
    print("=" * 60)

    # 1. Generar proyecto nativo campaña
    ejecutar([PYTHON, "tools/generar_proyecto_nativo.py"], "Generando proyecto nativo campaña")

    # 2. Generar proyecto nativo salas de prueba
    ejecutar([PYTHON, "tools/generar_proyecto_rediseñado.py"], "Generando proyecto nativo salas de prueba")

    # 3. Exportar datos JSON para runtime JS
    ejecutar([PYTHON, "tools/export_gdevelop.py"], "Exportando game_data.json")

    # 4. Sincronizar build nativo
    sincronizar_build()

    # 5. Auditorías de paridad y AST de eventos
    ejecutar([PYTHON, "tools/verificar_paridad.py"], "Verificando paridad geométrica y de entidades")
    ejecutar([PYTHON, "tools/validar_eventos_gd.py"], "Validando AST de eventos GDevelop 5.6")

    # 6. Tests del runtime JS
    ejecutar(["node", "tests/test_runtime_gdevelop.js"], "Ejecutando tests headless del runtime JS")

    # 7. Empaquetar ZIP final
    zip_path = empaquetar_zip()

    print("\n" + "=" * 60)
    print("  ¡EXPORTACIÓN COMPLETADA CON ÉXITO!")
    print(f"  Paquete ZIP: {zip_path}")
    print("=" * 60)

if __name__ == "__main__":
    main()
