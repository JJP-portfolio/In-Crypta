#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tools/medir_web.py
==================
Mide cualquier página HTML5 de IN CRYPTA en un Chromium real (Playwright).
Sirve para la build Pygbag (WebAssembly) de Pygame-CE.

Modos:
  - pygbag : aparece el botón de inicio (--boton). Se hace click y se mide
             hasta que el canvas queda en 1280x720.
  - generico : no hay botón. Se mide cuándo aparece el canvas.

Métricas:
  - t_load_s, t_boton_visible_s, t_canvas_visible_s, t_click_a_canvas_1280x720_s
  - fps_medio, frame_ms_p50, frame_ms_p95, pct_cuadros_lentos (>33 ms, menos de 30 fps)
  - bytes_por_dominio_mib: cuánto baja de cada host (lo que sirve Render cuenta
    contra su cuota de egreso; el runtime de pygame-web no).
  - bytes_antes_click_mib / bytes_despues_click_mib: si la descarga pesada ocurre
    antes o después del click (diagnóstico de arranque).
  - descargas_mas_grandes: las 10 respuestas más pesadas, con su momento.
  - errores: consola, excepciones, HTTP >= 400.

Uso:
  python tools/medir_web.py http://localhost:8000/
  python tools/medir_web.py http://localhost:8000/ --teclas Enter,Enter --segundos 10
  python tools/medir_web.py https://jjp-portfolio.github.io/In-Crypta/ --segundos 10

Requisitos (una vez):
  pip install playwright
  playwright install chromium
