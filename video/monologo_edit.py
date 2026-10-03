# Pasa el texto de ANURA a monólogo: nuevas frases, tipografía (Archivo 500 cuerpo, ANURA 800,
# Instrument Serif itálica en la frase que acompaña, JetBrains Mono en números) y blur en todo texto que viaja.
# Parte siempre de _respaldo_v1 para poder ejecutarse más de una vez.
import os, re, shutil

VID = r"D:\Anura\video"
ESC = os.path.join(VID, "escenas")
BAK = os.path.join(VID, "_respaldo_v1")

FONTS = """
      @font-face { font-family: "Instrument Serif"; src: url("assets/fonts/InstrumentSerif-Italic.woff2") format("woff2"); font-style: italic; font-weight: 400; }
      @font-face { font-family: "JetBrains Mono"; src: url("assets/fonts/JetBrainsMono.woff2") format("woff2"); font-weight: 100 800; }
      .serif { font-family: "Instrument Serif", serif; font-style: italic; font-weight: 400; }
      .mono { font-family: "JetBrains Mono", monospace; font-weight: 500; font-style: normal; letter-spacing: -0.02em; }
      .brand { font-weight: 800; font-style: normal; font-family: "Archivo", sans-serif; }
      #root p, #root h1, #root span { text-decoration: none; }
"""

A = '<span class="brand">ANURA</span>'
def M(n):
    return f'<span class="mono">{n}</span>'

class Scene:
    def __init__(self, n):
        self.n = n
        self.path = os.path.join(ESC, f"s{n:02d}", "index.html")
        self.s = open(os.path.join(BAK, f"s{n:02d}", "index.html"), encoding="utf-8").read()
        self.s = self.s.replace("</style>", FONTS + "    </style>", 1)

    def rep(self, old, new, count=1):
        k = self.s.count(old)
        assert k >= 1, (self.n, old[:90])
        if count == 1:
            assert k == 1, (self.n, "ambiguo", k, old[:90])
        self.s = self.s.replace(old, new)
        return self

    def sub(self, pat, new, min_count=1):
        self.s, k = re.subn(pat, new, self.s)
        assert k >= min_count, (self.n, pat[:90])
        return self

    def blur(self, *sels, inpx=12, outpx=10):
        """Añade blur a las entradas (fromTo … opacity 0 → 1) y salidas (to … opacity 0) de esos selectores."""
        for sel in sels:
            q = re.escape(sel)
            self.s, a = re.subn(r"(tl\.fromTo\(" + q + r", \{ )([^{}]*?opacity: 0(?![.\d])[^{}]*?)( \}, \{ )([^{}]*?opacity: 1(?![.\d]))",
                                r'\1\2, filter: "blur(' + str(inpx) + r'px)"\3\4, filter: "blur(0px)"', self.s)
            self.s, b = re.subn(r"(tl\.to\(" + q + r", \{ )([^{}]*?opacity: 0(?![.\d]))(,| \})",
                                r'\1\2, filter: "blur(' + str(outpx) + r'px)"\3', self.s)
            assert a + b >= 1, (self.n, "sin tweens para", sel)
        return self

    def save(self):
        open(self.path, "w", encoding="utf-8").write(self.s)
        print("ok", self.n)

# ---------- S01–S03: hola / pregunta / o estos ----------
for n in (1, 2, 3):
    sc = Scene(n)
    # la frase que acompaña a «hola» pasa a serif itálica
    sc.sub(r"(#pregunta \{\s*margin: 24px 0 0 0;\s*)font-size: 48px;\s*font-weight: 400;",
           r'\1font-family: "Instrument Serif", serif; font-style: italic; font-size: 64px; font-weight: 400;')
    if n in (2, 3):
        sc.sub(r"(#estos \{[^}]*?)font-size: 96px;\s*font-weight: 700;",
               r'\1font-family: "Instrument Serif", serif; font-style: italic; font-size: 120px; font-weight: 400;')
    if n == 2:
        sc.blur('["#hola", "#pregunta"]', '"#estos"')
    sc.save()

