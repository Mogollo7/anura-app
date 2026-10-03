# Genera S29–S35: la cáscara del admin (dark) emulada a partir de nav.ts, sidebar, topbar y las páginas reales.
import json, os, shutil, html, re

SCR = os.path.dirname(os.path.abspath(__file__))  # tools/: icons.json y Geist.woff2
ESC = r"D:\Anura\video\escenas"
IC = json.load(open(os.path.join(SCR, "icons.json"), encoding="utf-8"))

def icon(name, size, sw=2, cls=""):
    return (f'<svg class="ic {cls}" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
            f'stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round">{IC[name]}</svg>')

# nav.ts, tal cual
AREAS = [
    ("inicio", "/dashboard", "Inicio", "LayoutDashboard", []),
    ("analitica", "/analitica", "Analítica", "BarChart3", []),
    ("modelo", "/modelo", "Modelo", "Repeat", [
        ("Conseguir", [("scraping", "Scraping", "Download"), ("curacion", "Imágenes", "Images"), ("catalogo", "Especies", "BookMarked"),
                       ("paquetes", "Regiones", "Package"), ("contenido", "Contenido", "BookOpen"), ("destacados", "Destacados", "CalendarDays")]),
        ("Limpiar", [("ficha", "Ficha", "FileText"), ("calidad", "Calidad", "ShieldAlert")]),
        ("Procesar", [("ia", "Worker", "BrainCircuit"), ("vectorial", "DB vectorial", "Database"), ("centroides", "Centroides", "Target"),
                      ("clusteres", "Clústeres", "Layers"), ("osr", "OSR", "ShieldQuestion")]),
        ("Resultado", [("valtec", "Validación", "ClipboardCheck"), ("compilador", "Release", "PackageCheck"),
                       ("laboratorio", "Simulador", "FlaskConical"), ("metricas", "Métricas", "FlaskConical")]),
    ]),
    ("movil", "/movil", "App", "Smartphone", [("x", [("u", "Usuarios", "Users"), ("d", "Dispositivos", "Smartphone"), ("o", "Observaciones", "ClipboardList")])]),
    ("operacion", "/operacion", "Operación", "UploadCloud", [("x", [("a", "Actualizaciones", "UploadCloud")])]),
    ("sistema", "/sistema", "Sistema", "Settings", []),
]

# Página: (id, fila del nav, etiqueta del topbar, h1 de la página, blurb de nav.ts)
PAGES = [
    ("dashboard", None, "Inicio", None, None),
    ("scraping", "scraping", "Scraping", "Scraping", "iNaturalist y GBIF, con los mismos filtros del script."),
    ("curacion", "curacion", "Imágenes", "Imágenes", "Fotos ya en el servidor. Excluir o invalidar, con motivo."),
    ("catalogo", "catalogo", "Especies", "Especies", "Crear y revisar la taxonomía."),
    ("ficha", "ficha", "Ficha", "Ficha de especie", "Altitud, sustrato, atípicos y pesos."),
    ("calidad", "calidad", "Calidad", "Calidad", "Lo que hay que corregir antes de entrenar."),
    ("ia", "ia", "Worker", "Worker y embeddings", "BioCLIP escribe los vectores de 512."),
    ("vectorial", "vectorial", "DB vectorial", "DB vectorial", "Dónde quedan esos vectores para verlos."),
    ("centroides", "centroides", "Centroides", "Centroides y morfos", "Global, regional y morfo."),
    ("osr", "osr", "OSR", "OSR · rechazo de desconocidas", "Umbrales de rechazo. La persona los valida."),
    ("valtec", "valtec", "Validación", "Validación técnica", "Lista para compilar, o el motivo por el que no."),
    ("compilador", "compilador", "Release", "Release", "Compilar, aprobar y publicar el paquete de cada subregión."),
]
PAGE = {p[0]: p for p in PAGES}

def nav_html():
    out = ['<div id="navc">', '<div id="hl"></div>']
    for aid, href, label, ic, sections in AREAS:
        kids = sections if aid == "modelo" else sections
        chev = f'<span class="chev" id="chev-{aid}">{icon("ChevronDown", 14)}</span>' if kids else ""
        out.append(f'<div class="area" id="ar-{aid}"><div class="arow" id="a-{aid}"><span class="aic">{icon(ic, 16)}</span><span>{label}</span></div>{chev}</div>')
        if aid == "modelo":
            out.append('<div id="open-modelo" class="open"><div class="openin">')
            for title, items in sections:
                out.append(f'<div class="sec" id="s-{title}"><p class="stitle" id="st-{title}">{title}</p>')
                for iid, il, iic in items:
                    out.append(f'<div class="irow" id="r-{iid}">{icon(iic, 14)}<span>{il}</span></div>')
                out.append("</div>")
            out.append("</div></div>")
    out.append("</div>")
    return "\n".join(out)

def kpi(ic, value, label, hint):
    return (f'<div class="card"><span class="kic">{icon(ic, 16)}</span><p class="kval">{value}</p>'
            f'<p class="klab">{label}</p><p class="khint">{hint}</p></div>')

# ---- piezas del admin (clases de Tailwind traducidas a CSS; textos copiados de los componentes) ----
def btn(label, kind="p", ic=None, extra="", idattr=""):
    i = icon(ic, 13) if ic else ""
    return f'<span class="b b{kind} {extra}"{idattr}>{i}<span>{label}</span></span>'

def field(label, inner, cls=""):
    return f'<div class="fld {cls}"><span class="fl">{label}</span>{inner}</div>'

def inp(val="", ph="", w=None):
    st = f' style="width:{w}px"' if w else ""
    return f'<span class="in{"" if val else " ph"}"{st}>{html.escape(val or ph)}</span>'

def sel(val, w=None):
    st = f' style="min-width:{w}px"' if w else ""
    return f'<span class="in sel"{st}><span>{html.escape(val)}</span>{icon("ChevronDown", 12)}</span>'

def card(inner, cls=""):
    return f'<div class="card {cls}">{inner}</div>'

def ch(title, right="", ic=None):
    i = icon(ic, 14, cls="cti") if ic else ""
    return f'<div class="chd"><h3 class="ct">{i}{title}</h3>{right}</div>'

def badge(t, tone="n"):
    return f'<span class="bd bd{tone}">{t}</span>'

def head(h1, blurb):
    return f'<h2 class="ph1">{html.escape(h1)}</h2><p class="pblurb">{html.escape(blurb)}</p>'

def txt(t, cls="t2"):
    return f'<p class="{cls}">{t}</p>'

