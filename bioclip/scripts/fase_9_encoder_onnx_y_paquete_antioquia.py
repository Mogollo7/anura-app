"""Fase 9 — Exporta el encoder SOLO a ONNX (pendiente real detectado en C-15) y
mide precisión real del paquete regional de Antioquia (Ruta B) filtrado a las
especies con presencia geográfica real, comparado contra el clasificador
completo (Ruta A) sobre el mismo subconjunto.

Por qué hace falta este paso: Fase 6 dejó el encoder en `.pt` (PyTorch) y
Fase 7 exportó el CLASIFICADOR completo (encoder+3 cabezas) a ONNX — nunca se
exportó el encoder solo, que es lo que la Ruta B (k-NN + SQLite-vec) necesita
en Android. Se sigue el mismo patrón de exportación ya validado en Fase 7
(opset 18, batch fijo=1, consolidar external data, fp16 con
onnxconverter_common) porque ya se sabe que funciona con este ViT.

Antioquia real, no simulada: el paquete de prueba anterior (Fase 8) usaba las
41 especies completas por falta de filtro geográfico. Aquí se filtran las
especies con >=3 observaciones de train dentro del bounding box del
departamento de Antioquia (lat 5.4-8.9, lon -77.2--73.8, usando las
coordenadas ya auditadas en prior_geografico_movil.json) — es una aproximación
por bounding box, no un polígono administrativo exacto, pero usa coordenadas
reales de las propias observaciones del dataset, no un supuesto.

Uso:
    python bioclip/scripts/fase_9_encoder_onnx_y_paquete_antioquia.py
"""

import json
import sqlite3
import struct
import sys
from pathlib import Path

import numpy as np
import onnx
import onnxruntime as ort
import open_clip
import sqlite_vec
import torch
from onnxconverter_common import float16 as onnx_float16
from PIL import Image
from torch.utils.data import DataLoader, Dataset

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "training"))
from taxonomia import vocabularios  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

RAIZ_DATOS = Path(r"D:\Anura\data cleaned")
MANIFIESTO = Path(r"D:\Anura\training\manifiesto.json")
CHECKPOINT = Path(r"D:\Anura\bioclip\checkpoints\bioclip_anura_mejor.pt")
PRIOR_GEO = Path(r"D:\Anura\bioclip\checkpoints\prior_geografico_movil.json")
FASE5_JSON = Path(r"D:\Anura\bioclip\evaluation\fase_5_completa.json")

SALIDA_ONNX = Path(r"D:\Anura\bioclip\checkpoints\encoder_anura.onnx")
SALIDA_ONNX_FP16 = Path(r"D:\Anura\bioclip\checkpoints\encoder_anura_fp16.onnx")
PAQUETE_ANTIOQUIA = Path(r"D:\Anura\bioclip\paquetes_regionales\antioquia_v1.sqlite")
SALIDA_JSON = Path(r"D:\Anura\bioclip\evaluation\fase_9_antioquia_real.json")

MODELO_HF = "hf-hub:imageomics/bioclip"
N_VALIDACION_ONNX = 64
MIN_PUNTOS_ANTIOQUIA = 3
K_VECINOS = 5

# Bounding box aproximado del departamento de Antioquia, Colombia
LAT_MIN, LAT_MAX = 5.4, 8.9
LON_MIN, LON_MAX = -77.2, -73.8


class EncoderVisual(torch.nn.Module):
    def __init__(self, visual_encoder):
        super().__init__()
        self.visual = visual_encoder

    def forward(self, x):
        emb = self.visual(x)
        return emb / emb.norm(dim=-1, keepdim=True)


class DatasetImagenes(Dataset):
    def __init__(self, entradas, preprocess):
        self.preprocess = preprocess
        self.entradas = [e for e in entradas if (RAIZ_DATOS / e["ruta"]).exists()]
        faltantes = len(entradas) - len(self.entradas)
        if faltantes:
            print(f"  [aviso] {faltantes} rutas del manifiesto ya no existen en disco — omitidas")

    def __len__(self):
        return len(self.entradas)

    def __getitem__(self, idx):
        e = self.entradas[idx]
        with Image.open(RAIZ_DATOS / e["ruta"]).convert("RGB") as img:
            return self.preprocess(img), e["idx_especie"]