# ---------- S04 ----------
sc = Scene(4)
sc.rep('<h1 id="l1">Ellos son los anuros,</h1>', '<h1 id="l1">Ellos son los anuros</h1>')
sc.rep('<p id="l2">los anfibios sin cola.</p>', '<p id="l2">los anfibios sin cola</p>')
sc.sub(r'(#l1 \{[^}]*?)font-weight: 800;', r'\1font-weight: 500;')
sc.blur('"#l1"', '"#l2"')
sc.rep('tl.to("#block", { scale: 0.96, opacity: 0,', 'tl.to("#block", { scale: 0.96, opacity: 0, filter: "blur(10px)",')
sc.save()

# ---------- S05: «En el mundo hay cerca de» + «9009 especies» ----------
sc = Scene(5)
sc.rep('<p id="sub">especies de ellos</p>', '<p id="sub" class="serif">especies</p>')
sc.sub(r'(#sub \{\s*)margin: 16px 0 0 0;\s*font-weight: 500;\s*font-size: 56px;', r'\1margin: 40px 0 0 0; font-size: 80px; line-height: 1;')
sc.sub(r'#num \{\s*margin: 24px 0 0 0;\s*font-weight: 800;\s*font-stretch: 120%;\s*font-size: 260px;',
       '#num { margin: 24px 0 0 0; font-family: "JetBrains Mono", monospace; font-weight: 500; letter-spacing: -0.04em; font-size: 240px; line-height: 0.9;')
# el squash del número ya no usa el eje de ancho (Mono no lo tiene): scaleX 1.08 → 1
sc.rep('''      const w = { s: 120 };
      const setW = () => { num.style.fontStretch = w.s + "%"; };
      tl.to(w, { s: 125, duration: 0.05, ease: "none", onUpdate: setW }, 1.95);
      tl.to(w, { s: 100, duration: 0.2, ease: "power2.out", onUpdate: setW }, 2);''',
       '''      tl.to("#num", { scaleX: 1.08, scaleY: 0.94, duration: 0.05, ease: "power1.out" }, 1.95);
      tl.to("#num", { scaleX: 1, scaleY: 1, duration: 0.35, ease: "back.out(3)" }, 2);''')
sc.blur('"#label"', '"#sub"')
sc.save()

# ---------- S06 ----------
sc = Scene(6)
sc.rep('<p id="sub">especies de ellos</p>', '<p id="sub" class="serif">especies</p>')
sc.rep('#sub { margin-top: 16px; }', '#sub { margin-top: 40px; font-weight: 400; font-size: 80px; line-height: 1; }')
sc.rep('#num { margin: 24px 0 0 0; width: fit-content; font-weight: 800; font-stretch: 100%; font-size: 260px;',
       '#num { margin: 24px 0 0 0; width: fit-content; font-family: "JetBrains Mono", monospace; font-weight: 500; letter-spacing: -0.04em; font-size: 240px; line-height: 0.9;')
# de centrado a x=96 sin medir al montar: left fijo + xPercent (-50 → 0) y x (864 → 0), con blur mientras viaja
sc.rep('''      lines.forEach((id) => {
        const r = $(id).getBoundingClientRect();
        const dx = 960 - (r.left + r.width / 2);
        tl.fromTo("#" + id, { x: dx }, { x: 0, duration: 0.4, ease: EASE }, 0);
      });''',
       '''      lines.forEach((id, k) => {
        tl.fromTo("#" + id, { x: 864, xPercent: -50, filter: "blur(10px)" }, { x: 0, xPercent: 0, filter: "blur(0px)", duration: 0.5, ease: EASE }, k * 0.04);
      });''')
sc.rep('tl.to("#block", { y: -24, opacity: 0,', 'tl.to("#block", { y: -24, opacity: 0, filter: "blur(10px)",')
sc.save()

# ---------- S07 ----------
sc = Scene(7)
sc.rep('<p id="frase">Colombia es el segundo país más rico en anuros en el mundo.</p>',
       '<p id="frase">Colombia es el segundo país más rico en anuros en el mundo</p>')
