package me.juanlabs.anura

import android.app.Application
import me.juanlabs.anura.core.data.AnuraRepository

/**
 * Punto de entrada de proceso de ANURA.
 *
 * El repositorio local (Room + archivos en filesDir) se crea aquí para que
 * sobreviva a la Activity y pueda hidratar el prototipo funcional. Sin Hilt
 * todavía: un único holder de aplicación es suficiente mientras no haya
 * grafo de dependencias real.
 */
class AnuraApplication : Application() {
    lateinit var repository: AnuraRepository
        private set

    override fun onCreate() {
        super.onCreate()
        repository = AnuraRepository.create(this)
    }
}