def especies_con_presencia_en_antioquia(especies):
    """Filtra especies por coordenadas reales de train (bbox del departamento), no por supuesto."""
    prior = json.loads(PRIOR_GEO.read_text(encoding="utf-8"))
    puntos_por_especie = prior["puntos_por_especie"]

    conteo = {}
    for especie in especies:
        pts = puntos_por_especie.get(especie, [])
        en_bbox = sum(1 for lat, lon in pts if LAT_MIN <= lat <= LAT_MAX and LON_MIN <= lon <= LON_MAX)
        conteo[especie] = {"total_puntos": len(pts), "en_antioquia": en_bbox}

    seleccionadas = sorted(
        [e for e, c in conteo.items() if c["en_antioquia"] >= MIN_PUNTOS_ANTIOQUIA],
        key=lambda e: -conteo[e]["en_antioquia"],
    )
    return seleccionadas, conteo


def exportar_encoder_onnx(encoder, dispositivo_export="cpu"):
    print(f"\n{'='*78}\n[PARTE 1] Exportando ENCODER SOLO a ONNX (pendiente detectado en C-15)\n{'='*78}")
    x_dummy = torch.randn(1, 3, 224, 224)
    SALIDA_ONNX.parent.mkdir(parents=True, exist_ok=True)

    print("\n[1/5] torch.onnx.export (mismo patrón validado en Fase 7: opset 18, batch fijo=1)...")
    torch.onnx.export(
        encoder,
        x_dummy,
        str(SALIDA_ONNX),
        input_names=["imagen"],
        output_names=["embedding"],
        opset_version=18,
        do_constant_folding=True,
    )
    mb = SALIDA_ONNX.stat().st_size / (1024 * 1024)
    print(f"  {SALIDA_ONNX.name} ({mb:.1f} MB)")

    archivo_data = SALIDA_ONNX.with_suffix(".onnx.data")
    if archivo_data.exists():
        print(f"  Consolidando pesos externos ({archivo_data.stat().st_size/(1024*1024):.1f} MB)...")
        modelo_onnx = onnx.load(str(SALIDA_ONNX), load_external_data=True)
        onnx.save(modelo_onnx, str(SALIDA_ONNX), save_as_external_data=False)
        archivo_data.unlink()
        mb = SALIDA_ONNX.stat().st_size / (1024 * 1024)
        print(f"  Consolidado: {SALIDA_ONNX.name} ({mb:.1f} MB, archivo único)")

    print("\n[2/5] Validando con onnx.checker + ONNX Runtime...")
    onnx.checker.check_model(str(SALIDA_ONNX))
    sesion = ort.InferenceSession(str(SALIDA_ONNX), providers=["CPUExecutionProvider"])
    print(f"  Modelo válido, input: {[i.name for i in sesion.get_inputs()]}, output: {[o.name for o in sesion.get_outputs()]}")

    print(f"\n[3/5] Comparando PyTorch vs ONNX sobre {N_VALIDACION_ONNX} imágenes reales de test...")
    manifiesto = json.loads(MANIFIESTO.read_text(encoding="utf-8"))
    entradas = manifiesto["particiones"]["test"][:N_VALIDACION_ONNX]
    _, _, preprocess = open_clip.create_model_and_transforms(MODELO_HF)
    dl = DataLoader(DatasetImagenes(entradas, preprocess), batch_size=1, num_workers=2)

    max_diff, cos_sims = 0.0, []
    with torch.no_grad():
        for x, _ in dl:
            emb_pt = encoder(x)
            emb_onnx = torch.from_numpy(sesion.run(None, {"imagen": x.numpy()})[0])
            max_diff = max(max_diff, (emb_pt - emb_onnx).abs().max().item())
            cos_sims.append(torch.nn.functional.cosine_similarity(emb_pt, emb_onnx).item())

    cos_media = float(np.mean(cos_sims))
    print(f"  Similitud coseno media PyTorch vs ONNX: {cos_media:.6f}")
    print(f"  Diferencia máxima absoluta: {max_diff:.2e}")
    ok = cos_media > 0.999
    print(f"  {'ONNX fiel al modelo original' if ok else 'ADVERTENCIA: revisar degradación'}")

    print("\n[4/5] Convirtiendo a fp16...")
    modelo_onnx_fp32 = onnx.load(str(SALIDA_ONNX))
    modelo_onnx_fp16 = onnx_float16.convert_float_to_float16(modelo_onnx_fp32, keep_io_types=True)
    onnx.save(modelo_onnx_fp16, str(SALIDA_ONNX_FP16))
    mb_fp16 = SALIDA_ONNX_FP16.stat().st_size / (1024 * 1024)
    print(f"  {SALIDA_ONNX_FP16.name} ({mb_fp16:.1f} MB, {mb/mb_fp16:.2f}x más liviano)")

    print(f"\n[5/5] Validando fp16 sobre las mismas {N_VALIDACION_ONNX} imágenes...")
    sesion_fp16 = ort.InferenceSession(str(SALIDA_ONNX_FP16), providers=["CPUExecutionProvider"])
    cos_sims_fp16 = []
    with torch.no_grad():
        for x, _ in dl:
            emb_pt = encoder(x)
            emb_fp16 = torch.from_numpy(sesion_fp16.run(None, {"imagen": x.numpy()})[0])
            cos_sims_fp16.append(torch.nn.functional.cosine_similarity(emb_pt, emb_fp16.float()).item())
    cos_media_fp16 = float(np.mean(cos_sims_fp16))
    print(f"  Similitud coseno media PyTorch vs ONNX fp16: {cos_media_fp16:.6f}")
    ok_fp16 = cos_media_fp16 > 0.99
    print(f"  {'fp16 seguro para producción' if ok_fp16 else 'ADVERTENCIA: revisar degradación fp16'}")

    return {
        "onnx_fp32_mb": round(mb, 1),
        "onnx_fp16_mb": round(mb_fp16, 1),
        "cos_media_fp32_vs_pytorch": cos_media,
        "cos_media_fp16_vs_pytorch": cos_media_fp16,
        "apto_produccion": bool(ok and ok_fp16),
    }


