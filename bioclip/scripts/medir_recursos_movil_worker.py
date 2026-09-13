"""Worker que mide RAM real y latencia del modelo ONNX, corriendo en un
proceso aislado con SOLO las dependencias que existirían en el celular real
(onnxruntime + numpy). Nada de torch/open_clip aquí: eso inflaría la memoria
medida con cientos de MB que en el móvil no existen — ahí el preprocesamiento
lo hace código nativo (Bitmap/CIImage), no PyTorch.

Los tensores ya vienen preprocesados de antemano (tensores_validacion_movil.npy).

Un hilo de muestreo mide RSS cada 20ms durante la carga y la inferencia, para
capturar el PICO real y no solo el estado antes/después.

Imprime una única línea JSON a stdout; todo lo demás a stderr.

Uso:
    python medir_recursos_movil_worker.py --modelo <ruta.onnx> --threads N
"""

import argparse
import json
import sys
import threading
import time
from pathlib import Path

import numpy as np
import onnxruntime as ort
import psutil

TENSORES = Path(r"D:\Anura\bioclip\evaluation\tensores_validacion_movil.npy")


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--modelo", required=True)
    p.add_argument("--threads", type=int, required=True)
    return p.parse_args()


class MonitorRSS:
    def __init__(self, proceso, intervalo=0.02):
        self.proceso = proceso
        self.intervalo = intervalo
        self.pico_mb = 0.0
        self._parar = threading.Event()
        self._hilo = threading.Thread(target=self._loop, daemon=True)

    def _loop(self):
        while not self._parar.is_set():
            rss = self.proceso.memory_info().rss / (1024 * 1024)
            self.pico_mb = max(self.pico_mb, rss)
            time.sleep(self.intervalo)

    def __enter__(self):
        self._hilo.start()
        return self

    def __exit__(self, *a):
        self._parar.set()
        self._hilo.join(timeout=1)


def main():
    args = parse_args()
    proceso = psutil.Process()
    rss_baseline = proceso.memory_info().rss / (1024 * 1024)

    opciones = ort.SessionOptions()
    opciones.intra_op_num_threads = args.threads
    opciones.inter_op_num_threads = 1
    opciones.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL

    with MonitorRSS(proceso) as mon_carga:
        t0 = time.perf_counter()
        sesion = ort.InferenceSession(args.modelo, sess_options=opciones,
                                       providers=["CPUExecutionProvider"])
        t_carga_s = time.perf_counter() - t0
    rss_tras_carga = proceso.memory_info().rss / (1024 * 1024)

    tensores = np.load(TENSORES)
    nombre_input = sesion.get_inputs()[0].name

    sesion.run(None, {nombre_input: tensores[0:1]})  # warm-up, no cuenta

    with MonitorRSS(proceso) as mon_inferencia:
        latencias = []
        for i in range(tensores.shape[0]):
            t0 = time.perf_counter()
            sesion.run(None, {nombre_input: tensores[i:i + 1]})
            latencias.append((time.perf_counter() - t0) * 1000)

    resultado = {
        "threads": args.threads,
        "modelo": Path(args.modelo).name,
        "rss_baseline_mb": round(rss_baseline, 1),
        "rss_tras_carga_mb": round(rss_tras_carga, 1),
        "pico_rss_carga_mb": round(mon_carga.pico_mb, 1),
        "pico_rss_inferencia_mb": round(mon_inferencia.pico_mb, 1),
        "delta_solo_modelo_mb": round(mon_carga.pico_mb - rss_baseline, 1),
        "delta_total_mb": round(mon_inferencia.pico_mb - rss_baseline, 1),
        "tiempo_carga_s": round(t_carga_s, 2),
        "latencia_media_ms": round(float(np.mean(latencias)), 1),
        "latencia_p95_ms": round(float(np.percentile(latencias, 95)), 1),
        "latencia_max_ms": round(float(np.max(latencias)), 1),
    }
    print(json.dumps(resultado))
    return 0


if __name__ == "__main__":
    sys.exit(main())
