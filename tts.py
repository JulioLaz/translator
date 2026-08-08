'''
=============================================================
TTS - TEXT TO SPEECH - AGENTE TRADUCTOR
=============================================================
Convierte texto a audio WAV usando Piper TTS local.
El idioma de síntesis (ES o EN) lo recibe como parámetro desde
el pipeline (ya lo determinó Whisper en el paso de STT).
=============================================================
Versión: 1.2.0
Cambios:
  1.0.0 - Versión inicial con Piper TTS
  1.1.0 - Detección de idioma mejorada por palabras clave
          reemplaza detección por caracteres especiales
  1.2.0 - Se elimina la re-detección por palabras clave; el
          idioma ahora se pasa explícitamente desde el pipeline
=============================================================
'''

import subprocess
import os
import tempfile

# === PATHS ===
PIPER_EXE = r'C:\JulioPrograma\agente_traductor\piper\piper_windows_amd64\piper\piper.exe'
VOZ_ES = r'C:\JulioPrograma\agente_traductor\piper\piper_windows_amd64\piper\es_ES-davefx-medium.onnx'
# VOZ_EN = r'C:\JulioPrograma\agente_traductor\piper\piper_windows_amd64\piper\en_US-lessac-medium.onnx'
VOZ_EN = r'C:\JulioPrograma\agente_traductor\piper\piper_windows_amd64\piper\en_US-ryan-medium.onnx'
def sintetizar(texto, idioma):
    """
    Convierte texto a audio WAV usando Piper TTS.
    idioma: 'es' o 'en', el idioma del texto a sintetizar (ya conocido
    por el pipeline, no se re-detecta acá).
    Retorna: path al archivo WAV generado
    """
    voz = VOZ_ES if idioma == 'es' else VOZ_EN

    if not os.path.exists(voz):
        print(f"⚠️  Modelo de voz no encontrado: {voz}")
        return None

    tmp = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
    tmp_path = tmp.name
    tmp.close()

    print(f"🔊 Sintetizando voz ({idioma})...")

    try:
        proceso = subprocess.run(
            [PIPER_EXE, '--model', voz, '--output_file', tmp_path],
            input=texto,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )

        if proceso.returncode != 0:
            print(f"❌ Error en TTS: {proceso.stderr}")
            return None

        if not os.path.exists(tmp_path) or os.path.getsize(tmp_path) == 0:
            print("❌ Archivo WAV vacío o no generado")
            return None

        return tmp_path

    except Exception as e:
        print(f"❌ Error en TTS: {e}")
        return None


def limpiar_temporal(wav_path):
    """Elimina archivo WAV temporal."""
    try:
        if wav_path and os.path.exists(wav_path):
            os.remove(wav_path)
    except Exception:
        pass