BLURB = {
    "scraping": "Conseguir observaciones antes de curarlas. Los filtros son los del extractor de iNaturalist y los de la descarga de ocurrencias de GBIF.",
    "curacion": "Revisa las fotos de cada especie. Excluir una foto la saca del entrenamiento; invalidar una observación saca todas sus fotos. Siempre con motivo, y nada se borra: todo se puede revertir.",
    "catalogo": "Todas las especies del dataset, por familia. Toda especie empieza aquí, con su nombre científico y su familia: así la ven Imágenes, Contenido y los paquetes. Desde aquí se cura sus fotos o se edita su ficha pública.",
    "ficha": "El perfil ecológico y los pesos propuestos se calculan con las observaciones válidas de cada especie: altitud por observación, sustrato etiquetado y morfos declarados en Imágenes. Lo que decide una persona (rango de altitud, pesos y LRC) se guarda en el servidor, con quién y cuándo.",
    "ia": "Un trabajo le pide al worker del PC con GPU que calcule, con el mismo encoder del teléfono, el vector de 512 de cada foto que aún no lo tiene. El worker calcula; no decide ciencia ni publica.",
    "vectorial": "Los vectores que el worker guardó en el servidor (pgvector, float32, normalizados L2), uno por foto y encoder. Solo se comparan vectores del mismo encoder. De aquí salen los centroides y la matriz de clústeres.",
    "centroides": "Todo sale de los embeddings del worker: centroides globales, regionales por subregión, supercentroides de género y familia, y un centroide por cada morfo con individuos suficientes.",
    "osr": "Calcula el umbral τ que impide que la app le ponga nombre a una rana que no conoce. El servidor lo mide con los vectores reales y lo propone; una persona lo valida o lo ajusta. El release usa el último τ validado de cada paquete.",
    "valtec": "Antes de compilar, el servidor revisa el paquete de cada subregión: especies entrenables, vectores del encoder del teléfono, centroides al día y umbral OSR validado por una persona. Si algo falta, dice qué es y dónde se arregla.",
    "compilador": "El servidor compila el paquete de una subregión (sqlite de identificación y su manifiesto) con los vectores, centroides, umbral OSR y Ficha de hoy. Solo compila si la validación está lista. Para que la app lo descargue necesita dos aprobaciones, científica y técnica.",
}
TITLE = {"scraping": "Scraping", "curacion": "Imágenes", "catalogo": "Especies", "ficha": "Ficha de especie", "ia": "Worker y embeddings",
         "vectorial": "DB vectorial", "centroides": "Centroides y morfos", "osr": "OSR · rechazo de desconocidas",
         "valtec": "Validación técnica", "compilador": "Release"}
SUB = "Antioquia · Valle de Aburrá"   # subregión real (S12)
ESPECIE, FAMILIA, GENERO = "Rhinella horribilis", "Bufonidae", "Rhinella"   # del catálogo real (species_registry)
LISTA = ["Rhinella alata", "Rhinella horribilis", "Rhinella margaritifera", "Pristimantis achatinus", "Pristimantis paisa"]

