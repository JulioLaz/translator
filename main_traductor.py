'''
=============================================================
AGENTE TRADUCTOR ES <-> EN - CUCHER / USO PERSONAL
=============================================================
Agente de traducción en tiempo real español ↔ inglés.
Flujo: Micrófono → Whisper.cpp (STT) → Qwen2.5 1.5B
       (Traducción via Ollama) → Piper TTS → Parlante.
100% local, sin APIs externas, sin costo por uso.
=============================================================
Versión: 1.0.0
Cambios:
  1.0.0 - Versión inicial con stack local completo
=============================================================
'''

import os
import sys
import time
from audio_utils import grabar_hasta_silencio, reproducir_wav
from stt import transcribir
from translator import traducir, verificar_ollama
from tts import sintetizar, limpiar_temporal


def mostrar_banner():
    print("=" * 55)
    print("   🌐 AGENTE TRADUCTOR ES <-> EN")
    print("   Stack: Whisper.cpp | Qwen2.5 1.5B | Piper TTS")
    print("=" * 55)
    print("  Hablá en ESPAÑOL → escuchás en INGLÉS")
    print("  Hablá en INGLÉS  → escuchás en ESPAÑOL")
    print("  Presioná Ctrl+C para salir")
    print("=" * 55)


def procesar_turno():
    """
    Ejecuta un ciclo completo de traducción:
    Graba → STT → Traduce → TTS → Reproduce
    """
    wav_entrada = None
    wav_salida = None

    try:
        # PASO 1: Grabar audio
        wav_entrada = grabar_hasta_silencio()
        if not wav_entrada:
            print("⚠️  No se detectó audio. Intentá de nuevo.")
            return

        # PASO 2: Transcribir
        t0 = time.time()
        texto = transcribir(wav_entrada)
        if not texto:
            print("⚠️  No se pudo transcribir. Intentá de nuevo.")
            return
        t_stt = time.time() - t0

        # PASO 3: Traducir
        t1 = time.time()
        traduccion = traducir(texto)
        if not traduccion:
            print("⚠️  No se pudo traducir. Intentá de nuevo.")
            return
        t_trad = time.time() - t1

        # PASO 4: Sintetizar voz
        t2 = time.time()
        wav_salida = sintetizar(traduccion)
        if not wav_salida:
            print("⚠️  No se pudo sintetizar audio.")
            return
        t_tts = time.time() - t2

        # PASO 5: Reproducir
        t_total = t_stt + t_trad + t_tts
        print(f"\n⏱️  Latencia: STT={t_stt:.1f}s | Trad={t_trad:.1f}s | TTS={t_tts:.1f}s | Total={t_total:.1f}s")
        print(f"🔊 Reproduciendo...")
        reproducir_wav(wav_salida)

    finally:
        # Limpiar temporales
        limpiar_temporal(wav_entrada)
        limpiar_temporal(wav_salida)


def main_traductor():
    """Función principal del agente traductor."""
    mostrar_banner()

    # Verificar Ollama antes de arrancar
    print("\n🔍 Verificando componentes...")
    if not verificar_ollama():
        print("\n❌ Corregí el error y volvé a ejecutar.")
        sys.exit(1)

    print("\n✅ Todo listo. ¡Podés empezar a hablar!\n")

    while True:
        try:
            print("\n" + "-" * 40)
            procesar_turno()
        except KeyboardInterrupt:
            print("\n\n👋 Agente traductor detenido.")
            sys.exit(0)
        except Exception as e:
            print(f"❌ Error inesperado: {e}")
            time.sleep(1)
            continue


if __name__ == '__main__':
    main_traductor()
