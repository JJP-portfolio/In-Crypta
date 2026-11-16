#---- Importamos librerias ----#
import ast
from pathlib import Path
import sys

#---- Constantes de medicion ----#
RAIZ = Path(__file__).resolve().parent.parent
CARPETAS_EXCLUIDAS = {".venv", "tests", "__pycache__", ".git", ".pytest_cache", "build", "dist"}
TOPE_FUNCION_SUAVE = 40
TOPE_FUNCION_DURO = 60
TOPE_LINEA_SUAVE = 100
TOPE_LINEA_DURO = 120


#---- Recorrido de archivos ----#
def listar_archivos_python(raiz):
    """Devuelve los archivos Python del proyecto excluyendo tests, entornos y mapas."""
    archivos = []
    for ruta in sorted(raiz.rglob("*.py")):
        partes = set(ruta.relative_to(raiz).parts)
        if partes & CARPETAS_EXCLUIDAS:
            continue
        if ruta.name.startswith("niveles"):
            continue
        archivos.append(ruta)
    return archivos


#---- Analisis AST por archivo ----#
def _es_except_generico(nodo):
    # Detectamos except: o except Exception
    if not isinstance(nodo, ast.ExceptHandler):
        return False
    if nodo.type is None:
        return True
    return isinstance(nodo.type, ast.Name) and nodo.type.id == "Exception"


def _contar_en_funciones(arbol):
    # Recorremos las funciones para medir largo e imports locales
    funcs_60 = []
    funcs_40 = []
    imports_locales = 0
    en_funcion = []

    def visitar(nodo):
        nonlocal imports_locales
        es_func = isinstance(nodo, (ast.FunctionDef, ast.AsyncFunctionDef))
        if es_func:
            largo = (nodo.end_lineno or nodo.lineno) - nodo.lineno + 1
            if largo >= TOPE_FUNCION_DURO:
                funcs_60.append((nodo.name, largo))
            elif largo > TOPE_FUNCION_SUAVE:
                funcs_40.append((nodo.name, largo))
            en_funcion.append(nodo.name)
        elif en_funcion and isinstance(nodo, (ast.Import, ast.ImportFrom)):
            imports_locales += 1

        for hijo in ast.iter_child_nodes(nodo):
            visitar(hijo)

        if es_func:
            en_funcion.pop()

    visitar(arbol)
    return funcs_60, funcs_40, imports_locales


def analizar_archivo(ruta):
    """Calcula lineas, funciones largas, except genericos e imports internos de un archivo."""
    texto = ruta.read_text(encoding="utf-8")
    lineas = texto.splitlines()
    arbol = ast.parse(texto, filename=str(ruta))
    funcs_60, funcs_40, imports_locales = _contar_en_funciones(arbol)
    excepts = sum(1 for nodo in ast.walk(arbol) if _es_except_generico(nodo))
    largas_120 = sum(1 for linea in lineas if len(linea) > TOPE_LINEA_DURO)
    largas_100 = sum(1 for linea in lineas if len(linea) > TOPE_LINEA_SUAVE)
    return {
        "ruta": str(ruta.relative_to(RAIZ)),
        "lineas": len(lineas),
        "funcs_60": funcs_60,
        "funcs_40": funcs_40,
        "largas_120": largas_120,
        "largas_100": largas_100,
        "excepts": excepts,
        "imports_locales": imports_locales,
    }


#---- Reporte en consola ----#
def imprimir_reporte(resultados):
    """Imprime la tabla de metricas por modulo y el resumen total."""
    cabecera = (
        f"{'Archivo':<36} {'Lineas':>6} {'>=60L':>5} {'>40L':>5} "
        f"{'>120c':>5} {'>100c':>5} {'Excep':>5} {'ImpIn':>5}"
    )
    print(cabecera)
    print("-" * len(cabecera))
    totales = [0, 0, 0, 0, 0, 0, 0]
    for res in resultados:
        c60 = len(res["funcs_60"])
        c40 = len(res["funcs_40"]) + c60
        print(
            f"{res['ruta']:<36} {res['lineas']:>6} {c60:>5} {c40:>5} "
            f"{res['largas_120']:>5} {res['largas_100']:>5} "
            f"{res['excepts']:>5} {res['imports_locales']:>5}"
        )
        valores = (
            res["lineas"], c60, c40, res["largas_120"],
            res["largas_100"], res["excepts"], res["imports_locales"],
        )
        totales = [a + b for a, b in zip(totales, valores)]

    print("-" * len(cabecera))
    print(
        f"{'TOTAL':<36} {totales[0]:>6} {totales[1]:>5} {totales[2]:>5} "
        f"{totales[3]:>5} {totales[4]:>5} {totales[5]:>5} {totales[6]:>5}"
    )
    return totales


def main():
    """Punto de entrada del script de metricas de estilo."""
    estricto = "--estricto" in sys.argv
    resultados = [analizar_archivo(ruta) for ruta in listar_archivos_python(RAIZ)]
    totales = imprimir_reporte(resultados)
    if estricto and (totales[1] > 0 or totales[3] > 0 or totales[5] > 0):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