def page_body(pid):
    if pid == "dashboard":
        k = (kpi("ShieldQuestion", "0", "Observaciones refutadas", "0 sin decidir") + kpi("Package", "9", "Paquetes descargables", "9 subregiones")
             + kpi("BookMarked", "41", "Especies en el dataset", "41 en el catálogo") + kpi("Activity", "0", "Actividad en 7 días", "eventos de la app"))
        pan = ('<div class="g2 mt24">'
               + card(ch("Problemas abiertos", badge("0", "a")) + f'<p class="t2 row g8">{icon("CheckCircle2", 16, cls="ok")} Nada pendiente por ahora.</p>', "p20")
               + card(ch("Actividad reciente", '<span class="lnk">Ver todo</span>') + txt("Todavía no hay acciones en la bitácora."), "p20") + "</div>")
        return f'<div class="kgrid">{k}</div>{pan}'
    h = head(TITLE[pid], BLURB[pid]) if pid in TITLE else ""
    if pid == "scraping":
        cmd = "python scraper_inaturalist.py --input especies_input.txt --quality-grade research --min-photos 70 --skip-audio --delay 1"
        inat = ('<div class="card p0"><p class="sum">' + icon("ChevronDown", 14) + 'iNaturalist</p><div class="px20 pb20 stack12">'
                + '<div class="g3">' + field("Especies", inp(ph="Pristimantis paisa"), "c2") + field("Grado de calidad", sel("Investigación (research)"))
                + field("Mínimo de fotos", inp("70")) + field("Máximo de fotos", inp(ph="opcional")) + field("Espera entre peticiones (s)", inp("1")) + "</div>"
                + '<div class="row g16 t2"><span class="row g8"><span class="cb on"></span>Omitir audios</span><span class="row g8" id="ensayo"><span class="cb"></span>Ensayo: taxonomía y conteo, sin bajar archivos</span></div>'
                + '<div class="row g12">' + btn("Consultar muestra", "p") + f'<code class="code">{html.escape(cmd)}</code></div></div></div>')
        gbif = '<div class="card p0 mt16"><p class="sum">' + icon("ChevronRight", 14) + 'GBIF</p></div>'
        return h + '<div class="mt24">' + inat + gbif + "</div>"
    if pid == "curacion":
        izq = ('<div class="card p0"><div class="bb p12">' + f'<span class="in ph w100">{icon("Search", 14)}<span>Especie o familia</span></span></div><ul class="lst">'
               + "".join(f'<li class="{"on" if n == ESPECIE else ""}"><i>{n}</i></li>' for n in LISTA) + "</ul></div>")
        tiles = "".join(f'<li class="tile"><span class="sq"></span><span class="tf">{btn("Excluir", "g", "Trash2", "danger")}</span></li>' for _ in range(6))
        der = card(ch(f'<i class="big">{ESPECIE}</i>', btn("Subir foto", "p", "Upload")) + f'<p class="t3 mb12">{FAMILIA} · {GENERO}</p>'
                   + '<div class="row g8 mb12"><span class="chipf on">Todas</span></div>'
                   + '<section class="grp"><div class="row g8 t2 mb8"><span class="ml">' + btn("Invalidar observación", "g", "ShieldOff", "danger") + '</span></div>'
                   + f'<ul class="tiles">{tiles}</ul></section>')
        return h + f'<div class="gcur mt24">{izq}<div>{der}</div></div>'
    if pid == "catalogo":
        cab = f'<div class="row jb mt16"><span></span>{btn("Añadir especie", "p", "Plus")}</div>'
        arbol = ('<div class="card p0"><div class="bb p12">' + f'<span class="in ph w100">{icon("Search", 14)}<span>Especie o familia</span></span></div><div class="p8">'
                 + f'<p class="fam">{FAMILIA}</p>' + "".join(f'<p class="sp {"on" if n == ESPECIE else ""}"><i>{n}</i></p>' for n in LISTA[:3])
                 + '<p class="fam">Craugastoridae</p>' + "".join(f'<p class="sp"><i>{n}</i></p>' for n in LISTA[3:]) + "</div></div>")
        det = card(f'<div class="row jb"><div><p class="t3">{FAMILIA} · {GENERO}</p><h3 class="h2i">{ESPECIE}</h3></div>'
                   + btn("Editar nombre y familia", "o", "Pencil", "sm") + "</div>")
        return h + cab + f'<div class="gcat mt16">{arbol}<div>{det}</div></div>'
    if pid == "ficha":
        c = card(ch("Perfil ecológico", ic="Mountain") + txt("La altitud sale de las observaciones válidas de la especie (sin invalidar y con al menos una foto activa), con la coordenada que decidió la limpieza.", "t2 clamp2")
                 + '<div class="sep row g12">' + btn("Calcular altitudes faltantes", "o", extra="sm") + "</div>"
                 + '<div class="sep"><p class="t3 mb8 fw5">Rango de altitud efectivo (mínimo–máximo)</p><div class="row g12 ae">'
                 + field("Mínimo (m)", inp(w=112)) + field("Máximo (m)", inp(w=112)) + btn("Guardar como manual", "p", extra="sm") + btn("Volver al calculado", "o", extra="sm") + "</div></div>")
        return h + f'<div class="mt24">{c}</div>'
    if pid == "calidad":
        c1 = card(ch("Limpieza del dataset", btn("Correr la limpieza", "o", "RefreshCw", "sm"))
                  + txt("La limpieza automática solo propone; lo que decidas aquí queda registrado en la auditoría y ninguna corrida nueva lo cambia. La coordenada original nunca se borra."))
        tipos = '<div class="row g8 wrap mt16">' + "".join(f'<span class="chipf {"on" if i == 0 else ""}">{t} · 0 pendientes</span>' for i, t in enumerate(
            ["Coordenadas aproximadas", "Coordenadas atípicas", "Sin coordenada", "Todos los derechos reservados", "Sin licencia"])) + "</div>"
        c2 = card(ch("Coordenadas aproximadas", '<span class="row g6">' + btn("Pendientes (0)", "s", extra="sm") + btn("Decididos (0)", "g", extra="sm") + "</span>")
                  + txt("Ocultas por iNaturalist o con más incertidumbre que el umbral. La propuesta usa la mediana de los registros precisos de la misma especie en su celda; si hay menos del mínimo, solo se usa a nivel de celda.", "t2 mb12")
                  + txt("No queda nada por decidir en este tipo."), "mt16")
        return f'<div>{c1}{tipos}{c2}</div>'
    if pid == "ia":
        w = card(ch("Workers", badge("0"), "Cpu") + txt("Aún no se ha conectado ningún worker. Arranca model-service en el PC con GPU: al arrancar registra su encoder aquí y pide trabajo cada 15 s.", "t2 clamp3"))
        e = card(ch("Encoders registrados") + txt("Aún no hay encoders. El worker registra el suyo (el mismo ONNX del teléfono) la primera vez que se conecta.", "t2 clamp3"))
        n = card(ch("Nuevo trabajo de vectores") + '<div class="row g12 ae wrap">' + field("Encoder", sel("encoder del teléfono", 150))
                 + field("Fotos", sel("Todas las que no tienen vector", 190)) + btn("Crear trabajo", "p", "Play") + "</div>")
        q = card(ch("Cola e historial") + txt("Aún no hay trabajos. Crea uno arriba para calcular los vectores de las fotos del dataset.", "t2 clamp3"))
        return h + f'<div class="g2 mt24 g16">{w}{e}{n}{q}</div>'
    if pid == "vectorial":
        stats = "".join(f'<div class="stat"><p class="sv">—</p><p class="t3">{l}</p></div>' for l in
                        ["Vectores de este encoder", "Dimensiones", "Métrica", "Búsqueda"])
        c = card(f'<div class="g4 g12">{stats}</div><div class="sep row jb"><p class="t3 fw5">Latencia de búsqueda</p>' + btn("Medir latencia", "o", "Gauge", "sm") + "</div>")
        links = '<p class="t2 mt4"><span class="lnk">Worker que los escribe</span><span class="t3"> · </span><span class="lnk">Centroides</span></p>'
        return h + links + f'<div class="mt24">{c}</div>'
    if pid == "centroides":
        v = card('<div class="row jb as"><div>' + '<h3 class="ct">Versión del dataset</h3>'
                 + txt("Reparte las fotos entre entrenamiento, validación y prueba, siempre por individuo: las fotos de una misma observación van juntas.", "t3 mt4") + "</div></div>"
                 + '<div class="mt12">' + btn("Crear versión", "p") + "</div>")
        c = card('<div class="row jb as g12"><div>' + '<h3 class="ct">Centroides del servidor</h3>'
                 + txt("Media L2 de las fotos de entrenamiento de la versión del dataset, con el encoder del teléfono.", "t3 mt4") + "</div>" + btn("Calcular centroides", "p") + "</div>"
                 + txt("Todavía no hay un lote. Calcula los centroides con los vectores que el worker ya guardó.", "t2 mt12"), "mt16")
        return h + f'<div class="mt24">{v}{c}</div>'
    if pid == "osr":
        top = ('<div class="row jb ae mt24">' + field("Paquete (una calibración por paquete)", sel(SUB, 240)) + badge("Sin τ validado") + "</div>")
        calc = card(ch("Calcular la propuesta") + txt("Distancia de Mahalanobis mínima a las medias de las especies del paquete, con la covarianza Ledoit-Wolf de las fotos de entrenamiento (igual que el teléfono).", "t3 mb12 clamp2")
                    + '<div class="row g12 ae">' + field("KAR objetivo", sel("95 %", 150)) + btn("Calcular propuesta", "p") + "</div>", "mt16")
        filas = "".join(f'<tr><td>{k}</td><td class="r">—</td><td class="r">—</td><td class="r">—</td><td class="r">{btn("Usar", "g", extra="xs")}</td></tr>'
                        for k in ["90 %", "95 %", "97,5 %", "99 %"])
        pts = card(ch("Puntos de operación") + txt("τ más alto acepta más fotos del paquete y deja pasar más desconocidas. Elige uno o escribe el tuyo abajo.", "t3 mb8")
                   + f'<table class="tb"><thead><tr><th>KAR objetivo</th><th class="r">τ</th><th class="r">KAR medido</th><th class="r">FAR</th><th></th></tr></thead><tbody>{filas}</tbody></table>', "mt16")
        val = card(ch("Validar τ") + '<div class="row g12 ae">' + field("τ (distancia de Mahalanobis)", inp(w=140)) + field("Nota (opcional)", inp(ph="Por qué este τ"), "grow")
                   + btn("Validar τ", "p", "ShieldCheck") + "</div>", "mt16")
        return h + top + calc + pts + val
    if pid == "valtec":
        g = ('<div class="g3 g12 mt24">'
             + card(ch("Encoder del teléfono") + '<p class="t3 danger">Sin registrar.</p>')
             + card(ch("Centroides") + txt("Todavía no se calcularon.", "t3"))
             + card(ch("Umbral OSR", badge("sin validar")) + txt("Una persona lo valida en OSR.", "t3")) + "</div>")
        es = card(ch("Especies de la subregión", badge("0 entran al paquete")) + txt("Ninguna especie tiene individuos de entrenamiento ubicados en esta subregión. Sube fotos con coordenada en Imágenes y recalcula los centroides."), "mt16")
        return h + g + es
    if pid == "compilador":
        top = ('<div class="row g12 ae mt24">' + field("Subregión (un paquete por subregión)", sel(SUB + " — lista", 260))
               + '<span class="b bp" id="bcomp">' + icon("PackageCheck", 14) + '<span class="bl"><span id="btn-a">Compilar paquete</span><span id="btn-b">Compilando…</span></span></span></div>')
        apro = btn("Aprobar (científica)", "o", "ShieldCheck", "xs") + btn("Aprobar (técnica)", "o", "ShieldCheck", "xs")
        filas = (f'<tr><td>—</td><td>{badge("Borrador", "i")}</td><td class="r">—</td><td class="r">—</td><td>—</td><td>—</td><td class="r"><span class="row g6 je">{apro}</span></td></tr>'
                 f'<tr><td>—</td><td>{badge("Aprobado, sin publicar", "w")}</td><td class="r">—</td><td class="r">—</td><td>—</td><td>—</td><td class="r">{btn("Publicar", "p", "CheckCircle2", "xs")}</td></tr>')
        tb = card(ch("Versiones de esta subregión") + '<table class="tb"><thead><tr><th>Versión</th><th>Estado</th><th class="r">Especies</th><th class="r">Tamaño</th>'
                  f'<th>Compilado</th><th>Aprobaciones</th><th></th></tr></thead><tbody>{filas}</tbody></table>', "mt16")
        return h + top + tb
    return h

