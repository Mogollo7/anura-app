package me.juanlabs.anura.core.data

import android.database.sqlite.SQLiteDatabase

/**
 * Especies del catálogo más probables cerca de una coordenada, usando el mismo prior de zona
 * horneado en el paquete regional (`zone_prior`/`grid_cells`, ver
 * `PackageVectorIndex.zoneIdFor`/`zonePrior` en `core/inference`) — lectura de tablas planas,
 * sin necesitar la extensión sqlite-vec (a diferencia de la identificación real).
 */
object NearbySpecies {
    private const val CellSizeDegrees = 0.25

    /**
     * Hasta [limit] `taxon_id` ordenados por P(especie|zona) descendente. Lista vacía sin
     * ubicación, sin zona para esa celda, o si el paquete no trae las tablas — nunca lanza.
     */
    fun rankedTaxonIds(packagePath: String, latitude: Double, longitude: Double, limit: Int): List<String> =
        runCatching {
            SQLiteDatabase.openDatabase(packagePath, null, SQLiteDatabase.OPEN_READONLY).use { db ->
                val row = Math.rint(latitude / CellSizeDegrees).toLong()
                val col = Math.rint(longitude / CellSizeDegrees).toLong()
                val zoneId = db.rawQuery(
                    "select zone_id from grid_cells where row = ? and col = ?",
                    arrayOf(row.toString(), col.toString()),
                ).use { c -> if (c.moveToFirst()) c.getString(0) else null } ?: return@use emptyList()
                db.rawQuery(
                    "select taxon_id from zone_prior where zone_id = ? order by p desc limit ?",
                    arrayOf(zoneId, limit.toString()),
                ).use { c -> buildList { while (c.moveToNext()) add(c.getString(0)) } }
            }
        }.getOrDefault(emptyList())
}
