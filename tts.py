'''
=============================================================
TTS - TEXT TO SPEECH - AGENTE TRADUCTOR
=============================================================
Convierte texto a audio WAV usando Piper TTS local.
Detecta automáticamente el idioma por palabras clave
para seleccionar la voz correcta (ES o EN).
=============================================================
Versión: 1.1.0
Cambios:
  1.0.0 - Versión inicial con Piper TTS
  1.1.0 - Detección de idioma mejorada por palabras clave
          reemplaza detección por caracteres especiales
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
# === VOCABULARIO PARA DETECCIÓN DE IDIOMA ===
PALABRAS_ES = {
    'el', 'la', 'los', 'las', 'es', 'en', 'de', 'que', 'y',
    'un', 'una', 'por', 'con', 'se', 'su', 'al', 'del', 'yo',
    'mi', 'me', 'no', 'si', 'soy', 'tengo', 'quiero', 'hola',
    'como', 'para', 'pero', 'hay', 'mas', 'muy', 'bien', 'todo',
    'este', 'esta', 'son', 'ser', 'fue', 'han', 'tiene', 'hacer'
}

PALABRAS_EN = {
    'the', 'is', 'are', 'in', 'of', 'and', 'to', 'a', 'an',
    'i', 'my', 'me', 'you', 'he', 'she', 'we', 'it', 'this',
    'that', 'for', 'with', 'am', 'have', 'want', 'hello', 'hi',
    'was', 'been', 'has', 'can', 'will', 'not', 'but', 'from',
    'they', 'all', 'its', 'our', 'your', 'her', 'his', 'do'
}


def detectar_idioma(texto):
    """
    Detecta si el texto es español o inglés por palabras clave.
    Retorna: 'es' o 'en'
    """
    tokens = set(texto.lower().split())
    score_es = len(tokens & PALABRAS_ES)
    score_en = len(tokens & PALABRAS_EN)
    return 'es' if score_es >= score_en else 'en'


def sintetizar(texto):
    """
    Convierte texto a audio WAV usando Piper TTS.
    Detecta automáticamente el idioma y selecciona la voz correcta.
    Retorna: path al archivo WAV generado
    """
    idioma = detectar_idioma(texto)
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