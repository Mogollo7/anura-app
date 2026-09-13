"""Fase 4 — Transfer Learning de BioCLIP v1 sobre el dataset de Anura.

Flujo (C-11): BioCLIP v1 completo -> congelar la mayor parte del ViT-B/16 ->
entrenar 3 cabezas jerárquicas (Familia/Género/Especie) + descongelar
progresivamente las últimas capas -> guardar el MEJOR checkpoint.

Ese checkpoint es la entrada de Fase 6 (extraer model.visual). No se extrae
el encoder antes de entrenar — el objetivo es un encoder adaptado al dominio,
no el original (ver discusión de arquitectura, C-11).

Usa el manifiesto ya construido con GroupSplit por obs_id
(training/manifiesto.json) — ninguna partición comparte individuos.

Uso:
    # Variante A (imagen completa) — fallback si H4 no llega a tiempo
    python bioclip/scripts/fase_4_transfer_learning.py --permitir-sin-mascaras

    # Variante C (recorte segmentado) — target real, requiere H4
    python bioclip/scripts/fase_4_transfer_learning.py --masks-dir "D:/Anura/segmentacion/masks"
"""

import argparse
import gc
import io
import json
import sys
import time
from pathlib import Path

import numpy as np
import open_clip
import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision.transforms as T
from PIL import Image
from scipy import ndimage
from torch.utils.data import DataLoader, Dataset

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace", line_buffering=True)
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "training"))
from taxonomia import vocabularios  # noqa: E402

RAIZ_DATOS = Path(r"D:\Anura\data cleaned")
MANIFIESTO = Path(r"D:\Anura\training\manifiesto.json")
MODELO_HF = "hf-hub:imageomics/bioclip"
DIM_EMBEDDING = 512


# ─── Dataset ────────────────────────────────────────────────────────────────

