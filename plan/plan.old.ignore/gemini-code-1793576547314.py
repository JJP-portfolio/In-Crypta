import wave

def exportar_musica_procedural_wav(ruta_salida="assets/musica_gotica_procedural.wav"):
    audio_estereo = sintetizar_tema_gotico_multicanal(tempo_bpm=96)
    # Convertir float (-1.0 a 1.0) a PCM 16-bit
    audio_pcm16 = (audio_estereo * 32767).astype(np.int16)

    with wave.open(ruta_salida, 'wb') as wav_file:
        wav_file.setnchannels(2)        # Estéreo
        wav_file.setsampwidth(2)        # 16-bit
        wav_file.setframerate(SAMPLE_RATE)
        wav_file.writeframes(audio_pcm16.tobytes())
    print(f"Música procedural exportada exitosamente a: {ruta_salida}")

if __name__ == "__main__":
    exportar_musica_procedural_wav()