def pages_html():
    def body(pid):
        b = page_body(pid)
        # OSR baja (scroll) por debajo de la barra superior: el recorte es intencional.
        return re.sub(r"<(span|p|h2|h3|th|td)([ >])", r"<\1 data-layout-allow-occlusion\2", b) if pid == "osr" else b
    return "\n".join(f'<section class="page" id="p-{pid}"><div class="pin">{body(pid)}</div></section>' for pid, *_ in PAGES)

def titles_html():
    return "".join(f'<span class="ttl" id="t-{p[0]}">{p[2]}</span>' for p in PAGES)

CSS = r"""
@font-face { font-family: "Archivo"; src: url("assets/fonts/Archivo.woff2") format("woff2"); font-weight: 100 900; font-stretch: 62% 125%; }
@font-face { font-family: "Instrument Serif"; src: url("assets/fonts/InstrumentSerif-Italic.woff2") format("woff2"); font-style: italic; font-weight: 400; }
.serif { font-family: "Instrument Serif", serif; font-style: italic; font-weight: 400; }
@font-face { font-family: "Geist"; src: url("assets/fonts/Geist.woff2") format("woff2"); font-weight: 100 900; }
body { margin: 0; background: #eef5ee; }
#root { position: relative; width: 100%; height: 100%; overflow: hidden; background: #eef5ee; color: #1b1c1e; font-family: "Archivo", sans-serif; }
#t30old { position: absolute; margin: 0; left: 80px; top: 80px; width: 1680px; font-weight: 700; font-size: 36px; line-height: 1.2; color: #1b1c1e; }
#t30 { position: absolute; margin: 0; left: 80px; top: 80px; width: 1680px; font-weight: 500; font-size: 36px; line-height: 1.2; white-space: nowrap; color: #1b1c1e; }
#t30 b { font-weight: 700; }
#panel { position: absolute; left: 80px; top: 150px; width: 1760px; height: 750px; border-radius: 16px; overflow: hidden; box-sizing: border-box; border: 1px solid #38383a; background: #000; box-shadow: 0 24px 48px rgba(27, 28, 30, 0.28); transform-origin: 0 0; }
#ui { position: absolute; left: 0; top: 0; width: 1173.33px; height: 500px; transform: scale(1.5); transform-origin: 0 0; display: flex; font-family: "Geist", -apple-system, "Segoe UI", sans-serif; color: #fff; -webkit-font-smoothing: antialiased; }
.ic { display: block; flex: none; }
aside { width: 240px; flex: none; display: flex; flex-direction: column; background: #1c1c1e; border-right: 1px solid #38383a; }
.brand { height: 56px; box-sizing: border-box; flex: none; display: flex; align-items: center; gap: 8px; padding: 0 20px; border-bottom: 1px solid #38383a; }
.brand .logo { width: 28px; height: 28px; border-radius: 6px; background: #30d158; color: #062b12; display: flex; align-items: center; justify-content: center; }
.brand b { font-size: 14px; font-weight: 600; letter-spacing: -0.01em; }
nav { position: relative; flex: 1; overflow: hidden; padding: 12px 8px; }
#navc { position: relative; }
.area { display: flex; align-items: center; gap: 2px; margin-bottom: 2px; }
.arow { flex: 1; min-width: 0; height: 32px; box-sizing: border-box; display: flex; align-items: center; gap: 8px; padding: 0 8px; border-radius: 6px; font-size: 13px; color: #aeaeb2; }
.arow .aic { color: #98989d; }
.chev { width: 28px; height: 32px; flex: none; display: flex; align-items: center; justify-content: center; color: #98989d; }
.chev .ic { transform: rotate(-90deg); }
.open { margin-left: 12px; overflow: hidden; height: 0; }
.openin { margin: 2px 0 8px 0; padding-left: 8px; border-left: 1px solid #38383a; }
.sec { margin-top: 6px; }
.stitle { margin: 0; height: 18px; padding: 0 8px; font-size: 11px; line-height: 16px; font-weight: 500; text-transform: uppercase; letter-spacing: 0.05em; color: #98989d; }
.irow { height: 30px; box-sizing: border-box; display: flex; align-items: center; gap: 8px; padding: 0 8px; border-radius: 6px; font-size: 13px; color: #aeaeb2; }
#hl { position: absolute; left: 0; top: 0; width: 10px; height: 10px; border-radius: 8px; border: 2px solid #30d158; box-sizing: border-box; opacity: 0; pointer-events: none; }
.col { flex: 1; min-width: 0; display: flex; flex-direction: column; }
header { height: 56px; box-sizing: border-box; flex: none; display: flex; align-items: center; justify-content: space-between; gap: 16px; padding: 0 20px; background: #1c1c1e; border-bottom: 1px solid #38383a; }
.ttls { position: relative; width: 200px; height: 20px; }
.ttl { position: absolute; left: 0; top: 0; font-size: 14px; line-height: 20px; font-weight: 600; opacity: 0; white-space: nowrap; }
.hr { display: flex; align-items: center; gap: 12px; }
.search { width: 320px; height: 32px; box-sizing: border-box; display: flex; align-items: center; gap: 8px; padding: 0 10px; border: 1px solid #38383a; border-radius: 6px; background: #2c2c2e; color: #98989d; font-size: 14px; }
.bell { color: #aeaeb2; }
.chip { display: flex; align-items: center; padding: 4px 8px; border-radius: 999px; background: #2c2c2e; color: #aeaeb2; }
main { position: relative; flex: 1; background: #000; overflow: hidden; }
.page { position: absolute; left: 24px; top: 24px; right: 24px; opacity: 0; }
.ph1 { margin: 0; font-size: 24px; line-height: 32px; font-weight: 700; letter-spacing: -0.02em; }
.pblurb { margin: 4px 0 0 0; font-size: 14px; line-height: 20px; color: #aeaeb2; white-space: nowrap; }
.kgrid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; }
.card { border-radius: 8px; border: 1px solid #38383a; background: #1c1c1e; padding: 16px; }
.kic { width: 32px; height: 32px; margin-bottom: 12px; border-radius: 6px; background: rgba(48, 209, 88, 0.16); color: #30d158; display: flex; align-items: center; justify-content: center; }
.kval { margin: 0; font-size: 24px; line-height: 32px; font-weight: 600; }
.klab { margin: 0; font-size: 12px; line-height: 16px; color: #aeaeb2; }
.khint { margin: 4px 0 0 0; font-size: 11px; line-height: 16px; color: #98989d; }
.pin { position: relative; }
.chip { gap: 6px; padding: 4px 4px 4px 8px !important; }
.uname { font-size: 12px; line-height: 16px; color: #fff; white-space: nowrap; }
.uout { display: flex; align-items: center; justify-content: center; width: 28px; height: 28px; color: #98989d; }
.pblurb { white-space: normal !important; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; max-width: 880px; }
.row { display: flex; align-items: center; } .jb { justify-content: space-between; } .je { justify-content: flex-end; } .ae { align-items: flex-end; } .as { align-items: flex-start; } .wrap { flex-wrap: wrap; }
.g6 { gap: 6px; } .g8 { gap: 8px; } .g12 { gap: 12px; } .g16 { gap: 16px; }
.mt4 { margin-top: 4px; } .mt12 { margin-top: 12px; } .mt16 { margin-top: 16px; } .mt24 { margin-top: 24px; } .mb8 { margin-bottom: 8px; } .mb12 { margin-bottom: 12px; }
.p0 { padding: 0 !important; } .p8 { padding: 8px; } .p12 { padding: 12px; } .p20 { padding: 20px !important; } .px20 { padding-left: 20px; padding-right: 20px; } .pb20 { padding-bottom: 20px; }
.stack12 > * + * { margin-top: 12px; }
.g2 { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; } .g2.g16 { gap: 16px; } .g3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; } .g4 { display: grid; grid-template-columns: repeat(4, 1fr); }
.c2 { grid-column: span 2; } .grow { flex: 1; } .w100 { width: 100%; box-sizing: border-box; } .fw5 { font-weight: 500; }
.t2 { margin: 0; font-size: 14px; line-height: 20px; color: #aeaeb2; } .t3 { margin: 0; font-size: 12px; line-height: 16px; color: #98989d; }
.clamp2, .clamp3 { display: -webkit-box; -webkit-box-orient: vertical; overflow: hidden; } .clamp2 { -webkit-line-clamp: 2; } .clamp3 { -webkit-line-clamp: 3; }
.danger { color: #ff453a !important; } .ok { color: #30d158; flex: none; } .lnk { font-size: 12px; font-weight: 500; color: #30d158; }
.chd { margin-bottom: 12px; display: flex; align-items: center; justify-content: space-between; gap: 8px; }
.ct { margin: 0; display: flex; align-items: center; gap: 6px; font-size: 14px; line-height: 20px; font-weight: 600; color: #fff; }
.cti { color: #fff; } .big { font-size: 16px; font-weight: 600; } .h2i { margin: 2px 0 0 0; font-size: 18px; line-height: 28px; font-weight: 600; font-style: italic; }
.sum { margin: 0; display: flex; align-items: center; gap: 6px; padding: 16px 20px; font-size: 14px; font-weight: 600; color: #fff; }
.b { position: relative; display: inline-flex; align-items: center; justify-content: center; gap: 6px; height: 34px; padding: 0 14px; box-sizing: border-box; border-radius: 6px; font-size: 14px; font-weight: 500; white-space: nowrap; flex: none; }
.b.sm { height: 30px; padding: 0 10px; font-size: 12px; } .b.xs { height: 26px; padding: 0 8px; font-size: 12px; }
.bp { background: #30d158; color: #062b12; } .bo { border: 1px solid #38383a; color: #fff; background: transparent; } .bg { color: #aeaeb2; } .bs { background: #2c2c2e; color: #fff; }
.bl { position: relative; display: inline-grid; } .bl > span { grid-area: 1 / 1; }
#btn-b { opacity: 0; }
.fld { display: flex; flex-direction: column; gap: 6px; } .fl { font-size: 12px; line-height: 16px; font-weight: 500; color: #aeaeb2; }
.in { display: flex; align-items: center; gap: 8px; height: 34px; box-sizing: border-box; padding: 0 10px; border: 1px solid #38383a; border-radius: 6px; background: #1c1c1e; color: #fff; font-size: 14px; white-space: nowrap; overflow: hidden; }
.in.ph { color: #8e8e93; } .in.sel { justify-content: space-between; } .in.sel .ic { color: #98989d; }
.cb { width: 14px; height: 14px; box-sizing: border-box; border: 1px solid #6e6e73; border-radius: 3px; } .cb.on { background: #30d158; border-color: #30d158; }
.code { max-width: 560px; overflow: hidden; white-space: nowrap; text-overflow: ellipsis; border-radius: 6px; background: #2c2c2e; padding: 4px 8px; font-family: ui-monospace, Menlo, monospace; font-size: 11px; color: #aeaeb2; }
.bd { display: inline-flex; align-items: center; padding: 2px 8px; border-radius: 999px; font-size: 12px; line-height: 16px; font-weight: 500; white-space: nowrap; }
.bdn { background: #2c2c2e; color: #aeaeb2; } .bda { background: rgba(48, 209, 88, 0.16); color: #30d158; } .bdi { background: rgba(100, 210, 255, 0.12); color: #64d2ff; } .bdw { background: rgba(255, 159, 10, 0.15); color: #ff9f0a; }
.bb { border-bottom: 1px solid #38383a; } .sep { margin-top: 16px; padding-top: 16px; border-top: 1px solid #38383a; }
.gcur { display: grid; grid-template-columns: 200px 1fr; gap: 24px; } .gcat { display: grid; grid-template-columns: 240px 1fr; gap: 24px; }
.lst { list-style: none; margin: 0; padding: 0; } .lst li { padding: 8px 12px; font-size: 14px; color: #fff; border-bottom: 1px solid #38383a; } .lst li.on { background: rgba(48, 209, 88, 0.1); }
.fam { margin: 0; padding: 4px 8px; font-size: 12px; font-weight: 600; color: #aeaeb2; } .sp { margin: 0; padding: 5px 8px 5px 14px; font-size: 13px; color: #fff; border-radius: 6px; } .sp.on { background: rgba(48, 209, 88, 0.16); color: #30d158; }
.chipf { border: 1px solid #38383a; border-radius: 999px; padding: 4px 10px; font-size: 12px; color: #aeaeb2; white-space: nowrap; } .chipf.on { border-color: #30d158; background: rgba(48, 209, 88, 0.16); color: #30d158; }
.grp { border: 1px solid #38383a; border-radius: 8px; padding: 12px; } .ml { margin-left: auto; }
.tiles { list-style: none; margin: 0; padding: 0; display: grid; grid-template-columns: repeat(6, 1fr); gap: 8px; }
.tile { border: 1px solid #38383a; border-radius: 6px; overflow: hidden; } .tile .sq { display: block; aspect-ratio: 1 / 1; background: #2c2c2e; } .tile .tf { display: block; border-top: 1px solid #38383a; padding: 2px 4px; }
.stat { border-radius: 6px; background: #2c2c2e; padding: 12px; } .sv { margin: 0; font-size: 14px; font-weight: 600; color: #fff; }
.tb { width: 100%; border-collapse: collapse; font-size: 12px; } .tb th { padding: 6px 8px; text-align: left; font-weight: 500; color: #98989d; border-bottom: 1px solid #38383a; white-space: nowrap; }
.tb td { padding: 6px 8px; color: #fff; border-bottom: 1px solid #38383a; white-space: nowrap; } .tb .r { text-align: right; }
#pie { position: absolute; margin: 0; left: 80px; top: 960px; width: 1760px; height: 34px; font-weight: 500; font-size: 28px; line-height: 1.2; color: #1b1c1e; }
#pie span { position: absolute; left: 0; top: 0; white-space: nowrap; opacity: 0; }
#paq { position: absolute; left: 0; top: 0; display: flex; flex-direction: column; align-items: center; opacity: 0; }
#paqic { width: 120px; height: 120px; color: #1f7a33; }
#t31 { margin: 96px 0 0 0; white-space: nowrap; font-weight: 700; font-size: 44px; line-height: 1.2; color: #1b1c1e; opacity: 0; }
"""

