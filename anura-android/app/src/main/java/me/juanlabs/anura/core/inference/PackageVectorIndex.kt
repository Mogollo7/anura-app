package me.juanlabs.anura.core.inference

import android.content.Context
import androidx.sqlite.SQLiteConnection
import androidx.sqlite.driver.bundled.BundledSQLiteDriver
import androidx.sqlite.driver.bundled.SQLITE_OPEN_READONLY
import java.io.File
import java.nio.ByteBuffer
import java.nio.ByteOrder

/**
 * Búsqueda k-NN sobre la tabla `vec_references` (vec0, coseno) de un paquete regional instalado,
 * con la extensión sqlite-vec 0.1.9 (la misma versión que construyó el paquete en PC).
 */
class PackageVectorIndex private constructor(
    val packagePath: String,
    private val connection: SQLiteConnection,
) : AutoCloseable {
    private class Taxon(val scientificName: String, val genus: String, val family: String)

    private val taxa: Map<String, Taxon> =
        connection.prepare("select taxon_id, scientific_name, genus, family from taxa").use { st ->
            buildMap { while (st.step()) put(st.getText(0), Taxon(st.getText(1), st.getText(2), st.getText(3))) }
        }

    fun nearest(embedding: FloatArray, k: Int): List<Neighbor> {
        val blob = ByteBuffer.allocate(embedding.size * 4).order(ByteOrder.LITTLE_ENDIAN)
            .apply { embedding.forEach { putFloat(it) } }.array()
        return connection.prepare(
            "select taxon_id, distance from vec_references where embedding match ? and k = ? order by distance",
        ).use { st ->
            st.bindBlob(1, blob)
            st.bindLong(2, k.toLong())
            buildList {
                while (st.step()) {
                    val taxonId = st.getText(0)
                    val taxon = taxa[taxonId]
                    add(Neighbor(taxonId, taxon?.scientificName ?: taxonId, st.getDouble(1), taxon?.genus.orEmpty(), taxon?.family.orEmpty()))
                }
            }
        }
    }

    /**
     * Modelo de rechazo Open Set del paquete (tabla `open_set_model`). Un paquete sin la tabla o sin
     * fila —los compilados antes de que el servidor lo incluyera— devuelve [PackageOpenSet.Unavailable].
     */
    fun readOpenSet(): PackageOpenSet {
        class Row(val format: String, val sha256: String, val data: ByteArray)
        val row = runCatching {
            connection.prepare("select format, sha256, data from open_set_model where id = 1").use { st ->
                if (st.step()) Row(st.getText(0), st.getText(1), st.getBlob(2)) else null
            }
        }.getOrElse { return PackageOpenSet.Unavailable("El paquete no trae modelo de rechazo") }
            ?: return PackageOpenSet.Unavailable("El paquete no trae modelo de rechazo")
        return PackageOpenSets.decode(row.format, row.sha256, row.data, taxa.keys)
    }

    fun vecVersion(): String = connection.prepare("select vec_version()").use { st -> st.step(); st.getText(0) }

    /**
     * Zona geográfica de una coordenada (celda 0.25°, redondeo al par más cercano — igual regla
     * que `package_info.cell_rule` y `pipeline_dataset/paquetes_zonales.py`). Null si la celda no
     * tiene zona asignada en este paquete (fuera de cobertura): la decisión visual no se descarta,
     * solo no recibe ajuste geográfico.
     */
    fun zoneIdFor(latitude: Double, longitude: Double): String? {
        val row = Math.rint(latitude / CellSizeDegrees).toLong()
        val col = Math.rint(longitude / CellSizeDegrees).toLong()
        return connection.prepare("select zone_id from grid_cells where row = ? and col = ?").use { st ->
            st.bindLong(1, row)
            st.bindLong(2, col)
            if (st.step()) st.getText(0) else null
        }
    }

    /**
     * Prior geográfico P(especie|zona) horneado en el paquete (`pipeline_dataset/paquetes_zonales.py`,
     * validado con control de fuga: Top-1 62.9%→72.5% sobre 167 imágenes de prueba —
     * `COLOMBIA_ANURA/ANTIOQUIA/reports/packages_v1.0.0.json`). Especies sin fila propia en la zona
     * usan `p_unobserved` (Laplace), nunca cero. Null si la zona no existe en este paquete.
     */
    fun zonePrior(zoneId: String): GeoZonePrior? {
        val (weight, unobserved) = connection.prepare(
            "select prior_weight, p_unobserved from zone_prior_meta where zone_id = ?",
        ).use { st ->
            st.bindText(1, zoneId)
            if (!st.step()) return null
            st.getDouble(0) to st.getDouble(1)
        }
        val byTaxon = connection.prepare("select taxon_id, p from zone_prior where zone_id = ?").use { st ->
            st.bindText(1, zoneId)
            buildMap { while (st.step()) put(st.getText(0), st.getDouble(1)) }
        }
        return GeoZonePrior(zoneId, weight, unobserved, byTaxon)
    }

    /**
     * Prior de clima por especie (`weather_prior`, ver `evaluation/geo_weather_v1/`, control de
     * fuga: Top-1 61.2%→65.1%, n=129). Especies sin fila (visual pero poca cobertura de clima en
     * train) quedan fuera del mapa — sin ajuste, nunca penalizadas. Null si el paquete no trae la
     * tabla (paquetes más antiguos sin esta hornada).
     */
    fun weatherPrior(): Map<String, WeatherStats>? = runCatching {
        connection.prepare("select taxon_id, n, temp_mean, temp_std, hum_mean, hum_std from weather_prior").use { st ->
            buildMap { while (st.step()) put(st.getText(0), WeatherStats(st.getLong(1).toInt(), st.getDouble(2), st.getDouble(3), st.getDouble(4), st.getDouble(5))) }
        }
    }.getOrNull()

    fun weatherPriorWeight(): Double? = runCatching {
        connection.prepare("select value from weather_prior_meta where key = 'weight'").use { st ->
            if (st.step()) st.getText(0).toDouble() else null
        }
    }.getOrNull()

    override fun close() = connection.close()

    companion object {
        private const val ExtensionLibrary = "libvec0.so"
        private const val EntryPoint = "sqlite3_vec_init"
        private const val CellSizeDegrees = 0.25

        fun open(context: Context, packagePath: String): PackageVectorIndex {
            val library = File(context.applicationInfo.nativeLibraryDir, ExtensionLibrary)
            check(library.exists()) { "Falta la extensión sqlite-vec para esta ABI (${library.path})" }
            val driver = BundledSQLiteDriver().apply { addExtension(library.absolutePath, EntryPoint) }
            return PackageVectorIndex(packagePath, driver.open(packagePath, SQLITE_OPEN_READONLY))
        }
    }
}
