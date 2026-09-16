package me.juanlabs.anura

import android.app.Application

/**
 * Punto de entrada de proceso de ANURA.
 *
 * Sin Hilt en esta fase: no hay todavía ningún `ViewModel` ni repositorio real que
 * inyectar (eso llega con los contratos de dominio y sus implementaciones fake/reales,
 * bloque B4 en adelante del plan de implementación). Añadir el módulo de DI antes de
 * tener algo que inyectar sería dependencia sin justificación (§20).
 */
class AnuraApplication : Application()