sc.sub(r'(#frase \{[^}]*?)left: 260px; width: 1400px;([^}]*?)font-weight: 600; font-size: 44px;', r'\1left: 80px; width: 1760px;\2font-weight: 500; font-size: 52px;')
sc.blur('"#frase"')
sc.rep('tl.to("#group", { y: -20, opacity: 0,', 'tl.to("#group", { y: -20, opacity: 0, filter: "blur(10px)",')
sc.save()

# ---------- S08: «Para reconocerlos nació ANURA» y luego los semilleros ----------
sc = Scene(8)
sc.rep('<p id="t8">ANURA es una iniciativa de 3 semilleros de investigación de la Corporación Universitaria Lasallista.</p>',
       f'<p id="t7b">Para reconocerlos nació {A}</p>\n        <p id="t8">{A} es una iniciativa de {M(3)} semilleros de la Corporación Universitaria Lasallista</p>')
sc.rep('</style>', '      #t7b { position: absolute; left: 80px; width: 1760px; top: 440px; margin: 0; text-align: center; font-weight: 500; font-size: 96px; line-height: 1.15; opacity: 0; }\n    </style>')
sc.rep('''      // 29.10 -> local 0.00
      tl.fromTo("#t8", { y: 24, opacity: 0 }, { y: 0, opacity: 1, duration: 0.4, ease: EASE }, 0);
      // logos: local 1.00, 1.50, 2.00
      [0, 1, 2].forEach((i) => {
        tl.fromTo("#s" + i, { y: 24, opacity: 0 }, { y: 0, opacity: 1, duration: 0.4, ease: EASE }, 1 + i * 0.5);
      });''',
       '''      // 29.00: justo después del mapa, «Para reconocerlos nació ANURA» al centro y grande
      tl.fromTo("#t7b", { y: 60, opacity: 0, filter: "blur(14px)" }, { y: 0, opacity: 1, filter: "blur(0px)", duration: 0.5, ease: EASE }, 0);
      // 30.50 (beat): sube hacia el sitio del título, se encoge y se desvanece mientras entra T8 en su lugar
      tl.to("#t7b", { y: -300, scale: 0.55, opacity: 0, filter: "blur(12px)", duration: 0.5, ease: "expo.inOut" }, 1.5);
      tl.fromTo("#t8", { y: 40, opacity: 0, filter: "blur(12px)" }, { y: 0, opacity: 1, filter: "blur(0px)", duration: 0.5, ease: EASE }, 1.75);
      // logos: 2.25, 2.50, 2.75 con resorte
      [0, 1, 2].forEach((i) => {
        tl.fromTo("#s" + i, { y: 40, scale: 0.9, opacity: 0, filter: "blur(10px)" }, { y: 0, scale: 1, opacity: 1, filter: "blur(0px)", duration: 0.55, ease: "back.out(1.8)" }, 2.25 + i * 0.25);
      });''')
sc.rep('tl.to("#group", { y: -20, opacity: 0,', 'tl.to("#group", { y: -20, opacity: 0, filter: "blur(10px)",')
sc.save()

# ---------- S09 ----------
sc = Scene(9)
sc.rep('<p id="t9">Juntos creamos ANURA, una app móvil para la identificación de anuros.</p>',
       f'<p id="t9">Juntos creamos {A} <span class="serif">una app móvil para identificar anuros</span></p>')
sc.sub(r'(#t9 \{[^}]*?)font-weight: 600; font-size: 56px;', r'\1font-weight: 500; font-size: 64px;')
sc.blur('"#t9"')
sc.rep('tl.to(["#c0", "#c1"], { y: -20, opacity: 0,', 'tl.to(["#c0", "#c1"], { y: -20, opacity: 0, filter: "blur(8px)",')
sc.save()

# ---------- S10 ----------
sc = Scene(10)
sc.rep('<p id="t13">Ya sea monte, desierto o llano, ANURA funciona en tu celular.</p>',
       f'<p id="t13"><span class="serif">En monte desierto o llano</span> {A} funciona en tu celular</p>')
sc.blur('"#t13"', '["#pillB", "#t13"]')
sc.save()

# ---------- S11 ----------
sc = Scene(11)
sc.rep('<p id="t14" class="t" data-layout-allow-overlap>Con los paquetes descargables llevas solo la zona donde estás.</p>',
       '<p id="t14" class="t" data-layout-allow-overlap>Los paquetes descargables llevan solo la zona donde estás</p>')
