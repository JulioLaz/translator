'''
=============================================================
STT - SPEECH TO TEXT - AGENTE TRADUCTOR
=============================================================
Convierte audio WAV a texto usando Whisper.cpp local.
Detecta automáticamente el idioma (español/inglés).
=============================================================
Versión: 1.0.0
Cambios:
  1.0.0 - Versión inicial con whisper-cli.exe
=============================================================
'''

import subprocess
import os
import re

WHISPER_EXE = r'C:\JulioPrograma\agente_traductor\whisper-blas-bin-x64\Release\whisper-cli.exe'
WHISPER_MODEL = r'C:\JulioPrograma\agente_traductor\whisper-blas-bin-x64\Release\models\ggml-base.bin'

def transcribir(wav_path):
    if not os.path.exists(wav_path):
        return None

    cmd = [
        WHISPER_EXE,
        '-m', WHISPER_MODEL,
        '-f', wav_path,
        '-l', 'auto',
        '--no-timestamps',
    ]

    try:
        resultado = subprocess.run(cmd, capture_output=True, text=True,
                                   encoding='utf-8', errors='replace')
        texto = resultado.stdout.strip()
        texto = re.sub(r'\[.*?\]', '', texto).strip()
        if not texto:
                return None
                # Filtrar ruido no latino
        if not re.search(r'[a-zA-ZáéíóúüñÁÉÍÓÚÜÑ]', texto):
                print("⚠️  Audio no reconocido como español/inglés, ignorando...")
                return None
        print(f"📝 Transcripción: {texto}")
        return texto
    except Exception as e:
        print(f"❌ Error en STT: {e}")
        return None