package me.juanlabs.anura.core.data

import androidx.room.Dao
import androidx.room.Database
import androidx.room.Entity
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.PrimaryKey
import androidx.room.Query
import androidx.room.RoomDatabase
import androidx.room.migration.Migration
import androidx.sqlite.db.SupportSQLiteDatabase
import me.juanlabs.anura.core.observations.ObservacionLocalDao
import me.juanlabs.anura.core.observations.ObservacionLocalEntity

@Entity(tableName = "anura_snapshot")
data class SnapshotEntity(
    @PrimaryKey val id: Int = 1,
    val payload: String,
)

@Dao
interface SnapshotDao {
    @Query("SELECT * FROM anura_snapshot WHERE id = 1")
    suspend fun load(): SnapshotEntity?

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun save(entity: SnapshotEntity)
}

@Database(
    entities = [SnapshotEntity::class, ObservacionLocalEntity::class],
    version = 2,
    exportSchema = false,
)
abstract class AnuraDatabase : RoomDatabase() {
    abstract fun snapshotDao(): SnapshotDao
    abstract fun observacionLocalDao(): ObservacionLocalDao

    companion object {
        /** Añade `observacion_local` sin tocar `anura_snapshot` (la destructiva borraría el snapshot). */
        val Migration1To2 = object : Migration(1, 2) {
            override fun migrate(db: SupportSQLiteDatabase) {
                db.execSQL(
                    "CREATE TABLE IF NOT EXISTS `observacion_local` (`id` TEXT NOT NULL, `visibilidad` TEXT NOT NULL, " +
                        "`sync` TEXT NOT NULL, `fotos_json` TEXT NOT NULL, `visibilidad_cambiada_en` INTEGER NOT NULL, " +
                        "PRIMARY KEY(`id`))",
                )
            }
        }
    }
}