sc.rep('<p id="t15" class="t" data-layout-allow-overlap>Y a su vez se dividen en regiones.</p>',
       '<p id="t15" class="t" data-layout-allow-overlap>Esas zonas <span class="serif">se dividen en regiones</span></p>')
sc.blur('"#t14"', '"#t15"')
sc.save()

# ---------- S12 ----------
sc = Scene(12)
sc.rep('<p id="t15old" data-layout-allow-overlap>Y a su vez se dividen en regiones.</p>',
       '<p id="t15old" data-layout-allow-overlap>Esas zonas <span class="serif">se dividen en regiones</span></p>')
sc.rep('<p id="t15" data-layout-allow-overlap>Y a su vez se dividen en regiones.</p>',
       '<p id="t15" data-layout-allow-overlap>Esas zonas <span class="serif">se dividen en regiones</span></p>')
sc.sub(r'(#t15 \{[^}]*?)font-weight: 600; font-size: 56px;', r'\1font-weight: 500; font-size: 60px;')
sc.blur('"#t15old"', '"#t15"')
sc.rep('tl.to(["#list", "#antioquia"], { opacity: 0,', 'tl.to(["#list", "#antioquia"], { opacity: 0, filter: "blur(8px)",')
sc.save()

# ---------- S13–S14 ----------
for n in (13, 14):
    sc = Scene(n)
    sc.rep('<p id="t16">ANURA utiliza datos geográficos para mejorar la precisión del modelo.</p>',
           f'<p id="t16">{A} usa datos geográficos <span class="serif">para afinar el modelo</span></p>')
    sc.sub(r'(#t16 \{[^}]*?)font-weight: 600; font-size: 64px;', r'\1font-weight: 500; font-size: 68px;')
    sc.blur('"#t16"')
    sc.save()

# ---------- S15–S18: el cuestionario ----------
Q = 'Un cuestionario <span class="serif" style="white-space:nowrap">paso a paso</span> afina el modelo'
sc = Scene(15)
sc.rep('<p id="t17">ANURA hace un cuestionario, <span style="white-space:nowrap">paso a paso,</span> para afinar el modelo.</p>', f'<p id="t17">{Q}</p>')
sc.sub(r'(#t17 \{[^}]*?)font-weight: 600; font-size: 88px;', r'\1font-weight: 500; font-size: 96px;')
sc.blur('"#t17"')
sc.rep('tl.to("#folder", { y: 40, opacity: 0,', 'tl.to("#folder", { y: 40, opacity: 0, filter: "blur(10px)",')
sc.save()

sc = Scene(16)
sc.rep('<p id="t17old" class="t" data-layout-allow-overlap>ANURA hace un cuestionario, <span style="white-space:nowrap">paso a paso,</span> para afinar el modelo.</p>',
       f'<p id="t17old" class="t" data-layout-allow-overlap>{Q}</p>')
sc.rep('<p id="t17" class="t" data-layout-allow-overlap>ANURA hace un cuestionario, paso a paso, para afinar el modelo.</p>',
       f'<p id="t17" class="t" data-layout-allow-overlap>{Q}</p>')
sc.rep('.t { position: absolute; margin: 0; text-align: center; font-weight: 600; }', '.t { position: absolute; margin: 0; text-align: center; font-weight: 500; }')
sc.sub(r'(#t17old \{[^}]*?)font-size: 88px;', r'\1font-size: 96px;')
sc.sub(r'(#t17 \{[^}]*?)font-size: 52px;', r'\1font-size: 56px;')
sc.blur('"#t17old"', '"#t17"')
sc.save()

