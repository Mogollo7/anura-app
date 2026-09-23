package me.juanlabs.anura.core.data

import android.database.sqlite.SQLiteDatabase

/**
 * Coordenadas reales de ocurrencia (GBIF, tabla `occurrence_points` horneada en el paquete
 * regional — ver `LocalPackageCatalog` v1.1.0) para pintar el mapa de distribución de una
 * ficha técnica. Lectura de tabla plana, igual que [NearbySpecies].
 */
object SpeciesOccurrences {
    /** Hasta 300 puntos por especie ya vienen capados en el paquete; acá se leen todos los
     * de [taxonIds] tal cual. Lista vacía sin paquete, sin tabla, o `taxonIds` vacío — nunca
     * lanza. */
    fun pointsFor(packagePath: String, taxonIds: List<String>): List<Pair<Double, Double>> {
        if (taxonIds.isEmpty()) return emptyList()
        return runCatching {
            SQLiteDatabase.openDatabase(packagePath, null, SQLiteDatabase.OPEN_READONLY).use { db ->
                val placeholders = taxonIds.joinToString(",") { "?" }
                db.rawQuery(
                    "select latitude, longitude from occurrence_points where taxon_id in ($placeholders)",
                    taxonIds.toTypedArray(),
                ).use { c ->
                    buildList {
                        while (c.moveToNext()) add(c.getDouble(0) to c.getDouble(1))
                    }
                }
            }
        }.getOrDefault(emptyList())
    }
}
