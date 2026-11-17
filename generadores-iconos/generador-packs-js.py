# -*- coding: utf-8 -*-
"""Genera pc/static/packs.js con los paquetes de iconos integrados en iMandro:
Photoshop (Estilo 1 Moderno Oscuro y Estilo 5 Profesional Pro) y Windows (Iconos web).
Cada icono va como data URI (documento independiente: sin choque de degradados).

Desde la 1.7.2, en los dos paquetes de Photoshop las entradas que son una
herramienta de la barra o un comando real de Photoshop con equivalente en el
«Photoshop Workbench Icon Pack» de GitHub (redibujo fiel de Jean Almeida,
licencia MIT declarada en su README; copia en Photoshop-Completo/fuente-ulanzi/)
enseñan ese PNG en vez del dibujo propio. Las entradas sin equivalente
conservan su SVG de cada estilo. El mapeo completo y los motivos están en
REGISTRO-CAMBIOS-1.7.2.md. Los PNG con baldosa se incrustan reducidos a
paleta de 256 colores (visualmente idénticos a tamaño de botón, ~8 veces
más ligeros); los glifos sin fondo van como PNG RGBA completos desde la
segunda reedición de la 1.7.3 (ver más abajo). Las fuentes del proyecto
quedan intactas.

Desde la 1.7.3, esos PNG van SIN la baldosa negra del pack: solo el glifo
blanco sobre transparente (procesados en Photoshop-Completo/ulanzi-sin-fondo/
con alfa por «blancura»: min(r,g,b) reforzado; el glifo queda grande sobre
el color del botón, como los demás iconos). Excepción: los iconos cuyo
distintivo de color es parte del glifo (el «+» azul de Nuevo, las flechas
azules de Abrir/Guardar/Exportar, la «i» azul de Información y el candado
azul de Bloquear capa) conservan la baldosa, porque sin ella cuatro
documentos quedarían indistinguibles y el candado se perdería; ver
EXCEPCIONES_BALDOSA y REGISTRO-CAMBIOS-1.7.3.md.

Reedición de la 1.7.3 (2026-11-07, sin cambio de versión por orden de
Liesky): los glifos de ulanzi-sin-fondo/ se reencuadraron casi sin
margen — el dibujo ocupa ~94 % del marco en vez del ~82 % anterior —
porque en el panel se veían chiquitos frente a los demás iconos. El
proceso de «blancura» es el mismo; solo cambia el reencuadre.

Segunda reedición de la 1.7.3 (2026-11-07, también sin cambio de
versión): aun reencuadrados, los glifos dibujaban ~15 px en la caja
de 30 px del panel frente a los 25-27 px de los demás iconos, porque
el arte trae franjas tenues (su núcleo con alfa fuerte era ~50 % de
la extensión) y la paleta las rebajaba aún más. Ahora los archivos
de ulanzi-sin-fondo/ se generan con la curva reforzada
a' = clamp((min(r,g,b)-28)*4) — anulando antes la banda exterior de
14 px, donde vive la línea de marco de la baldosa — y se incrustan
como PNG RGBA completos, SIN cuantizar a paleta. Resultado medido:
extensión con alfa fuerte >= 98 % de la extensión total en los 60
glifos. Las excepciones con baldosa se incrustan como siempre (con
paleta): sus data URIs no cambian."""
import os, base64, json, re, io

RAIZ = os.path.dirname(os.path.abspath(__file__))
SALIDA = os.path.join(RAIZ, "..", "pc", "static", "packs.js")
CARPETA_ULANZI = os.path.join(RAIZ, "Photoshop-Completo", "fuente-ulanzi")
CARPETA_SIN_FONDO = os.path.join(RAIZ, "Photoshop-Completo", "ulanzi-sin-fondo")

# Códigos Ulanzi que CONSERVAN la baldosa en la 1.7.3: su distintivo azul es
# parte del glifo y el proceso de «blancura» lo borraría (ver docstring).
EXCEPCIONES_BALDOSA = {
    2454,  # new: el «+» azul distingue el documento nuevo
    2457,  # open: la flecha azul de abrir
    2474,  # save: la flecha azul de guardar
    2418,  # export as: la flecha azul de exportar
    2419,  # file info: la «i» azul de información
    2444,  # lock layers: el candado azul es el significado del icono
}

FUENTES = [
    ("ps1", "Photoshop · Moderno Oscuro", os.path.join(RAIZ, "Photoshop-Completo", "Estilo-1-Moderno-Oscuro")),
    ("ps5", "Photoshop · Profesional Pro", os.path.join(RAIZ, "Photoshop-Completo", "Estilo-5-Profesional-Pro")),
    ("win", "Windows · Iconos web", os.path.join(RAIZ, "Windows-Hibrido-Web")),
]