for n in (17, 18):
    sc = Scene(n)
    sc.rep('<p id="t17">ANURA hace un cuestionario, paso a paso, para afinar el modelo.</p>', f'<p id="t17">{Q}</p>')
    sc.sub(r'(#t17 \{ position: absolute; margin: 0; text-align: center; )font-weight: 600;(.*?)font-size: 52px;', r'\1font-weight: 500;\2font-size: 56px;')
    if n == 18:
        sc.rep('<p id="t18">Con más contexto recibes mejores resultados en tu observación.</p>',
               '<p id="t18">Con más contexto <span class="serif">el resultado de tu observación mejora</span></p>')
        sc.sub(r'(#t18 \{[^}]*?)font-weight: 600; font-size: 64px;', r'\1font-weight: 500; font-size: 68px;')
        sc.blur('"#t17"', '"#t18"')
    sc.save()

# ---------- S19–S22 ----------
sc = Scene(19)
sc.rep('<p id="t18" data-layout-allow-occlusion>Con más contexto recibes mejores resultados en tu observación.</p>',
       '<p id="t18" data-layout-allow-occlusion>Con más contexto <span class="serif">el resultado de tu observación mejora</span></p>')
sc.sub(r'(#t18 \{[^}]*?)font-weight: 600; font-size: 64px;', r'\1font-weight: 500; font-size: 68px;')
sc.rep('<p id="t19">Cuando tengas internet puedes sincronizar con nuestro servidor,</p>',
       '<p id="t19">Cuando tengas internet puedes sincronizar con nuestro servidor</p>')
sc.sub(r'(#t19 \{[^}]*?)font-weight: 600; font-size: 84px;', r'\1font-weight: 500; font-size: 84px;')
sc.blur('"#t19"')
sc.save()

sc = Scene(20)
sc.rep('<p id="t19" data-layout-allow-overlap>Cuando tengas internet puedes sincronizar con nuestro servidor,</p>',
       '<p id="t19" data-layout-allow-overlap>Cuando tengas internet puedes sincronizar con nuestro servidor</p>')
sc.sub(r'(#t19 \{[^}]*?)font-weight: 600; font-size: 84px;', r'\1font-weight: 500; font-size: 84px;')
sc.sub(r'(#t20 \{[^}]*?)font-weight: 700; font-size: 80px;', r'\1font-family: "Instrument Serif", serif; font-style: italic; font-weight: 400; font-size: 96px;')
sc.blur('"#t19"', '"#t20"')
sc.save()

sc = Scene(21)
sc.rep('<p id="t21" class="t" data-layout-allow-overlap>con diferentes personas.</p>',
       '<p id="t21" class="t" data-layout-allow-overlap>con diferentes personas</p>')
sc.rep('.t { position: absolute; left: 80px; top: 380px; width: 700px; margin: 0; font-weight: 700; font-size: 80px; line-height: 1.15; }',
       '.t { position: absolute; left: 80px; top: 380px; width: 700px; margin: 0; font-family: "Instrument Serif", serif; font-style: italic; font-weight: 400; font-size: 96px; line-height: 1.1; }')
sc.blur('"#t20"', '"#t21"')
sc.save()

sc = Scene(22)
sc.rep('<p id="t20" class="t" data-layout-allow-overlap>con diferentes personas.</p>',
       '<p id="t20" class="t serif" data-layout-allow-overlap>con diferentes personas</p>')
sc.rep('.t { position: absolute; left: 80px; top: 380px; width: 700px; margin: 0; font-weight: 700; font-size: 80px; line-height: 1.15; }',
       '.t { position: absolute; left: 80px; top: 380px; width: 700px; margin: 0; font-weight: 500; font-size: 80px; line-height: 1.15; }\n      #t20.serif { font-size: 96px; line-height: 1.1; }')
sc.blur('"#t20"', '"#t21"')
sc.save()

# ---------- S23–S24 ----------
T23 = 'y si alguien cree que es otra especie <span class="serif">puede proponerlo en los comentarios</span>'
sc = Scene(23)
sc.rep('<p id="t23">y, si alguien cree que es otra especie, puede proponerlo en los comentarios.</p>', f'<p id="t23">{T23}</p>')
sc.blur('"#t23"')
sc.save()

sc = Scene(24)
sc.rep('<p id="t23" class="t" data-layout-allow-overlap>y, si alguien cree que es otra especie, puede proponerlo en los comentarios.</p>',
       f'<p id="t23" class="t" data-layout-allow-overlap>{T23}</p>')
