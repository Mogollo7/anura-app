"""Fase 7b — Mide RAM y latencia reales del modelo móvil, emulando gama de
chips por número de hilos de CPU (1 = gama baja tipo Cortex-A53, 2 = gama
media, 4 = gama alta). Cada medición corre en un PROCESO NUEVO Y LIMPIO
(medir_recursos_movil_worker.py) para que no se contaminen entre sí ni con el
overhead de este script.

Traduce los números medidos a una tabla de "requisitos mínimos / recomendados"
igual que las specs de un juego — pero basada en mediciones reales, no en
estimaciones de "tamaño del archivo x2" que suelen estar mal.

Uso:
    python bioclip/scripts/medir_recursos_movil.py
"""

import json
import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

PYTHON = sys.executable
WORKER = Path(__file__).resolve().parent / "medir_recursos_movil_worker.py"
MODELO_FP16 = Path(r"D:\Anura\bioclip\checkpoints\anura_clasificador_fp16.onnx")
MODELO_FP32 = Path(r"D:\Anura\bioclip\checkpoints\anura_clasificador.onnx")
SALIDA = Path(r"D:\Anura\bioclip\evaluation\requisitos_movil.json")

# threads -> a qué gama de celular corresponde (aproximado, referencia de mercado)
GAMA = {1: "gama baja (chip 4-8 núcleos viejos/lentos, ej. Helio G-series bajo, Cortex-A53)",
        2: "gama media (ej. Snapdragon 6xx/7xx, Exynos gama media)",
        4: "gama alta (ej. Snapdragon 8-series, Apple A/M-series)"}


def correr_worker(modelo: Path, threads: int) -> dict:
    proc = subprocess.run(
        [PYTHON, str(WORKER), "--modelo", str(modelo), "--threads", str(threads)],
        capture_output=True, text=True, timeout=300,
    )
    if proc.returncode != 0:
        print(f"  ✗ falló (threads={threads}): {proc.stderr[-2000:]}")
        return None
    # stdout puede traer basura de warnings de librerías antes del JSON: nos
    # quedamos con la última línea no vacía, que es la que imprime el worker.
    lineas = [l for l in proc.stdout.strip().splitlines() if l.strip()]
    return json.loads(lineas[-1])


def main():
    print(f"{'='*88}\nFASE 7b: Medición real de RAM y latencia en emulación de móvil\n{'='*88}\n")

    resultados = []
    for modelo, etiqueta in [(MODELO_FP16, "fp16"), (MODELO_FP32, "fp32")]:
        if not modelo.exists():
            print(f"  (omitido: {modelo.name} no existe)")
            continue
        for threads in (1, 2, 4):
            print(f"[{etiqueta}, {threads} hilo(s)] {GAMA[threads].split(' (')[0]}...")
            r = correr_worker(modelo, threads)
            if r:
                r["precision"] = etiqueta
                resultados.append(r)
                print(f"  RAM pico (modelo cargado): {r['pico_rss_carga_mb']:.0f} MB "
                      f"(+{r['delta_solo_modelo_mb']:.0f} MB sobre baseline)")
                print(f"  RAM pico (con inferencia): {r['pico_rss_inferencia_mb']:.0f} MB "
                      f"(+{r['delta_total_mb']:.0f} MB sobre baseline)")
                print(f"  Latencia: media={r['latencia_media_ms']:.0f}ms  "
                      f"p95={r['latencia_p95_ms']:.0f}ms  carga={r['tiempo_carga_s']:.1f}s\n")

    # ── Tabla de requisitos, estilo specs de juego ──
    print(f"{'='*88}\nTABLA DE REQUISITOS (medida, no estimada)\n{'='*88}")
    print(f"{'CONFIG':<38}{'RAM APP':>12}{'LATENCIA':>12}{'CARGA':>10}")
    print("-" * 88)
    for r in resultados:
        etiqueta = f"{r['precision']} / {r['threads']} hilo(s)"
        print(f"{etiqueta:<38}{r['delta_total_mb']:>9.0f} MB{r['latencia_media_ms']:>10.0f} ms"
              f"{r['tiempo_carga_s']:>9.1f} s")

    # Referencias: fp16 es el que se envía. threads=2 como piso razonable
    # (casi todo celular vendido hoy tiene ≥4 núcleos, pero al menos 2 libres
    # para la app en primer plano no es garantía en gama baja saturada).
    fp16_2h = next((r for r in resultados if r["precision"] == "fp16" and r["threads"] == 2), None)
    fp16_4h = next((r for r in resultados if r["precision"] == "fp16" and r["threads"] == 4), None)
    fp16_1h = next((r for r in resultados if r["precision"] == "fp16" and r["threads"] == 1), None)

    print(f"\n{'='*88}\nREQUISITOS DE LA APP (basados en fp16, el formato de despliegue)\n{'='*88}")
    if fp16_1h:
        margen_min = fp16_1h["delta_total_mb"] * 1.3  # margen de seguridad: SO + otras apps
        print(f"MÍNIMOS:")
        print(f"  RAM libre necesaria     : ~{fp16_1h['delta_total_mb']:.0f} MB medidos "
              f"(recomendar {margen_min:.0f} MB libres con margen)")
        print(f"  RAM total del dispositivo recomendada: 3 GB (Android) / cualquier iPhone con iOS soportado")
        print(f"  Latencia esperada       : ~{fp16_1h['latencia_media_ms']:.0f} ms/foto en 1 hilo "
              f"(gama baja) — usable pero notorio")
        print(f"  Tiempo de carga inicial : ~{fp16_1h['tiempo_carga_s']:.1f} s")
    if fp16_4h:
        print(f"\nRECOMENDADOS:")
        print(f"  RAM libre necesaria     : ~{fp16_4h['delta_total_mb']:.0f} MB medidos")
        print(f"  RAM total del dispositivo recomendada: 6 GB+")
        print(f"  Latencia esperada       : ~{fp16_4h['latencia_media_ms']:.0f} ms/foto en 4 hilos "
              f"(gama alta) — instantáneo")
        print(f"  Tiempo de carga inicial : ~{fp16_4h['tiempo_carga_s']:.1f} s")

    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    SALIDA.write_text(json.dumps(resultados, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nGuardado en {SALIDA}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