class DatasetAnura(Dataset):
    """Lee el manifiesto de GroupSplit ya construido. Opcionalmente recorta
    por máscara de segmentación (variante C) antes del preprocess de CLIP.

    `transform` puede ser una única transform (val/test) o un par
    (moderada, agresiva): las entradas marcadas `aumentada` en el manifiesto
    — repeticiones de oversampling de `prepare_dataset.py` para especies con
    <70 individuos — reciben la transform agresiva, el resto la moderada.
    """

    def __init__(self, entradas: list[dict], transform, masks_dir: Path | None):
        self.entradas = entradas
        self.masks_dir = masks_dir
        if isinstance(transform, tuple):
            self.transform_moderada, self.transform_agresiva = transform
        else:
            self.transform_moderada = self.transform_agresiva = transform

    def __len__(self):
        return len(self.entradas)

    def auditar_mascaras(self) -> dict:
        """GATE 3: cuenta cuántas imágenes tienen máscara usable ANTES de entrenar.

        Sin esto, una ruta de máscaras mal configurada hace que TODAS las imágenes
        caigan al fallback silenciosamente: el entrenamiento corre "sin error" pero
        en variante A, creyendo uno que está en variante C.
        """
        if self.masks_dir is None:
            return {"con_mascara": 0, "sin_archivo": 0, "degenerada": 0, "total": len(self.entradas)}

        conteo = {"con_mascara": 0, "sin_archivo": 0, "degenerada": 0, "total": len(self.entradas)}
        for entrada in self.entradas:
            ruta_mascara = self.masks_dir / Path(entrada["ruta"]).with_suffix(".png")
            if not ruta_mascara.exists():
                conteo["sin_archivo"] += 1
                continue
            try:
                with Image.open(ruta_mascara).convert("L") as m:
                    mascara = np.array(m)
                if (mascara > 127).any():
                    conteo["con_mascara"] += 1
                else:
                    conteo["degenerada"] += 1
            except Exception:
                conteo["degenerada"] += 1
        return conteo

    def _recortar_por_mascara(self, imagen: Image.Image, ruta_relativa: str) -> Image.Image:
        """Variante C real: fondo a negro con la máscara binaria (pixel a pixel)
        + recorte al bounding box del individuo. Es la definición documentada
        en [[Modelo de Visión — BioCLIP]] §5 y la que sostuvo el ~99% de la
        Etapa I — "recorte CON fondo puesto a negro/neutro usando la máscara",
        no solo un zoom rectangular. Una versión anterior de esta función solo
        recortaba (sin enmascarar los píxeles), lo que dejaba todo el fondo
        original visible dentro del recorte y anulaba la ventaja real de la
        variante C: quitarle al modelo la opción de aprender sustrato en vez
        de morfología.

        Si no hay máscara para esta imagen, cae a la imagen completa (evita
        reventar el entrenamiento por una máscara faltante puntual).
        """
        ruta_mascara = self.masks_dir / Path(ruta_relativa).with_suffix(".png")
        if not ruta_mascara.exists():
            return imagen
        with Image.open(ruta_mascara).convert("L") as m:
            mascara = np.array(m) > 127
        if not mascara.any():
            return imagen
        # El bbox de TODOS los píxeles marcados es frágil: un solo falso
        # positivo en la esquina opuesta (el segmentador se entrenó con 9
        # especies y se aplica a 41 — domain shift real en 32 de ellas)
        # estira el recorte hasta casi la imagen completa. Medido en
        # Dendrobates_truncatus: 34% de las máscaras tienen ≥2 componentes
        # separados, y el bbox resultante duplicaba en promedio el área real
        # de la rana (15,8% vs 7,4%). Quedarse con el componente conexo más
        # grande (la rana, no el ruido disperso) es el fix.
        etiquetas, n_componentes = ndimage.label(mascara)
        if n_componentes > 1:
            tamanos = ndimage.sum(mascara, etiquetas, range(1, n_componentes + 1))
            mascara = etiquetas == (np.argmax(tamanos) + 1)

        arr = np.array(imagen)
        arr[~mascara] = 0  # fondo a negro, pixel a pixel — la parte que faltaba
        imagen_enmascarada = Image.fromarray(arr)

        filas = np.any(mascara, axis=1)
        cols = np.any(mascara, axis=0)
        y0, y1 = np.where(filas)[0][[0, -1]]
        x0, x1 = np.where(cols)[0][[0, -1]]
        return imagen_enmascarada.crop((int(x0), int(y0), int(x1) + 1, int(y1) + 1))

    def __getitem__(self, idx):
        entrada = self.entradas[idx]
        ruta = RAIZ_DATOS / entrada["ruta"]
        transform = self.transform_agresiva if entrada.get("aumentada") else self.transform_moderada
        with Image.open(ruta).convert("RGB") as img:
            if self.masks_dir is not None:
                img = self._recortar_por_mascara(img, entrada["ruta"])
            tensor = transform(img)
        return (
            tensor,
            entrada["idx_familia"],
            entrada["idx_genero"],
            entrada["idx_especie"],
        )


