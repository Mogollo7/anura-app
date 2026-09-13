"""Fase 3 — Baseline con BioCLIP v1 sin Transfer Learning.

Evalúa BioCLIP original (sin entrenar en Anura) usando nearest-neighbors sobre
los embeddings generados en Fase 2. Proporciona la línea de referencia antes
de Transfer Learning.

Pregunta clave: ¿Cuánto funciona BioCLIP puro sobre las 28 especies de Anura?

Uso:
    python bioclip/scripts/fase_3_baseline.py
"""

import io
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace", line_buffering=True)
from sklearn.model_selection import StratifiedKFold
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import top_k_accuracy_score, f1_score, confusion_matrix


EMBEDDINGS = Path(r"D:\Anura\bioclip\datasets\embeddings_muestra.npy")
META = Path(r"D:\Anura\bioclip\datasets\embeddings_muestra_meta.json")
SALIDA_INFORME = Path(r"D:\Anura\bioclip\evaluation\baseline_bioclip_v1.json")


def cargar_datos():
    emb = np.load(EMBEDDINGS)
    meta = json.loads(META.read_text(encoding="utf-8"))
    etiquetas = [m["especie"] for m in meta]
    return emb, etiquetas


def main():
    if not EMBEDDINGS.exists():
        print(f"[ERROR] No se encontraron embeddings en {EMBEDDINGS}")
        print("       Ejecuta primero: python bioclip/scripts/fase_2_obtener_embeddings.py")
        return 1

    print(f"{'='*60}")
    print("FASE 3: Baseline BioCLIP v1 (sin Transfer Learning)")
    print(f"{'='*60}")

    emb, etiquetas = cargar_datos()
    le = LabelEncoder()
    y = le.fit_transform(etiquetas)
    n_clases = len(le.classes_)

    print(f"Dataset: {len(emb)} embeddings, {n_clases} especies")
    conteo = Counter(etiquetas)
    print(f"Distribución: min {min(conteo.values())}, max {max(conteo.values())} imgs/especie")

    # k-NN con cosine similarity (los embeddings ya están L2-normalizados)
    # cosine distance ≡ euclidean distance sobre vectores normalizados
    knn = KNeighborsClassifier(n_neighbors=5, metric="cosine", n_jobs=-1)

    # Validación cruzada estratificada (5 folds)
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    resultados_top1 = []
    resultados_top3 = []
    resultados_f1 = []
    y_reales_total = []
    y_pred_total = []

    print("\nValidación cruzada (5 folds)...")
    for fold, (train_idx, test_idx) in enumerate(cv.split(emb, y), 1):
        knn.fit(emb[train_idx], y[train_idx])
        y_pred = knn.predict(emb[test_idx])
        y_proba = knn.predict_proba(emb[test_idx])

        top1 = np.mean(y_pred == y[test_idx])
        top3 = top_k_accuracy_score(y[test_idx], y_proba, k=3, labels=np.arange(n_clases))
        f1 = f1_score(y[test_idx], y_pred, average="macro", zero_division=0)

        resultados_top1.append(top1)
        resultados_top3.append(top3)
        resultados_f1.append(f1)
        y_reales_total.extend(y[test_idx].tolist())
        y_pred_total.extend(y_pred.tolist())

        print(f"  Fold {fold}: Top-1 {top1:.1%}  Top-3 {top3:.1%}  F1 {f1:.1%}")

    top1_mean = np.mean(resultados_top1)
    top3_mean = np.mean(resultados_top3)
    f1_mean = np.mean(resultados_f1)

    print(f"\n{'='*60}")
    print(f"BASELINE BioCLIP v1 (k-NN, 5-fold CV)")
    print(f"{'='*60}")
    print(f"  Top-1 Accuracy:  {top1_mean:.1%} ± {np.std(resultados_top1):.1%}")
    print(f"  Top-3 Accuracy:  {top3_mean:.1%} ± {np.std(resultados_top3):.1%}")
    print(f"  F1-macro:        {f1_mean:.1%} ± {np.std(resultados_f1):.1%}")

    # F1 por especie
    print("\nF1 por especie:")
    f1_por_especie = f1_score(y_reales_total, y_pred_total, average=None, zero_division=0)
    for i, (especie, f1) in enumerate(zip(le.classes_, f1_por_especie)):
        barra = "█" * int(f1 * 20)
        print(f"  {especie:<35} {f1:.1%} {barra}")

    # Guardar informe
    SALIDA_INFORME.parent.mkdir(parents=True, exist_ok=True)
    informe = {
        "modelo": "BioCLIP v1 (sin fine-tuning)",
        "metodo": "k-NN cosine, k=5, 5-fold CV",
        "n_muestras": len(emb),
        "n_especies": n_clases,
        "top1_mean": round(top1_mean, 4),
        "top1_std": round(np.std(resultados_top1), 4),
        "top3_mean": round(top3_mean, 4),
        "top3_std": round(np.std(resultados_top3), 4),
        "f1_macro_mean": round(f1_mean, 4),
        "f1_por_especie": {esp: round(f1, 4) for esp, f1 in zip(le.classes_, f1_por_especie)},
    }
    SALIDA_INFORME.write_text(json.dumps(informe, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n✅ FASE 3 OK — Informe guardado en {SALIDA_INFORME}")
    print(f"\nEste es el baseline: cualquier mejora con Transfer Learning debe superar {top1_mean:.1%} Top-1")

    return 0


if __name__ == "__main__":
    sys.exit(main())
