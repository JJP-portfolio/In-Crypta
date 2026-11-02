# Frecuencias de notas musicales (Escala Do Menor Armónico: C, D, Eb, F, G, Ab, B)
NOTAS = {
    'C3': 130.81, 'D3': 146.83, 'Eb3': 155.56, 'F3': 174.61, 'G3': 196.00, 'Ab3': 207.65, 'B3': 246.94,
    'C4': 261.63, 'D4': 293.66, 'Eb4': 311.13, 'F4': 349.23, 'G4': 392.00, 'Ab4': 415.30, 'B4': 493.88,
    'C5': 523.25, 'OFF': 0.0
}

def sintetizar_tema_gotico_multicanal(tempo_bpm=100):
    duracion_corchea = 60.0 / tempo_bpm / 2.0
    
    # Patrón Melódico (Canal 1 - Pulse 1)
    patron_melodia = ['C4', 'Eb4', 'G4', 'C5', 'B4', 'G4', 'Eb4', 'B3', 'C4', 'F4', 'Ab4', 'C5', 'G4', 'Eb4', 'D4', 'B3']
    # Patrón Arpegiado (Canal 2 - Pulse 2)
    patron_arpegio = ['C3', 'G3', 'Eb3', 'G3', 'B2', 'G3', 'D3', 'G3', 'C3', 'Ab3', 'F3', 'Ab3', 'G2', 'D3', 'B2', 'D3']
    # Patrón de Bajo (Canal 3 - Triangle)
    patron_bajo    = ['C3', 'OFF', 'C3', 'OFF', 'B2', 'OFF', 'B2', 'OFF', 'F2', 'OFF', 'F2', 'OFF', 'G2', 'OFF', 'G2', 'OFF']
    # Patrón Percusión (Canal 4 - Noise)
    patron_bateria = [1, 0, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 0, 1, 1, 0]

    buffer_canal1 = []
    buffer_canal2 = []
    buffer_canal3 = []
    buffer_canal4 = []

    for idx in range(len(patron_melodia)):
        # Canal 1: Melodía Principal
        n1 = NOTAS.get(patron_melodia[idx], 0.0)
        c1 = generar_onda_cuadrada(n1, duracion_corchea, duty=0.5, volumen=0.25) if n1 > 0 else np.zeros(int(SAMPLE_RATE * duracion_corchea))
        buffer_canal1.append(c1)

        # Canal 2: Arpegio de Acompañamiento
        n2 = NOTAS.get(patron_arpegio[idx % len(patron_arpegio)], 0.0)
        c2 = generar_onda_cuadrada(n2, duracion_corchea, duty=0.25, volumen=0.15) if n2 > 0 else np.zeros(int(SAMPLE_RATE * duracion_corchea))
        buffer_canal2.append(c2)

        # Canal 3: Línea de Bajo
        n3 = NOTAS.get(patron_bajo[idx % len(patron_bajo)], 0.0)
        c3 = generar_onda_triangular(n3, duracion_corchea, volumen=0.35) if n3 > 0 else np.zeros(int(SAMPLE_RATE * duracion_corchea))
        buffer_canal3.append(c3)

        # Canal 4: Batería / Percusión
        hit = patron_bateria[idx % len(patron_bateria)]
        c4 = generar_ruido_percusivo(duracion_corchea, volumen=0.2, decaimiento=20.0) if hit else np.zeros(int(SAMPLE_RATE * duracion_corchea))
        buffer_canal4.append(c4)

    # Mezcla de los 4 canales
    audio_c1 = np.concatenate(buffer_canal1)
    audio_c2 = np.concatenate(buffer_canal2)
    audio_c3 = np.concatenate(buffer_canal3)
    audio_c4 = np.concatenate(buffer_canal4)

    mezcla_mono = audio_c1 + audio_c2 + audio_c3 + audio_c4
    # Normalización para evitar distorsión
    max_val = np.max(np.abs(mezcla_mono))
    if max_val > 0:
        mezcla_mono = mezcla_mono / max_val * 0.85

    # Estéreo (2 canales interleaved)
    mezcla_estereo = np.column_stack((mezcla_mono, mezcla_mono))
    return mezcla_estereo