def construir_transforms(preprocess_val):
    """Torchvision transforms con augmentation moderada + fuerte regularización en el optimizer.

    Lección aprendida: Albumentations causó degradación masiva (probablemente por normalización rota).
    Revertir a torchvision que funciona (69.2% Top-1), combatir overfitting con regularización
    del modelo (weight_decay, dropout, early stopping agresivo) en lugar de augmentation extrema.

    Dos variantes de train: la moderada (de siempre) para individuos reales, y una
    agresiva reservada para las repeticiones de oversampling (`aumentada: true` en el
    manifiesto, especies con <70 individuos — ver `prepare_dataset.py`). Sin esto, una
    especie escasa vería la MISMA imagen una y otra vez con variación idéntica a la de
    cualquier otra foto, desperdiciando la repetición. Hue se mantiene igual en ambas
    (± política de "Estrategia de Construcción del Dataset": no pasar de HueShift 15°,
    ya al límite en 0.05 ≈ 18°) — la fuerza extra va en geometría, color y oclusión.
    """
    # Augmentation para entrenamiento: más agresiva que antes
    entrenar_moderada = T.Compose([
        T.RandomResizedCrop(224, scale=(0.6, 1.0)),       # rango más amplio de crop
        T.RandomHorizontalFlip(p=0.5),
        T.RandomVerticalFlip(p=0.3),                      # ranas invertidas
        T.RandomRotation(degrees=20),
        T.ColorJitter(brightness=0.25, contrast=0.25, saturation=0.15, hue=0.05),
        T.RandomAffine(degrees=15, translate=(0.1, 0.1), scale=(0.85, 1.15)),
        T.ToTensor(),  # ToTensor debe estar antes de transformaciones que trabajan con tensores
        T.GaussianBlur(kernel_size=3, sigma=(0.1, 0.5)),  # blur suave (solo en tensores)
        T.RandomErasing(p=0.2, scale=(0.02, 0.1)),        # oclusión pequeña (solo en tensores)
        preprocess_val.transforms[-1],                    # Normalize de OpenCLIP
    ])
    entrenar_agresiva = T.Compose([
        T.RandomResizedCrop(224, scale=(0.4, 1.0)),       # crop más agresivo: hasta 40% del encuadre
        T.RandomHorizontalFlip(p=0.5),
        T.RandomVerticalFlip(p=0.4),
        T.RandomRotation(degrees=30),
        T.ColorJitter(brightness=0.35, contrast=0.35, saturation=0.25, hue=0.05),  # hue igual, resto +40%
        T.RandomAffine(degrees=20, translate=(0.15, 0.15), scale=(0.75, 1.25)),
        T.ToTensor(),
        T.GaussianBlur(kernel_size=3, sigma=(0.1, 1.0)),
        T.RandomErasing(p=0.35, scale=(0.02, 0.2)),       # oclusión más grande y más frecuente
        preprocess_val.transforms[-1],
    ])
    return (entrenar_moderada, entrenar_agresiva), preprocess_val  # val/test usan preprocess oficial sin augmentation


# ─── Modelo: BioCLIP + 3 cabezas jerárquicas ────────────────────────────────

class BioClipMultiHead(nn.Module):
    """Envuelve model.visual de BioCLIP con 3 cabezas lineales. El propio
    model.visual es el que se extrae en Fase 6 una vez entrenado.
    """

    def __init__(self, visual_encoder: nn.Module, n_familias: int, n_generos: int, n_especies: int, dropout=0.4):
        super().__init__()
        self.visual = visual_encoder
        self.dropout = nn.Dropout(p=dropout)
        # Dropout antes de cada cabeza para combatir overfitting
        self.cabeza_familia = nn.Linear(DIM_EMBEDDING, n_familias)
        self.cabeza_genero = nn.Linear(DIM_EMBEDDING, n_generos)
        self.cabeza_especie = nn.Linear(DIM_EMBEDDING, n_especies)

    def forward(self, x):
        embedding = self.visual(x)
        embedding = F.normalize(embedding, dim=-1)
        embedding_dropped = self.dropout(embedding)  # Dropout solo en train (eval mode lo desactiva)
        return embedding, (
            self.cabeza_familia(embedding_dropped),
            self.cabeza_genero(embedding_dropped),
            self.cabeza_especie(embedding_dropped),
        )


def congelar_backbone(visual: nn.Module, n_bloques_descongelados: int):
    """Congela todo el ViT salvo los últimos n_bloques_descongelados resblocks
    y la proyección final. n_bloques_descongelados=0 -> solo entrenan las cabezas.
    """
    for p in visual.parameters():
        p.requires_grad = False

    if n_bloques_descongelados <= 0:
        return

    # open_clip.VisionTransformer expone los bloques en .transformer.resblocks
    bloques = visual.transformer.resblocks
    for bloque in bloques[-n_bloques_descongelados:]:
        for p in bloque.parameters():
            p.requires_grad = True

    # La proyección final a 512-d siempre se descongela junto con las últimas capas
    if hasattr(visual, "proj") and visual.proj is not None:
        visual.proj.requires_grad = True
    if hasattr(visual, "ln_post"):
        for p in visual.ln_post.parameters():
            p.requires_grad = True


