package me.juanlabs.anura.core.notifications

import android.content.Context
import androidx.work.BackoffPolicy
import androidx.work.Constraints
import androidx.work.CoroutineWorker
import androidx.work.ExistingPeriodicWorkPolicy
import androidx.work.NetworkType
import androidx.work.PeriodicWorkRequestBuilder
import androidx.work.WorkManager
import androidx.work.WorkerParameters
import java.util.concurrent.TimeUnit
import me.juanlabs.anura.core.data.AnuraRepository
import me.juanlabs.anura.core.data.ContentCatalog

/**
 * Sin FCM (no hay proyecto de Firebase configurado): esto es lo que hace que un aviso nuevo
 * llegue como notificación real aunque la app esté cerrada — un `CoroutineWorker` periódico que
 * pide `GET /api/notifications` y deja que `AnuraRepository.hydrateNotifications` dispare
 * `AnuraNotifications.show` para lo que sea nuevo. 15 minutos es el mínimo que WorkManager
 * permite para trabajo periódico; no hay forma de bajar de ahí sin push real.
 */
class AvisosPollWorker(context: Context, params: WorkerParameters) : CoroutineWorker(context, params) {
    override suspend fun doWork(): Result {
        if (!AnuraRepository.isInitialized) return Result.retry()
        val repository = AnuraRepository.instance
        // Room carga la sesión en segundo plano. Sin esperarla, el snapshot está vacío y
        // cada corrida volvería a notificar avisos que la persona ya vio.
        repository.awaitHydrated()
        runCatching { ContentCatalog.sync(applicationContext) }
        if (repository.snapshot.session.authToken == null) return Result.success()
        return runCatching {
            when (val report = repository.reportDevice(applicationContext as android.app.Application)) {
                is me.juanlabs.anura.core.data.DeviceReportResult.Unauthorized,
                me.juanlabs.anura.core.data.DeviceReportResult.Suspended,
                -> return@runCatching Result.success()
                is me.juanlabs.anura.core.data.DeviceReportResult.Ok -> {
                    if (!repository.snapshot.deviceBlocked) repository.syncPendingObservations()
                    if (report.sincronizar && !report.bloqueado) repository.ackDeviceSync()
                }
                me.juanlabs.anura.core.data.DeviceReportResult.Failed -> {
                    if (!repository.snapshot.deviceBlocked) repository.syncPendingObservations()
                }
            }
            repository.hydrateNotifications(applicationContext)
            Result.success()
        }.getOrElse { Result.retry() }
    }

    companion object {
        private const val UniqueWorkName = "anura-avisos-poll"

        fun schedule(context: Context) {
            val constraints = Constraints.Builder()
                .setRequiredNetworkType(NetworkType.CONNECTED)
                .build()
            val request = PeriodicWorkRequestBuilder<AvisosPollWorker>(15, TimeUnit.MINUTES)
                .setConstraints(constraints)
                .setBackoffCriteria(BackoffPolicy.EXPONENTIAL, 30, TimeUnit.SECONDS)
                .build()
            WorkManager.getInstance(context).enqueueUniquePeriodicWork(
                UniqueWorkName,
                ExistingPeriodicWorkPolicy.KEEP,
                request,
            )
        }
    }
}
