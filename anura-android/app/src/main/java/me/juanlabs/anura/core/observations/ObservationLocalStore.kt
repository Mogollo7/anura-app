package me.juanlabs.anura.core.observations

import androidx.room.ColumnInfo
import androidx.room.Dao
import androidx.room.Entity
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.PrimaryKey
import androidx.room.Query
import kotlinx.serialization.builtins.ListSerializer
import kotlinx.serialization.json.Json

/** Fila Room de `observacion_local` (migración 1→2 en [me.juanlabs.anura.core.data.AnuraDatabase]). */
@Entity(tableName = "observacion_local")
data class ObservacionLocalEntity(
    @PrimaryKey val id: String,
    val visibilidad: String,
    val sync: String,
    @ColumnInfo(name = "fotos_json") val fotosJson: String,
    @ColumnInfo(name = "visibilidad_cambiada_en") val visibilidadCambiadaEn: Long,
) {
    fun toModel() = ObservacionLocal(
        id = id,
        visibilidad = Visibilidad.entries.first { it.wire == visibilidad },
        sync = EstadoSync.valueOf(sync),
        fotos = json.decodeFromString(ListSerializer(FotoLocal.serializer()), fotosJson),
        visibilidadCambiadaEn = visibilidadCambiadaEn,
    )

    companion object {
        private val json = Json { ignoreUnknownKeys = true }

        fun from(o: ObservacionLocal) = ObservacionLocalEntity(
            id = o.id,
            visibilidad = o.visibilidad.wire,
            sync = o.sync.name,
            fotosJson = json.encodeToString(ListSerializer(FotoLocal.serializer()), o.fotos),
            visibilidadCambiadaEn = o.visibilidadCambiadaEn,
        )
    }
}

@Dao
interface ObservacionLocalDao {
    @Query("SELECT * FROM observacion_local")
    suspend fun todas(): List<ObservacionLocalEntity>

    @Query("SELECT * FROM observacion_local WHERE id = :id")
    suspend fun porId(id: String): ObservacionLocalEntity?

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun guardar(entity: ObservacionLocalEntity)

    @Query("DELETE FROM observacion_local WHERE id = :id")
    suspend fun borrar(id: String)
}

/** Almacén local que usa [ObservationSync]; interfaz para probar sin Room ni disco. */
interface ObservationLocalStore {
    suspend fun todas(): List<ObservacionLocal>
    suspend fun obtener(id: String): ObservacionLocal?
    suspend fun guardar(obs: ObservacionLocal)

    /** Borra la fila y los archivos de las fotos. */
    suspend fun borrarConArchivos(id: String)
}

class RoomObservationLocalStore(private val dao: ObservacionLocalDao) : ObservationLocalStore {
    override suspend fun todas() = dao.todas().map { it.toModel() }
    override suspend fun obtener(id: String) = dao.porId(id)?.toModel()
    override suspend fun guardar(obs: ObservacionLocal) = dao.guardar(ObservacionLocalEntity.from(obs))

    override suspend fun borrarConArchivos(id: String) {
        val obs = dao.porId(id)?.toModel() ?: return
        // Primero la fila marcada como sincronizada ya está en la base; se borran archivos y luego la fila.
        // Si la app muere entre los dos pasos, la fila sigue y la siguiente reconciliación repite el borrado.
        obs.fotos.forEach { java.io.File(it.ruta).delete() }
        dao.borrar(id)
    }
}
