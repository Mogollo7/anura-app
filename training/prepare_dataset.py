"""Construye el manifiesto de entrenamiento con GroupSplit por individuo.

El identificador de individuo sale del propio nombre de archivo del scraper de
iNaturalist (`col_obs_<observacion>_photo_<foto>.jpg`): todas las fotos de una
misma observación son el mismo animal, así que nunca pueden repartirse entre
train y validación sin producir fuga de información.

Uso:
    python training/prepare_dataset.py
    python training/prepare_dataset.py --tope-obs 150 --salida training/manifiesto_v2.json
"""

import argparse
import json
import random
import re
from collections import defaultdict
from pathlib import Path

from taxonomia import familia_de, genero_de, vocabularios

PATRON_OBSERVACION = re.compile(r"obs_(\d+)_")
EXTENSIONES = {".jpg", ".jpeg", ".png"}


def cargar_lista_negra(ruta: Path | None) -> set[str]:
    if ruta is None or not ruta.exists():
        return set()
    return set(json.loads(ruta.read_text(encoding="utf-8")))


def descubrir_imagenes(raiz: Path, especie: str, lista_negra: set[str]) -> list[Path]:
    carpeta = raiz / especie
    if not carpeta.is_dir():
        return []
    return sorted(
        p
        for p in carpeta.rglob("*")
        if p.is_file()
        and p.suffix.lower() in EXTENSIONES
        and "sonidos" not in p.parts
        and str(p.relative_to(raiz)).replace("\\", "/") not in lista_negra
    )


def cargar_fusiones(ruta: Path | None) -> dict[str, str]:
    """obs_id -> obs_id representante del cluster.

    Generado por detección de duplicados perceptuales: observaciones con
    obs_id DISTINTO que comparten al menos una foto idéntica (mismo evento
    reportado dos veces en iNaturalist). Sin esto, GroupSplit los trata como
    individuos diferentes y puede repartir el mismo animal entre particiones
    aunque el chequeo "grupos repartidos" no lo detecte (cada obs_id por
    separado sí queda en una sola partición, el problema es que son el mismo
    individuo bajo dos obs_id).
    """
    if ruta is None or not ruta.exists():
        return {}
    clusters = json.loads(ruta.read_text(encoding="utf-8"))
    mapa = {}
    for cluster in clusters:
        representante = min(cluster)
        for obs_id in cluster:
            mapa[obs_id] = representante
    return mapa


def agrupar_por_individuo(imagenes: list[Path], fusiones: dict[str, str]) -> dict[str, list[Path]]:
    grupos: dict[str, list[Path]] = defaultdict(list)
    for ruta in imagenes:
        encontrado = PATRON_OBSERVACION.search(ruta.name)
        # Sin patrón (fotos de museo, dendrowiki, etc.) cada archivo es su propio
        # individuo: es el supuesto conservador, nunca junta dos animales distintos.
        if encontrado:
            obs_id = encontrado.group(1)
            clave = fusiones.get(obs_id, obs_id)
        else:
            clave = f"manual::{ruta.stem}"
        grupos[clave].append(ruta)
    return grupos


def repartir(claves: list[str], proporciones: tuple[float, float, float]) -> dict[str, list[str]]:
    n = len(claves)
    n_train = int(round(n * proporciones[0]))
    n_val = int(round(n * proporciones[1]))
    # Con pocos grupos el redondeo puede dejar val o test vacíos; se les garantiza uno.
    if n >= 3:
        n_train = min(n_train, n - 2)
        n_val = max(1, min(n_val, n - n_train - 1))
    return {
        "train": claves[:n_train],
        "val": claves[n_train : n_train + n_val],
        "test": claves[n_train + n_val :],
    }


MULTIPLICADOR_OVERSAMPLING_MAXIMO = 4


