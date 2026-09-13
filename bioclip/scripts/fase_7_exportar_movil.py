"""Fase 7 — Exporta el modelo COMPLETO (encoder + 3 cabezas) a ONNX para
inference on-device en móvil (sin servidor).

Fase 6 exportó solo el encoder (para embeddings/búsqueda). Esto es distinto:
exporta el clasificador completo, que da directamente logits de familia,
género y especie — lo que la app necesita para mostrar "es un Dendrobates
truncatus con 92% de confianza".

`torch.jit.trace` falló en Fase 6 con el ViT por las branches condicionales
internas de open_clip. `torch.onnx.export` usa su propio tracer (o el nuevo
exportador dynamo) y suele manejar mejor estos casos — se valida aquí mismo:
si falla, se sabe antes de tocar la parte móvil.

También empaqueta el prior geográfico (Fase 6c, con coordenadas ya filtradas
por calidad) en un JSON compacto para embeber en la app — sin esto, el GPS
del celular no sirve de nada porque no hay dónde consultar qué especies viven
cerca.

Uso:
    python bioclip/scripts/fase_7_exportar_movil.py
"""

import json
import re
import sys
from pathlib import Path

import numpy as np
import onnxruntime as ort
import open_clip
import torch
from onnxconverter_common import float16 as onnx_float16
from PIL import Image
from torch.utils.data import DataLoader, Dataset

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "training"))

from fase_4_transfer_learning import BioClipMultiHead  # noqa: E402
from taxonomia import vocabularios  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

RAIZ_DATOS = Path(r"D:\Anura\data cleaned")
RAIZ_COORDS = Path(r"D:\Anura\data dirty")
MANIFIESTO = Path(r"D:\Anura\training\manifiesto.json")
CHECKPOINT = Path(r"D:\Anura\bioclip\checkpoints\bioclip_anura_mejor.pt")
SALIDA_ONNX = Path(r"D:\Anura\bioclip\checkpoints\anura_clasificador.onnx")
SALIDA_ONNX_FP16 = Path(r"D:\Anura\bioclip\checkpoints\anura_clasificador_fp16.onnx")
SALIDA_VOCAB = Path(r"D:\Anura\bioclip\checkpoints\vocabulario.json")
SALIDA_PRIOR = Path(r"D:\Anura\bioclip\checkpoints\prior_geografico_movil.json")
MODELO_HF = "hf-hub:imageomics/bioclip"

UMBRAL_ACCURACY_M = 10_000
N_VALIDACION = 64


class ModeloExport(torch.nn.Module):
    """Envuelve BioClipMultiHead: solo logits de especie + género + familia,
    ya con softmax aplicado (la app no debería reimplementar eso)."""

    def __init__(self, modelo):
        super().__init__()
        self.modelo = modelo

    def forward(self, x):
        _, (logit_fam, logit_gen, logit_esp) = self.modelo(x)
        return (
            torch.softmax(logit_fam, dim=-1),
            torch.softmax(logit_gen, dim=-1),
            torch.softmax(logit_esp, dim=-1),
        )


class DatasetTest(Dataset):
    def __init__(self, entradas, preprocess):
        self.entradas = entradas
        self.preprocess = preprocess

    def __len__(self):
        return len(self.entradas)

    def __getitem__(self, idx):
        e = self.entradas[idx]
        with Image.open(RAIZ_DATOS / e["ruta"]).convert("RGB") as img:
            return self.preprocess(img), e["idx_especie"]


def obs_id_de(ruta: str):
    m = re.search(r"obs_(\d+)_photo", ruta)
    return m.group(1) if m else None