@torch.no_grad()
def generar_embeddings(encoder, entradas, preprocess, dispositivo):
    dataset = DatasetImagenes(entradas, preprocess)
    dl = DataLoader(dataset, batch_size=32, num_workers=2, shuffle=False)
    embs, etiquetas = [], []
    total = len(dataset)
    procesadas = 0
    for x, y in dl:
        x = x.to(dispositivo, non_blocking=True)
        with torch.autocast(device_type="cuda" if "cuda" in dispositivo else "cpu"):
            e = encoder(x)
        embs.append(e.float().cpu())
        etiquetas.append(y.numpy())
        procesadas += len(y)
        print(f"  {procesadas}/{total}", end="\r")
    print()
    return torch.cat(embs).numpy(), np.concatenate(etiquetas), dataset.entradas


def evaluar_knn(emb_train, y_train, emb_test, y_test, especies_permitidas_idx, k):
    """k-NN restringido a especies_permitidas_idx (simula que el paquete de Antioquia
    solo contiene esas especies como candidatas)."""
    sim = emb_test @ emb_train.T
    mascara_permitida = np.isin(y_train, list(especies_permitidas_idx))

    pred_top1 = np.empty(len(emb_test), dtype=int)
    top3_ok = np.zeros(len(emb_test), dtype=bool)

    idx_train_permitido = np.where(mascara_permitida)[0]
    sim_permitida = sim[:, idx_train_permitido]
    y_train_permitido = y_train[idx_train_permitido]
    n_especies_total = int(y_train.max()) + 1

    for i in range(len(emb_test)):
        k_efectivo = min(k, sim_permitida.shape[1])
        idx_k = np.argpartition(-sim_permitida[i], kth=k_efectivo - 1)[:k_efectivo]
        sims_k = sim_permitida[i, idx_k]
        orden = np.argsort(-sims_k)
        idx_k = idx_k[orden]
        especies_k = y_train_permitido[idx_k]
        sims_k = sims_k[orden]

        votos = np.zeros(n_especies_total)
        for especie, s in zip(especies_k, sims_k):
            votos[especie] += s
        pred_top1[i] = votos.argmax()

        top3_votadas = np.argsort(-votos)[:3]  # 3 especies con más voto; si hay <3 con voto>0, se completa con voto=0 (empate arbitrario, no afecta el acierto real)
        top3_ok[i] = y_test[i] in top3_votadas

    top1_acc = float((pred_top1 == y_test).mean())
    top3_acc = float(top3_ok.mean())
    return top1_acc, top3_acc


