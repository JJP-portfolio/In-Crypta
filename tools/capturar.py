#---- Captura de pantallas y salidas de ejemplo ----#

import array
import os
from pathlib import Path
import sys
import wave

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

RAIZ = Path(__file__).resolve().parent.parent
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

import numpy as np
import pygame

pygame.mixer.pre_init(44100, -16, 2, 2048)
pygame.init()

import config
from audio import FRECUENCIA_MUESTREO, sintetizar_campana_carillon, sintetizar_corazon_delator
from camara import Camara
from config import ORO_LITÚRGICO, TILE, TURQUESA_ÁNIMA
from entidades import Jugador, OndaCustodio
from juego import Juego
from nivel import Nivel
from tools import generar_musica_synthlab as synth

RUTA_FUENTE = RAIZ / config.RUTA_FUENTE_GOTICA


def _fuente(tam):
    if RUTA_FUENTE.exists():
        return pygame.font.Font(str(RUTA_FUENTE), tam)
    return pygame.font.SysFont("monospace", tam, bold=True)


def _capturar_pantallas_principales(destino):
    # Portada
    juego = Juego()
    for _ in range(30):
        juego.actualizar(1 / 60)
    juego.dibujar()
    pygame.image.save(juego.pantalla, str(destino / "titulo.png"))

    # Menu principal
    juego = Juego()
    juego.abrir_menu()
    juego.menu_opcion = 0
    for _ in range(5):
        juego.actualizar(1 / 60)
    juego.dibujar()
    pygame.image.save(juego.pantalla, str(destino / "menu_tutorial.png"))

    # Tutorial
    juego = Juego()
    juego.iniciar_tutorial()
    for _ in range(30):
        juego.actualizar(1 / 60)
    juego.dibujar()
    pygame.image.save(juego.pantalla, str(destino / "tutorial.png"))

    # Actos 1 a 3
    for idx in range(3):
        juego = Juego()
        juego.cargar_nivel(idx, vidas=3)
        for _ in range(30):
            juego.actualizar(1 / 60)
        juego.dibujar()
        pygame.image.save(juego.pantalla, str(destino / f"nivel_{idx + 1}.png"))


def _limpiar_toast_hud(juego):
    juego.hud.mensajes.estado = juego.hud.mensajes.OCULTO
    juego.hud.mensajes.texto = ""
    juego.hud.mensajes.prioridad = 0


def _capturar_minijefe_carcelero(destino):
    # Escena de arena del Carcelero con muro emergente y estado vulnerable
    juego = Juego()
    juego.cargar_nivel(2, vidas=4)
    _limpiar_toast_hud(juego)
    j = juego.jugador
    j.tiene_pala = True
    j.tiene_dash = True
    j.x = float(126 * TILE)
    j.y = float(12 * TILE)
    j.rect.topleft = (round(j.x), round(j.y))
    j.vy = -120.0
    j.en_suelo = False
    j.direccion = 1

    carcelero = juego.nivel.minijefes[0]
    carcelero.activado = True
    carcelero.vida = 2
    carcelero.x = float(133 * TILE)
    carcelero.rect.x = round(carcelero.x)
    carcelero.direccion = -1
    carcelero.estado = "cansado"
    carcelero.vulnerable = True
    carcelero.temporizador = 1.4

    muro = juego.nivel.muros_minijefe[1]
    muro.estado = "armado"
    muro.progreso = 1.0
    muro.tiempo_impacto = 0.14

    juego.camara.x = float(118 * TILE)
    juego.camara.y = 0.0
    juego.actualizar(1 / 60)
    juego.dibujar()
    pygame.image.save(juego.pantalla, str(destino / "minijefe_carcelero.png"))