# Motor común: estados del nav y cambios de página, todo seek-safe (set/to en la timeline).
JS_CORE = r"""
const tl = gsap.timeline({ paused: true });
const EASE = "expo.out";
const $ = (s) => document.querySelector(s);
const PAGES = __PAGES__;
const OPEN = $("#open-modelo"), NAVC = $("#navc"), VIEW = 420;
const OPEN_H = OPEN.scrollHeight;
const offTop = (el) => { let y = 0; while (el && el !== NAVC) { y += el.offsetTop; el = el.offsetParent; } return y; };
// Cajas en coordenadas de #navc, con Modelo abierto (siempre lo está cuando se resalta algo).
const box = (el) => ({ x: el.offsetLeft, y: offTop(el), w: el.offsetWidth, h: el.offsetHeight });
// Todas las cajas se miden una vez con Modelo abierto (fuentes y alturas fijas: el resultado no depende del cuadro).
gsap.set(OPEN, { height: OPEN_H });
const CACHE = {};
const CLIP = [...document.querySelectorAll(".area, .stitle, .irow")];
document.querySelectorAll(".sec, .irow, .area, .stitle").forEach((el) => { CACHE[el.id] = box(el); });
const NAV_H = NAVC.scrollHeight;
const secBox = (name) => { const b = CACHE["s-" + name]; return { x: b.x - 4, y: b.y - 2, w: b.w + 8, h: b.h + 4 }; };
const rowBox = (id) => { const b = CACHE["r-" + id]; return { x: b.x - 2, y: b.y - 2, w: b.w + 4, h: b.h + 4 }; };
const scrollFor = (b) => { const max = Math.max(0, NAV_H - VIEW); let s = Math.max(0, b.y + b.h + 12 - VIEW); if (b.y - s < 8) s = b.y - 8; return Math.min(max, Math.max(0, s)); };
// Filas fuera de la vista del nav: ya las recorta el overflow; además quedan en visibility hidden.
const inView = (el, sc) => { const b = CACHE[el.id]; return b.y + b.h > sc && b.y < sc + VIEW; };
function clipAt(sc, t) {
  CLIP.forEach((el) => {
    if (el.closest(".open") && areaOf(cur) !== "modelo" && t === undefined) return;
    const v = inView(el, sc) ? "visible" : "hidden";
    if (t === undefined) gsap.set(el, { visibility: v }); else if (v === "visible") tl.set(el, { visibility: v }, t); else tl.set(el, { visibility: v }, t + 0.4);
  });
}
const ON_AREA = { backgroundColor: "#2c2c2e", color: "#ffffff" }, OFF_AREA = { backgroundColor: "rgba(44,44,46,0)", color: "#aeaeb2" };
const ON_ROW = { backgroundColor: "rgba(48,209,88,0.16)", color: "#30d158" }, OFF_ROW = { backgroundColor: "rgba(48,209,88,0)", color: "#aeaeb2" };
const areaOf = (pid) => (pid === "dashboard" ? "inicio" : "modelo");

// Estado de partida de la escena (lo que dejó la anterior).
function start(pid, hl) {
  gsap.set(".arow", OFF_AREA); gsap.set(".irow", OFF_ROW);
  gsap.set("#a-" + areaOf(pid), ON_AREA); gsap.set("#a-" + areaOf(pid) + " .aic", { color: "#30d158" });
  const row = PAGES[pid];
  if (row) gsap.set("#r-" + row, ON_ROW);
  const open = areaOf(pid) === "modelo";
  gsap.set(OPEN, open ? { height: OPEN_H, visibility: "visible" } : { height: 0, visibility: "hidden" });
  gsap.set("#chev-modelo .ic", { rotation: open ? 0 : -90 });
  gsap.set(".page", { opacity: 0 }); gsap.set("#p-" + pid, { opacity: 1 });
  gsap.set(".ttl", { opacity: 0 }); gsap.set("#t-" + pid, { opacity: 1 });
  cur = pid;
  if (hl) { gsap.set("#hl", { opacity: 1, x: hl.x, y: hl.y, width: hl.w, height: hl.h }); gsap.set(NAVC, { y: -scrollFor(hl) }); clipAt(scrollFor(hl)); }
  else if (open) clipAt(0);
}
let cur = null;

// Cambia de pantalla sin recargar: fila activa, topbar y lienzo.
function go(t, pid, hl) {
  const prev = cur;
  if (areaOf(prev) !== areaOf(pid)) {
    tl.to("#a-" + areaOf(prev), { ...OFF_AREA, duration: 0.15 }, t);
    tl.to("#a-" + areaOf(prev) + " .aic", { color: "#98989d", duration: 0.15 }, t);
    tl.to("#a-" + areaOf(pid), { ...ON_AREA, duration: 0.15 }, t);
    tl.to("#a-" + areaOf(pid) + " .aic", { color: "#30d158", duration: 0.15 }, t);
    if (areaOf(pid) === "modelo") {
      tl.set(OPEN, { visibility: "visible" }, t);
      tl.to(OPEN, { height: OPEN_H, duration: 0.35, ease: "power3.out" }, t);
      tl.to("#chev-modelo .ic", { rotation: 0, duration: 0.25, ease: "power2.out" }, t);
    }
  }
  if (PAGES[prev]) tl.to("#r-" + PAGES[prev], { ...OFF_ROW, duration: 0.15 }, t);
  if (PAGES[pid]) tl.to("#r-" + PAGES[pid], { ...ON_ROW, duration: 0.15 }, t);
  tl.to("#t-" + prev, { opacity: 0, duration: 0.12 }, t);
  tl.to("#t-" + pid, { opacity: 1, duration: 0.2 }, t + 0.08);
  tl.to("#p-" + prev, { opacity: 0, y: -6, duration: 0.15, ease: "power2.in" }, t);
  tl.fromTo("#p-" + pid, { opacity: 0, y: 8 }, { opacity: 1, y: 0, duration: 0.3, ease: EASE, immediateRender: false }, t + 0.1);
  if (hl) {
    if (!hlShown) { tl.set("#hl", { x: hl.x, y: hl.y, width: hl.w, height: hl.h }, t); tl.fromTo("#hl", { opacity: 0 }, { opacity: 1, duration: 0.25, immediateRender: false }, t + 0.1); hlShown = true; }
    else tl.to("#hl", { x: hl.x, y: hl.y, width: hl.w, height: hl.h, duration: 0.4, ease: "power3.inOut" }, t);
    tl.to(NAVC, { y: -scrollFor(hl), duration: 0.4, ease: "power3.inOut" }, t);
    clipAt(scrollFor(hl), t);
  }
  cur = pid;
}
let hlShown = false;
function foot(t, from, to) {
  if (from) tl.to(from, { y: -12, opacity: 0, duration: 0.25, ease: "power2.in" }, t);
  if (to) tl.fromTo(to, { y: 16, opacity: 0 }, { y: 0, opacity: 1, duration: 0.4, ease: EASE }, t + 0.15);
}
"""

