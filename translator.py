'''
=============================================================
TRANSLATOR - AGENTE TRADUCTOR
=============================================================
Traduce texto entre español e inglés usando Qwen2.5 1.5B
corriendo localmente via Ollama.
=============================================================
Versión: 1.0.0
Cambios:
  1.0.0 - Versión inicial con Ollama API local
=============================================================
'''

import requests
import json

# === CONFIGURACIÓN OLLAMA ===
OLLAMA_URL = 'http://localhost:11434/api/generate'
MODELO = 'qwen2.5:1.5b'
# MODELO = 'qwen2.5:1.5b'
# MODELO = 'gemma3:1b'
TIMEOUT = 30  # segundos

def traducir(texto):
    instruccion = f'''You are a translator. If the following text is in Spanish, translate it to English. Return ONLY the translation, nothing else:

{texto}'''
    # instruccion = f'''You are a translator. If the following text is in Spanish, translate it to English. If it is in English, translate it to Spanish. Return ONLY the translation, nothing else:

#     instruccion = f'''You are a professional translator specialized in Data Science, Business Intelligence and retail analytics. 

# Context: The speaker is a Data Scientist and BI Lead working for a supermarket chain in Argentina. Topics include: demand forecasting, inventory analysis, dashboards, SQL, Python, LightGBM, supplier management, stock analysis, sales tickets, KPIs.

# Translation rules:
# - Keep technical terms in English when commonly used as-is: pipeline, dashboard, forecast, KPI, dataframe, query, script, deploy
# - Translate domain terms naturally: sucursal=branch, pronóstico=forecast, stock dormido=dormant stock, proveedor=supplier
# - If Spanish → translate to English. If English → translate to Spanish.
# - Return ONLY the translation, nothing else.

# Text:
# {texto}'''

    print(f"🔄 Traduciendo...")

    payload = {
        'model': MODELO,
        'prompt': instruccion,
        'stream': False,
        # 'stream': False,
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