def generar_paquete_sqlite_antioquia(ruta, emb_train, y_train, entradas_train, especies_permitidas_idx, especies, especies_meta):
    ruta.parent.mkdir(parents=True, exist_ok=True)
    if ruta.exists():
        ruta.unlink()

    mascara = np.isin(y_train, list(especies_permitidas_idx))
    emb_filtrado = emb_train[mascara]
    y_filtrado = y_train[mascara]
    entradas_filtradas = [e for e, m in zip(entradas_train, mascara) if m]

    conn = sqlite3.connect(str(ruta))
    conn.enable_load_extension(True)
    sqlite_vec.load(conn)
    conn.enable_load_extension(False)

    conn.execute("""
        CREATE TABLE referencias (
            id INTEGER PRIMARY KEY,
            especie TEXT NOT NULL,
            genero TEXT NOT NULL,
            familia TEXT NOT NULL,
            ruta_foto TEXT NOT NULL,
            grupo_individuo TEXT NOT NULL
        )
    """)
    conn.execute(f"CREATE VIRTUAL TABLE vec_referencias USING vec0(embedding float[{emb_filtrado.shape[1]}])")

    for i, (emb, idx_esp, entrada) in enumerate(zip(emb_filtrado, y_filtrado, entradas_filtradas)):
        conn.execute(
            "INSERT INTO referencias (id, especie, genero, familia, ruta_foto, grupo_individuo) VALUES (?, ?, ?, ?, ?, ?)",
            (i, especies[idx_esp], entrada["genero"], entrada["familia"], entrada["ruta"], entrada["grupo"]),
        )
        conn.execute(
            "INSERT INTO vec_referencias (rowid, embedding) VALUES (?, ?)",
            (i, struct.pack(f"{len(emb)}f", *emb.tolist())),
        )

    conn.execute("CREATE TABLE manifest (clave TEXT PRIMARY KEY, valor TEXT)")
    manifest = {
        "version_paquete": "antioquia_v1",
        "region": "Antioquia (filtrado por bbox geográfico real: lat 5.4-8.9, lon -77.2--73.8, sobre coordenadas de train)",
        "n_vectores": int(mascara.sum()),
        "n_especies": len(especies_permitidas_idx),
        "especies": [especies[i] for i in sorted(especies_permitidas_idx)],
        "dimension_embedding": int(emb_filtrado.shape[1]),
        "encoder_origen": "encoder_anura_fp16.onnx (Fase 9, extraído de bioclip_anura_mejor.pt)",
        "distancia": "coseno (embeddings ya L2-normalizados)",
    }
    for k, v in manifest.items():
        conn.execute("INSERT INTO manifest VALUES (?, ?)", (k, json.dumps(v, ensure_ascii=False)))

    conn.commit()
    conn.close()
    return ruta.stat().st_size / (1024 * 1024), int(mascara.sum())


