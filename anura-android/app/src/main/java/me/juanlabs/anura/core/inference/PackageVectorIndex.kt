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

    fun vecVersion(): String = connection.prepare("select vec_version()").use { st -> st.step(); st.getText(0) }

    override fun close() = connection.close()

    companion object {
        private const val ExtensionLibrary = "libvec0.so"
        private const val EntryPoint = "sqlite3_vec_init"

        fun open(context: Context, packagePath: String): PackageVectorIndex {
            val library = File(context.applicationInfo.nativeLibraryDir, ExtensionLibrary)
            check(library.exists()) { "Falta la extensión sqlite-vec para esta ABI (${library.path})" }
            val driver = BundledSQLiteDriver().apply { addExtension(library.absolutePath, EntryPoint) }
            return PackageVectorIndex(packagePath, driver.open(packagePath, SQLITE_OPEN_READONLY))
        }
    }
}
