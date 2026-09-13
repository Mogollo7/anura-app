"""Fase 8 — Comparación real: k-NN (Ruta B, patrón Merlin) vs Clasificador softmax (Ruta A).

Responde la pregunta que decide la arquitectura de producción: si Anura usa
k-NN sobre embeddings + paquetes regionales SQLite-vec (como Merlin Bird ID),
¿cuánta precisión se pierde o se gana frente al clasificador softmax de 3
cabezas (Fase 4/5)?

Metodología (mismo test set que Fase 5, para que la comparación sea justa):
  1. Cargar el ENCODER (sin cabezas) del checkpoint de Fase 4 — el mismo peso
     visual que ya usa el clasificador, solo que aquí se usa para embeddings.
  2. Generar embeddings 512-d L2-normalizados de TODO train (sin aumentar,
     3.261 imágenes) y de TODO test (766 imágenes, exactamente las de Fase 5).
  3. Para cada embedding de test, buscar los k vecinos más cercanos en train
     por similitud coseno (= producto punto, ya normalizados) y votar especie
     por mayoría (k=5) y por vecino más cercano puro (k=1).
  4. Comparar Top-1/Top-3 de ambos esquemas de k-NN contra el 57,0%/82,4%
     de Fase 5 (clasificador softmax).
  5. Generar un paquete SQLite-vec de prueba (patrón Merlin: un archivo
     .sqlite autocontenido) con los embeddings de train como "paquete
     regional" simulado, para que Android tenga algo real que consultar.

Uso:
    python bioclip/scripts/fase_8_knn_vs_clasificador.py
"""

import json
import sqlite3
import struct
import sys
from pathlib import Path

import numpy as np
import open_clip
import sqlite_vec
import torch
from PIL import Image
from torch.utils.data import DataLoader, Dataset

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "training"))
from taxonomia import vocabularios  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

RAIZ_DATOS = Path(r"D:\Anura\data cleaned")
MANIFIESTO = Path(r"D:\Anura\training\manifiesto.json")
CHECKPOINT = Path(r"D:\Anura\bioclip\checkpoints\bioclip_anura_mejor.pt")
FASE5_JSON = Path(r"D:\Anura\bioclip\evaluation\fase_5_completa.json")
SALIDA_JSON = Path(r"D:\Anura\bioclip\evaluation\fase_8_knn_vs_clasificador.json")
PAQUETE_SQLITE = Path(r"D:\Anura\bioclip\paquetes_regionales\antioquia_prueba_v1.sqlite")
MODELO_HF = "hf-hub:imageomics/bioclip"
K_VECINOS = 5


class EncoderVisual(torch.nn.Module):
    def __init__(self, visual_encoder):
        super().__init__()
        self.visual = visual_encoder

    def forward(self, x):
        emb = self.visual(x)
        return emb / emb.norm(dim=-1, keepdim=True)


class DatasetImagenes(Dataset):
    """Filtra en __init__ las rutas que ya no existen (p. ej. movidas a cuarentena
    tras la limpieza de duplicados) para no fallar a mitad de un DataLoader worker."""

    def __init__(self, entradas, preprocess):
        self.preprocess = preprocess
        self.entradas = []
        faltantes = 0
        for e in entradas:
            if (RAIZ_DATOS / e["ruta"]).exists():
                self.entradas.append(e)
            else:
                faltantes += 1
        if faltantes:
            print(f"  [aviso] {faltantes} rutas del manifiesto ya no existen en disco — omitidas")

    def __len__(self):
        return len(self.entradas)

    def __getitem__(self, idx):
        entrada = self.entradas[idx]
        with Image.open(RAIZ_DATOS / entrada["ruta"]).convert("RGB") as img:
            tensor = self.preprocess(img)
        return tensor, entrada["idx_especie"]


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


def knn_predecir(emb_train, y_train, emb_test, k):
    """Vota por especie entre los k vecinos más cercanos (similitud coseno = dot, ya normalizado)."""
    sim = emb_test @ emb_train.T  # (n_test, n_train)
    top_k_idx = np.argpartition(-sim, kth=min(k, sim.shape[1] - 1), axis=1)[:, :k]

    pred_top1 = np.empty(len(emb_test), dtype=int)
    top3_ok = np.zeros(len(emb_test), dtype=bool)
    n_especies = int(y_train.max()) + 1

    for i in range(len(emb_test)):
        vecinos_idx = top_k_idx[i]
        vecinos_sim = sim[i, vecinos_idx]
        orden = np.argsort(-vecinos_sim)
        vecinos_idx = vecinos_idx[orden]
        vecinos_especies = y_train[vecinos_idx]

        # Voto mayoritario ponderado por similitud entre los k vecinos
        votos = np.zeros(n_especies)
        for especie, s in zip(vecinos_especies, sim[i, vecinos_idx]):
            votos[especie] += s
        pred_top1[i] = votos.argmax()

        # Top-3: especies presentes entre los primeros 3 vecinos únicos por score
        especies_unicas_ordenadas = []
        for especie in vecinos_especies:
            if especie not in especies_unicas_ordenadas:
                especies_unicas_ordenadas.append(especie)
        top3_especies = especies_unicas_ordenadas[:3]
        top3_ok[i] = True  # se corrige abajo con la etiqueta real

    return pred_top1, top_k_idx, sim


