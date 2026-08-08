'''
=============================================================
STT - SPEECH TO TEXT - AGENTE TRADUCTOR
=============================================================
Convierte audio WAV a texto usando Whisper.cpp local.
Devuelve también el idioma detectado (es/en) para que el resto
del pipeline no tenga que re-adivinarlo.
=============================================================
Versión: 1.2.0
Cambios:
  1.0.0 - Versión inicial con whisper-cli.exe
  1.1.0 - transcribir() retorna (texto, idioma) usando el idioma
          auto-detectado por Whisper, con fallback por palabras
          clave si Whisper no lo reporta
  1.2.0 - Cuando Whisper detecta un idioma no soportado (ej. confunde
          español con italiano/portugués/catalán en audios cortos),
          re-transcribe forzando -l es y -l en, y se queda con la
          que tenga más palabras reconocibles. El auto-detect de
          Whisper no solo etiqueta el idioma: también decodifica
          con esa hipótesis, así que una mala detección arruinaba
          el propio texto, no solo el idioma.
=============================================================
'''

import subprocess
import os
import re

WHISPER_EXE = r'C:\JulioPrograma\agente_traductor\whisper-blas-bin-x64\Release\whisper-cli.exe'
WHISPER_MODEL = r'C:\JulioPrograma\agente_traductor\whisper-blas-bin-x64\Release\models\ggml-base.bin'

# === Palabras clave para desempatar entre es/en cuando Whisper detecta
#     un idioma no soportado (ej. italiano, portugués, catalán) ===
PALABRAS_ES = {
    'el', 'la', 'los', 'las', 'es', 'en', 'de', 'que', 'y',
    'un', 'una', 'por', 'con', 'se', 'su', 'al', 'del', 'yo',
    'mi', 'me', 'no', 'si', 'soy', 'tengo', 'quiero', 'hola',
    'como', 'para', 'pero', 'hay', 'mas', 'muy', 'bien', 'todo',
}
PALABRAS_EN = {
    'the', 'is', 'are', 'in', 'of', 'and', 'to', 'a', 'an',
    'i', 'my', 'me', 'you', 'he', 'she', 'we', 'it', 'this',
    'that', 'for', 'with', 'am', 'have', 'want', 'hello', 'hi',
}


def _score_idioma(texto, palabras):
    """Cuenta cuántas palabras clave del idioma aparecen en el texto."""
    if not texto:
        return -1
    tokens = set(texto.lower().split())
    return len(tokens & palabras)


def _ejecutar_whisper(wav_path, idioma):
    """
    Corre whisper-cli forzando (o autodetectando) un idioma.
    Retorna: (texto, codigo_idioma_detectado_por_whisper)
    """
    cmd = [
        WHISPER_EXE,
        '-m', WHISPER_MODEL,
        '-f', wav_path,
        '-l', idioma,
        '--no-timestamps',
    ]
    resultado = subprocess.run(cmd, capture_output=True, text=True,
                               encoding='utf-8', errors='replace')
    texto = re.sub(r'\[.*?\]', '', resultado.stdout).strip()

    # Whisper reporta el idioma detectado en stderr, ej:
    # "auto-detected language: es (p = 0.987654)"
    match = re.search(r'auto-detected language:\s*([a-z]{2})', resultado.stderr)
    codigo = match.group(1) if match else idioma
    return texto, codigo


def transcribir(wav_path):
    """
    Transcribe un WAV con Whisper.cpp.
    Retorna: (texto, idioma) donde idioma es 'es' o 'en', o (None, None) si falla.
    """
    if not os.path.exists(wav_path):
        return None, None

    try:
        texto, codigo = _ejecutar_whisper(wav_path, 'auto')

        if not texto or not re.search(r'[a-zA-ZáéíóúüñÁÉÍÓÚÜÑ]', texto):
            print("⚠️  Audio no reconocido como español/inglés, ignorando...")
            return None, None

        if codigo == 'es':
            idioma = 'es'
        elif codigo == 'en':
            idioma = 'en'
        else:
            # Whisper detectó un idioma no soportado y probablemente decodificó
            # mal el propio texto con esa hipótesis equivocada. Re-transcribimos
            # forzando es/en y nos quedamos con la que tenga más sentido.
            print(f"⚠️  Whisper detectó '{codigo}' (no soportado), reintentando forzando es/en...")
            texto_es, _ = _ejecutar_whisper(wav_path, 'es')
            texto_en, _ = _ejecutar_whisper(wav_path, 'en')
            if _score_idioma(texto_en, PALABRAS_EN) > _score_idioma(texto_es, PALABRAS_ES):
                texto, idioma = texto_en, 'en'
            else:
                texto, idioma = texto_es, 'es'
            if not texto:
                return None, None

        print(f"📝 Transcripción ({idioma}): {texto}")
        return texto, idioma
    except Exception as e:
        print(f"❌ Error en STT: {e}")
        return None, None