# Entrada de los paquetes de Photoshop (ruta sin extensión, igual en ps1 y
# ps5) -> código del icono equivalente en el pack Ulanzi (el número _NNNN_
# del nombre de archivo, único en el pack).
SUSTITUCIONES_PS = {
    "01_Archivo/001_nuevo": 2454,                    # new
    "01_Archivo/002_abrir": 2457,                    # open
    "01_Archivo/003_guardar": 2474,                  # save
    "01_Archivo/007_exportar": 2418,                 # export as (el principal; también hay quick export png)
    "01_Archivo/009_información": 2419,              # file info
    "01_Archivo/011_deshacer": 2489,                 # undo
    "02_Seleccion/016_marco_rectangular": 2470,      # rectangular marquee
    "02_Seleccion/017_marco_elíptico": 2416,         # elliptical marquee
    "02_Seleccion/018_lazo": 2438,                   # lasso
    "02_Seleccion/019_lazo_poligonal": 2466,         # polygonal lasso
    "02_Seleccion/020_lazo_magnético": 2447,         # magnetic lasso
    "02_Seleccion/021_selección_rápida": 2468,       # quick selection
    "02_Seleccion/022_varita_mágica": 2446,          # magic wand
    "03_Navegacion/031_recortar": 2405,              # crop
    "03_Navegacion/032_recorte_perspectiva": 2464,   # perspective crop
    "03_Navegacion/033_sector": 2480,                # slice
    "03_Navegacion/034_mover": 2450,                 # move
    "03_Navegacion/035_mesa_de_trabajo": 2388,       # artboard
    "03_Navegacion/037_regla": 2473,                 # ruler
    "03_Navegacion/038_nota": 2455,                  # note
    "03_Navegacion/039_mano": 2430,                  # hand
    "03_Navegacion/040_zoom": 2492,                  # zoom
    "03_Navegacion/041_zoom": 2492,                  # zoom
    "03_Navegacion/042_rotar_vista": 2472,           # rotate view
    "04_Pinceles_Retoque/046_pincel": 2394,          # brush
    "04_Pinceles_Retoque/047_lápiz": 2463,           # pencil
    "04_Pinceles_Retoque/048_pincel_mezclador": 2449,  # mixer brush
    "04_Pinceles_Retoque/049_borrador": 2417,        # eraser
    "04_Pinceles_Retoque/050_borrador_de_fondo": 2390,  # background eraser
    "04_Pinceles_Retoque/051_borrador_mágico": 2445,    # magic eraser
    "04_Pinceles_Retoque/052_degradado": 2429,       # gradient
    "04_Pinceles_Retoque/053_bote_de_pintura": 2458,    # paint bucket
    "04_Pinceles_Retoque/054_desenfocar": 2392,      # blur (herramienta)
    "04_Pinceles_Retoque/055_enfocar": 2476,         # sharpen (herramienta)
    "04_Pinceles_Retoque/056_dedo": 2481,            # smudge
    "04_Pinceles_Retoque/057_sobreexponer": 2412,    # dodge
    "04_Pinceles_Retoque/058_subexponer": 2395,      # burn
    "04_Pinceles_Retoque/059_esponja": 2484,         # sponge
    "04_Pinceles_Retoque/060_clonar": 2396,          # clone stamp
    "04_Pinceles_Retoque/061_pincel_corrector": 2431,   # healing brush
    "04_Pinceles_Retoque/062_parche": 2460,          # patch
    "04_Pinceles_Retoque/063_mover_contenido": 2400,    # content-aware move
    "04_Pinceles_Retoque/064_ojos_rojos": 2471,      # red eye
    "05_Capas/068_grupo": 2453,                      # new group
    "05_Capas/076_bloquear_capa": 2444,              # lock layers
    "05_Capas/079_alinear_capas": 2383,              # align horizontal centers (el principal; también hay align vertical centers)
    "06_Color/081_niveles": 2441,                    # levels
    "06_Color/085_equilibrio_de_color": 2382,        # adjust color balance
    "06_Color/086_blanco_y_negro": 2380,             # adjust black and white
    "07_Filtros/102_licuar": 2443,                   # liquify
    "07_Filtros/107_filtros_neuronales": 2451,       # neutral filters (así los nombra el pack: son los Neural Filters)
    "08_Texto_Formas/111_texto": 2434,               # horizontal type
    "08_Texto_Formas/112_texto_vertical": 2491,      # vertical type
    "08_Texto_Formas/114_rectángulo": 2469,          # rectangle
    "08_Texto_Formas/115_elipse": 2415,              # ellipse
    "08_Texto_Formas/116_línea": 2442,               # line
    "08_Texto_Formas/117_forma_personalizada": 2407,    # custom shape
    "08_Texto_Formas/118_pluma": 2462,               # pen
    "08_Texto_Formas/119_pluma_curvatura": 2406,     # curvature pen
}

