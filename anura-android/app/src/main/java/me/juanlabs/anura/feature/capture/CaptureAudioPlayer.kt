package me.juanlabs.anura.feature.capture

import android.content.Context
import android.media.MediaCodec
import android.media.MediaExtractor
import android.media.MediaFormat
import android.media.MediaPlayer
import android.media.audiofx.Visualizer
import android.net.Uri
import android.os.Handler
import android.os.Looper
import androidx.compose.runtime.Composable
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.rememberUpdatedState
import androidx.compose.runtime.mutableFloatStateOf
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.platform.LocalContext
import java.nio.ByteBuffer
import java.nio.ByteOrder
import kotlin.coroutines.cancellation.CancellationException
import kotlin.math.min
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.delay
import kotlinx.coroutines.withContext

internal class DecodedPcm(
    val sampleRate: Int,
    val samples: ShortArray,
) {
    fun rmsAt(positionMs: Int, windowMs: Int = 40): Float {
        if (samples.isEmpty() || sampleRate <= 0) return 0f
        val start = ((positionMs / 1000.0) * sampleRate).toInt().coerceIn(0, samples.lastIndex)
        val window = ((windowMs / 1000.0) * sampleRate).toInt().coerceAtLeast(32)
        val end = min(samples.size, start + window)
        return pcmRms(samples.copyOfRange(start, end), end - start)
    }
}

internal class CaptureAudioPlayer(private val context: Context) {
    private var player: MediaPlayer? = null

    val media: MediaPlayer? get() = player

    fun load(uri: Uri): MediaPlayer? {
        release()
        player = runCatching {
            MediaPlayer().apply {
                setDataSource(context, uri)
                prepare()
            }
        }.getOrNull()
        return player
    }

    fun play() {
        player?.start()
    }

    fun pause() {
        if (player?.isPlaying == true) player?.pause()
    }

    fun seekTo(millis: Int) {
        player?.seekTo(millis)
    }

    fun release() {
        runCatching {
            player?.reset()
            player?.release()
        }
        player = null
    }
}

@Composable
internal fun rememberCaptureAudioPlayer(uri: Uri): CaptureAudioPlayerState {
    val context = LocalContext.current
    val controller = remember(uri) { CaptureAudioPlayer(context) }
    var playing by rememberSaveable(uri) { mutableStateOf(false) }
    var positionMs by remember { mutableIntStateOf(0) }
    var durationMs by remember { mutableIntStateOf(1) }
    var sessionId by remember { mutableIntStateOf(0) }

    DisposableEffect(uri) {
        val player = controller.load(uri)
        durationMs = player?.duration?.coerceAtLeast(1) ?: 1
        sessionId = player?.audioSessionId ?: 0
        player?.setOnCompletionListener {
            playing = false
            positionMs = durationMs
        }
        onDispose {
            playing = false
            controller.release()
        }
    }

    LaunchedEffect(playing, uri) {
        if (playing) {
            controller.play()
            val player = controller.media
            while (playing && player != null) {
                positionMs = player.currentPosition.coerceIn(0, durationMs)
                delay(50)
            }
        } else {
            controller.pause()
        }
    }

    return CaptureAudioPlayerState(
        playing = playing,
        positionMs = positionMs,
        durationMs = durationMs,
        sessionId = sessionId,
        onTogglePlay = { playing = !playing },
        onSeekBy = { delta ->
            val target = (positionMs + delta).coerceIn(0, durationMs)
            controller.seekTo(target)
            positionMs = target
        },
        onStopPlayback = { playing = false },
    )
}

internal data class CaptureAudioPlayerState(
    val playing: Boolean,
    val positionMs: Int,
    val durationMs: Int,
    val sessionId: Int,
    val onTogglePlay: () -> Unit,
    val onSeekBy: (Int) -> Unit,
    val onStopPlayback: () -> Unit,
)

