package me.juanlabs.anura.core.data

import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test
import java.io.File

class ReconcilePackagesTest {
    // Id de un paquete de subregión tal como lo publica el servidor ("<DANE>.<CLAVE>").
    private val packageId = "05.VALLE_DE_ABURRA"
    private val catalog = listOf(packageId)

    @Test
    fun legacySnapshotWithFictionalZones_getsAntioquiaAndDropsOldZones() {
        val stored = listOf("EJE", "CHOCO", "AMAZONIA", "SIERRA").map {
            RegionalPackageRecord(it, RegionalPackageStatus.Available)
        }

        val result = reconcilePackages(stored, catalog)

        assertEquals(listOf(RegionalPackageRecord(packageId, RegionalPackageStatus.Available)), result)
    }

    @Test
    fun installedAndActivePackage_isKeptUntouched() {
        val installed = RegionalPackageRecord(
            id = packageId,
            status = RegionalPackageStatus.Installed,
            progress = 1f,
            version = "1.0.0",
            active = true,
            localPath = "/data/packages/05.VALLE_DE_ABURRA/1/package.sqlite",
        )

        assertEquals(listOf(installed), reconcilePackages(listOf(installed), catalog))
    }

    @Test
    fun downloadInterruptedByProcessDeath_isResetToAvailable() {
        val stuck = RegionalPackageRecord(packageId, RegionalPackageStatus.Downloading, progress = 0.4f)

        val result = reconcilePackages(listOf(stuck), catalog).single()

        assertEquals(RegionalPackageStatus.Available, result.status)
        assertEquals(0f, result.progress)
    }

    @Test
    fun priorVerifiedInstallRemainsUsableWhileUpdateIsDownloadingOrFailed() {
        val file = File.createTempFile("package", ".sqlite")
        try {
            file.writeBytes(byteArrayOf(1, 2, 3))
            listOf(RegionalPackageStatus.Downloading, RegionalPackageStatus.Error, RegionalPackageStatus.Available).forEach { status ->
                val prior = RegionalPackageRecord(
                    id = packageId,
                    status = status,
                    version = "1",
                    sha256 = "old-sha256",
                    active = true,
                    localPath = file.absolutePath,
                )
                assertTrue("$status debe conservar el archivo previamente verificado", prior.hasUsableLocalInstall())
            }
        } finally {
            file.delete()
        }
    }
}
