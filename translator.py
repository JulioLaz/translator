'''
=============================================================
TRANSLATOR - AGENTE TRADUCTOR
=============================================================
Traduce texto entre español e inglés usando Qwen2.5 1.5B
corriendo localmente via Ollama.
=============================================================
Versión: 1.1.0
Cambios:
  1.0.0 - Versión inicial con Ollama API local
  1.1.0 - Traducción bidireccional ES<->EN explícita según el
          idioma_origen recibido (antes solo traducía ES->EN)
=============================================================
'''

import requests

# === CONFIGURACIÓN OLLAMA ===
OLLAMA_URL = 'http://localhost:11434/api/generate'
MODELO = 'qwen2.5:1.5b'
TIMEOUT = 30  # segundos

IDIOMAS = {'es': 'Spanish', 'en': 'English'}


def traducir(texto, idioma_origen):
    """
    Traduce texto entre español e inglés.
    idioma_origen: 'es' o 'en'. El destino es el otro idioma soportado.
    """
    idioma_destino = 'en' if idioma_origen == 'es' else 'es'
    instruccion = f'''You are a translator. Translate the following text from {IDIOMAS[idioma_origen]} to {IDIOMAS[idioma_destino]}. Return ONLY the translation, nothing else:

{texto}'''

    print(f"🔄 Traduciendo ({idioma_origen} → {idioma_destino})...")

    payload = {
        'model': MODELO,
        'prompt': instruccion,
        'stream': False,
        'options': {
            'temperature': 0.1,
            'num_predict': 200,
            'num_ctx': 512,
        }
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=TIMEOUT)
        response.raise_for_status()
        data = response.json()
        traduccion = data.get('response', '').strip()
        if not traduccion:
            print("⚠️  Traducción vacía")
            return None
        print(f"✅ Traducción: {traduccion}")
        return traduccion
    except requests.exceptions.ConnectionError:
        print("❌ Error: Ollama no está corriendo.")
        return None
    except requests.exceptions.Timeout:
        print("❌ Error: Timeout en traducción")
        return None
    except Exception as e:
        print(f"❌ Error en traducción: {e}")
        return None

def verificar_ollama():
    """Verifica que Ollama esté corriendo y el modelo disponible."""
    try:
        response = requests.get('http://localhost:11434/api/tags', timeout=5)
        modelos = response.json().get('models', [])
        nombres = [m['name'] for m in modelos]
        if any(MODELO in n for n in nombres):
            print(f"✅ Ollama OK - Modelo {MODELO} disponible")
            return True
        else:
            print(f"⚠️  Modelo {MODELO} no encontrado. Ejecutá: ollama pull {MODELO}")
            return False
    except Exception:
        print("❌ Ollama no está corriendo. Ejecutá: ollama serve")
        return False
