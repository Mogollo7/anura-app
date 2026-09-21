package me.juanlabs.anura.feature.capture

import android.annotation.SuppressLint
import android.content.Context
import android.media.AudioFormat
import android.media.AudioRecord
import android.media.MediaRecorder
import android.os.Handler
import android.os.Looper
import androidx.annotation.RequiresPermission
import androidx.compose.runtime.Composable
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableFloatStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.platform.LocalContext
import java.io.File
import java.io.RandomAccessFile
import java.nio.ByteBuffer
import java.nio.ByteOrder
import java.util.concurrent.atomic.AtomicBoolean
import kotlin.math.min

internal class LiveAudioCaptureHandle {
    @Volatile
    var file: File? = null
}

@SuppressLint("MissingPermission")
@Composable
internal fun rememberMicWaveform(
    active: Boolean,
    paused: Boolean = false,
    barCount: Int = WaveformBarCount,
    capture: LiveAudioCaptureHandle? = null,
): LiveWaveformFrame {
    val context = LocalContext.current
    var amplitudes by remember { mutableStateOf(List(barCount) { 0f }) }
    var level by remember { mutableFloatStateOf(0f) }
    var dominantKhz by remember { mutableFloatStateOf(2.4f) }
    val pausedFlag = remember { AtomicBoolean(false) }
    pausedFlag.set(paused)
    DisposableEffect(active, barCount, capture) {
        if (!active) {
            onDispose { }
        } else {
            val recorder = runCatching { buildAudioRecord() }.getOrNull()
            if (recorder == null) {
                onDispose { }
            } else {
                val running = AtomicBoolean(true)
                val scroll = ScrollingWaveformBuffer(barCount)
                val main = Handler(Looper.getMainLooper())
                val writer = runCatching {
                    val dir = File(context.filesDir, "anura_media/audio").apply { mkdirs() }
                    val file = File(dir, "clip_${System.currentTimeMillis()}.wav")
                    capture?.file = file
                    WavPcmWriter(file, CapturePcmSampleRate)
                }.getOrNull()
                recorder.startRecording()
                val worker = Thread {
                    val pcm = ShortArray(1_024)
                    while (running.get()) {
                        val read = recorder.read(pcm, 0, pcm.size)
                        if (read <= 0) continue
                        if (pausedFlag.get()) continue
                        writer?.write(pcm, read)
                        val rms = boostWaveform(pcmRms(pcm, read))
                        scroll.push(rms)
                        val snapshot = scroll.snapshot()
                        main.post {
                            amplitudes = snapshot
                            level = rms
                            dominantKhz = (0.4f + rms * 7.6f).coerceIn(0.4f, 8f)
                        }
                    }
                }.apply { name = "anura-mic-wave"; start() }
                onDispose {
                    running.set(false)
                    runCatching { recorder.stop() }
                    recorder.release()
                    worker.join(400)
                    writer?.finish()
                }
            }
        }
    }
    return LiveWaveformFrame(amplitudes, level, dominantKhz)
}

@RequiresPermission(android.Manifest.permission.RECORD_AUDIO)
private fun buildAudioRecord(): AudioRecord? {
    val minBuffer = AudioRecord.getMinBufferSize(
        CapturePcmSampleRate,
        AudioFormat.CHANNEL_IN_MONO,
        AudioFormat.ENCODING_PCM_16BIT,
    )
    if (minBuffer <= 0) return null
    return runCatching {
        AudioRecord(
            MediaRecorder.AudioSource.MIC,
            CapturePcmSampleRate,
            AudioFormat.CHANNEL_IN_MONO,
            AudioFormat.ENCODING_PCM_16BIT,
            minBuffer * 2,
        ).takeIf { it.state == AudioRecord.STATE_INITIALIZED }
    }.getOrNull()
}

internal const val CapturePcmSampleRate = 44_100

internal class WavPcmWriter(
    val file: File,
    private val sampleRate: Int,
) {
    private val raf = RandomAccessFile(file, "rw")
    private var dataBytes = 0

    init {
        raf.setLength(0)
        raf.write(ByteArray(44))
    }

    @Synchronized
    fun write(samples: ShortArray, count: Int) {
        val n = min(count, samples.size)
        val bytes = ByteBuffer.allocate(n * 2).order(ByteOrder.LITTLE_ENDIAN)
        for (i in 0 until n) bytes.putShort(samples[i])
        raf.write(bytes.array(), 0, n * 2)
        dataBytes += n * 2
    }

    @Synchronized
    fun finish() {
        raf.seek(0)
        val header = ByteBuffer.allocate(44).order(ByteOrder.LITTLE_ENDIAN)
        header.put("RIFF".toByteArray())
        header.putInt(36 + dataBytes)
        header.put("WAVE".toByteArray())
        header.put("fmt ".toByteArray())
        header.putInt(16)
        header.putShort(1)
        header.putShort(1)
        header.putInt(sampleRate)
        header.putInt(sampleRate * 2)
        header.putShort(2)
        header.putShort(16)
        header.put("data".toByteArray())
        header.putInt(dataBytes)
        raf.write(header.array())
        raf.close()
    }
}