FOOTS = {
    30: "Conseguir las fotos y nombrar las especies.",
    31: "Limpiar lo que no debe entrenar.",
    32: "Procesar: vectores, centroides y lo que se confunde.",
    33: "Una persona valida el rechazo. Luego se mira si está listo.",
    34: "Compilar y publicar el paquete de la región.",
}

# T30 queda arriba (x=80, top=80) de S29 a S34; cada escena tiene su pie (top=960) y lo cambia por el suyo al empezar.
SCENES = {
    29: dict(title="Resumen del admin", dur=4, js=r"""
// 136.00–140.00. T30 ya está arriba (fin de S28): cambia a la frase nueva, quieta desde 136.40. Entra el panel en /dashboard.
start("dashboard");
tl.to("#t30old", { opacity: 0, y: -12, duration: 0.2, ease: "power2.in" }, 0);
tl.fromTo("#t30", { y: 12, opacity: 0 }, { y: 0, opacity: 1, duration: 0.3, ease: EASE }, 0.1);
tl.fromTo("#panel", { y: 40, opacity: 0 }, { y: 0, opacity: 1, duration: 0.5, ease: EASE }, 0.25);
tl.fromTo("#p-dashboard .card", { y: 12, opacity: 0 }, { y: 0, opacity: 1, duration: 0.4, ease: EASE, stagger: 0.08 }, 0.7);
"""),
    30: dict(title="Conseguir", dur=4, js=r"""
// 140.00–144.00. Se abre Modelo y se resalta Conseguir. Scraping, Imágenes y Especies, sin recargar.
start("dashboard");
foot(0.25, null, "#f30");
go(0.5, "scraping", secBox("Conseguir"));
go(1.75, "curacion");
go(3.0, "catalogo");
"""),
    31: dict(title="Limpiar", dur=3.5, js=r"""
// 144.00–147.50. El resalte baja a Limpiar: Ficha y Calidad.
start("catalogo", secBox("Conseguir")); hlShown = true;
gsap.set("#f30", { opacity: 1 });
foot(0.1, "#f30", "#f31");
go(0.25, "ficha", secBox("Limpiar"));
go(1.75, "calidad");
"""),
    32: dict(title="Procesar", dur=4, js=r"""
// 147.50–151.50. Procesar: Worker, DB vectorial, Centroides. Nada termina en cámara.
start("calidad", secBox("Limpiar")); hlShown = true;
gsap.set("#f31", { opacity: 1 });
foot(0.1, "#f31", "#f32");
go(0.25, "ia", secBox("Procesar"));
go(1.5, "vectorial");
go(2.5, "centroides");
"""),
    33: dict(title="Validar", dur=3.5, js=r"""
// 151.50–155.00. OSR (baja hasta «Validar τ») y luego Validación: el resalte va fila por fila.
start("centroides", secBox("Procesar")); hlShown = true;
gsap.set("#f32", { opacity: 1 });
foot(0.1, "#f32", "#f33");
go(0.25, "osr", rowBox("osr"));
const OSR_Y = -Math.max(0, $("#p-osr .pin").offsetHeight - 396);
tl.to("#p-osr .pin", { y: OSR_Y, duration: 0.6, ease: "power3.inOut" }, 0.85);
go(1.75, "valtec", rowBox("valtec"));
"""),
    34: dict(title="Publicar", dur=4, js=r"""
// 155.00–159.00. Release: se pulsa «Compilar paquete», el rótulo pasa a «Compilando…» y vuelve. No se publica nada.
start("valtec", rowBox("valtec")); hlShown = true;
gsap.set("#f33", { opacity: 1 });
foot(0.1, "#f33", "#f34");
go(0.25, "compilador", rowBox("compilador"));
tl.to("#bcomp", { scale: 0.96, duration: 0.08, ease: "power2.out" }, 0.95).to("#bcomp", { scale: 1, duration: 0.2, ease: "power2.out" }, 1.03);
tl.set("#btn-a", { opacity: 0 }, 1.0).set("#btn-b", { opacity: 1 }, 1.0);
tl.set("#btn-b", { opacity: 0 }, 2.75).set("#btn-a", { opacity: 1 }, 2.75);
"""),
    35: dict(title="Paquete listo", dur=4, js=r"""
// 159.00–163.00. La pantalla de Release se reduce a la izquierda (centro y=540). A la derecha, el paquete baja 80 px y aterriza; T31 96 px debajo.
start("compilador", rowBox("compilador")); hlShown = true;
gsap.set("#t30", { opacity: 1 }); gsap.set("#f34", { opacity: 1 });
const S = 0.42, PW = 1760, PH = 750;
const px = 80, py = 540 - (PH * S) / 2;                     // centro vertical del panel reducido: y=540
tl.to(["#t30", "#f34"], { opacity: 0, y: -12, duration: 0.3, ease: "power2.in" }, 0);
tl.to("#panel", { x: px - 80, y: py - 150, scale: S, duration: 0.7, ease: "expo.inOut" }, 0);
// grupo del paquete: centrado en la columna derecha y en y=540
const colL = px + PW * S + 40, colR = 1840;
const g = $("#paq"), gw = g.offsetWidth, gh = g.offsetHeight;
gsap.set(g, { x: (colL + colR) / 2 - gw / 2, y: 540 - gh / 2 });
tl.set(g, { opacity: 1 }, 0.5);
tl.fromTo("#paqic", { y: -80, opacity: 0 }, { y: 0, opacity: 1, duration: 0.8, ease: "back.out(1.7)" }, 0.5);
tl.fromTo("#t31", { y: 16, opacity: 0 }, { y: 0, opacity: 1, duration: 0.5, ease: EASE }, 1.0);
"""),
}