def oversamplear_train(claves_train: list[str], train_esperado: int, semilla_texto: str) -> list[str]:
    """Rellena train por repetición SOLO si hay escasez real, con doble tope.

    Una especie con el cupo completo (>= train_esperado individuos, p.ej. 49 de
    70 obs con reparto 70/15/15) no se toca — ya tiene lo que se espera de
    cualquier especie del catálogo, inflarla no aporta nada.

    Una especie escasa se rellena hacia `train_esperado`, pero sin pasar de
    MULTIPLICADOR_OVERSAMPLING_MAXIMO veces sus individuos reales: con 18
    individuos, repetir hasta 49 (2.7x) es razonable, pero con 8 individuos no
    se fuerza hasta 49 (6x, pura memorización) — se limita a 32 (4x) y el
    desbalance residual frente a las especies con cupo completo se corrige en
    la pérdida vía `calcular_pesos_clase`, no inflando más los datos.
    """
    if not claves_train or len(claves_train) >= train_esperado:
        return claves_train
    objetivo = min(train_esperado, len(claves_train) * MULTIPLICADOR_OVERSAMPLING_MAXIMO)
    rng = random.Random(semilla_texto)
    faltan = objetivo - len(claves_train)
    return claves_train + [rng.choice(claves_train) for _ in range(faltan)]


def calcular_pesos_clase(manifiesto_train: list[dict], n_especies: int) -> list[float]:
    """Peso por especie = total_train / (n_especies * frecuencia_en_train).

    Inversamente proporcional a la frecuencia: una especie con pocas imágenes en
    train pesa más en la pérdida de `fase_4_transfer_learning.py` sin necesidad
    de inflar el manifiesto más allá de lo estadísticamente razonable.
    """
    conteo = defaultdict(int)
    for entrada in manifiesto_train:
        conteo[entrada["idx_especie"]] += 1
    total = len(manifiesto_train)
    pesos = [1.0] * n_especies
    for idx, freq in conteo.items():
        if freq:
            pesos[idx] = total / (n_especies * freq)
    return pesos


def construir(
    raiz: Path,
    tope_obs: int,
    proporciones: tuple[float, float, float],
    semilla: int,
    lista_negra: set[str],
    fusiones: dict[str, str],
):
    familias, generos, especies = vocabularios()
    idx_familia = {f: i for i, f in enumerate(familias)}
    idx_genero = {g: i for i, g in enumerate(generos)}
    idx_especie = {e: i for i, e in enumerate(especies)}

    manifiesto = {"train": [], "val": [], "test": []}
    informe = []
    # Tamaño de train que tendría cualquier especie con el cupo completo (tope_obs
    # individuos, reparto estándar) — el objetivo de relleno para especies escasas.
    train_esperado = len(repartir(list(range(tope_obs)), proporciones)["train"])

    for especie in especies:
        imagenes = descubrir_imagenes(raiz, especie, lista_negra)
        if not imagenes:
            informe.append((especie, 0, 0, 0, 0, 0, "SIN IMÁGENES"))
            continue

        grupos = agrupar_por_individuo(imagenes, fusiones)
        claves = sorted(grupos)
        total_obs = len(claves)

        # Semilla por especie: recortar siempre al mismo subconjunto entre corridas.
        random.Random(f"{semilla}:{especie}").shuffle(claves)
        claves = claves[:tope_obs]

        reparto = repartir(claves, proporciones)
        n_train_real = len(reparto["train"])
        reparto["train"] = oversamplear_train(reparto["train"], train_esperado, f"{semilla}:{especie}:oversample")
        n_repeticiones = len(reparto["train"]) - n_train_real

        conteo = {}
        for particion, claves_particion in reparto.items():
            vistas = defaultdict(int)
            for clave in claves_particion:
                repeticion = vistas[clave]
                vistas[clave] += 1
                for ruta in grupos[clave]:
                    manifiesto[particion].append(
                        {
                            "ruta": str(ruta.relative_to(raiz)).replace("\\", "/"),
                            "grupo": f"{especie}::{clave}",
                            "especie": especie,
                            "genero": genero_de(especie),
                            "familia": familia_de(especie),
                            "idx_especie": idx_especie[especie],
                            "idx_genero": idx_genero[genero_de(especie)],
                            "idx_familia": idx_familia[familia_de(especie)],
                            "aumentada": repeticion > 0,
                        }
                    )
            conteo[particion] = len(claves_particion)

        aviso = ""
        if n_repeticiones > 0:
            mult = len(reparto["train"]) / n_train_real
            aviso = f"train {n_train_real} reales -> {len(reparto['train'])} ({mult:.0f}x, augmentación agresiva)"
        elif total_obs < 70:
            aviso = f"solo {total_obs} obs"
        informe.append(
            (
                especie,
                total_obs,
                len(claves),
                conteo["train"],
                conteo["val"],
                conteo["test"],
                aviso,
            )
        )

    pesos_clase = calcular_pesos_clase(manifiesto["train"], len(especies))
    meta = {
        "raiz": str(raiz),
        "tope_obs_por_especie": tope_obs,
        "oversampling_multiplicador_maximo": MULTIPLICADOR_OVERSAMPLING_MAXIMO,
        "proporciones": list(proporciones),
        "semilla": semilla,
        "agrupacion": "obs_id de iNaturalist extraído del nombre de archivo",
        "variante_entrada": "A: imagen completa (el recorte segmentado se descartó, ver experimento de control)",
        "familias": familias,
        "generos": generos,
        "especies": especies,
        "pesos_clase_especie": pesos_clase,
    }
    return meta, manifiesto, informe


