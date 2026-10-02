package me.juanlabs.anura.core.notifications

import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.content.Context
import android.content.Intent
import android.net.Uri
import android.os.Build
import androidx.core.app.NotificationCompat
import androidx.core.app.NotificationManagerCompat
import androidx.core.content.ContextCompat
import me.juanlabs.anura.R
import me.juanlabs.anura.core.data.AppNotification
import me.juanlabs.anura.core.data.cuerpoVisible
import me.juanlabs.anura.core.data.tokenPublico

/**
 * Notificación real del sistema para un aviso (`AppNotification`, C5) — hasta ahora los avisos
 * solo vivían dentro de la app (`NotificationsScreen`, "sin FCM todavía"). Sin servidor push
 * (Firebase Cloud Messaging no está configurado, ver `README`/decisión del equipo): esto se
 * dispara cuando la app hidrata avisos nuevos, ya sea en primer plano
 * (`AnuraRepository.hydrateNotifications`, llamado desde `AnuraScaffold`/`NotificationsScreen`)
 * o en segundo plano vía `AvisosPollWorker` (WorkManager, cada 15 min como mínimo permitido).
 *
 * Contenido expandible: la barra de notificaciones muestra título + una línea de resumen；
 * `BigTextStyle` deja expandirla (mantener presionado / deslizar con dos dedos) para el cuerpo
 * completo del aviso sin abrir la app. Tocarla sí abre la app en la pantalla de Avisos
 * (`anura://notifications`, ver `NotificationDeepLink.kt`) para marcarlo leído y ver más
 * contexto si lo hay (p. ej. "Nuevo paquete disponible: Antioquia actualizado").
 */
object AnuraNotifications {
    private const val CHANNEL_ID = "avisos"

    fun ensureChannel(context: Context) {
        if (Build.VERSION.SDK_INT < Build.VERSION_CODES.O) return
        val manager = context.getSystemService(NotificationManager::class.java) ?: return
        if (manager.getNotificationChannel(CHANNEL_ID) != null) return
        val channel = NotificationChannel(
            CHANNEL_ID,
            context.getString(R.string.notification_channel_avisos_name),
            NotificationManager.IMPORTANCE_DEFAULT,
        ).apply {
            description = context.getString(R.string.notification_channel_avisos_description)
        }
        manager.createNotificationChannel(channel)
    }

    private fun canNotify(context: Context): Boolean {
        if (Build.VERSION.SDK_INT < Build.VERSION_CODES.TIRAMISU) return true
        return ContextCompat.checkSelfPermission(
            context,
            android.Manifest.permission.POST_NOTIFICATIONS,
        ) == android.content.pm.PackageManager.PERMISSION_GRANTED
    }

    /** Materializa un aviso ya recibido como notificación de la barra de estado. No hace nada
     * si el usuario no concedió el permiso (Android 13+) — la app sigue mostrándolo en la lista
     * in-app de todas formas. */
    fun show(context: Context, notification: AppNotification) {
        if (!canNotify(context)) return
        ensureChannel(context)

        val openUri = Uri.parse("anura://notifications").buildUpon()
            .appendPath(notification.id)
            .build()
        val openIntent = Intent(Intent.ACTION_VIEW, openUri).apply {
            setPackage(context.packageName)
        }
        val pendingIntent = PendingIntent.getActivity(
            context,
            notification.id.hashCode(),
            openIntent,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE,
        )

        val full = notification.cuerpoVisible().ifBlank { "Toca para ver el detalle del aviso." }
        val summary = full.lineSequence().first().take(140)
        val builder = NotificationCompat.Builder(context, CHANNEL_ID)
            .setSmallIcon(R.drawable.ic_notification)
            .setContentTitle(notification.title)
            .setContentText(summary)
            .setStyle(
                NotificationCompat.BigTextStyle()
                    .bigText(full)
                    .setSummaryText("Anura"),
            )
            .setPriority(NotificationCompat.PRIORITY_DEFAULT)
            .setAutoCancel(true)
            .setContentIntent(pendingIntent)

        notification.tokenPublico()?.let { token ->
            val verUri = Uri.parse("anura://notifications").buildUpon()
                .appendPath(notification.id)
                .appendQueryParameter("completo", token)
                .build()
            val ver = Intent(Intent.ACTION_VIEW, verUri).apply {
                setPackage(context.packageName)
            }
            val verPending = PendingIntent.getActivity(
                context,
                notification.id.hashCode() xor 0x5A17,
                ver,
                PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE,
            )
            builder.addAction(0, context.getString(R.string.notifications_open_full), verPending)
        }

        runCatching {
            NotificationManagerCompat.from(context).notify(notification.id.hashCode(), builder.build())
        }
    }
}
