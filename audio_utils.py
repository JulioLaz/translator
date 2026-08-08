'''
=============================================================
AUDIO UTILS - AGENTE TRADUCTOR
=============================================================
Maneja la captura de audio desde el micrófono con detección
de silencio automática, y la reproducción de archivos WAV.
=============================================================
Versión: 1.0.0
Cambios:
  1.0.0 - Versión inicial
=============================================================
'''

import pyaudio
import wave
import numpy as np
import subprocess
import os
import tempfile

# === CONFIGURACIÓN DE AUDIO ===
SAMPLE_RATE = 16000       # Hz requerido por Whisper
CHANNELS = 1              # Mono
FORMAT = pyaudio.paInt16  # 16-bit
CHUNK = 1024              # Frames por buffer
SILENCE_THRESHOLD = 500   # Umbral RMS para detectar silencio
SILENCE_DURATION = 1.5    # Segundos de silencio para cortar grabación
MAX_DURATION = 30         # Segundos máximo de grabación


def calcular_rms(data):
    """Calcula el RMS (nivel de volumen) de un chunk de audio."""
    audio_array = np.frombuffer(data, dtype=np.int16).astype(np.float32)
    if len(audio_array) == 0:
        return 0
    return np.sqrt(np.mean(audio_array ** 2))

import threading

def grabar_hasta_silencio():
    p = pyaudio.PyAudio()
    stream = p.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=SAMPLE_RATE,
        input=True,
        input_device_index=1,
        frames_per_buffer=CHUNK
    )

    print("🎙️  Grabando... (presioná ENTER para terminar)")

    frames = []
    grabando = [True]

    def esperar_enter():
        input()
        grabando[0] = False

    hilo = threading.Thread(target=esperar_enter, daemon=True)
    hilo.start()

    while grabando[0]:
        data = stream.read(CHUNK, exception_on_overflow=False)
        frames.append(data)

    stream.stop_stream()
    stream.close()
    p.terminate()

    if not frames:
        return None

    tmp = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
    tmp_path = tmp.name
    tmp.close()

    with wave.open(tmp_path, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(pyaudio.PyAudio().get_sample_size(FORMAT))
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(b''.join(frames))

    return tmp_path

def grabar_hasta_silencio00():
    """
    Graba audio desde el micrófono hasta detectar silencio.
    Retorna el path al archivo WAV temporal grabado.
    """
    p = pyaudio.PyAudio()
    # stream = p.open(
    #     format=FORMAT,
    #     channels=CHANNELS,
    #     rate=SAMPLE_RATE,
    #     input=True,
    #     frames_per_buffer=CHUNK
    # )
    stream = p.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=SAMPLE_RATE,
        input=True,
        input_device_index=1,
        frames_per_buffer=CHUNK
    )
    print("🎙️  Escuchando... (hablá cuando quieras)")

    frames = []
    chunks_silencio = 0
    chunks_silencio_max = int(SILENCE_DURATION * SAMPLE_RATE / CHUNK)
    chunks_max = int(MAX_DURATION * SAMPLE_RATE / CHUNK)
    grabando = False
    chunk_count = 0

    while chunk_count < chunks_max:
        data = stream.read(CHUNK, exception_on_overflow=False)
        rms = calcular_rms(data)

        if rms > SILENCE_THRESHOLD:
            if not grabando:
                print("🔴 Grabando...")
                grabando = True
            frames.append(data)
            chunks_silencio = 0
        elif grabando:
            frames.append(data)
            chunks_silencio += 1
            if chunks_silencio >= chunks_silencio_max:
                print("⏹️  Silencio detectado, procesando...")
                break

        chunk_count += 1

    stream.stop_stream()
    stream.close()
    p.terminate()

    if not frames:
        return None

    # Guardar en archivo temporal
    tmp = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
    tmp_path = tmp.name
    tmp.close()

    with wave.open(tmp_path, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(b''.join(frames))

    return tmp_path


def reproducir_wav(wav_path):
    """Reproduce un archivo WAV usando el reproductor del sistema."""
    if not os.path.exists(wav_path):
        print(f"⚠️  Archivo no encontrado: {wav_path}")
        return
    # Reproducción bloqueante en Windows
    subprocess.run(['powershell', '-c', f'(New-Object Media.SoundPlayer "{wav_path}").PlaySync()'],
                   capture_output=True)
