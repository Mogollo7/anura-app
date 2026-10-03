# Montaje de ANURA: S01→S36 sin huecos, música y SFX según GUIA-OPUS.md.
# Los SFX que ya vienen dentro de las escenas (S01–S05, S07, S09, S14, S16, S17, S20, S22) se conservan en su sitio;
# aquí se añaden la música y los que la guía deja para el montaje (S28 teclas, S35 descarga, S36 campana).
import json, os, re, subprocess

VID = r"D:\Anura\video"
ESC = os.path.join(VID, "escenas")
BRAG = r"D:\server\Anura\.claude\skills\brag\assets"
MUSIC = os.path.join(BRAG, "music", "happy-beats-business-moves-vol-1-by-ende-dot-app.mp3")
SFX = os.path.join(BRAG, "sfx")
OUT = os.path.join(VID, "anura-presentacion.mp4")
POSTER = os.path.join(VID, "anura-presentacion-poster.png")
TOTAL = 167.0
MUSIC_LEN = 164.0

guide = open(os.path.join(VID, "GUIA-OPUS.md"), encoding="utf-8").read()
# S07a y S10a van detrás de S07 y S10. El id numérico de S01–S36 no cambia.
scenes = [(int(n), float(a), float(b)) for n, a, b in re.findall(r"^## S(\d{2}) — .*? · ([\d.]+)–([\d.]+) ·", guide, re.M)]
bridges = {}
for num, letter, a, b in re.findall(r"^## S(\d{2})([a-z]) — .*? · ([\d.]+)–([\d.]+) ·", guide, re.M):
    bridges.setdefault(int(num), []).append((f"s{num}{letter}", float(a), float(b)))
assert set(bridges) == {7, 10, 12}
assert [s[0] for s in scenes] == list(range(1, 37)), scenes
assert scenes[0][1] == 0 and scenes[-1][2] == TOTAL

def probe(path, *args):
    return subprocess.run(["ffprobe", "-v", "error", *args, "-of", "json", path], capture_output=True, text=True, check=True).stdout

order = []
for i, (n, a, b) in enumerate(scenes):
    order.append((f"s{n:02d}", a, b))
    cursor = b
    nxt = scenes[i + 1][1] if i + 1 < len(scenes) else TOTAL
    for name, ba, bb in bridges.get(n, []):
        assert abs(ba - cursor) < 0.001, (name, ba, cursor)
        cursor = bb
        order.append((name, ba, bb))
    assert abs(cursor - nxt) < 0.001, (n, cursor, nxt)

files, with_audio = [], []
for name, a, b in order:
    f = os.path.join(ESC, name, f"{name}.mp4")
    assert os.path.exists(f), f
    d = float(json.loads(probe(f, "-show_entries", "format=duration"))["format"]["duration"])
    assert abs(d - (b - a)) < 0.02, (name, d, b - a)
    files.append(f)
    if json.loads(probe(f, "-select_streams", "a", "-show_entries", "stream=index"))["streams"]:
        with_audio.append((f, a))

# SFX del montaje (tiempos absolutos).
# S28: una tecla al terminar cada línea de reglas.js (131.50 + 0.015 s/carácter, pausa 0.10 s).
keys = [131.98, 132.46, 133.98]
extra = [(os.path.join(SFX, "keyboard", "keypress-001.wav"), t) for t in keys]
extra.append((os.path.join(SFX, "interface", "drop_002.ogg"), 160.30))   # S35: back.out cruza el suelo en 1.30 s locales
# Escenas que ya salen mudas (guía: la tabla de SFX se coloca al unir).
roll = os.path.join(SFX, "ui", "rollover2.ogg")
extra += [(roll, 22.00), (roll, 29.40), (roll, 68.50), (roll, 74.00)]          # S07 mapa, S07a, S12a, S12b
extra.append((os.path.join(SFX, "casino", "card-fan-1.ogg"), 53.75))          # S10a abanico
extra.append((os.path.join(SFX, "interface", "click_003.ogg"), 107.00 + 2.585))  # S22 clic (CLICK de la grabación)
extra.append((os.path.join(SFX, "impact", "impactBell_heavy_000.ogg"), 163.50))  # S36 wordmark
for f, _ in extra:
    assert os.path.exists(f), f

# Video: filtro concat. Cada cuadro de cada escena se numera de nuevo (setpts=N a 1/60): ni se duplica ni se pierde ninguno.
# (El demuxer concat repetía el primer cuadro de cada escena y perdía el último.)
NS = len(files)
inputs = []
for f in files:
    inputs += ["-i", f]
inputs += ["-i", MUSIC]
for f, _ in with_audio + extra:
    inputs += ["-i", f]
vf = ("".join(f"[{i}:v]setpts=PTS-STARTPTS[v{i}];" for i in range(NS))
      + "".join(f"[v{i}]" for i in range(NS)) + f"concat=n={NS}:v=1:a=0,settb=1/60,setpts=N[vout]")

# Música 0.35 hasta 164 s; 0.22 en S20–S24 (98.50–119.50). De 164 a 167, silencio.
vol = "0.35-0.13*min(max((t-98.25)/0.5,0),1)+0.13*min(max((t-119.25)/0.5,0),1)"
fl = [vf, f"[{NS}:a]atrim=0:{MUSIC_LEN},asetpts=PTS-STARTPTS,volume='{vol}':eval=frame,afade=t=out:st={MUSIC_LEN-1}:d=1,apad=whole_dur={TOTAL},aformat=sample_rates=48000:channel_layouts=stereo[m]"]
labels = ["[m]"]
for k, (f, t) in enumerate(with_audio + extra):
    ms = int(round(t * 1000))
    fl.append(f"[{k+NS+1}:a]aformat=sample_rates=48000:channel_layouts=stereo,adelay={ms}|{ms}[a{k}]")
    labels.append(f"[a{k}]")
fl.append("".join(labels) + f"amix=inputs={len(labels)}:normalize=0:duration=longest,atrim=0:{TOTAL},alimiter=limit=0.95[aout]")

cmd = ["ffmpeg", "-y", "-hide_banner", *inputs, "-filter_complex", ";".join(fl),
       "-map", "[vout]", "-map", "[aout]",
       "-c:v", "libx264", "-preset", "slow", "-crf", "16", "-pix_fmt", "yuv420p", "-fps_mode", "passthrough",
       "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-t", str(TOTAL), "-movflags", "+faststart", OUT]
subprocess.run(cmd, check=True)

# Poster: S01 en 2.35 s (el abanico).
subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-ss", "2.35", "-i", OUT, "-frames:v", "1", POSTER], check=True)
print("escenas con audio propio:", [os.path.basename(f) for f, _ in with_audio])
print("teclas S28:", [round(t, 3) for t in keys])
print("listo:", OUT)