def verificar_sin_fuga(manifiesto: dict) -> list[str]:
    pertenencia = defaultdict(set)
    for particion, entradas in manifiesto.items():
        for entrada in entradas:
            pertenencia[entrada["grupo"]].add(particion)
    return [g for g, p in pertenencia.items() if len(p) > 1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raiz", type=Path, default=Path(r"D:\Anura\data dirty"))
    parser.add_argument("--tope-obs", type=int, default=70)
    parser.add_argument("--salida", type=Path, default=Path(r"D:\Anura\training\manifiesto.json"))
    parser.add_argument("--semilla", type=int, default=27)
    parser.add_argument("--proporciones", type=float, nargs=3, default=[0.70, 0.15, 0.15])
    parser.add_argument(
        "--lista-negra", type=Path, default=Path(r"D:\Anura\training\lista_negra.json")
    )
    parser.add_argument(
        "--fusiones", type=Path, default=Path(r"D:\Anura\training\individuos_fusionar.json"),
        help="Clusters de obs_id que son el mismo individuo (detectados por hash perceptual)"
    )
    args = parser.parse_args()

    lista_negra = cargar_lista_negra(args.lista_negra)
    if lista_negra:
        print(f"Excluyendo {len(lista_negra)} imágenes de la lista negra (validar_integridad.py)\n")

    fusiones = cargar_fusiones(args.fusiones)
    if fusiones:
        n_clusters = len(set(fusiones.values()))
        print(f"Fusionando {len(fusiones)} obs_id en {n_clusters} individuos reales (duplicados entre observaciones distintas)\n")

    meta, manifiesto, informe = construir(
        args.raiz, args.tope_obs, tuple(args.proporciones), args.semilla, lista_negra, fusiones
    )

    print(f"{'ESPECIE':<30}{'OBS':>6}{'USADAS':>8}{'TRAIN':>7}{'VAL':>5}{'TEST':>6}  AVISO")
    print("-" * 78)
    for fila in informe:
        print(f"{fila[0]:<30}{fila[1]:>6}{fila[2]:>8}{fila[3]:>7}{fila[4]:>5}{fila[5]:>6}  {fila[6]}")

    fugas = verificar_sin_fuga(manifiesto)
    print("-" * 78)
    for particion in ("train", "val", "test"):
        grupos = len({e["grupo"] for e in manifiesto[particion]})
        print(f"{particion:<8} {len(manifiesto[particion]):>6} imágenes  {grupos:>5} individuos")
    print(f"\nGrupos repartidos entre particiones (debe ser 0): {len(fugas)}")
    pesos = meta["pesos_clase_especie"]
    print(f"Class weights en train (min={min(pesos):.2f}, max={max(pesos):.2f}, ratio={max(pesos)/min(pesos):.1f}x)")
    if fugas:
        raise SystemExit(f"FUGA DETECTADA en {len(fugas)} grupos: {fugas[:5]}")

    args.salida.parent.mkdir(parents=True, exist_ok=True)
    args.salida.write_text(
        json.dumps({"meta": meta, "particiones": manifiesto}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"\nManifiesto escrito en {args.salida}")


if __name__ == "__main__":
    main()