"""

import argparse
import json
import statistics
import time
from collections import defaultdict
from pathlib import Path
from urllib.parse import urlparse

from playwright.sync_api import TimeoutError as PlaywrightTimeout
from playwright.sync_api import sync_playwright

BOTON_PYGBAG = "#incrypta-inicio-btn"
JS_CANVAS_1280 = (
    "() => { const c = document.querySelector('canvas');"
    " return !!c && c.width === 1280 && c.height === 720; }"
)
JS_CANVAS_CON_TAMANO = (
    "() => { const c = document.querySelector('canvas'); return !!c && c.width > 1 && c.height > 1; }"
)
# Devuelve los intervalos entre cuadros (ms) durante `segundos`.
JS_INTERVALOS = """(segundos) => new Promise(resolver => {
    const intervalos = [];
    let previo = null;
    const t0 = performance.now();
    const paso = (t) => {
        if (previo !== null) intervalos.push(t - previo);
        previo = t;
        if (t - t0 < segundos * 1000) requestAnimationFrame(paso);
        else resolver(intervalos);
    };
    requestAnimationFrame(paso);
})"""
UMBRAL_LENTO_MS = 1000 / 30  # por encima de esto el cuadro baja de 30 fps


def _percentil(valores, p):
    if not valores:
        return None
    ordenados = sorted(valores)
    k = max(0, min(len(ordenados) - 1, round((p / 100) * (len(ordenados) - 1))))
    return ordenados[k]


def _resumir_intervalos(intervalos):
    if not intervalos:
        return {"cuadros_medidos": 0}
    total_ms = sum(intervalos)
    return {
        "cuadros_medidos": len(intervalos),
        "fps_medio": round(len(intervalos) / (total_ms / 1000), 1),
        "frame_ms_p50": round(statistics.median(intervalos), 1),
        "frame_ms_p95": round(_percentil(intervalos, 95), 1),
        "pct_cuadros_lentos": round(100 * sum(1 for x in intervalos if x > UMBRAL_LENTO_MS) / len(intervalos), 1),
    }


def medir(url, segundos_fps, salida, timeout_s, boton, espera_boton_s, teclas, visible):
    salida.mkdir(parents=True, exist_ok=True)
    timeout_ms = int(timeout_s * 1000)
    errores = []
    bytes_por_dominio = defaultdict(int)
    descargas = []  # (t_rel_s, bytes, host, ruta, estado)
    resultado = {"url": url, "arranco": False}
    t_nav = None
    fase = {"actual": "carga"}  # "carga" | "despues_click"

    with sync_playwright() as p:
        navegador = p.chromium.launch(headless=not visible)
        try:
            pagina = navegador.new_page(viewport={"width": 1280, "height": 720})

            def al_consola(msg):
                if msg.type == "error":
                    errores.append(f"[consola] {msg.text}")

            def al_responder(resp):
                t_rel = time.perf_counter() - t_nav if t_nav else 0.0
                try:
                    tam = int(resp.headers.get("content-length", "0"))
                except ValueError:
                    tam = 0
                host = urlparse(resp.url).netloc or "desconocido"
                bytes_por_dominio[host] += tam
                descargas.append((round(t_rel, 2), tam, host, urlparse(resp.url).path[-60:], resp.status, fase["actual"]))
                if resp.status >= 400:
                    errores.append(f"[HTTP {resp.status}] {resp.url}")

            pagina.on("console", al_consola)
            pagina.on("pageerror", lambda exc: errores.append(f"[excepción] {exc}"))
            pagina.on("response", al_responder)

            t_nav = time.perf_counter()
            pagina.goto(url, wait_until="load", timeout=timeout_ms)
            resultado["t_load_s"] = round(time.perf_counter() - t_nav, 2)

            try:
                pagina.wait_for_selector(boton, state="visible", timeout=int(espera_boton_s * 1000))
                resultado["modo"] = "pygbag"
                resultado["t_boton_visible_s"] = round(time.perf_counter() - t_nav, 2)
                pagina.screenshot(path=str(salida / "1_antes_del_click.png"))
                fase["actual"] = "despues_click"
                t_click = time.perf_counter()
                pagina.click(boton)
                try:
                    pagina.wait_for_function(JS_CANVAS_1280, timeout=timeout_ms)
                    resultado["arranco"] = True
                    resultado["t_click_a_canvas_1280x720_s"] = round(time.perf_counter() - t_click, 2)
                except PlaywrightTimeout:
                    errores.append("[medición] el canvas no llegó a 1280x720 tras el click")
                pagina.wait_for_timeout(500)
                resultado["overlay_removido"] = pagina.query_selector(boton) is None
            except PlaywrightTimeout:
                resultado["modo"] = "generico"
                try:
                    pagina.wait_for_function(JS_CANVAS_CON_TAMANO, timeout=timeout_ms)
                    resultado["t_canvas_visible_s"] = round(time.perf_counter() - t_nav, 2)
                    resultado["arranco"] = True
                except PlaywrightTimeout:
                    errores.append("[medición] no apareció un canvas con tamaño")

            # Teclas para llegar al gameplay (p. ej. Enter en título y en menú)
            for tecla in teclas:
                pagina.keyboard.press(tecla)
                pagina.wait_for_timeout(1500)
            resultado["teclas_enviadas"] = teclas

            intervalos = pagina.evaluate(JS_INTERVALOS, segundos_fps)
            resultado.update(_resumir_intervalos(intervalos))
            resultado["segundos_medicion_fps"] = segundos_fps
            pagina.screenshot(path=str(salida / "2_medicion.png"))
        finally:
            navegador.close()

    return _cerrar(resultado, errores, bytes_por_dominio, descargas, salida)


def _cerrar(resultado, errores, bytes_por_dominio, descargas, salida):
    resultado["bytes_por_dominio_mib"] = {
        host: round(n / 1024 / 1024, 2)
        for host, n in sorted(bytes_por_dominio.items(), key=lambda kv: kv[1], reverse=True)
    }
    antes = sum(t for _, t, _, _, _, f in descargas if f == "carga")
    despues = sum(t for _, t, _, _, _, f in descargas if f == "despues_click")
    resultado["bytes_antes_click_mib"] = round(antes / 1024 / 1024, 2)
    resultado["bytes_despues_click_mib"] = round(despues / 1024 / 1024, 2)
    top = sorted(descargas, key=lambda d: d[1], reverse=True)[:10]
    resultado["descargas_mas_grandes"] = [
        {"t_s": t, "mib": round(b / 1024 / 1024, 2), "host": h, "ruta": r, "estado": s, "fase": f}
        for t, b, h, r, s, f in top if b > 0
    ]
    resultado["errores"] = errores[:30]
    (salida / "resumen.json").write_text(json.dumps(resultado, indent=2, ensure_ascii=False), encoding="utf-8")
    return resultado


def main():
    parser = argparse.ArgumentParser(description="Mide una build HTML5 de IN CRYPTA con Chromium")
    parser.add_argument("url", help="URL de la página (build Pygbag o runtime JS)")
    parser.add_argument("--segundos", type=float, default=5.0, help="Segundos de medición de FPS")
    parser.add_argument("--timeout", type=float, default=120.0, help="Espera máxima por paso, en segundos")
    parser.add_argument("--boton", default=BOTON_PYGBAG, help="Selector del botón de inicio (si aparece, se hace click)")
    parser.add_argument("--espera-boton", type=float, default=5.0,
                        help="Segundos para esperar el botón antes de pasar a modo genérico")
    parser.add_argument("--teclas", default="",
                        help="Teclas a pulsar antes de medir, separadas por coma. Ej: Enter,Enter")
    parser.add_argument("--visible", action="store_true",
                        help="Abre Chromium con ventana (requiere pantalla). Más fiel que headless")
    parser.add_argument("--salida", type=Path, default=Path("verificacion/medicion_web"),
                        help="Carpeta para capturas y resumen.json")
    args = parser.parse_args()
    teclas = [t.strip() for t in args.teclas.split(",") if t.strip()]

    resultado = medir(args.url, args.segundos, args.salida, args.timeout,
                      args.boton, args.espera_boton, teclas, args.visible)
    print(json.dumps(resultado, indent=2, ensure_ascii=False))
    print(f"\nCapturas y resumen en: {args.salida}")


if __name__ == "__main__":
    main()