def evaluar_knn(emb_train, y_train, emb_test, y_test, k):
    sim = emb_test @ emb_train.T
    n_especies = int(y_train.max()) + 1

    pred_top1 = np.empty(len(emb_test), dtype=int)
    top3_ok = np.zeros(len(emb_test), dtype=bool)

    for i in range(len(emb_test)):
        idx_k = np.argpartition(-sim[i], kth=k - 1)[:k]
        sims_k = sim[i, idx_k]
        orden = np.argsort(-sims_k)
        idx_k = idx_k[orden]
        especies_k = y_train[idx_k]
        sims_k = sims_k[orden]

        votos = np.zeros(n_especies)
        for especie, s in zip(especies_k, sims_k):
            votos[especie] += s
        pred_top1[i] = votos.argmax()

        top3_votadas = np.argsort(-votos)[:3]
        top3_ok[i] = y_test[i] in top3_votadas

    top1_acc = float((pred_top1 == y_test).mean())
    top3_acc = float(top3_ok.mean())
    return top1_acc, top3_acc, pred_top1


def evaluar_1nn(emb_train, y_train, emb_test, y_test):
    """Vecino más cercano puro (k=1) — el caso más simple de búsqueda por similitud."""
    sim = emb_test @ emb_train.T
    idx_mejor = sim.argmax(axis=1)
    pred = y_train[idx_mejor]
    top1_acc = float((pred == y_test).mean())

    top5_idx = np.argsort(-sim, axis=1)[:, :5]
    top3_ok = np.zeros(len(emb_test), dtype=bool)
    for i in range(len(emb_test)):
        especies_vistas = []
        for idx in top5_idx[i]:
            e = y_train[idx]
            if e not in especies_vistas:
                especies_vistas.append(e)
            if len(especies_vistas) == 3:
                break
        top3_ok[i] = y_test[i] in especies_vistas
    return top1_acc, float(top3_ok.mean())


def generar_paquete_sqlite(ruta, emb_train, y_train, entradas_train, especies, generos, familias):
    """Genera un paquete .sqlite real con sqlite-vec — patrón Merlin: archivo autocontenido."""
    ruta.parent.mkdir(parents=True, exist_ok=True)
    if ruta.exists():
        ruta.unlink()

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
    conn.execute(f"""
        CREATE VIRTUAL TABLE vec_referencias USING vec0(
            embedding float[{emb_train.shape[1]}]
        )
    """)

    for i, (emb, idx_esp, entrada) in enumerate(zip(emb_train, y_train, entradas_train)):
        conn.execute(
            "INSERT INTO referencias (id, especie, genero, familia, ruta_foto, grupo_individuo) VALUES (?, ?, ?, ?, ?, ?)",
            (i, especies[idx_esp], entrada["genero"], entrada["familia"], entrada["ruta"], entrada["grupo"]),
        )
        conn.execute(
            "INSERT INTO vec_referencias (rowid, embedding) VALUES (?, ?)",
            (i, struct.pack(f"{len(emb)}f", *emb.tolist())),
        )

    conn.execute("""
        CREATE TABLE manifest (
            clave TEXT PRIMARY KEY,
            valor TEXT
        )
    """)
    manifest = {
        "version_paquete": "prueba_v1",
        "region": "Antioquia (SIMULADO — usa el catálogo completo de 41 especies, no un recorte geográfico real)",
        "n_vectores": len(emb_train),
        "n_especies": len(especies),
        "dimension_embedding": int(emb_train.shape[1]),
        "encoder_origen": "bioclip_anura_mejor.pt (Fase 4, checkpoint fp32)",
        "distancia": "coseno (embeddings ya L2-normalizados, usar producto punto o L2 indistintamente)",
    }
    for k, v in manifest.items():
        conn.execute("INSERT INTO manifest VALUES (?, ?)", (k, json.dumps(v, ensure_ascii=False)))

    conn.commit()
    conn.close()
    return ruta.stat().st_size / (1024 * 1024)