# «La solicitud llega a evaluación» no está en el guion nuevo: la toma del admin queda sola
sc.rep('<p id="t24" class="t">La solicitud llega a evaluación.</p>\n', '')
sc.rep('      tl.fromTo("#t24", { y: 20, opacity: 0 }, { y: 0, opacity: 1, duration: 0.45, ease: EASE }, 0.1);\n', '')
sc.sub(r"\s*#t24 \{[^}]*\}", "")
sc.blur('"#t23"')
sc.save()

# ---------- S26: barras ----------
sc = Scene(26)
sc.rep('<p id="t25">ANURA ha pasado por distintas actualizaciones.</p>', f'<p id="t25">{A} ha pasado por distintas actualizaciones</p>')
sc.rep('<p id="t26">Pasamos de 10 especies a 28, y luego a 41.</p>',
       f'<p id="t26" class="serif">Pasamos de {M(10)} especies a {M(28)} y luego a {M(41)}</p>')
sc.rep('#t25 { font-weight: 600; font-size: 44px; line-height: 1.2; }', '#t25 { font-weight: 500; font-size: 52px; line-height: 1.15; }')
sc.rep('#t26 { font-weight: 500; font-size: 32px; line-height: 1.3; opacity: 0; }', '#t26 { font-size: 44px; line-height: 1.25; opacity: 0; }\n      #t26 .mono { font-size: 38px; }')
sc.rep('tl.fromTo("#t25", { y: 20 }, { y: 0, duration: 0.45, ease: EASE }, 0.2);',
       'tl.fromTo("#t25", { y: 40, filter: "blur(12px)" }, { y: 0, filter: "blur(0px)", duration: 0.5, ease: EASE }, 0.2);')
sc.blur('"#t26"')
sc.save()

# ---------- S27: el bloque de S26 sale y «Antes todo era manual» entra al centro ----------
sc = Scene(27)
sc.rep('<p id="t25">ANURA ha pasado por distintas actualizaciones.</p>', f'<p id="t25">{A} ha pasado por distintas actualizaciones</p>')
sc.rep('<p id="t26">Pasamos de 10 especies a 28, y luego a 41.</p>',
       f'<p id="t26" class="serif">Pasamos de {M(10)} especies a {M(28)} y luego a {M(41)}</p>')
sc.rep('#t25 { font-weight: 600; font-size: 44px; line-height: 1.2; }', '#t25 { font-weight: 500; font-size: 52px; line-height: 1.15; }')
sc.rep('#t26 { font-weight: 500; font-size: 32px; line-height: 1.3;  }', '#t26 { font-size: 44px; line-height: 1.25; }\n      #t26 .mono { font-size: 38px; }')
sc.rep('<p id="t27">Todo esto, desde la sección de administración.</p>', '<p id="t28c">Antes todo era manual</p>')
sc.sub(r'#t27 \{[^}]*\}', '#t28c { position: absolute; margin: 0; left: 80px; top: 460px; width: 1760px; text-align: center; font-weight: 500; font-size: 104px; line-height: 1.1; opacity: 0; }')
sc.rep('tl.to("#txt", { x: -160, opacity: 0, duration: 0.4, ease: "power2.in" }, 0);',
       'tl.to("#txt", { x: -160, opacity: 0, filter: "blur(12px)", duration: 0.5, ease: "power2.in" }, 1.0);')
sc.sub(r'tl\.to\("#bar" \+ i, \{ scaleY: 0, duration: 0\.5, ease: "power3\.inOut" \}, i \* 0\.05\);',
       'tl.to("#bar" + i, { scaleY: 0, duration: 0.5, ease: "power3.inOut" }, 1.0 + i * 0.05);')
sc.sub(r'tl\.to\("#val" \+ i, \{ y: H\[i\], opacity: 0, duration: 0\.5, ease: "power3\.inOut" \}, i \* 0\.05\);',
       'tl.to("#val" + i, { y: H[i], opacity: 0, duration: 0.5, ease: "power3.inOut" }, 1.0 + i * 0.05);')