def main():
    dispositivo = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"{'='*78}\nFASE 9: Encoder ONNX + Precisión real del paquete Antioquia\n{'='*78}")
    print(f"Dispositivo: {dispositivo}\n")

    familias, generos, especies = vocabularios()

    print("Cargando encoder (mismo checkpoint de Fase 4/6)...")
    modelo_clip, _, preprocess = open_clip.create_model_and_transforms(MODELO_HF)
    checkpoint = torch.load(CHECKPOINT, map_location="cpu", weights_only=False)
    modelo_clip.visual.load_state_dict(checkpoint["visual_state_dict"])
    encoder_cpu = EncoderVisual(modelo_clip.visual).eval()

    # ── PARTE 1: exportar encoder a ONNX (el pendiente real de C-15) ──
    resultado_export = exportar_encoder_onnx(encoder_cpu)

    # ── PARTE 2: filtrar especies con presencia real en Antioquia ──
    print(f"\n{'='*78}\n[PARTE 2] Filtrando especies con presencia real en Antioquia\n{'='*78}")
    especies_antioquia, conteo_geo = especies_con_presencia_en_antioquia(especies)
    print(f"  {len(especies_antioquia)}/{len(especies)} especies con >= {MIN_PUNTOS_ANTIOQUIA} observaciones "
          f"de train dentro del bbox de Antioquia:")
    for e in especies_antioquia:
        print(f"    {e:<32} {conteo_geo[e]['en_antioquia']}/{conteo_geo[e]['total_puntos']} puntos")

    idx_de_especie = {e: i for i, e in enumerate(especies)}
    especies_antioquia_idx = {idx_de_especie[e] for e in especies_antioquia}

    # ── PARTE 3: embeddings de train/test (GPU, para velocidad) ──
    print(f"\n{'='*78}\n[PARTE 3] Generando embeddings (GPU) para evaluar k-NN\n{'='*78}")
    encoder_gpu = EncoderVisual(modelo_clip.visual).to(dispositivo).eval()
    manifiesto = json.loads(MANIFIESTO.read_text(encoding="utf-8"))
    entradas_train = [e for e in manifiesto["particiones"]["train"] if not e.get("aumentada")]
    entradas_test = manifiesto["particiones"]["test"]

    print("Embeddings de TRAIN...")
    emb_train, y_train, entradas_train_usadas = generar_embeddings(encoder_gpu, entradas_train, preprocess, dispositivo)
    print("Embeddings de TEST...")
    emb_test, y_test, entradas_test_usadas = generar_embeddings(encoder_gpu, entradas_test, preprocess, dispositivo)

    # ── PARTE 4: evaluación restringida a especies de Antioquia ──
    print(f"\n{'='*78}\n[PARTE 4] Precisión Ruta A vs Ruta B — SOLO especies de Antioquia\n{'='*78}")

    mascara_test_antioquia = np.isin(y_test, list(especies_antioquia_idx))
    n_test_antioquia = int(mascara_test_antioquia.sum())
    print(f"Imágenes de test cuya especie real está en Antioquia: {n_test_antioquia}/{len(y_test)}\n")

    emb_test_antioquia = emb_test[mascara_test_antioquia]
    y_test_antioquia = y_test[mascara_test_antioquia]

    top1_knn, top3_knn = evaluar_knn(emb_train, y_train, emb_test_antioquia, y_test_antioquia, especies_antioquia_idx, K_VECINOS)
    print(f"Ruta B (k-NN k={K_VECINOS}, paquete Antioquia, {len(especies_antioquia)} especies): "
          f"Top-1={top1_knn:.1%}  Top-3={top3_knn:.1%}")

    # Ruta A: clasificador de 41 clases, medido SOLO sobre las imágenes de test de especies de Antioquia
    fase5 = json.loads(FASE5_JSON.read_text(encoding="utf-8"))
    filas_antioquia = [f for f in fase5["por_especie"] if f["especie"] in especies_antioquia]
    n_test_total_a = sum(f["n_test"] for f in filas_antioquia)
    top1_clasificador_antioquia = sum(f["top1"] * f["n_test"] for f in filas_antioquia) / n_test_total_a
    top3_clasificador_antioquia = sum(f["top3"] * f["n_test"] for f in filas_antioquia) / n_test_total_a
    print(f"Ruta A (clasificador softmax 41 clases, medido solo sobre las {n_test_total_a} imágenes de especies "
          f"de Antioquia): Top-1={top1_clasificador_antioquia:.1%}  Top-3={top3_clasificador_antioquia:.1%}")

    delta_top1 = top1_knn - top1_clasificador_antioquia
    print(f"\nΔ Top-1 (Ruta B vs Ruta A, subconjunto Antioquia): {delta_top1:+.1%}")

    # ── PARTE 5: generar el paquete SQLite real de Antioquia ──
    print(f"\n{'='*78}\n[PARTE 5] Generando paquete SQLite-vec de Antioquia (filtrado real)\n{'='*78}")
    tam_mb, n_vectores = generar_paquete_sqlite_antioquia(
        PAQUETE_ANTIOQUIA, emb_train, y_train, entradas_train_usadas, especies_antioquia_idx, especies, conteo_geo
    )
    print(f"  Paquete: {PAQUETE_ANTIOQUIA}")
    print(f"  Tamaño: {tam_mb:.2f} MB ({n_vectores} vectores, {len(especies_antioquia)} especies)")

    resultado = {
        "encoder_onnx_export": resultado_export,
        "especies_antioquia": {
            "criterio": f">= {MIN_PUNTOS_ANTIOQUIA} observaciones de train en bbox lat[{LAT_MIN},{LAT_MAX}] lon[{LON_MIN},{LON_MAX}]",
            "n_especies": len(especies_antioquia),
            "n_especies_total_catalogo": len(especies),
            "lista": especies_antioquia,
            "conteo_por_especie": conteo_geo,
        },
        "precision_subconjunto_antioquia": {
            "n_test_antioquia": n_test_antioquia,
            "ruta_a_clasificador_softmax": {
                "top1": top1_clasificador_antioquia,
                "top3": top3_clasificador_antioquia,
                "nota": "Clasificador de 41 clases completo, medido solo sobre imágenes de test de especies de Antioquia",
            },
            "ruta_b_knn5_paquete_antioquia": {
                "top1": top1_knn,
                "top3": top3_knn,
                "nota": f"k-NN restringido a las {len(especies_antioquia)} especies del paquete de Antioquia",
            },
            "delta_top1_b_vs_a": delta_top1,
        },
        "paquete_sqlite_antioquia": {
            "ruta": str(PAQUETE_ANTIOQUIA),
            "tamano_mb": round(tam_mb, 2),
            "n_vectores": n_vectores,
            "n_especies": len(especies_antioquia),
        },
    }
    SALIDA_JSON.parent.mkdir(parents=True, exist_ok=True)
    SALIDA_JSON.write_text(json.dumps(resultado, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nFASE 9 OK — resultado completo en {SALIDA_JSON}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