# ─── Pérdida jerárquica y métricas ──────────────────────────────────────────

def perdida_multihead(logits, objetivos, pesos_clase_especie=None, pesos=(0.2, 0.3, 0.5)):
    """CE ponderada por nivel taxonómico. Especie pesa más porque es el nivel
    que finalmente importa para identificación, pero familia/género siguen
    empujando al modelo a no cometer errores jerárquicamente imposibles.

    `pesos_clase_especie` (tensor por especie, de `prepare_dataset.py`) compensa
    el desbalance que el oversampling proporcional (tope 4x) deja sin resolver:
    inflar más allá de eso a especies con <20 individuos reales solo produce
    memorización, así que el resto del desbalance se corrige aquí, en la pérdida.
    """
    l_fam, l_gen, l_esp = logits
    y_fam, y_gen, y_esp = objetivos
    ce_fam = F.cross_entropy(l_fam, y_fam)
    ce_gen = F.cross_entropy(l_gen, y_gen)
    ce_esp = F.cross_entropy(l_esp, y_esp, weight=pesos_clase_especie)
    total = pesos[0] * ce_fam + pesos[1] * ce_gen + pesos[2] * ce_esp
    return total, (ce_fam.item(), ce_gen.item(), ce_esp.item())


@torch.no_grad()
def evaluar(modelo, cargador, dispositivo):
    modelo.eval()
    correctos = {"familia": 0, "genero": 0, "especie": 0}
    top3_especie = 0
    total = 0
    for x, y_fam, y_gen, y_esp in cargador:
        x = x.to(dispositivo, non_blocking=True)
        y_fam, y_gen, y_esp = (t.to(dispositivo, non_blocking=True) for t in (y_fam, y_gen, y_esp))
        with torch.autocast(device_type="cuda" if "cuda" in dispositivo else "cpu"):
            _, (l_fam, l_gen, l_esp) = modelo(x)

        correctos["familia"] += (l_fam.argmax(-1) == y_fam).sum().item()
        correctos["genero"] += (l_gen.argmax(-1) == y_gen).sum().item()
        correctos["especie"] += (l_esp.argmax(-1) == y_esp).sum().item()
        top3 = l_esp.topk(3, dim=-1).indices
        top3_especie += (top3 == y_esp.unsqueeze(-1)).any(-1).sum().item()
        total += x.size(0)

    return {
        "top1_familia": correctos["familia"] / total,
        "top1_genero": correctos["genero"] / total,
        "top1_especie": correctos["especie"] / total,
        "top3_especie": top3_especie / total,
    }