sc.rep('tl.to(["#axY", "#hdY", "#axX", "#hdX"], { opacity: 0, duration: 0.3, ease: "power2.in" }, 0.2);',
       'tl.to(["#axY", "#hdY", "#axX", "#hdX"], { opacity: 0, duration: 0.3, ease: "power2.in" }, 1.2);')
sc.rep('tl.fromTo("#t27", { y: 20, opacity: 0 }, { y: 0, opacity: 1, duration: 0.45, ease: "expo.out" }, 0.5);',
       'tl.fromTo("#t28c", { scale: 1.15, opacity: 0, filter: "blur(16px)" }, { scale: 1, opacity: 1, filter: "blur(0px)", duration: 0.55, ease: "expo.out" }, 1.75);')
sc.save()

# ---------- S28: la frase de S27 viaja a la columna izquierda ----------
sc = Scene(28)
sc.rep('<p id="t28">Antes todo era manual.</p>', '<p id="t28">Antes todo era manual</p>')
sc.rep('<p id="t29">Poco estandarizado, y un solo desarrollador tenía el control.</p>',
       '<p id="t29" class="serif">Poco estandarizado y un solo desarrollador tenía el control</p>')
sc.rep('<p id="t30">Ahora, con el modo admin, puedes repetir el ciclo.</p>', '<p id="t30">Ahora con el modo admin puedes repetir el ciclo</p>')
sc.rep('#t28 { font-weight: 700; font-size: 48px; line-height: 1.15; opacity: 0; }', '#t28 { width: fit-content; white-space: nowrap; font-weight: 500; font-size: 64px; line-height: 1.1; transform-origin: 50% 0; }')
sc.rep('#t29 { font-weight: 500; font-size: 32px; line-height: 1.3; opacity: 0; }', '#t29 { font-size: 44px; line-height: 1.2; opacity: 0; }')
sc.rep('#t30 { position: absolute; left: 80px; top: 280px; width: 760px; font-weight: 700; font-size: 48px; line-height: 1.15; opacity: 0; }',
       '#t30 { position: absolute; left: 80px; top: 280px; width: 760px; font-weight: 500; font-size: 56px; line-height: 1.15; opacity: 0; }')
# arranca donde la dejó S27 (centrada, 104 px en top 460) y viaja a su sitio con blur
sc.rep('tl.fromTo("#t28", { y: 20, opacity: 0 }, { y: 0, opacity: 1, duration: 0.45, ease: EASE }, 0.1);',
       '''tl.fromTo("#t28", { x: 880, xPercent: -50, y: 180, scale: 1.625 }, { x: 0, xPercent: 0, y: 0, scale: 1, duration: 0.5, ease: "expo.inOut" }, 0);
      tl.fromTo("#t28", { filter: "blur(0px)" }, { filter: "blur(10px)", duration: 0.25, ease: "power2.in", immediateRender: false }, 0);
      tl.to("#t28", { filter: "blur(0px)", duration: 0.25, ease: "power2.out" }, 0.25);''')
sc.blur('"#t29"', '"#t30"', '"#txt"')
sc.save()

# ---------- S36: cierre ----------
sc = Scene(36)
sc.rep('top: 420px; width: 1920px; text-align: center; font-weight: 900; font-stretch: 100%; font-size: 120px;', 'top: 470px; width: 1920px; text-align: center; font-weight: 800; font-stretch: 100%; font-size: 140px;')
sc.rep('      <p id="sub">Identificación de anuros.</p>\n', '')
sc.rep('      tl.fromTo("#sub", { y: 16, opacity: 0 }, { y: 0, opacity: 1, duration: 0.5, ease: "back.out(1.7)" }, 0.25);\n', '')
sc.sub(r"\s*#sub \{[^}]*\}", "")
sc.rep('tl.fromTo("#mark", { y: 24, scale: 0.92, opacity: 0 }, { y: 0, scale: 1, opacity: 1, duration: 0.5, ease: "back.out(1.7)" }, 0.2);',
       'tl.fromTo("#mark", { y: 40, scale: 0.9, opacity: 0, filter: "blur(14px)" }, { y: 0, scale: 1, opacity: 1, filter: "blur(0px)", duration: 0.5, ease: "back.out(1.7)" }, 0.2);')
sc.save()