@Composable
internal fun rememberPlaybackWaveform(
    uri: Uri,
    playing: Boolean,
    positionMs: Int,
    sessionId: Int,
    barCount: Int = WaveformBarCount,
): LiveWaveformFrame {
    val context = LocalContext.current
    var amplitudes by remember(uri) { mutableStateOf(List(barCount) { 0f }) }
    var level by remember { mutableFloatStateOf(0f) }
    var dominantKhz by remember { mutableFloatStateOf(2.4f) }
    var pcm by remember(uri) { mutableStateOf<DecodedPcm?>(null) }
    val scroll = remember(uri, barCount) { ScrollingWaveformBuffer(barCount) }

    LaunchedEffect(uri) {
        pcm = withContext(Dispatchers.IO) {
            runCatching { decodePcm(context, uri) }.getOrNull()
        }
    }

    DisposableEffect(sessionId, playing, barCount, uri, pcm) {
        if (!playing || sessionId == 0 || pcm != null) {
            onDispose { }
        } else {
            val visualizer = runCatching {
                Visualizer(sessionId).apply {
                    captureSize = Visualizer.getCaptureSizeRange()[1]
                    val main = Handler(Looper.getMainLooper())
                    setDataCaptureListener(
                        object : Visualizer.OnDataCaptureListener {
                            override fun onWaveFormDataCapture(
                                visualizer: Visualizer?,
                                waveform: ByteArray?,
                                samplingRate: Int,
                            ) {
                                if (waveform == null) return
                                val rms = waveformBytesRms(waveform)
                                scroll.push(rms)
                                val snapshot = scroll.snapshot()
                                main.post {
                                    amplitudes = snapshot
                                    level = rms
                                    dominantKhz = (0.4f + rms * 7.6f).coerceIn(0.4f, 8f)
                                }
                            }

                            override fun onFftDataCapture(
                                visualizer: Visualizer?,
                                fft: ByteArray?,
                                samplingRate: Int,
                            ) = Unit
                        },
                        Visualizer.getMaxCaptureRate() / 2,
                        true,
                        false,
                    )
                    enabled = true
                }
            }.getOrNull()
            onDispose { visualizer?.release() }
        }
    }

    val latestPosition = rememberUpdatedState(positionMs)
    LaunchedEffect(playing, pcm, uri) {
        val decoded = pcm ?: return@LaunchedEffect
        while (playing) {
            val rms = decoded.rmsAt(latestPosition.value)
            scroll.push(rms)
            amplitudes = scroll.snapshot()
            level = rms
            dominantKhz = (0.4f + rms * 7.6f).coerceIn(0.4f, 8f)
            delay(45)
        }
    }

    return LiveWaveformFrame(amplitudes, level, dominantKhz)
}

internal fun decodePcm(context: Context, uri: Uri): DecodedPcm? {
    val extractor = MediaExtractor()
    return try {
        extractor.setDataSource(context, uri, null)
        val track = (0 until extractor.trackCount).firstOrNull { index ->
            extractor.getTrackFormat(index).getString(MediaFormat.KEY_MIME)?.startsWith("audio/") == true
        } ?: return null
        extractor.selectTrack(track)
        val format = extractor.getTrackFormat(track)
        val mime = format.getString(MediaFormat.KEY_MIME) ?: return null
        val sampleRate = format.getInteger(MediaFormat.KEY_SAMPLE_RATE)
        val channels = runCatching { format.getInteger(MediaFormat.KEY_CHANNEL_COUNT) }.getOrDefault(1)
        val maxSamples = sampleRate * 180
        val collected = ArrayList<Short>(min(sampleRate * 8, maxSamples))
        if (mime == MediaFormat.MIMETYPE_AUDIO_RAW) {
            val buf = ByteBuffer.allocate(4096)
            while (collected.size < maxSamples) {
                buf.clear()
                val size = extractor.readSampleData(buf, 0)
                if (size < 0) break
                buf.limit(size)
                buf.order(ByteOrder.LITTLE_ENDIAN)
                appendPcm(buf, size, channels, collected, maxSamples)
                extractor.advance()
            }
        } else {
            val codec = MediaCodec.createDecoderByType(mime)
            codec.configure(format, null, null, 0)
            codec.start()
            val info = MediaCodec.BufferInfo()
            var inputDone = false
            var outputDone = false
            while (!outputDone && collected.size < maxSamples) {
                if (!inputDone) {
                    val inIndex = codec.dequeueInputBuffer(4_000)
                    if (inIndex >= 0) {
                        val input = codec.getInputBuffer(inIndex) ?: break
                        val size = extractor.readSampleData(input, 0)
                        if (size < 0) {
                            codec.queueInputBuffer(
                                inIndex, 0, 0, 0,
                                MediaCodec.BUFFER_FLAG_END_OF_STREAM,
                            )
                            inputDone = true
                        } else {
                            codec.queueInputBuffer(inIndex, 0, size, extractor.sampleTime, 0)
                            extractor.advance()
                        }
                    }
                }
                val outIndex = codec.dequeueOutputBuffer(info, 4_000)
                if (outIndex >= 0) {
                    val output = codec.getOutputBuffer(outIndex)
                    if (output != null && info.size > 0) {
                        output.position(info.offset)
                        output.limit(info.offset + info.size)
                        output.order(ByteOrder.LITTLE_ENDIAN)
                        appendPcm(output, info.size, channels, collected, maxSamples)
                    }
                    outputDone = info.flags and MediaCodec.BUFFER_FLAG_END_OF_STREAM != 0
                    codec.releaseOutputBuffer(outIndex, false)
                }
            }
            codec.stop()
            codec.release()
        }
        DecodedPcm(sampleRate, collected.toShortArray())
    } catch (cancelled: CancellationException) {
        throw cancelled
    } catch (_: Exception) {
        null
    } finally {
        extractor.release()
    }
}

private fun appendPcm(
    buffer: ByteBuffer,
    size: Int,
    channels: Int,
    out: ArrayList<Short>,
    maxSamples: Int,
) {
    val ch = channels.coerceAtLeast(1)
    val frames = size / (2 * ch)
    repeat(frames) {
        if (out.size >= maxSamples) return
        var acc = 0
        repeat(ch) {
            acc += buffer.short.toInt()
        }
        out.add((acc / ch).toShort())
    }
}