def empaquetar_prior_geografico(manifiesto, especies):
    """Puntos de train (lat, lon) por especie, filtrados por accuracy — el
    mismo criterio validado en Fase 6c. La app hace el conteo en radio y el
    suavizado localmente; aquí solo se exportan los puntos crudos."""
    coords = {}
    for archivo in RAIZ_COORDS.glob("*/coordenadas_distribucion.json"):
        try:
            registros = json.loads(archivo.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        for r in registros:
            lat, lon, acc = r.get("latitude"), r.get("longitude"), r.get("positional_accuracy")
            if lat is None or lon is None:
                continue
            if acc is not None and acc > UMBRAL_ACCURACY_M:
                continue
            coords[str(r["observation_id"])] = (round(float(lat), 4), round(float(lon), 4))

    idx_de_especie = {e: i for i, e in enumerate(especies)}
    puntos_por_especie = {i: [] for i in range(len(especies))}
    vistos = set()
    for e in manifiesto["particiones"]["train"]:
        if e.get("aumentada"):
            continue
        oid = obs_id_de(e["ruta"])
        if oid is None or oid in vistos or oid not in coords:
            continue
        vistos.add(oid)
        puntos_por_especie[idx_de_especie[e["especie"]]].append(coords[oid])

    return {
        "radio_km_recomendado": 50.0,
        "alpha_suavizado": 0.5,
        "peso_prior_recomendado": 0.75,
        "puntos_por_especie": {especies[i]: pts for i, pts in puntos_por_especie.items() if pts},
    }


def main():
    dispositivo = "cpu"  # export siempre desde CPU: es lo que va a correr en el celular
    print(f"{'='*78}\nFASE 7: Export para inference on-device (móvil)\n{'='*78}\n")

    familias, generos, especies = vocabularios()

    print("[0/7] Cargando BioCLIP v1 + pesos de Fase 4...")
    modelo_clip, _, preprocess = open_clip.create_model_and_transforms(MODELO_HF)
    ck = torch.load(CHECKPOINT, map_location="cpu", weights_only=False)
    modelo = BioClipMultiHead(modelo_clip.visual, len(familias), len(generos), len(especies))
    modelo.visual.load_state_dict(ck["visual_state_dict"])
    modelo.cabeza_familia.load_state_dict(ck["cabezas_state_dict"]["familia"])
    modelo.cabeza_genero.load_state_dict(ck["cabezas_state_dict"]["genero"])
    modelo.cabeza_especie.load_state_dict(ck["cabezas_state_dict"]["especie"])
    modelo.eval()

    envoltorio = ModeloExport(modelo).eval()

    print("\n[1/7] Exportando a ONNX (torch.onnx.export)...")
    x_dummy = torch.randn(1, 3, 224, 224)
    SALIDA_ONNX.parent.mkdir(parents=True, exist_ok=True)
    try:
        # Batch fijo en 1: en el celular se procesa una imagen a la vez. Dejar
        # el batch dinámico rompe el reshape de la atención multi-cabeza del
        # ViT con el exportador dynamo (produce un grafo corrupto de ~1MB en
        # vez de los ~330MB reales — visto y confirmado en la primera corrida).
        torch.onnx.export(
            envoltorio,
            x_dummy,
            str(SALIDA_ONNX),
            input_names=["imagen"],
            output_names=["prob_familia", "prob_genero", "prob_especie"],
            opset_version=18,
            do_constant_folding=True,
        )
        mb = SALIDA_ONNX.stat().st_size / (1024 * 1024)
        print(f"  ✓ {SALIDA_ONNX.name} ({mb:.1f} MB)")
    except Exception as e:
        print(f"  ✗ Export ONNX falló: {e}")
        return 1

    # El exportador dynamo separa los pesos grandes en un .onnx.data externo
    # (formato "external data"). Para móvil conviene UN solo archivo: se
    # consolida aquí, y se borra el .data suelto para no dejar basura.
    archivo_data = SALIDA_ONNX.with_suffix(".onnx.data")
    if archivo_data.exists():
        print(f"  Consolidando pesos externos ({archivo_data.stat().st_size/(1024*1024):.1f} MB) "
              f"en un solo archivo...")
        import onnx
        modelo_onnx = onnx.load(str(SALIDA_ONNX), load_external_data=True)
        onnx.save(modelo_onnx, str(SALIDA_ONNX), save_as_external_data=False)
        archivo_data.unlink()
        mb = SALIDA_ONNX.stat().st_size / (1024 * 1024)
        print(f"  ✓ Consolidado: {SALIDA_ONNX.name} ({mb:.1f} MB, archivo único)")

    print("\n[2/7] Validando con ONNX Runtime + onnx.checker...")
    import onnx
    onnx.checker.check_model(str(SALIDA_ONNX))
    sesion = ort.InferenceSession(str(SALIDA_ONNX), providers=["CPUExecutionProvider"])
    print(f"  ✓ Modelo válido, inputs: {[i.name for i in sesion.get_inputs()]}")

    print(f"\n[3/7] Comparando PyTorch vs ONNX sobre {N_VALIDACION} imágenes REALES de test...")
    manifiesto = json.loads(MANIFIESTO.read_text(encoding="utf-8"))
    entradas = manifiesto["particiones"]["test"][:N_VALIDACION]
    # batch_size=1: el ONNX se exportó con shape fijo [1,3,224,224]
    dl = DataLoader(DatasetTest(entradas, preprocess), batch_size=1, num_workers=2)

    acierto_pt, acierto_onnx, coinciden, max_diff = 0, 0, 0, 0.0
    with torch.no_grad():
        for x, y in dl:
            p_fam_pt, p_gen_pt, p_esp_pt = envoltorio(x)
            salidas_onnx = sesion.run(None, {"imagen": x.numpy()})
            p_esp_onnx = torch.from_numpy(salidas_onnx[2])

            pred_pt = p_esp_pt.argmax(-1)
            pred_onnx = p_esp_onnx.argmax(-1)
            acierto_pt += (pred_pt == y).sum().item()
            acierto_onnx += (pred_onnx == y).sum().item()
            coinciden += (pred_pt == pred_onnx).sum().item()
            max_diff = max(max_diff, (p_esp_pt - p_esp_onnx).abs().max().item())

    print(f"  Top-1 PyTorch : {acierto_pt/len(entradas):.1%}")
    print(f"  Top-1 ONNX    : {acierto_onnx/len(entradas):.1%}")
    print(f"  Predicciones idénticas PyTorch==ONNX: {coinciden}/{len(entradas)} "
          f"({coinciden/len(entradas):.1%})")
    print(f"  Diferencia máxima en probabilidades : {max_diff:.2e}")

    ok = coinciden == len(entradas) and max_diff < 1e-3
    print(f"\n  {'✓ ONNX es fiel al modelo original' if ok else '⚠ revisar: hay divergencia'}")

    # ── fp16 ──
    print(f"\n[5/6] Convirtiendo a fp16...")
    modelo_onnx_fp32 = onnx.load(str(SALIDA_ONNX))
    modelo_onnx_fp16 = onnx_float16.convert_float_to_float16(
        modelo_onnx_fp32, keep_io_types=True  # input/output siguen en fp32: la app no cambia
    )
    onnx.save(modelo_onnx_fp16, str(SALIDA_ONNX_FP16))
    mb_fp16 = SALIDA_ONNX_FP16.stat().st_size / (1024 * 1024)
    print(f"  ✓ {SALIDA_ONNX_FP16.name} ({mb_fp16:.1f} MB, {mb/mb_fp16:.2f}x más liviano)")

    print(f"\n[6/6] Validando fp16 sobre las mismas {N_VALIDACION} imágenes reales...")
    sesion_fp16 = ort.InferenceSession(str(SALIDA_ONNX_FP16), providers=["CPUExecutionProvider"])

    acierto_fp16, coinciden_fp16, max_diff_fp16 = 0, 0, 0.0
    with torch.no_grad():
        for x, y in dl:
            p_esp_pt = envoltorio(x)[2]
            salida_fp16 = sesion_fp16.run(None, {"imagen": x.numpy()})
            p_esp_fp16 = torch.from_numpy(salida_fp16[2])

            pred_pt = p_esp_pt.argmax(-1)
            pred_fp16 = p_esp_fp16.argmax(-1)
            acierto_fp16 += (pred_fp16 == y).sum().item()
            coinciden_fp16 += (pred_pt == pred_fp16).sum().item()
            max_diff_fp16 = max(max_diff_fp16, (p_esp_pt - p_esp_fp16).abs().max().item())

    print(f"  Top-1 fp32 (referencia) : {acierto_pt/len(entradas):.1%}")
    print(f"  Top-1 fp16              : {acierto_fp16/len(entradas):.1%}")
    print(f"  Predicciones idénticas fp32==fp16: {coinciden_fp16}/{len(entradas)} "
          f"({coinciden_fp16/len(entradas):.1%})")
    print(f"  Diferencia máxima en probabilidades: {max_diff_fp16:.2e}")

    ok_fp16 = coinciden_fp16 >= len(entradas) * 0.95 and max_diff_fp16 < 0.05
    print(f"\n  {'✓ fp16 es seguro para producción' if ok_fp16 else '⚠ revisar: degradación mayor a la esperada'}")

    print(f"\n[7/7] Empaquetando vocabulario y prior geográfico para la app...")
    SALIDA_VOCAB.write_text(json.dumps({
        "familias": familias, "generos": generos, "especies": especies,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  ✓ {SALIDA_VOCAB.name}")

    prior = empaquetar_prior_geografico(manifiesto, especies)
    SALIDA_PRIOR.write_text(json.dumps(prior, ensure_ascii=False), encoding="utf-8")
    n_puntos = sum(len(v) for v in prior["puntos_por_especie"].values())
    mb_prior = SALIDA_PRIOR.stat().st_size / 1024
    print(f"  ✓ {SALIDA_PRIOR.name} ({mb_prior:.0f} KB, {n_puntos} puntos, "
          f"{len(prior['puntos_por_especie'])}/{len(especies)} especies con soporte)")

    print(f"\n{'='*78}\n✅ FASE 7 OK — listo para empaquetar en la app\n{'='*78}")
    print(f"""
Archivos para incluir en el proyecto móvil:
  {SALIDA_ONNX_FP16.name:<32} modelo fp16 (ONNX Runtime Mobile / ORT) <- usar este
  {SALIDA_ONNX.name:<32} modelo fp32, referencia (no necesario en la app)
  {SALIDA_VOCAB.name:<32} nombres de especies/género/familia por índice
  {SALIDA_PRIOR.name:<32} puntos geográficos de train para el prior

Preprocesamiento que la app debe replicar antes de correr el modelo:
  - resize a 224x224, RGB
  - normalizar con mean/std de OpenAI CLIP: {open_clip.OPENAI_DATASET_MEAN} / {open_clip.OPENAI_DATASET_STD}
""")
    return 0


if __name__ == "__main__":
    sys.exit(main())
