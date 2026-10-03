"""Título en español a partir de un nombre en mayúsculas del DANE (MPIO_CNMBR/DPTO_CNMBR).

`str.title()` pone en mayúscula toda palabra, incluidas preposiciones y artículos que en
español van en minúscula dentro de un nombre ("San Andrés DE Cuerquía"); esto los baja,
excepto si son la primera palabra. No inventa nada: es una regla de capitalización fija, el
nombre en sí sigue siendo el que trae el DANE.
"""
import re

MINUSCULAS = {"de", "del", "la", "las", "los", "y"}


def titulo_espanol(nombre: str) -> str:
    palabras = nombre.title().split(" ")
    return " ".join(p if i == 0 or p.lower() not in MINUSCULAS else p.lower() for i, p in enumerate(palabras))