# Entradas NUEVAS de los paquetes de Photoshop (1.7.2): dos herramientas de la
# barra que no tenían entrada propia entre las 120 y que la página
# «Herramientas» necesita con el icono del pack. No sustituyen a ninguna:
# «Seleccionar sujeto» (comando) sigue con su dibujo, y la herramienta
# Selección de objetos es esta otra; «Quitar manchas» (Pincel corrector
# puntual) es distinta del «Pincel corrector» (061).
EXTRAS_PS = [
    ("02_Seleccion/023_selección_de_objetos", 2456),     # object selection
    ("04_Pinceles_Retoque/061_quitar_manchas", 2485),   # spot healing brush
]

_cache_ulanzi = {}

def uri_ulanzi(codigo):
    """Data URI del icono del pack Ulanzi con ese código. Desde la 1.7.3
    usa la versión sin fondo (solo el glifo blanco) de ulanzi-sin-fondo/,
    salvo los códigos de EXCEPCIONES_BALDOSA, que usan el PNG original
    con su baldosa. Desde la segunda reedición de la 1.7.3, los glifos
    sin fondo se incrustan como PNG RGBA completos, SIN cuantizar a
    paleta (la paleta rebajaba su franja tenue y en el panel se veían
    chiquitos); las excepciones con baldosa siguen con paleta, como en
    la 1.7.2, y sus URIs no cambian."""
    if codigo in _cache_ulanzi:
        return _cache_ulanzi[codigo]
    from PIL import Image
    if codigo not in EXCEPCIONES_BALDOSA:
        ruta_sin = os.path.join(CARPETA_SIN_FONDO, "ulanzi-%d.png" % codigo)
        if os.path.exists(ruta_sin):
            img = Image.open(ruta_sin).convert("RGBA")
            buf = io.BytesIO()
            img.save(buf, "PNG", optimize=True)
            uri = "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode("ascii")
            _cache_ulanzi[codigo] = uri
            return uri
    nombre = None
    for f in os.listdir(CARPETA_ULANZI):
        if f.endswith(".png") and ("_%d_" % codigo) in f:
            nombre = f
            break
    if nombre is None:
        raise FileNotFoundError("icono Ulanzi %d no encontrado en %s" % (codigo, CARPETA_ULANZI))
    img = Image.open(os.path.join(CARPETA_ULANZI, nombre)).convert("RGBA")
    buf = io.BytesIO()
    img.quantize(colors=256, method=Image.FASTOCTREE).save(buf, "PNG", optimize=True)
    uri = "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode("ascii")
    _cache_ulanzi[codigo] = uri
    return uri

def nombre_bonito(stem):
    n = re.sub(r"^\d+_", "", stem).replace("_", " ").strip()
    return n[:1].upper() + n[1:] if n else stem

iconos = {}
for prefijo, paquete, carpeta in FUENTES:
    for dirpath, _dirs, files in os.walk(carpeta):
        for f in sorted(files):
            if not f.endswith(".svg"):
                continue
            rel = os.path.relpath(os.path.join(dirpath, f), carpeta).replace(os.sep, "/")
            stem = f[:-4]
            clave = rel[:-4]
            if prefijo in ("ps1", "ps5") and clave in SUSTITUCIONES_PS:
                datos = uri_ulanzi(SUSTITUCIONES_PS[clave])
            else:
                with open(os.path.join(dirpath, f), "rb") as fh:
                    b64 = base64.b64encode(fh.read()).decode("ascii")
                datos = "data:image/svg+xml;base64," + b64
            iconos[f"{prefijo}/{clave}"] = {
                "n": nombre_bonito(stem),
                "p": paquete,
                "d": datos,
            }
    if prefijo in ("ps1", "ps5"):
        for clave, codigo in EXTRAS_PS:
            iconos[f"{prefijo}/{clave}"] = {
                "n": nombre_bonito(clave.split("/")[-1]),
                "p": paquete,
                "d": uri_ulanzi(codigo),
            }

js = ("// iMandro · Paquetes de iconos integrados (Photoshop y Windows)\n"
      "// Generado por paquetes-iconos/generador-packs-js.py — no editar a mano.\n"
      "const PACK_ICONOS = " + json.dumps(iconos, ensure_ascii=False) + ";\n")
with open(SALIDA, "w", encoding="utf-8") as fh:
    fh.write(js)
print(f"{len(iconos)} iconos -> {SALIDA} ({os.path.getsize(SALIDA)} bytes)")