def _capturar_jefe_custodio(destino):
    # Fase 1 junto a la compuerta derecha anclada al dintel de piedra
    juego = Juego()
    juego.cargar_nivel(2, vidas=5)
    _limpiar_toast_hud(juego)
    j = juego.jugador
    j.tiene_pala = True
    j.tiene_dash = True
    j.x = float(131 * TILE)
    j.y = float(28 * TILE)
    j.rect.topleft = (round(j.x), round(j.y))
    j.direccion = -1

    jefe = juego.jefe
    jefe.x = float(122 * TILE)
    jefe.rect.x = round(jefe.x)
    jefe.direccion = 1
    jefe.estado = "telegrafia"
    jefe.temporizador = 0.35
    for comp in juego.nivel.compuertas_arena:
        comp.cerrar()
        comp.progreso = 1.0

    juego.camara.x = float(117 * TILE)
    juego.camara.y = float(18 * TILE)
    juego.actualizar(1 / 60)
    juego.dibujar()
    pygame.image.save(juego.pantalla, str(destino / "jefe_custodio_f1.png"))

    # Fase 3: El Sepulcro con Guadana Consagrada y capa de criptas rota
    _limpiar_toast_hud(juego)
    j.rango_ataque_mejorado = True
    j.escudo_farol = True
    j.filo_anima = True
    j.x = float(113 * TILE)
    j.y = float(25 * TILE)
    j.rect.topleft = (round(j.x), round(j.y))
    j.direccion = 1
    j.ataque_tiempo = 0.12
    j.ataque_duracion = 0.22
    j.ataque_abajo = True

    for b in juego.nivel.bloques_cripta:
        col_b = b.rect.x // TILE
        fila_b = b.rect.y // TILE
        if fila_b == 30 and 112 <= col_b <= 122:
            b.roto = True

    jefe.fase = 3
    jefe.vida = 1
    jefe.estado = "aterrizaje_smb3"
    jefe.temporizador = 0.42
    jefe.x = float(116 * TILE)
    jefe.y = float(31 * TILE - jefe.rect.height)
    jefe.rect.topleft = (round(jefe.x), round(jefe.y))
    juego.ondas_jefe = [OndaCustodio(jefe.rect.centerx - 52, 31 * TILE - 12, -1, 210)]
    juego.camara.x = float(106 * TILE)
    juego.camara.y = float(18 * TILE)
    juego.dibujar()
    pygame.image.save(juego.pantalla, str(destino / "jefe_custodio_f3.png"))