# ─── Entrenamiento ───────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--masks-dir", type=Path, default=None, help="Carpeta de máscaras (variante C)")
    parser.add_argument("--permitir-sin-mascaras", action="store_true", help="Corre en variante A (imagen completa)")
    parser.add_argument("--epocas-cabezas", type=int, default=8, help="Fase A: solo cabezas, backbone congelado")
    parser.add_argument("--epocas-finetune", type=int, default=20, help="Fase B: cabezas + últimas capas del ViT")
    parser.add_argument("--capas-descongeladas", type=int, default=4, help="Últimos N resblocks del ViT-B/16 a descongelar en Fase B")
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--lr-cabezas", type=float, default=1e-3)
    parser.add_argument("--lr-backbone", type=float, default=1e-5, help="LR bajo: son pesos preentrenados, no arrancan de cero")
    parser.add_argument("--paciencia", type=int, default=2, help="Early stopping sobre top1_especie de validación (reducido a 2 para evitar overfitting tardío)")
    parser.add_argument("--salida", type=Path, default=Path(r"D:\Anura\bioclip\checkpoints"))
    args = parser.parse_args()

    if args.masks_dir is None and not args.permitir_sin_mascaras:
        print("[ERROR] Falta --masks-dir (variante C) o --permitir-sin-mascaras (variante A, fallback).")
        print("        Ver C-9/C-11 en la bóveda: variante C es el objetivo real; variante A es diagnóstica.")
        return 1

    variante = "C (segmentada)" if args.masks_dir else "A (imagen completa, fallback sin H4)"
    dispositivo = "cuda" if torch.cuda.is_available() else "cpu"
    args.salida.mkdir(parents=True, exist_ok=True)

    print(f"{'='*70}\nFASE 4: Transfer Learning BioCLIP v1 -> Anura (variante {variante})\n{'='*70}")
    print(f"Dispositivo: {dispositivo}")

    # ── Datos ──
    manifiesto = json.loads(MANIFIESTO.read_text(encoding="utf-8"))
    familias, generos, especies = vocabularios()
    print(f"Taxonomía: {len(familias)} familias, {len(generos)} géneros, {len(especies)} especies")
    for particion, n in ((k, len(v)) for k, v in manifiesto["particiones"].items()):
        print(f"  {particion}: {n} imágenes")

    pesos_clase_especie = None
    lista_pesos = manifiesto.get("meta", {}).get("pesos_clase_especie")
    if lista_pesos:
        pesos_clase_especie = torch.tensor(lista_pesos, dtype=torch.float32, device=dispositivo)
        print(f"  Class weights especie: min={min(lista_pesos):.2f} max={max(lista_pesos):.2f} "
              f"(compensa desbalance residual tras oversampling proporcional)")

    print("\nCargando BioCLIP v1...")
    modelo_clip, _, preprocess_val = open_clip.create_model_and_transforms(MODELO_HF)
    entrenar_tf, val_tf = construir_transforms(preprocess_val)

    ds_train = DatasetAnura(manifiesto["particiones"]["train"], entrenar_tf, args.masks_dir)
    ds_val = DatasetAnura(manifiesto["particiones"]["val"], val_tf, args.masks_dir)
    ds_test = DatasetAnura(manifiesto["particiones"]["test"], val_tf, args.masks_dir)

    # persistent_workers evita relanzar los procesos worker (spawn en Windows, caro)
    # en cada época — sin esto, cada época paga de nuevo el costo de arranque de 4 procesos.
    dl_train = DataLoader(
        ds_train, batch_size=args.batch_size, shuffle=True,
        num_workers=4, pin_memory=True, persistent_workers=True,
    )
    dl_val = DataLoader(
        ds_val, batch_size=args.batch_size,
        num_workers=2, pin_memory=True, persistent_workers=True,
    )
    dl_test = DataLoader(ds_test, batch_size=args.batch_size, num_workers=2, pin_memory=True)

    # ── GATE 3: verificar que variante C realmente está usando máscaras ──
    if args.masks_dir is not None:
        print(f"\n[GATE 3 — Uso real de máscaras (variante C)]")
        aborta = False
        for nombre, ds in (("train", ds_train), ("val", ds_val), ("test", ds_test)):
            c = ds.auditar_mascaras()
            pct = c["con_mascara"] / c["total"] if c["total"] else 0.0
            print(f"  {nombre:<6} {c['con_mascara']}/{c['total']} con máscara usable ({pct:.1%})  "
                  f"| sin archivo: {c['sin_archivo']}  degeneradas: {c['degenerada']}")
            if pct < 0.80:
                aborta = True
        if aborta:
            print(f"\n  ❌ FALLA: menos del 80% de las imágenes tienen máscara usable.")
            print(f"     Entrenar así sería variante A disfrazada de variante C.")
            print(f"     Revisa --masks-dir ({args.masks_dir}) y corre segmentacion/aplicar_a_dataset.py.")
            return 2
        print(f"  ✅ OK: máscaras presentes y usables, entrenando en variante C real.")

    modelo = BioClipMultiHead(modelo_clip.visual, len(familias), len(generos), len(especies)).to(dispositivo)

    # ── Fase A: solo cabezas (backbone congelado) ──
    print(f"\n=== Fase A: {args.epocas_cabezas} épocas, solo cabezas (backbone congelado) ===")
    congelar_backbone(modelo.visual, n_bloques_descongelados=0)
    params_entrenables = [p for p in modelo.parameters() if p.requires_grad]
    print(f"  Parámetros entrenables: {sum(p.numel() for p in params_entrenables):,}")

    opt = torch.optim.AdamW(params_entrenables, lr=args.lr_cabezas, weight_decay=0.05)
    # GradScaler: sin esto, autocast en FP16 puede producir gradientes tan pequeños
    # que hacen underflow a 0 en el backward — se "entrena" pero sin aprender bien,
    # silenciosamente. El scaler amplifica la pérdida antes de backward y reescala
    # los gradientes después, evitando esa pérdida de precisión.
    scaler = torch.amp.GradScaler("cuda") if "cuda" in dispositivo else None
    mejor_top1_especie = 0.0
    sin_mejora = 0
    historial = []

    def uso_memoria_gb():
        if "cuda" not in dispositivo:
            return 0.0, 0.0
        return (
            torch.cuda.memory_allocated() / 1e9,
            torch.cuda.max_memory_allocated() / 1e9,
        )

    def ciclo_entrenamiento(dl, opt, epocas, nombre_fase):
        nonlocal mejor_top1_especie, sin_mejora
        for epoca in range(1, epocas + 1):
            modelo.train()
            t0 = time.time()
            perdida_acum = 0.0
            for x, y_fam, y_gen, y_esp in dl:
                x = x.to(dispositivo, non_blocking=True)
                y_fam, y_gen, y_esp = (t.to(dispositivo, non_blocking=True) for t in (y_fam, y_gen, y_esp))
                opt.zero_grad(set_to_none=True)  # set_to_none evita escribir ceros en memoria ya alojada
                with torch.autocast(device_type="cuda" if "cuda" in dispositivo else "cpu"):
                    _, logits = modelo(x)
                    perdida, (ce_f, ce_g, ce_e) = perdida_multihead(logits, (y_fam, y_gen, y_esp), pesos_clase_especie)
                if scaler is not None:
                    scaler.scale(perdida).backward()
                    scaler.step(opt)
                    scaler.update()
                else:
                    perdida.backward()
                    opt.step()
                perdida_acum += perdida.item()

            metricas_val = evaluar(modelo, dl_val, dispositivo)
            dt = time.time() - t0
            mem_actual, mem_pico = uso_memoria_gb()
            print(
                f"  [{nombre_fase}] época {epoca}/{epocas}  L={perdida_acum/len(dl):.4f}  "
                f"val top1: fam={metricas_val['top1_familia']:.1%} gen={metricas_val['top1_genero']:.1%} "
                f"esp={metricas_val['top1_especie']:.1%}  top3_esp={metricas_val['top3_especie']:.1%}  "
                f"({dt:.0f}s, VRAM {mem_actual:.1f}/{mem_pico:.1f} GB actual/pico)"
            )
            historial.append({
                "fase": nombre_fase, "epoca": epoca, "perdida": perdida_acum / len(dl),
                "vram_gb": mem_actual, "vram_pico_gb": mem_pico, **metricas_val,
            })

            if metricas_val["top1_especie"] > mejor_top1_especie:
                mejor_top1_especie = metricas_val["top1_especie"]
                sin_mejora = 0
                torch.save(
                    {
                        "visual_state_dict": modelo.visual.state_dict(),
                        "cabezas_state_dict": {
                            "familia": modelo.cabeza_familia.state_dict(),
                            "genero": modelo.cabeza_genero.state_dict(),
                            "especie": modelo.cabeza_especie.state_dict(),
                        },
                        "metricas_val": metricas_val,
                        "fase": nombre_fase,
                        "epoca": epoca,
                        "familias": familias,
                        "generos": generos,
                        "especies": especies,
                    },
                    args.salida / "bioclip_anura_mejor.pt",
                )
                print(f"    -> nuevo mejor checkpoint (top1_especie={mejor_top1_especie:.1%})")
            else:
                sin_mejora += 1
                if sin_mejora >= args.paciencia:
                    print(f"    -> parada temprana ({args.paciencia} épocas sin mejora)")
                    return True
        return False

    ciclo_entrenamiento(dl_train, opt, args.epocas_cabezas, "cabezas")

    # Liberar el optimizer de Fase A (sus estados de Adam ya no sirven) y limpiar
    # el allocator de PyTorch antes de sumar 28M+ parámetros entrenables nuevos —
    # evita que la fragmentación de Fase A reduzca la memoria contigua disponible
    # para Fase B, que es la fase con más VRAM en juego.
    del opt, params_entrenables
    gc.collect()
    if "cuda" in dispositivo:
        torch.cuda.empty_cache()
        torch.cuda.reset_peak_memory_stats()

    # ── Fase B: descongelar últimas capas del ViT ──
    print(f"\n=== Fase B: {args.epocas_finetune} épocas, últimas {args.capas_descongeladas} capas + cabezas ===")
    congelar_backbone(modelo.visual, n_bloques_descongelados=args.capas_descongeladas)
    params_backbone = [p for p in modelo.visual.parameters() if p.requires_grad]
    params_cabezas = list(modelo.cabeza_familia.parameters()) + list(modelo.cabeza_genero.parameters()) + list(modelo.cabeza_especie.parameters())
    print(f"  Parámetros backbone descongelados: {sum(p.numel() for p in params_backbone):,}")
    print(f"  Parámetros cabezas: {sum(p.numel() for p in params_cabezas):,}")

    opt_ft = torch.optim.AdamW([
        {"params": params_backbone, "lr": args.lr_backbone, "weight_decay": 0.02},  # backbone: weight decay conservador
        {"params": params_cabezas, "lr": args.lr_cabezas, "weight_decay": 0.05},  # cabezas: weight decay más fuerte
    ])
    sin_mejora = 0  # reinicia el contador de early stopping para la fase B
    ciclo_entrenamiento(dl_train, opt_ft, args.epocas_finetune, "finetune")

    # ── Evaluación final sobre test con el mejor checkpoint ──
    print("\n=== Evaluación final (test, mejor checkpoint) ===")
    checkpoint = torch.load(args.salida / "bioclip_anura_mejor.pt", map_location=dispositivo, weights_only=False)
    modelo.visual.load_state_dict(checkpoint["visual_state_dict"])
    modelo.cabeza_familia.load_state_dict(checkpoint["cabezas_state_dict"]["familia"])
    modelo.cabeza_genero.load_state_dict(checkpoint["cabezas_state_dict"]["genero"])
    modelo.cabeza_especie.load_state_dict(checkpoint["cabezas_state_dict"]["especie"])

    metricas_test = evaluar(modelo, dl_test, dispositivo)
    print(f"  Top-1 familia:  {metricas_test['top1_familia']:.1%}")
    print(f"  Top-1 género:   {metricas_test['top1_genero']:.1%}")
    print(f"  Top-1 especie:  {metricas_test['top1_especie']:.1%}")
    print(f"  Top-3 especie:  {metricas_test['top3_especie']:.1%}")

    (args.salida / "historial_entrenamiento.json").write_text(
        json.dumps({"variante": variante, "historial": historial, "metricas_test": metricas_test}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"\n✅ FASE 4 OK — mejor checkpoint en {args.salida / 'bioclip_anura_mejor.pt'}")
    print(f"   Listo para Fase 5 (evaluación completa) y Fase 6 (extraer model.visual)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