def main():
    dispositivo = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"{'='*78}\nFASE 8: k-NN (Ruta B) vs Clasificador softmax (Ruta A)\n{'='*78}")
    print(f"Dispositivo: {dispositivo}\n")

    familias, generos, especies = vocabularios()
    manifiesto = json.loads(MANIFIESTO.read_text(encoding="utf-8"))
    entradas_train = [e for e in manifiesto["particiones"]["train"] if not e.get("aumentada")]
    entradas_test = manifiesto["particiones"]["test"]

    print(f"Train (sin aumentar): {len(entradas_train)} imágenes")
    print(f"Test: {len(entradas_test)} imágenes (idénticas a Fase 5)\n")

    print("[1/4] Cargando encoder (mismo peso visual que el clasificador de Fase 4)...")
    modelo_clip, _, preprocess = open_clip.create_model_and_transforms(MODELO_HF)
    checkpoint = torch.load(CHECKPOINT, map_location="cpu", weights_only=False)
    modelo_clip.visual.load_state_dict(checkpoint["visual_state_dict"])
    encoder = EncoderVisual(modelo_clip.visual).to(dispositivo).eval()
    print("  OK\n")

    print("[2/4] Generando embeddings de TRAIN (base de referencia del paquete regional)...")
    emb_train, y_train, entradas_train_usadas = generar_embeddings(encoder, entradas_train, preprocess, dispositivo)
    print(f"  {emb_train.shape}\n")

    print("[3/4] Generando embeddings de TEST (mismo split que Fase 5)...")
    emb_test, y_test, entradas_test_usadas = generar_embeddings(encoder, entradas_test, preprocess, dispositivo)
    print(f"  {emb_test.shape}\n")

    print("[4/4] Evaluando k-NN...")
    top1_1nn, top3_1nn = evaluar_1nn(emb_train, y_train, emb_test, y_test)
    print(f"  1-NN (vecino más cercano puro):  Top-1={top1_1nn:.1%}  Top-3={top3_1nn:.1%}")

    top1_knn5, top3_knn5, pred_knn5 = evaluar_knn(emb_train, y_train, emb_test, y_test, k=K_VECINOS)
    print(f"  k-NN (k={K_VECINOS}, voto ponderado):    Top-1={top1_knn5:.1%}  Top-3={top3_knn5:.1%}")

    # ── Cargar resultados de Fase 5 (Ruta A) para comparación directa ──
    fase5 = json.loads(FASE5_JSON.read_text(encoding="utf-8"))
    top1_clasificador = fase5["meta"]["top1_global"]
    top3_clasificador = fase5["meta"]["top3_global"]
    print(f"\n  Clasificador softmax (Ruta A, Fase 5): Top-1={top1_clasificador:.1%}  Top-3={top3_clasificador:.1%}")

    print(f"\n{'='*78}\nCOMPARACIÓN FINAL — Ruta A vs Ruta B\n{'='*78}")
    print(f"{'Método':<38}{'Top-1':>10}{'Top-3':>10}")
    print("-" * 58)
    print(f"{'Ruta A: Clasificador softmax (3 cabezas)':<38}{top1_clasificador:>9.1%}{top3_clasificador:>10.1%}")
    print(f"{'Ruta B: 1-NN (vecino más cercano)':<38}{top1_1nn:>9.1%}{top3_1nn:>10.1%}")
    print(f"{'Ruta B: k-NN (k=5, voto ponderado)':<38}{top1_knn5:>9.1%}{top3_knn5:>10.1%}")

    delta_1nn = top1_1nn - top1_clasificador
    delta_knn5 = top1_knn5 - top1_clasificador
    print(f"\nΔ Top-1 (1-NN vs clasificador):  {delta_1nn:+.1%}")
    print(f"Δ Top-1 (k-NN5 vs clasificador): {delta_knn5:+.1%}")

    print(f"\n{'='*78}\nGenerando paquete SQLite-vec de prueba...\n{'='*78}")
    tam_mb = generar_paquete_sqlite(PAQUETE_SQLITE, emb_train, y_train, entradas_train_usadas, especies, generos, familias)
    print(f"  Paquete: {PAQUETE_SQLITE}")
    print(f"  Tamaño: {tam_mb:.2f} MB ({len(entradas_train_usadas)} vectores de referencia, {len(especies)} especies)")

    resultado = {
        "meta": {
            "n_train_referencia": len(entradas_train_usadas),
            "n_test": len(entradas_test_usadas),
            "n_especies": len(especies),
            "k_vecinos_evaluado": K_VECINOS,
        },
        "ruta_a_clasificador_softmax": {
            "top1": top1_clasificador,
            "top3": top3_clasificador,
            "fuente": "fase_5_completa.json",
        },
        "ruta_b_1nn": {
            "top1": top1_1nn,
            "top3": top3_1nn,
        },
        "ruta_b_knn5_voto_ponderado": {
            "top1": top1_knn5,
            "top3": top3_knn5,
        },
        "delta_top1_1nn_vs_clasificador": delta_1nn,
        "delta_top1_knn5_vs_clasificador": delta_knn5,
        "paquete_sqlite_generado": {
            "ruta": str(PAQUETE_SQLITE),
            "tamano_mb": round(tam_mb, 2),
            "n_vectores": len(entradas_train_usadas),
            "nota": "SIMULADO: usa el catálogo completo de 41 especies como si fuera 'Antioquia' — no hay recorte geográfico real todavía, falta el dato de región por observación",
        },
    }
    SALIDA_JSON.parent.mkdir(parents=True, exist_ok=True)
    SALIDA_JSON.write_text(json.dumps(resultado, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n✅ FASE 8 OK — resultado en {SALIDA_JSON}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