def build(n):
    sc = SCENES[n]
    d = os.path.join(ESC, f"s{n}")
    os.makedirs(os.path.join(d, "assets", "fonts"), exist_ok=True)
    os.makedirs(os.path.join(d, "capturas"), exist_ok=True)
    shutil.copy(os.path.join(ESC, "s24", "assets", "fonts", "Archivo.woff2"), os.path.join(d, "assets", "fonts"))
    shutil.copy(os.path.join(SCR, "Geist.woff2"), os.path.join(d, "assets", "fonts"))
    extra = ""
    if n == 29:
        extra += '      <p id="t30old">Ahora con el modo admin puedes repetir el ciclo</p>\n'
    if 29 <= n <= 35:
        extra += '      <p id="t30">Ahora con el modo admin puedes tener <b>control total</b> del sistema</p>\n'
    if 30 <= n <= 35:
        extra += '      <p id="pie">' + "".join(f'<span id="f{k}">{html.escape(v)}</span>' for k, v in FOOTS.items() if k in (n - 1, n)) + "</p>\n"
    if n == 35:
        extra += ('      <div id="paq"><div id="paqic">' + icon("Package", 120, 1.75) + '</div>'
                  '<p id="t31">y así obtienes un nuevo paquete listo para usar</p></div>\n')
    pages = json.dumps({p[0]: p[1] for p in PAGES})
    doc = f"""<!doctype html>
<html lang="es">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1920, height=1080" />
    <title>ANURA S{n} {sc['title']}</title>
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
    <style>{CSS}    </style>
  </head>
  <body>
    <div id="root" data-composition-id="s{n}" data-start="0" data-width="1920" data-height="1080" data-duration="{sc['dur']}" data-fps="60">
{extra}
      <div id="panel" data-layout-allow-overflow>
        <div id="ui">
          <aside>
            <div class="brand"><span class="logo">{icon("Leaf", 16, 2.5)}</span><b>ANURA Admin</b></div>
            <nav>
{nav_html()}
            </nav>
          </aside>
          <div class="col">
            <header data-layout-allow-occlusion>
              <div class="ttls">{titles_html()}</div>
              <div class="hr"><div class="search">{icon("Search", 14)}<span>Ir a una pantalla…</span></div><span class="bell">{icon("Bell", 18)}</span><span class="chip">{icon("CircleUserRound", 16)}<span class="uname">Sebastián Martínez · super usuario</span><span class="uout">{icon("LogOut", 14)}</span></span></div>
            </header>
            <main>
{pages_html()}
            </main>
          </div>
        </div>
      </div>
    </div>

    <script>
{JS_CORE.replace("__PAGES__", pages)}
{sc['js']}
window.__timelines["s{n}"] = tl;
    </script>
  </body>
</html>
"""
    open(os.path.join(d, "index.html"), "w", encoding="utf-8").write(doc)

import sys
for n in (map(int, sys.argv[1:]) if len(sys.argv) > 1 else SCENES):
    build(n)
    print("ok", n)