def _generar_ejemplo_sepulturero(dir_ej):
    poses = [
        ("Reposo + Farol", 50, 1, "idle", False, False, 0.0),
        ("Tajo con Guadana", 24, 1, "ataque2", True, True, 0.0),
        ("Dash Espectral", 64, 1, "dash", False, False, 0.14),
    ]
    w_panel, h_panel = 136, 76
    escala = 3
    lienzo = pygame.Surface((w_panel * 3 * escala, (h_panel + 18) * escala))
    lienzo.fill((14, 12, 18))
    cam = Camara()
    cam.x, cam.y = 0.0, 0.0
    fnt = _fuente(16)

    for idx, (titulo, px, d, pose, es_guad, filo, t_dash) in enumerate(poses):
        sub = pygame.Surface((w_panel, h_panel))
        sub.fill((22, 19, 28))
        pygame.draw.rect(sub, (46, 40, 52), (0, h_panel - 14, w_panel, 14))
        pygame.draw.line(sub, (180, 170, 150), (0, h_panel - 14), (w_panel, h_panel - 14), 2)

        jug = Jugador(px, h_panel - 14 - config.JUGADOR_ALTO, tiene_dash=True)
        jug.tiene_pala = True
        jug.en_suelo = True
        jug.direccion = d
        jug.dash_direccion = d
        jug.dash_tiempo = t_dash
        jug.rango_ataque_mejorado = es_guad
        jug.filo_anima = filo
        if pose.startswith("ataque"):
            jug.ataque_tiempo = 0.12
            jug.ataque_duracion = 0.22
        jug.dibujar(sub, cam, 1.4, pose=pose, con_pala=True)

        amp = pygame.transform.scale(sub, (w_panel * escala, h_panel * escala))
        x_dest = idx * w_panel * escala
        lienzo.blit(amp, (x_dest, 0))
        pygame.draw.rect(lienzo, (68, 56, 44), (x_dest, 0, w_panel * escala, h_panel * escala), 1)
        txt = fnt.render(titulo, True, ORO_LITÚRGICO)
        lienzo.blit(txt, (x_dest + (w_panel * escala - txt.get_width()) // 2, h_panel * escala + 16))

    pygame.image.save(lienzo, str(dir_ej / "render_sepulturero.png"))


def _generar_ejemplo_autotiling(dir_ej):
    # Usamos 18 filas para activar fila_rel techo (1..3) y piso (>=15)
    mapa_18 = "\n".join([
        "###########",
        "#.#...###.#",
        "#.........#",
        "#.........#",
        "#.........#",
        "#.........#",
        "#.........#",
        "#.........#",
        "#.........#",
        "#.........#",
        "#.........#",
        "#.........#",
        "#.........#",
        "#...####..#",
        "#P.......G#",
        "###########",
        "###########",
        "###########",
    ])
    temas = [("camposanto", "Camposanto"), ("cripta", "La Cripta"), ("osario", "El Osario")]
    cam = Camara()
    cam.x, cam.y = 0.0, 0.0
    col_w = 11 * TILE
    fnt = _fuente(15)
    lienzo = pygame.Surface((col_w * 3, 7 * TILE + 34))
    lienzo.fill((14, 12, 18))

    for idx, (tema, nombre) in enumerate(temas):
        niv = Nivel(mapa_18, tema=tema)
        full = pygame.Surface((col_w, 18 * TILE))
        full.fill((18, 16, 24) if tema != "osario" else (24, 13, 18))
        niv.dibujar_solidos(full, cam)

        recorte = pygame.Surface((col_w, 7 * TILE))
        recorte.blit(full, (0, 0), (0, 0, col_w, 3 * TILE))
        recorte.blit(full, (0, 3 * TILE), (0, 13 * TILE, col_w, 4 * TILE))

        x0 = idx * col_w
        lienzo.blit(recorte, (x0, 0))
        pygame.draw.rect(lienzo, (70, 58, 44), (x0, 0, col_w, 7 * TILE), 1)
        txt = fnt.render(nombre, True, ORO_LITÚRGICO)
        lienzo.blit(txt, (x0 + (col_w - txt.get_width()) // 2, 7 * TILE + 6))

    pygame.image.save(lienzo, str(dir_ej / "render_autotiling.png"))


def _generar_ejemplo_shaders(dir_ej):
    juego = Juego()
    juego.cargar_nivel(1, vidas=3)
    juego.jugador.x = float(29 * TILE)
    juego.jugador.rect.x = round(juego.jugador.x)
    for _ in range(10):
        juego.actualizar(1 / 60)
    _limpiar_toast_hud(juego)

    modos = [
        (2, 2, "Puro (Sin filtros)"),
        (1, 0, "Suave (Penumbra + Bloom)"),
        (0, 0, "Gotico (Bloom + CRT)"),
    ]
    w, h = config.ANCHO, config.ALTO
    tercio = w // 3
    recorte_x = max(0, (w // 2) - (tercio // 2) + 40)
    comp = pygame.Surface((tercio * 3, h + 32))
    comp.fill((12, 10, 16))
    fnt = _fuente(15)

    for idx, (modo_sh, modo_cal, etiqueta) in enumerate(modos):
        juego.config_shader_idx = modo_sh
        juego.config_calidad_idx = modo_cal
        juego.dibujar()
        x0 = idx * tercio
        comp.blit(juego.pantalla, (x0, 32), (recorte_x, 0, tercio, h))
        if idx > 0:
            pygame.draw.line(comp, ORO_LITÚRGICO, (x0, 0), (x0, h + 32), 2)
        txt = fnt.render(etiqueta, True, ORO_LITÚRGICO)
        comp.blit(txt, (x0 + (tercio - txt.get_width()) // 2, 5))

    pygame.image.save(comp, str(dir_ej / "render_shaders.png"))


def _guardar_wav_desde_sound(sonido, ruta_wav):
    crudo = sonido.get_raw()
    with wave.open(str(ruta_wav), "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(FRECUENCIA_MUESTREO)
        wf.writeframes(crudo)
    muestras = np.frombuffer(crudo, dtype=np.int16).reshape(-1, 2).mean(axis=1) / 32767.0
    return muestras.astype(np.float32)


def _dibujar_onda_panel(surf, r_onda, mono):
    pygame.draw.rect(surf, (22, 19, 28), r_onda)
    pygame.draw.rect(surf, (70, 58, 44), r_onda, 1)
    cy = r_onda.centery
    pygame.draw.line(surf, (46, 42, 54), (r_onda.left, cy), (r_onda.right, cy), 1)
    bloque = max(1, len(mono) // r_onda.width)
    amp_max = max(float(np.max(np.abs(mono))), 1e-4)
    for x in range(r_onda.width):
        seg = mono[x * bloque:(x + 1) * bloque]
        if len(seg) == 0:
            break
        y1 = cy - int((float(np.max(seg)) / amp_max) * (r_onda.height // 2 - 4))
        y2 = cy - int((float(np.min(seg)) / amp_max) * (r_onda.height // 2 - 4))
        pygame.draw.line(surf, TURQUESA_ÁNIMA, (r_onda.x + x, y1), (r_onda.x + x, max(y1, y2)))


def _dibujar_fft_panel(surf, r_fft, mono, f_max, marcas_hz, fnt_sm):
    pygame.draw.rect(surf, (22, 19, 28), r_fft)
    pygame.draw.rect(surf, (70, 58, 44), r_fft, 1)
    espectro = np.abs(np.fft.rfft(mono * np.hanning(len(mono))))
    freqs = np.fft.rfftfreq(len(mono), d=1.0 / FRECUENCIA_MUESTREO)
    mascara = freqs <= f_max
    f_vis, e_vis = freqs[mascara], espectro[mascara]
    e_norm = e_vis / max(float(np.max(e_vis)), 1e-6)

    for px in range(r_fft.width):
        f_a, f_b = (px / r_fft.width) * f_max, ((px + 1) / r_fft.width) * f_max
        sel = e_norm[(f_vis >= f_a) & (f_vis < f_b)]
        val = float(np.max(sel)) if len(sel) else 0.0
        alto_b = int(val * (r_fft.height - 16))
        if alto_b > 0:
            pygame.draw.line(
                surf,
                (215, 165, 82),
                (r_fft.x + px, r_fft.bottom - 2),
                (r_fft.x + px, r_fft.bottom - 2 - alto_b),
                2,
            )
    if marcas_hz:
        for freq_m, eti in marcas_hz:
            mx = r_fft.x + int((freq_m / f_max) * r_fft.width)
            if r_fft.left <= mx <= r_fft.right:
                pygame.draw.line(surf, (215, 75, 95), (mx, r_fft.top + 14), (mx, r_fft.bottom - 2), 1)
                surf.blit(fnt_sm.render(eti, True, (240, 215, 180)), (mx + 2, r_fft.top + 2))


def _graficar_onda_y_espectro(mono, titulo, ruta_png, marcas_hz=None, f_max=4500.0):
    w, h = 640, 300
    surf = pygame.Surface((w, h))
    surf.fill((14, 12, 18))
    fnt, fnt_sm = _fuente(13), _fuente(11)
    surf.blit(fnt.render(titulo, True, ORO_LITÚRGICO), (14, 8))
    _dibujar_onda_panel(surf, pygame.Rect(14, 34, w - 28, 108), mono)
    _dibujar_fft_panel(surf, pygame.Rect(14, 156, w - 28, 118), mono, f_max, marcas_hz, fnt_sm)
    surf.blit(fnt_sm.render(f"Tiempo: 0 .. {len(mono) / FRECUENCIA_MUESTREO:.2f} s", True, (175, 170, 182)), (18, 140))
    surf.blit(fnt_sm.render(f"Espectro: 0 .. {int(f_max)} Hz", True, (175, 170, 182)), (18, 278))
    pygame.image.save(surf, str(ruta_png))


def _sintetizar_fragmento_custodio(spec):
    corchea16 = (60.0 / spec["bpm"]) / 4.0
    pasos = 32
    dur_total = pasos * corchea16
    pista = synth.PistaEstereo(dur_total, en_bucle=True)
    rng = np.random.default_rng(7)
    bateria = (
        synth.percusion_bombo(0.95),
        synth.percusion_caja(0.88, rng),
        synth.percusion_caja(0.34, rng),
        synth.percusion_charleston(False, 0.52, rng),
        synth.percusion_charleston(True, 0.45, rng),
    )

    def tiempo_paso(p):
        offset = (spec["swing"] - 0.5) * 2.0 * corchea16 if (p % 2 == 1) else 0.0
        return max(0.0, (p * corchea16 + offset) % dur_total)

    synth._mezclar_armonia(pista, spec["acordes"][:2], tiempo_paso, 16, corchea16, True, True)
    synth._mezclar_ritmo_y_bajo(
        pista, pasos, spec["acordes"][:2], 16, spec["bajo_patron"],
        (spec["ritmo_kick"], spec["ritmo_snare"], spec["ritmo_hat"]),
        bateria, tiempo_paso, corchea16, spec["overdrive_bajo"],
    )
    for step, m_nota, dur_pasos in spec["melodia_pasos"]:
        if 0 <= step < pasos:
            lead = synth.inst_lead_expresivo(synth.midi_a_hz(m_nota), dur_pasos * corchea16, 0.86)
            pista.mezclar(tiempo_paso(step), lead, pan=-0.08)
    estereo = pista.aplicar_espacio_y_master(retardo_s=corchea16 * 3.0, feedback_echo=0.22)
    return (estereo.mean(axis=1) / 32767.0).astype(np.float32)


def _generar_ejemplos_audio(dir_ej):
    campana = sintetizar_campana_carillon(587.33)
    mono_campana = _guardar_wav_desde_sound(campana, dir_ej / "campana_re5.wav")
    _graficar_onda_y_espectro(
        mono_campana,
        "sintetizar_campana_carillon(587.33) — Bronce Inarmonico (Re5)",
        dir_ej / "audio_campana.png",
        marcas_hz=[
            (587.3, "1.0x"),
            (1174.7, "2.0x"),
            (1399.0, "2.38x"),
            (1770.2, "3.01x"),
            (2390.4, "4.07x"),
            (3189.2, "5.43x"),
        ],
        f_max=3450.0,
    )

    corazon = sintetizar_corazon_delator()
    crudo_c = corazon.get_raw()
    mono_c = (np.frombuffer(crudo_c, dtype=np.int16).reshape(-1, 2).mean(axis=1) / 32767.0).astype(np.float32)
    _graficar_onda_y_espectro(
        mono_c,
        "sintetizar_corazon_delator() — Doble Pulso (55 Hz + 48 Hz)",
        dir_ej / "audio_corazon.png",
        marcas_hz=[(55.0, "55 Hz")],
        f_max=400.0,
    )

    spec = next(p for p in synth.ESPECIFICACIONES_PISTAS if p["nombre"] == "custodio_f3")
    mono_f3 = _sintetizar_fragmento_custodio(spec)
    _graficar_onda_y_espectro(
        mono_f3,
        "generar_musica_synthlab.py — Custodio Fase 3 (154 BPM, 2 compases)",
        dir_ej / "audio_custodio_f3.png",
        marcas_hz=[(73.4, "73Hz"), (293.7, "D4"), (587.3, "D5"), (1174.7, "D6")],
        f_max=3000.0,
    )


def main():
    destino = RAIZ / "capturas"
    dir_ej = destino / "ejemplos"
    destino.mkdir(exist_ok=True)
    dir_ej.mkdir(exist_ok=True)

    _capturar_pantallas_principales(destino)
    _capturar_minijefe_carcelero(destino)
    _capturar_jefe_custodio(destino)
    _generar_ejemplo_sepulturero(dir_ej)
    _generar_ejemplo_autotiling(dir_ej)
    _generar_ejemplo_shaders(dir_ej)
    _generar_ejemplos_audio(dir_ej)

    pygame.quit()
    print(f"CAPTURAS_OK en {destino}")


if __name__ == "__main__":
    main()
