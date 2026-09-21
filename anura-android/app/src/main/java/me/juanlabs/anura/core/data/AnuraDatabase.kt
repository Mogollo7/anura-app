package me.juanlabs.anura.core.data

import androidx.room.Dao
import androidx.room.Database
import androidx.room.Entity
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.PrimaryKey
import androidx.room.Query
import androidx.room.RoomDatabase

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
    entities = [SnapshotEntity::class],
    version = 1,
    exportSchema = false,
)
abstract class AnuraDatabase : RoomDatabase() {
    abstract fun snapshotDao(): SnapshotDao
}
