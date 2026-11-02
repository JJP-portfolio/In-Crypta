#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tools/medir_web.py
==================
Mide la build web de IN CRYPTA en un Chromium real (Playwright). Reporta:

  - t_boton_visible_s: cuánto tarda la página en mostrar el botón de inicio.
  - t_click_a_canvas_1280x720_s: desde el click hasta que el juego fija su canvas.
  - fps_medio: cuadros por segundo sostenidos durante unos segundos.
  - bytes_por_dominio: cuánto se descarga de cada host. Lo que sirve Render
    se cuenta contra su cuota de egreso; el runtime de pygame-web no.
  - errores: errores de consola, excepciones de página y respuestas HTTP >= 400.

Uso:
  python tools/medir_web.py http://localhost:8000/
  python tools/medir_web.py https://jjp-portfolio.github.io/In-Crypta/ --segundos 10

Requisitos (una vez):
  pip install playwright
  playwright install chromium
"""

import argparse
import json
import time
from collections import defaultdict
from pathlib import Path
from urllib.parse import urlparse

from playwright.sync_api import TimeoutError as PlaywrightTimeout
from playwright.sync_api import sync_playwright

BOTON = "#incrypta-inicio-btn"
JS_CANVAS_LISTO = (
    "() => { const c = document.querySelector('canvas');"
    " return !!c && c.width === 1280 && c.height === 720; }"
)
JS_FPS = """(segundos) => new Promise(resolver => {
    let cuadros = 0;
    const t0 = performance.now();
    const paso = (t) => {
        cuadros++;
        if (t - t0 < segundos * 1000) requestAnimationFrame(paso);
        else resolver(cuadros / ((t - t0) / 1000));
    };
    requestAnimationFrame(paso);
})"""


def medir(url, segundos_fps, salida, timeout_s):
    salida.mkdir(parents=True, exist_ok=True)
    timeout_ms = int(timeout_s * 1000)
    errores = []
    bytes_por_dominio = defaultdict(int)
    resultado = {"url": url, "arranco": False}

    with sync_playwright() as p:
        navegador = p.chromium.launch(headless=True)
        pagina = navegador.new_page(viewport={"width": 1280, "height": 720})

        def al_consola(msg):
            if msg.type == "error":
                errores.append(f"[consola] {msg.text}")

        def al_responder(resp):
            host = urlparse(resp.url).netloc or "desconocido"
            try:
                bytes_por_dominio[host] += int(resp.headers.get("content-length", "0"))
            except ValueError:
                pass
            if resp.status >= 400:
                errores.append(f"[HTTP {resp.status}] {resp.url}")

        pagina.on("console", al_consola)
        pagina.on("pageerror", lambda exc: errores.append(f"[excepción] {exc}"))
        pagina.on("response", al_responder)

        t0 = time.perf_counter()
        pagina.goto(url, wait_until="domcontentloaded", timeout=timeout_ms)
        try:
            pagina.wait_for_selector(BOTON, state="visible", timeout=timeout_ms)
        except PlaywrightTimeout:
            errores.append("[medición] no apareció el botón de inicio")
            navegador.close()
            return _cerrar(resultado, errores, bytes_por_dominio, salida)
        resultado["t_boton_visible_s"] = round(time.perf_counter() - t0, 2)
        pagina.screenshot(path=str(salida / "1_antes_del_click.png"))

        t_click = time.perf_counter()
        pagina.click(BOTON)
        try:
            pagina.wait_for_function(JS_CANVAS_LISTO, timeout=timeout_ms)
            resultado["arranco"] = True
            resultado["t_click_a_canvas_1280x720_s"] = round(time.perf_counter() - t_click, 2)
        except PlaywrightTimeout:
            errores.append("[medición] el canvas no llegó a 1280x720 tras el click")

        pagina.wait_for_timeout(500)
        resultado["overlay_removido"] = pagina.query_selector(BOTON) is None
        pagina.screenshot(path=str(salida / "2_despues_del_click.png"))

        if resultado["arranco"]:
            resultado["fps_medio"] = round(pagina.evaluate(JS_FPS, segundos_fps), 1)
            resultado["segundos_medicion_fps"] = segundos_fps

        navegador.close()
    return _cerrar(resultado, errores, bytes_por_dominio, salida)


def _cerrar(resultado, errores, bytes_por_dominio, salida):
    resultado["bytes_por_dominio_mib"] = {
        host: round(n / 1024 / 1024, 2)
        for host, n in sorted(bytes_por_dominio.items(), key=lambda kv: kv[1], reverse=True)
    }
    resultado["errores"] = errores[:30]
    (salida / "resumen.json").write_text(json.dumps(resultado, indent=2, ensure_ascii=False), encoding="utf-8")
    return resultado


def main():
    parser = argparse.ArgumentParser(description="Mide la build web de IN CRYPTA con Chromium")
    parser.add_argument("url", help="URL de la build (local o publicada)")
    parser.add_argument("--segundos", type=float, default=5.0, help="Segundos de medición de FPS")
    parser.add_argument("--timeout", type=float, default=120.0, help="Espera máxima por paso, en segundos")
    parser.add_argument("--salida", type=Path, default=Path("verificacion/medicion_web"),
                        help="Carpeta para capturas y resumen.json")
    args = parser.parse_args()

    resultado = medir(args.url, args.segundos, args.salida, args.timeout)
    print(json.dumps(resultado, indent=2, ensure_ascii=False))
    print(f"\nCapturas y resumen en: {args.salida}")


if __name__ == "__main__":
    main()
