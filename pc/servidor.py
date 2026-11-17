# -*- coding: utf-8 -*-
"""iMandro v1.0 — Programa de la PC.
Recibe los toques de los teléfonos por la red local y ejecuta la acción
en esta computadora (atajos de teclado, acciones de Photoshop, programas…).
También sirve el editor con el que se cambian los botones.
Creador: Liesky Vázquez.

1.7.7 — los arreglos de la auditoría de la 1.7.6:
- Sondeo ligero del panel: GET /api/estado devuelve solo la versión,
  la revisión de la configuración y el programa en primer plano; la
  configuración entera solo viaja cuando su revisión cambia.
- Las teclas sueltas que no son A-Z/0-9 se traducen con VkKeyScanW
  del diseño de teclado activo (la «Ñ» y el «+» ya salen bien).
- La carpeta propia entra en sys.path antes de importar módulos
  hermanos: con el Python embebido, «import bandeja» moría en
  silencio y la bandeja nunca arrancaba.
- Nace servidor.log, junto a la configuración: los arranques y los
  fallos que antes no se veían en ningún sitio.
- «Iniciar con Windows» opcional (GET/POST /api/autoinicio), apagado
  de fábrica: un acceso directo en la carpeta de Inicio del usuario.

1.7.8 — dos únicos cambios:
- El menú de la bandeja, con sus textos: la familia del menú
  (AppendMenuW y compañía) gana sus prototipos ctypes en bandeja.py;
  sin ellos el texto viajaba mal convertido y el menú salía en blanco.
- «Efecto al tocar» en el panel: cada equipo escoge en sus Ajustes el
  efecto que se ve al tocar un botón (Destello, Salto, Pulso, Onda,
  Marca o Ninguno). Es cosa del panel; el servidor no cambia en esto.

1.7.9 — versión de seguridad y durabilidad (auditoría de la 1.7.8;
informe en AUDITORIA-1.7.8.md y plan en PLAN-1.7.9.md). Por fuera se
ve y se usa igual; por dentro:
- El token del editor solo se entrega sin cabecera Origin o con
  Origin y Host de la lista blanca literal (localhost, 127.0.0.1,
  IPs propias, con su puerto): el origen «null» ya no lo recibe ni
  se refleja en el CORS. Por cable USB, el teléfono escribe el
  código de emparejamiento la primera vez, como por Wi-Fi.
- La administración (configuración, dispositivos, autoinicio,
  buscar rutas, estado interno) exige el token del editor; un
  teléfono emparejado ya no puede usarla.
- Freno de emparejamiento compartido entre HTTP y Bluetooth: a los
  10 códigos fallidos seguidos, pausa de 60 s que se dobla en cada
  ronda. El token Bluetooth se revalida en cada mensaje: revocar
  vale en caliente. Líneas Bluetooth con tope de 8 MB.
- imandro-dispositivos.json gana la red de la configuración: copia
  .bak en cada guardado y, si se daña, se conserva como
  .corrupta-<fecha> y se restaura la copia, avisando en
  servidor.log. Los avisos de daño de los dos archivos ya van
  también al registro.
- Copia previa a la actualización: al primer arranque de una
  versión nueva sobre datos de otra, configuración y dispositivos
  se copian con el sello «pre-<versión>-<fecha» antes de cargar
  nada; restaurar es renombrar la copia a su nombre.
- Robustez: timeout de socket de 60 s al aceptar, autorización
  antes de leer el cuerpo, espera «multi» validada (0–5 000 ms) y
  la vía PowerShell del puente consulta el papelito si su espera
  vence, como las demás.

1.7.10 — dos únicos cambios:
- El menú de la bandeja, instrumentado (bandeja.py): la línea
  «activa» de bandeja.log se escribe al registrar el icono, con la
  bandeja viva, y enseñar el menú anota cada paso (qué AppendMenuW
  devuelve falso, el resultado de TrackPopupMenu con el último
  error de Windows, cualquier excepción) sin cambiar su estructura
  ni sus textos. El servidor no cambia en esto.
- El editor gana «Mover a…» y «Copiar a…» entre páginas (tarjeta
  del botón y arrastre hasta el nombre de la página destino): es
  cosa del editor (static/editor.html); el formato de la
  configuración y el protocolo (2) no cambian.

1.8 — tres cambios reunidos por orden de Liesky, que descartó la
numeración pensada primero («O mejor ponle 1.8»). El primero,
en bandeja.py: el menú de la
bandeja cambia cómo mete sus textos. Era AppendMenuW con cadenas
anchas vía ctypes y en la PC de Liesky el menú se abría con toda
su estructura pero sin pintar ni una letra (medido y confirmado
con el diario de la 1.7.10; los menús de Windows sí pintan los
suyos en esa PC). Ahora el menú se arma con InsertMenuItemW +
MENUITEMINFOW, la vía de las aplicaciones de verdad, y antes de
enseñarlo se lee de vuelta su primer texto (GetMenuStringW) y
queda en bandeja.log, junto a los milisegundos que estuvo
abierto.

El segundo cambio es del editor: su columna lateral de
páginas se ensancha arrastrando el borde (solo editor.html).
El tercero, añadido por orden de Liesky (2026-11-11, tras
aprobar la maqueta): la tarjeta CONEXIÓN del editor enseña la
fila «Dirección en tu red · IP y puerto», como en las demás
aplicaciones. La IP principal sale de ip_principal() (sobre
ips_locales()) y el puerto es el propio; los dos viajan en el
sondeo ligero /api/estado, que el panel sigue consumiendo como
siempre (ignora los campos nuevos).

1.9.1 — correcciones de la revisión externa del código (solo los
puntos que Liesky aprobó el 2026-11-13; el punto 1 de esa revisión
queda para su propia versión posterior):
- La bandeja dibuja su menú ella misma (bandeja.py, menú de dibujo
  propio): las letras vuelven porque ya no dependen del pintor de
  menús de Windows. Y si el servidor termina por puerto ocupado, la
  bandeja retira su icono antes de salir; «Cerrar iMandro» cierra
  también la ventana del editor.
- La «Ñ» sale por fin: VkKeyScanW se llama con su prototipo
  declarado (carácter ancho); sin él, ctypes mandaba el carácter
  como ANSI, Windows devolvía -1 y se caía en el ord() de siempre
  (0xD1, la tecla equivocada). El «+» funcionaba porque está en la
  tabla fija y no pasaba por esa llamada.
- Las teclas se inyectan con SendInput (la vía moderna) en vez de
  keybd_event, con las estructuras INPUT de 64 bits declaradas.
  Si el programa en primer plano corre como administrador (mayor
  integridad que el servidor), el editor lo avisa junto al programa
  detectado: Windows no deja que los atajos le lleguen.
- La instancia única usa un kernel32 con use_last_error de verdad.
- El código de emparejamiento se compara con
  secrets.compare_digest, por HTTP y por Bluetooth.
- Los pasos de «Varios pasos seguidos» se despachan por la misma
  lógica que los botones sueltos (herramientas, scripts, abrir,
  multimedia, ratón y sistema incluidos); un paso que no se
  reconoce devuelve error en vez de ignorarse en silencio.
- Candados en las modificaciones de los dispositivos y en el
  registro de actividad; las IPs locales se cachean unos segundos.
- Los archivos estáticos (panel, editor, iconos) se sirven con
  ETag y must-revalidate en vez de no-store: el navegador los
  revalida y los cambios llegan igual de al instante, pero sin
  descargarlos enteros cada vez. El no-store queda solo en /api/*.
"""
import base64, ctypes, glob, hashlib, json, os, secrets, shutil, socket, subprocess, sys, tempfile, threading, time
from ctypes import wintypes
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

VERSION = "1.9.2"
# Identificador del protocolo PC <-> teléfono (1.7). La 1.6.2 y anteriores
# no lo llevaban (para el panel cuentan como protocolo 1). Si el panel y la
# PC no coinciden en protocolo, el panel avisa de que hay que actualizar
# las dos a la vez en vez de fallar en silencio.
PROTOCOLO = 2
CREADOR = "Liesky Vázquez"
BASE = os.path.dirname(os.path.abspath(__file__))
# 1.7.7: con el Python embebido del instalador, sys.path NO trae esta
# carpeta (python312._pth), y un «import bandeja» moría en silencio:
# la bandeja nunca arrancaba y nadie veía el error (la misma lección
# del fallo de Liclick). La carpeta propia va la primera, antes de
# importar ningún módulo hermano.
if BASE not in sys.path:
    sys.path.insert(0, BASE)
STATIC = os.path.join(BASE, "static")
ARCHIVO_CONFIG = os.path.join(BASE, "imandro-config.json")
ARCHIVO_DISPOSITIVOS = os.path.join(BASE, "imandro-dispositivos.json")
ARCHIVO_LOG = os.path.join(BASE, "servidor.log")
_candado_log = threading.Lock()

def registra_servidor(texto):
    """Registro del servidor (1.7.7): arranques y los fallos que antes
    eran invisibles (bajo pythonw los print() no van a ninguna parte)
    quedan escritos en servidor.log, junto a la configuración, con
    fecha y hora. Nunca lanza: si el registro falla, el servidor
    sigue. Al pasar de ~1 MB se empieza de nuevo conservando el
    final (~200 KB), para que no crezca sin fin."""
    try:
        linea = "%s · %s\n" % (time.strftime("%Y-%m-%d %H:%M:%S"), texto)
        with _candado_log:
            try:
                if os.path.getsize(ARCHIVO_LOG) > 1024 * 1024:
                    with open(ARCHIVO_LOG, "rb") as f:
                        f.seek(0, 2)
                        f.seek(max(0, f.tell() - 200 * 1024))
                        datos = f.read()
                    corte = datos.find(b"\n")
                    if corte >= 0:
                        datos = datos[corte + 1:]
                    with open(ARCHIVO_LOG, "wb") as f:
                        f.write(datos)
            except Exception:
                pass
            with open(ARCHIVO_LOG, "a", encoding="utf-8") as f:
                f.write(linea)
    except Exception:
        pass
PUERTO = 8931
PUERTO_DESCUBRIR = 8932   # los teléfonos preguntan aquí
PUERTO_AVISO = 8933       # la PC anuncia su presencia aquí

ES_WINDOWS = sys.platform.startswith("win")

# CREATE_NO_WINDOW: ningún proceso hijo enseña consola en la PC (v1.6.1;
# se acabaron las ventanitas de CMD/PowerShell que entraban y salían).
SIN_VENTANA = 0x08000000 if ES_WINDOWS else 0

# ---------------------------------------------------------------- configuración
def boton(nombre, icono, color, accion):
    return {"name": nombre, "icon": icono, "color": color, "action": accion}

def h(keys):  return {"type": "hotkey", "keys": keys}
def pa(nombre): return {"type": "psaction", "name": nombre, "set": ""}
def nada():   return {"type": "none"}
def media(k): return {"type": "media", "key": k}
def abrir(t): return {"type": "open", "target": t}
def sist(c):  return {"type": "system", "cmd": c}
def script(jsx): return {"type": "psscript", "script": jsx}
_ADDADJ = ("function addAdj(t){var d=new ActionDescriptor();var r=new ActionReference();"
           "r.putClass(stringIDToTypeID('adjustmentLayer'));d.putReference(stringIDToTypeID('null'),r);"
           "var u=new ActionDescriptor();u.putClass(stringIDToTypeID('type'),stringIDToTypeID(t));"
           "d.putObject(stringIDToTypeID('using'),stringIDToTypeID('adjustmentLayer'),u);"
           "executeAction(stringIDToTypeID('make'),d,DialogModes.NO);} ")
def adj(t): return script(_ADDADJ + "if(app.documents.length) addAdj('" + t + "');")
def pag(p):   return {"type": "page", "page": p}
def tool(t):  return {"type": "pstool", "tool": t}

AZUL, VIOLETA, VERDE, AMBAR = "#4cc3ff", "#b18cff", "#3ddc97", "#f6b73c"

def jsx_herramienta(tid):
    """JSX que selecciona UNA herramienta de Photoshop por su nombre interno,
    aunque comparta letra con las demás de su grupo.
    Desde la 1.7.6 lleva DOS métodos dentro del mismo script: primero el
    de siempre (executeAction), y solo si ese lanza un error se prueba
    con app.currentTool. Hay herramientas rebeldes (Selección de objetos
    es la famosa: la comunidad de Adobe documenta que hay versiones de
    Photoshop donde no se deja activar por un camino) y así cada una
    entra por el que su Photoshop acepte. Las que ya funcionaban siguen
    entrando por el primer método, sin cambiar en nada."""
    return ("try{var r=new ActionReference();r.putClass(stringIDToTypeID('" + tid + "'));"
            "var d=new ActionDescriptor();d.putReference(charIDToTypeID('null'),r);"
            "executeAction(charIDToTypeID('slct'),d,DialogModes.NO);}"
            "catch(e){app.currentTool='" + tid + "';}")

def pagina_herramientas():
    """La página «Herramientas» de la v1.5, con las 12 herramientas que escogió
    Liesky (números 1, 7, 10, 11, 13, 23, 28, 32, 36, 37, 53 y 68 de la lista
    completa de 70), cada una con su selección exacta."""
    return {"id": "herramientas", "name": "Herramientas", "icon": "varita", "columns": 3,
            "sliders": [],
            "buttons": [
                boton("Mover", "pack:ps5/03_Navegacion/034_mover", AZUL, tool("moveTool")),
                boton("Lazo", "pack:ps5/02_Seleccion/018_lazo", AZUL, tool("lassoTool")),
                boton("Selección de objetos", "pack:ps5/02_Seleccion/023_selección_de_objetos", AZUL, tool("objectSelectionTool")),
                boton("Selección rápida", "pack:ps5/02_Seleccion/021_selección_rápida", AZUL, tool("quickSelectTool")),
                boton("Recortar", "pack:ps5/03_Navegacion/031_recortar", AZUL, tool("cropTool")),
                boton("Quitar manchas", "pack:ps5/04_Pinceles_Retoque/061_quitar_manchas", AZUL, tool("spotHealingBrushTool")),
                boton("Quitar", "pack:ps5/04_Pinceles_Retoque/065_eliminar_objeto", VIOLETA, tool("removeTool")),
                boton("Pincel", "pack:ps5/04_Pinceles_Retoque/046_pincel", AZUL, tool("paintbrushTool")),
                boton("Tampón de clonar", "pack:ps5/04_Pinceles_Retoque/060_clonar", AZUL, tool("cloneStampTool")),
                boton("Borrador", "pack:ps5/04_Pinceles_Retoque/049_borrador", AZUL, tool("eraserTool")),
                boton("Borrador de fondo", "pack:ps5/04_Pinceles_Retoque/050_borrador_de_fondo", AZUL, tool("backgroundEraserTool")),
                boton("Texto horizontal", "pack:ps5/08_Texto_Formas/111_texto", AZUL, tool("typeCreateOrEditTool")),
            ]}

def config_por_defecto():
    return {
        "app": "iMandro", "version": VERSION, "_rev": 1,
        "pcName": socket.gethostname(),
        "customIcons": {},
        "customButtons": {},
        "pages": [
            {"id": "retoque", "name": "Retoque", "icon": "pincel", "columns": 3,
             "sliders": [{"id": "s-retoque-1", "name": "Tamaño del pincel", "type": "brush", "min": 1, "max": 200, "value": 45}],
             "buttons": [
                 boton("Deshacer", "deshacer", AZUL, h("Ctrl+Z")),
                 boton("Rehacer", "rehacer", AZUL, h("Ctrl+Shift+Z")),
                 boton("Quitar manchas", "curita", AZUL, tool("spotHealingBrushTool")),
                 boton("Tampón de clonar", "tampon", AZUL, tool("cloneStampTool")),
                 boton("Pincel corrector", "pincel", AZUL, tool("magicStampTool")),
                 boton("Licuar", "gota", AZUL, h("Ctrl+Shift+X")),
                 boton("Suavizar piel", "cara", VIOLETA, pa("Suavizar piel")),
                 boton("Enfocar ojos", "ojo", VIOLETA, pa("Enfocar ojos")),
                 boton("Blanquear dientes", "brillos", VIOLETA, pa("Blanquear dientes")),
                 boton("Quitar brillo", "brillos", VIOLETA, pa("Quitar brillo")),
                 boton("Separación de frecuencias", "capas", VIOLETA, pa("Separación de frecuencias")),
                 boton("Luces y sombras", "mitad", VIOLETA, pa("Luces y sombras")),
                 boton("Recortar", "recortar", AZUL, tool("cropTool")),
                 boton("Guardar", "guardar", AZUL, h("Ctrl+S")),
                 boton("Exportar", "exportar", AZUL, h("Ctrl+Alt+Shift+S")),
             ]},
            {"id": "color", "name": "Color", "icon": "paleta", "columns": 3,
             "sliders": [{"id": "s-color-1", "name": "Opacidad de la capa", "type": "opacity", "min": 0, "max": 100, "value": 80}],
             "buttons": [
                 boton("Camera Raw", "camara", VIOLETA, h("Ctrl+Shift+A")),
                 boton("Curvas", "curvas", AZUL, h("Ctrl+M")),
                 boton("Niveles", "deslizadores", AZUL, h("Ctrl+L")),
                 boton("Exposición", "sol", AZUL, adj("exposure")),
                 boton("Brillo y contraste", "mitad", AZUL, adj("brightnessAndContrast")),
                 boton("Tono y saturación", "paleta", AZUL, h("Ctrl+U")),
                 boton("Equilibrio de color", "gota", AZUL, h("Ctrl+B")),
                 boton("Corrección selectiva", "varita", AZUL, adj("selectiveColor")),
                 boton("Intensidad", "brillos", AZUL, adj("vibrance")),
                 boton("Desaturar", "mitad", AZUL, h("Ctrl+Shift+U")),
                 boton("Filtro de fotografía", "sol", AZUL, adj("photoFilter")),
                 boton("Sombras e iluminaciones", "mitad", AZUL, nada()),
                 boton("Mapa de degradado", "capas", AZUL, adj("gradientMap")),
                 boton("Invertir", "intercambiar", AZUL, h("Ctrl+I")),
                 boton("Color automático", "varita", AZUL, h("Ctrl+Shift+B")),
             ]},
            {"id": "capas", "name": "Capas", "icon": "capas", "columns": 3,
             "sliders": [{"id": "s-capas-1", "name": "Opacidad de la capa", "type": "opacity", "min": 0, "max": 100, "value": 100}],
             "buttons": [
                 boton("Nueva capa", "mas", AZUL, h("Ctrl+Shift+N")),
                 boton("Duplicar capa", "copiar", AZUL, h("Ctrl+J")),
                 boton("Eliminar capa", "papelera", AZUL, script("if(app.documents.length){var l=app.activeDocument.activeLayer; if(!l.isBackgroundLayer) l.remove();}")),
                 boton("Máscara de capa", "mascara", AZUL, script("function addMask(){var d=new ActionDescriptor();d.putClass(charIDToTypeID('Nw  '),charIDToTypeID('Chnl'));var r=new ActionReference();r.putEnumerated(charIDToTypeID('Chnl'),charIDToTypeID('Chnl'),charIDToTypeID('Msk '));d.putReference(charIDToTypeID('At  '),r);d.putEnumerated(charIDToTypeID('Usng'),charIDToTypeID('UsrM'),charIDToTypeID('RvlA'));executeAction(charIDToTypeID('Mk  '),d,DialogModes.NO);} if(app.documents.length) addMask();")),
                 boton("Agrupar", "carpeta", AZUL, h("Ctrl+G")),
                 boton("Desagrupar", "carpeta", AZUL, h("Ctrl+Shift+G")),
                 boton("Combinar visibles", "capas", AZUL, h("Ctrl+Shift+E")),
                 boton("Subir capa", "subir", AZUL, h("Ctrl+]")),
                 boton("Bajar capa", "bajar", AZUL, h("Ctrl+[")),
                 boton("Renombrar capa", "lapiz", AZUL, script("if(app.documents.length){var l=app.activeDocument.activeLayer; var n=prompt('Nombre de la capa:', l.name); if(n) l.name=n;}")),
                 boton("Quitar candado", "candado", AZUL, script("if(app.documents.length){var b=app.activeDocument.backgroundLayer; if(b) b.isBackgroundLayer=false;}")),
                 boton("Capa de ajuste", "mitad", AZUL, adj("curves")),
                 boton("Objeto inteligente", "cubo", AZUL, script("if(app.documents.length) executeAction(stringIDToTypeID('newPlacedLayer'), new ActionDescriptor(), DialogModes.NO);")),
                 boton("Rasterizar", "texto", AZUL, script("if(app.documents.length) app.activeDocument.activeLayer.rasterize(RasterizeType.ENTIRELAYER);")),
                 boton("Acoplar imagen", "capas", AZUL, script("if(app.documents.length) app.activeDocument.flatten();")),
             ]},
            {"id": "sistema", "name": "Sistema", "icon": "deslizadores", "columns": 3,
             "sliders": [{"id": "s-sistema-1", "name": "Volumen", "type": "volume", "min": 0, "max": 100, "value": 50}],
             "buttons": [
                 boton("Abrir Photoshop", "camara", AMBAR, abrir("photoshop")),
                 boton("Abrir Lightroom", "sol", AMBAR, abrir("lightroom")),
                 boton("Mi carpeta de fotos", "carpeta", AMBAR, abrir("fotos")),
                 boton("Volumen +", "volumen", VERDE, media("volup")),
                 boton("Volumen −", "volumen", VERDE, media("voldn")),
                 boton("Silencio", "volumen", VERDE, media("mute")),
                 boton("Reproducir / Pausar", "play", VERDE, media("playpause")),
                 boton("Captura de pantalla", "camara", VERDE, sist("screenshot")),
                 boton("Bloquear la PC", "candado", VERDE, sist("lock")),
                 boton("Explorador", "carpeta", VERDE, sist("explorer")),
                 boton("Ir a Retoque", "pagina", AMBAR, pag("retoque")),
                 boton("Ir a Color", "pagina", AMBAR, pag("color")),
                 boton("Ir a Capas", "pagina", AMBAR, pag("capas")),
                 boton("Foto a pantalla", "recortar", AZUL, h("Ctrl+0")),
                 boton("Zoom al 100 %", "ojo", AZUL, h("Ctrl+1")),
             ]},
            pagina_herramientas(),
        ],
    }

CONFIG = None
candado_config = threading.RLock()

# ------------------------------------------------- seguridad: emparejamiento
# Desde la 1.7 ningún teléfono controla la PC sin emparejarse antes:
# la PC enseña un código de 6 dígitos en el editor; el teléfono lo escribe
# una sola vez y recibe un token largo que guarda y envía en cada petición
# (cabecera «X-iMandro-Token» por HTTP, primer mensaje «auth» por Bluetooth).
# En el servidor solo se guardan los hash (SHA-256) de los tokens, nunca el
# token en claro, en un archivo aparte: imandro-dispositivos.json.
# El editor de la PC recibe su propio token por /api/token-local, que solo
# responde a peticiones que vienen de ESTA PC (bucle local o su propia IP)
# y, desde la 1.7.9, solo sin cabecera Origin o con Origin y Host de la
# lista blanca literal; ver la nota junto a ese endpoint en do_GET.
DISPOSITIVOS = {"codigo": "", "lista": []}
candado_dispositivos = threading.Lock()

def _hash_token(token):
    return hashlib.sha256((token or "").encode("utf-8")).hexdigest()

def guardar_dispositivos():
    """Guardado atómico (temporal + renombrar) con copia .bak de la
    versión anterior en cada guardado (1.7.9): el archivo de
    dispositivos gana la misma red que la configuración."""
    with candado_dispositivos:
        if os.path.exists(ARCHIVO_DISPOSITIVOS):
            try:
                shutil.copyfile(ARCHIVO_DISPOSITIVOS, ARCHIVO_DISPOSITIVOS + ".bak")
            except Exception:
                pass
        tmp = ARCHIVO_DISPOSITIVOS + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(DISPOSITIVOS, f, ensure_ascii=False)
        os.replace(tmp, ARCHIVO_DISPOSITIVOS)

def _dispositivos_validos(datos):
    return (isinstance(datos, dict) and bool(datos.get("codigo"))
            and isinstance(datos.get("lista"), list))

def cargar_dispositivos():
    """Carga los emparejamientos sin perderlos NUNCA en silencio
    (1.7.9, auditoría S2): si el archivo está dañado, se conserva
    renombrado «.corrupta-<fecha>», se avisa también a servidor.log
    y se arranca con la última copia .bak válida; solo si no hay
    ninguna se empieza de cero, con código nuevo — y el daño queda
    escrito. Antes, un archivo dañado borraba TODOS los
    emparejamientos sin dejar rastro."""
    global DISPOSITIVOS
    if os.path.exists(ARCHIVO_DISPOSITIVOS):
        try:
            with open(ARCHIVO_DISPOSITIVOS, encoding="utf-8") as f:
                datos = json.load(f)
            if not _dispositivos_validos(datos):
                raise ValueError("el archivo no tiene la forma esperada")
            DISPOSITIVOS = datos
            return
        except Exception as e:
            guardada = ""
            try:
                guardada = ARCHIVO_DISPOSITIVOS + ".corrupta-" + time.strftime("%Y%m%d-%H%M%S")
                os.replace(ARCHIVO_DISPOSITIVOS, guardada)
            except Exception:
                guardada = "(no se pudo renombrar)"
            aviso = ("AVISO: el archivo de dispositivos estaba dañado (%s). "
                     "Se conserva en %s y se intenta la última copia buena."
                     % (e, guardada))
            print("[iMandro] " + aviso, flush=True)
            registra_servidor(aviso)
            bak = ARCHIVO_DISPOSITIVOS + ".bak"
            if os.path.exists(bak):
                try:
                    with open(bak, encoding="utf-8") as f:
                        datos = json.load(f)
                    if not _dispositivos_validos(datos):
                        raise ValueError("la copia tampoco es válida")
                    DISPOSITIVOS = datos
                    guardar_dispositivos()
                    aviso2 = ("Dispositivos recuperados de la copia .bak "
                              "(%d en la lista)." % len(DISPOSITIVOS.get("lista", [])))
                    print("[iMandro] " + aviso2, flush=True)
                    registra_servidor(aviso2)
                    return
                except Exception:
                    DISPOSITIVOS = None
    DISPOSITIVOS = {"codigo": "%06d" % secrets.randbelow(1000000), "lista": []}
    guardar_dispositivos()

# ------------------------------------------- freno de emparejamiento
# 1.7.9 (auditoría B1): el código de 6 dígitos es permanente; sin
# freno, un programa dentro de la red podía probarlo sin límite hasta
# acertar. Contador de fallos COMPARTIDO entre la puerta HTTP
# (/api/emparejar) y la Bluetooth («emparejar» en atender_bt): a los
# 10 fallos seguidos el emparejamiento se pausa 60 s — durante la
# pausa ni el código bueno entra — y la pausa se dobla en cada ronda
# (60, 120, 240… hasta un tope de 1 h). Un acierto reinicia todo.
# Cada bloqueo queda escrito en servidor.log. El código NO caduca ni
# se regenera solo: encaja con la forma de trabajar de Liesky y el
# freno ya quita el peligro práctico.
_freno = {"fallos": 0, "pausa_hasta": 0.0, "duracion": 60}
_candado_freno = threading.Lock()
FRENO_FALLOS = 10
FRENO_PAUSA_INICIAL = 60
FRENO_PAUSA_MAXIMA = 3600

def freno_activo():
    """Segundos de pausa de emparejamiento que quedan (0 = sin pausa)."""
    with _candado_freno:
        quedan = _freno["pausa_hasta"] - time.time()
    return quedan if quedan > 0 else 0.0

def freno_registra_fallo():
    """Anota un código fallido; al llegar a FRENO_FALLOS seguidos
    entra la pausa de la ronda (que se dobla para la siguiente)."""
    with _candado_freno:
        _freno["fallos"] += 1
        if _freno["fallos"] >= FRENO_FALLOS:
            duracion = _freno["duracion"]
            _freno["pausa_hasta"] = time.time() + duracion
            _freno["duracion"] = min(duracion * 2, FRENO_PAUSA_MAXIMA)
            _freno["fallos"] = 0
            registra_servidor("Emparejamiento pausado %d s: demasiados "
                              "códigos incorrectos seguidos." % duracion)

def freno_registra_acierto():
    """Un emparejamiento bueno reinicia el contador y la pausa."""
    with _candado_freno:
        _freno["fallos"] = 0
        _freno["duracion"] = FRENO_PAUSA_INICIAL
        _freno["pausa_hasta"] = 0.0

def msg_pausa_emparejar(quedan):
    """El mensaje que el panel enseña durante la pausa: explica la
    espera que toca, sin más tecnicismos."""
    if quedan > 90:
        return ("demasiados intentos: espera %d minutos e inténtalo otra vez"
                % int(round(quedan / 60.0)))
    return "demasiados intentos: espera un minuto e inténtalo otra vez"

# --------------------------------------- ventana de emparejamiento
# 1.9.2 (punto 2 de la revisión, el «modo emparejar»): el
# emparejamiento nace PAUSADO. Un teléfono nuevo solo entra mientras
# el editor tiene abierta la ventana con su botón «Permitir
# emparejar (2 minutos)» (POST /api/emparejar-ventana, solo editor);
# al pasar el tiempo, la ventana se cierra sola. Fuera de ella,
# /api/emparejar y el «emparejar» de Bluetooth contestan «pausado»
# con el aviso claro de abajo, y el panel enseña ese mismo texto.
# El freno de intentos de la 1.7.9 sigue vivo DENTRO de la ventana:
# son dos pausas distintas y no se pisan — la de la ventana manda
# primero porque sin ventana ni se mira el código.
_ventana_emp = {"hasta": 0.0}
_candado_ventana_emp = threading.Lock()
VENTANA_EMPAREJAR_S = 120
MSG_EMPAREJAR_PAUSADO = ("El emparejamiento está pausado. "
                         "Ábrelo desde el editor de la PC.")

def emparejar_quedan():
    """Segundos de ventana de emparejamiento que quedan (0 = pausado)."""
    with _candado_ventana_emp:
        quedan = _ventana_emp["hasta"] - time.time()
    return quedan if quedan > 0 else 0.0

def abrir_ventana_emparejar(segundos=VENTANA_EMPAREJAR_S):
    """Abre la ventana de emparejamiento los segundos dados (el editor
    pide 120) y devuelve cuántos quedan."""
    try:
        segundos = int(segundos)
    except Exception:
        segundos = VENTANA_EMPAREJAR_S
    segundos = max(1, min(segundos, 600))
    with _candado_ventana_emp:
        _ventana_emp["hasta"] = time.time() + segundos
    registra_servidor("Ventana de emparejamiento abierta %d s desde "
                      "el editor." % segundos)
    return emparejar_quedan()

# --------------------------------- copia previa a la actualización
def _copias_previas_actualizacion():
    """Copia previa a la actualización (1.9): la primera vez que una
    versión nueva arranca sobre datos de una anterior, ANTES de
    cargar y migrar nada, la configuración y los dispositivos se
    copian con el sello «pre-<versión>-<fecha>» junto a los
    originales. Se hace una sola vez por salto de versión (si ya hay
    una copia con el sello de esta versión, no se repite). Restaurar
    = cerrar iMandro y renombrar la copia a su nombre
    (imandro-config.json / imandro-dispositivos.json); queda escrito
    en servidor.log cada vez que se hace. Nunca lanza: si la copia
    falla, el arranque sigue."""
    try:
        if glob.glob(ARCHIVO_CONFIG + ".pre-" + VERSION + "-*") or \
           glob.glob(ARCHIVO_DISPOSITIVOS + ".pre-" + VERSION + "-*"):
            return  # la copia de este salto ya se hizo
        version_datos = ""
        if os.path.exists(ARCHIVO_CONFIG):
            try:
                with open(ARCHIVO_CONFIG, encoding="utf-8") as f:
                    version_datos = str(json.load(f).get("version", "") or "")
            except Exception:
                version_datos = ""
        if version_datos == VERSION:
            return  # los datos ya son de esta versión: nada que sellar
        sello = time.strftime("%Y%m%d-%H%M%S")
        hechas = []
        for ruta in (ARCHIVO_CONFIG, ARCHIVO_DISPOSITIVOS):
            if os.path.exists(ruta):
                destino = "%s.pre-%s-%s" % (ruta, VERSION, sello)
                try:
                    shutil.copyfile(ruta, destino)
                    hechas.append(os.path.basename(destino))
                except Exception:
                    pass
        if hechas:
            registra_servidor(
                "Copia previa a la actualización a la %s hecha (los datos "
                "eran de la %s): %s. Para volver atrás: cierra iMandro y "
                "renombra la copia a su nombre (imandro-config.json / "
                "imandro-dispositivos.json)."
                % (VERSION, version_datos or "versión anterior",
                   ", ".join(hechas)))
    except Exception:
        pass

def token_valido(token):
    """Devuelve el dispositivo autorizado de ese token, o None."""
    if not token:
        return None
    h = _hash_token(token)
    # 1.9.1 (punto 7): la escritura de «ultimo» también va con el
    # candado de dispositivos — guardar_dispositivos lo tomaba para
    # el archivo, pero esta mutación en memoria quedaba fuera.
    with candado_dispositivos:
        for d in DISPOSITIVOS.get("lista", []):
            if secrets.compare_digest(d.get("hash", ""), h):
                d["ultimo"] = time.strftime("%Y-%m-%d %H:%M")
                return d
    return None

def crear_token(nombre):
    token = secrets.token_urlsafe(32)
    with candado_dispositivos:
        DISPOSITIVOS.setdefault("lista", []).append({
            "id": secrets.token_hex(4),
            "nombre": (nombre or "Teléfono").strip()[:60] or "Teléfono",
            "hash": _hash_token(token),
            "creado": time.strftime("%Y-%m-%d %H:%M"),
            "ultimo": time.strftime("%Y-%m-%d %H:%M"),
        })
    guardar_dispositivos()
    return token

def token_del_editor():
    """Token propio y permanente del editor de esta PC. Se crea la primera
    vez y se reutiliza; aparece en la lista como «Editor de esta PC»."""
    for d in DISPOSITIVOS.get("lista", []):
        if d.get("editor") and d.get("token"):
            return d["token"]
    token = secrets.token_urlsafe(32)
    with candado_dispositivos:
        DISPOSITIVOS.setdefault("lista", []).append({
            "id": "editor", "nombre": "Editor de esta PC", "editor": True,
            "hash": _hash_token(token), "token": token,
            "creado": time.strftime("%Y-%m-%d %H:%M"),
            "ultimo": time.strftime("%Y-%m-%d %H:%M"),
        })
    guardar_dispositivos()
    return token

def quitar_barras(cfg):
    """v1.6.1: las barras deslizantes desaparecen. Se retiran de cada
    página al cargar la configuración, para que una copia vieja las
    pierda también en la PC y nunca lleguen a los teléfonos."""
    for pg in (cfg or {}).get("pages", []):
        pg.pop("sliders", None)

def cargar_config():
    """Carga la configuración sin perderla NUNCA en silencio (1.7):
    si el archivo está dañado, se conserva renombrado «.corrupta-<fecha>»,
    se avisa y se arranca con la última copia .bak válida; solo si no hay
    ninguna se usa la de fábrica (y la dañada sigue guardada aparte)."""
    global CONFIG
    if os.path.exists(ARCHIVO_CONFIG):
        try:
            with open(ARCHIVO_CONFIG, encoding="utf-8") as f:
                CONFIG = json.load(f)
            if not isinstance(CONFIG, dict) or "pages" not in CONFIG:
                raise ValueError("la configuración no tiene páginas")
            quitar_barras(CONFIG)
            migrar_v150()
            migrar_v172()
            return
        except Exception as e:
            guardada = ""
            try:
                guardada = ARCHIVO_CONFIG + ".corrupta-" + time.strftime("%Y%m%d-%H%M%S")
                os.replace(ARCHIVO_CONFIG, guardada)
            except Exception:
                guardada = "(no se pudo renombrar)"
            # 1.7.9 (auditoría S1): el aviso va también a servidor.log;
            # antes solo iba a un print() que bajo pythonw no se ve en
            # ningún sitio y la recuperación no dejaba rastro.
            aviso = ("AVISO: la configuración estaba dañada (%s). "
                     "Se conserva en %s y se intenta la última copia buena."
                     % (e, guardada))
            print("[iMandro] " + aviso, flush=True)
            registra_servidor(aviso)
            bak = ARCHIVO_CONFIG + ".bak"
            if os.path.exists(bak):
                try:
                    with open(bak, encoding="utf-8") as f:
                        CONFIG = json.load(f)
                    if not isinstance(CONFIG, dict) or "pages" not in CONFIG:
                        raise ValueError("la copia tampoco es válida")
                    quitar_barras(CONFIG)
                    guardar_config(subir_rev=False)
                    migrar_v150()
                    migrar_v172()
                    aviso2 = "Configuración recuperada de la copia .bak."
                    print("[iMandro] " + aviso2, flush=True)
                    registra_servidor(aviso2)
                    return
                except Exception:
                    CONFIG = None
    CONFIG = config_por_defecto()
    guardar_config(subir_rev=False)

def guardar_config(subir_rev=True):
    """Guardado atómico (temporal + renombrar) con copia .bak automática
    de la configuración anterior en cada guardado (1.7), para poder volver
    atrás si un guardado o una importación salen mal."""
    with candado_config:
        if subir_rev:
            CONFIG["_rev"] = int(CONFIG.get("_rev", 1)) + 1
        if os.path.exists(ARCHIVO_CONFIG):
            try:
                shutil.copyfile(ARCHIVO_CONFIG, ARCHIVO_CONFIG + ".bak")
            except Exception:
                pass
        tmp = ARCHIVO_CONFIG + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(CONFIG, f, ensure_ascii=False)
            f.flush()
            try:
                os.fsync(f.fileno())
            except Exception:
                pass
        os.replace(tmp, ARCHIVO_CONFIG)


def migrar_v150():
    """v1.5: añade la página «Herramientas» a las configuraciones que ya existían.

    Se hace una sola vez (queda la marca «_herramientas150»): si el usuario
    borra la página después, no vuelve a aparecer. No toca ninguna otra página
    ni ningún botón de la configuración."""
    if CONFIG.get("_herramientas150"):
        return
    CONFIG["_herramientas150"] = True
    if not any(pg.get("id") == "herramientas" for pg in CONFIG.get("pages", [])):
        CONFIG.setdefault("pages", []).append(pagina_herramientas())
    guardar_config(subir_rev=False)

def migrar_v172():
    """v1.7.2: en la página «Herramientas», los botones de «Selección de
    objetos» y «Quitar manchas» pasan a los iconos nuevos del paquete de
    Photoshop (las entradas 023_selección_de_objetos y 061_quitar_manchas,
    que estrenan dibujo en esta versión). Hasta la 1.7.1 esos dos botones
    apuntaban a «023_seleccionar_sujeto» y a la tirita genérica «curita».

    Se hace una sola vez (marca «_iconos172») y solo toca esos dos botones
    de esa página, identificados por su herramienta; ningún otro botón ni
    ninguna otra página de la configuración se modifica."""
    if CONFIG.get("_iconos172"):
        return
    CONFIG["_iconos172"] = True
    nuevos = {
        "objectSelectionTool": "pack:ps5/02_Seleccion/023_selección_de_objetos",
        "spotHealingBrushTool": "pack:ps5/04_Pinceles_Retoque/061_quitar_manchas",
    }
    for pg in CONFIG.get("pages", []):
        if pg.get("id") != "herramientas":
            continue
        for b in pg.get("buttons", []):
            accion = b.get("action") or {}
            if accion.get("type") == "pstool" and accion.get("tool") in nuevos:
                b["icon"] = nuevos[accion["tool"]]
    guardar_config(subir_rev=False)

# ------------------------------------- Win32 declarado (1.9.1)
# Instancias propias de las DLL con use_last_error=True y los
# prototipos declarados UNA vez: con ctypes.windll, get_last_error()
# no es fiable y las llamadas sin firma improvisan la conversión de
# cada argumento (así se perdía la «Ñ»: VkKeyScanW recibía el
# carácter como ANSI y devolvía -1). Las pruebas pueden sustituir la
# función SendInput por una falsa (SEND_INPUT_PRUEBA) y el resolvedor
# de caracteres por otro (VK_KEY_SCAN), sin Windows.
_user32_declarado = None
_kernel32_declarado = None
_advapi32_declarado = None
SEND_INPUT_PRUEBA = None


class KEYBDINPUT(ctypes.Structure):
    # dwExtraInfo es ULONG_PTR (c_size_t). En el Windows de 64 bits
    # la estructura mide 24 bytes; el ctypes de Linux la cuenta como
    # 32 por su alineación, y da igual: lo que SendInput exige es el
    # tamaño de INPUT, que sale 40 en los dos sitios.
    _fields_ = [("wVk", wintypes.WORD), ("wScan", wintypes.WORD),
                ("dwFlags", wintypes.DWORD), ("time", wintypes.DWORD),
                ("dwExtraInfo", ctypes.c_size_t)]


class _INPUT_UNION(ctypes.Union):
    _fields_ = [("ki", KEYBDINPUT),
                ("_relleno", ctypes.c_byte * 32)]


class INPUT(ctypes.Structure):
    # En 64 bits: type (4) + relleno (4) + la unión alineada a 8
    # (32 bytes, como la MOUSEINPUT mayor) = 40 bytes en total.
    # El banco lo verifica con sizeof.
    _fields_ = [("type", wintypes.DWORD), ("u", _INPUT_UNION)]


def _user32():
    global _user32_declarado
    if _user32_declarado is None:
        u = ctypes.WinDLL("user32", use_last_error=True)
        u.VkKeyScanW.argtypes = [ctypes.c_wchar]
        u.VkKeyScanW.restype = ctypes.c_short
        u.SendInput.argtypes = [wintypes.UINT, ctypes.POINTER(INPUT),
                                ctypes.c_int]
        u.SendInput.restype = wintypes.UINT
        u.GetForegroundWindow.argtypes = []
        u.GetForegroundWindow.restype = wintypes.HWND
        u.GetWindowThreadProcessId.argtypes = [wintypes.HWND,
                                               ctypes.POINTER(wintypes.DWORD)]
        u.GetWindowThreadProcessId.restype = wintypes.DWORD
        _user32_declarado = u
    return _user32_declarado


def _kernel32():
    global _kernel32_declarado
    if _kernel32_declarado is None:
        k = ctypes.WinDLL("kernel32", use_last_error=True)
        k.CreateMutexW.argtypes = [ctypes.c_void_p, wintypes.BOOL,
                                   wintypes.LPCWSTR]
        k.CreateMutexW.restype = wintypes.HANDLE
        k.SetLastError.argtypes = [wintypes.DWORD]
        k.SetLastError.restype = None
        k.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL,
                                  wintypes.DWORD]
        k.OpenProcess.restype = wintypes.HANDLE
        k.QueryFullProcessImageNameW.argtypes = [wintypes.HANDLE, wintypes.DWORD,
                                                 wintypes.LPWSTR,
                                                 ctypes.POINTER(wintypes.DWORD)]
        k.QueryFullProcessImageNameW.restype = wintypes.BOOL
        k.CloseHandle.argtypes = [wintypes.HANDLE]
        k.CloseHandle.restype = wintypes.BOOL
        _kernel32_declarado = k
    return _kernel32_declarado


def _advapi32():
    global _advapi32_declarado
    if _advapi32_declarado is None:
        a = ctypes.WinDLL("advapi32", use_last_error=True)
        a.OpenProcessToken.argtypes = [wintypes.HANDLE, wintypes.DWORD,
                                       ctypes.POINTER(wintypes.HANDLE)]
        a.OpenProcessToken.restype = wintypes.BOOL
        a.GetTokenInformation.argtypes = [wintypes.HANDLE, ctypes.c_int,
                                          ctypes.c_void_p, wintypes.DWORD,
                                          ctypes.POINTER(wintypes.DWORD)]
        a.GetTokenInformation.restype = wintypes.BOOL
        a.GetSidSubAuthorityCount.argtypes = [ctypes.c_void_p]
        a.GetSidSubAuthorityCount.restype = ctypes.POINTER(ctypes.c_ubyte)
        a.GetSidSubAuthority.argtypes = [ctypes.c_void_p, wintypes.DWORD]
        a.GetSidSubAuthority.restype = ctypes.POINTER(wintypes.DWORD)
        _advapi32_declarado = a
    return _advapi32_declarado


def _envia_tecla(vk, bajar):
    """Un pulso (bajar o subir) por SendInput, la vía moderna
    (1.9.1, punto 8 de la revisión; antes era keybd_event). Misma
    semántica de siempre: INPUT_KEYBOARD con KEYEVENTF_KEYUP al
    subir. En las pruebas, SEND_INPUT_PRUEBA captura la secuencia."""
    inp = INPUT()
    inp.type = 1  # INPUT_KEYBOARD
    inp.u.ki.wVk = vk
    inp.u.ki.wScan = 0
    inp.u.ki.dwFlags = 0 if bajar else 0x0002  # KEYEVENTF_KEYUP
    inp.u.ki.time = 0
    inp.u.ki.dwExtraInfo = 0
    if SEND_INPUT_PRUEBA is not None:
        SEND_INPUT_PRUEBA(inp)
        return
    _user32().SendInput(1, ctypes.byref(inp), ctypes.sizeof(INPUT))

# ------------------------------------------------------- programa en primer plano
_fg_cache = {"t": 0.0, "v": "", "pid": 0}
_fg_elev_cache = {"t": 0.0, "v": None}

def programa_en_primer_plano():
    """Nombre del ejecutable de la ventana activa (p. ej. «Photoshop.exe»).

    Sirve para los perfiles por programa: el panel salta solo a la página
    vinculada al programa que el usuario abra en la PC. Fuera de Windows
    devuelve «» (o lo que fije IMANDRO_FG_SIM, para pruebas)."""
    sim = os.environ.get("IMANDRO_FG_SIM")
    if sim is not None:
        return sim
    if not ES_WINDOWS:
        return ""
    ahora = time.time()
    if ahora - _fg_cache["t"] < 0.8:
        return _fg_cache["v"]
    valor = ""
    pid_fg = 0
    try:
        user32 = _user32()
        kernel32 = _kernel32()
        hwnd = user32.GetForegroundWindow()
        if hwnd:
            pid = wintypes.DWORD()
            user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
            if pid.value:
                pid_fg = pid.value
                handle = kernel32.OpenProcess(0x1000, False, pid.value)  # QUERY_LIMITED_INFORMATION
                if handle:
                    try:
                        buf = ctypes.create_unicode_buffer(1024)
                        tam = wintypes.DWORD(1024)
                        if kernel32.QueryFullProcessImageNameW(handle, 0, buf, ctypes.byref(tam)):
                            valor = os.path.basename(buf.value)
                    finally:
                        kernel32.CloseHandle(handle)
    except Exception:
        valor = ""
        pid_fg = 0
    _fg_cache["t"] = ahora
    _fg_cache["v"] = valor
    _fg_cache["pid"] = pid_fg
    return valor

def _nivel_integridad_proceso(pid):
    """El RID del nivel de integridad del token de un proceso (el
    último subauthority de su SID de TokenIntegrityLevel), o None si
    no se puede leer. Referencia: 0x1000 bajo, 0x2000 medio,
    0x3000 alto (administrador)."""
    try:
        kernel32 = _kernel32()
        advapi32 = _advapi32()
        handle = kernel32.OpenProcess(0x1000, False, pid)  # QUERY_LIMITED_INFORMATION
        if not handle:
            return None
        try:
            token = wintypes.HANDLE()
            if not advapi32.OpenProcessToken(handle, 0x0008, ctypes.byref(token)):  # TOKEN_QUERY
                return None
            try:
                class SID_AND_ATTRIBUTES(ctypes.Structure):
                    _fields_ = [("Sid", ctypes.c_void_p),
                                ("Attributes", wintypes.DWORD)]
                class TOKEN_MANDATORY_LABEL(ctypes.Structure):
                    _fields_ = [("Label", SID_AND_ATTRIBUTES)]
                tam = wintypes.DWORD(0)
                advapi32.GetTokenInformation(token, 25, None, 0, ctypes.byref(tam))  # TokenIntegrityLevel
                if not tam.value:
                    return None
                buf = ctypes.create_string_buffer(tam.value)
                if not advapi32.GetTokenInformation(token, 25, buf, tam.value, ctypes.byref(tam)):
                    return None
                etiqueta = ctypes.cast(buf, ctypes.POINTER(TOKEN_MANDATORY_LABEL)).contents
                sid = etiqueta.Label.Sid
                if not sid:
                    return None
                puntero_cuenta = advapi32.GetSidSubAuthorityCount(sid)
                if not puntero_cuenta:
                    return None
                cuenta = puntero_cuenta.contents.value
                if not cuenta:
                    return None
                puntero_rid = advapi32.GetSidSubAuthority(sid, cuenta - 1)
                if not puntero_rid:
                    return None
                return puntero_rid.contents.value
            finally:
                kernel32.CloseHandle(token)
        finally:
            kernel32.CloseHandle(handle)
    except Exception:
        return None

def fg_elevado():
    """True si el programa en primer plano corre con un nivel de
    integridad MAYOR que el de este servidor (1.9.1, punto 8 de la
    revisión): entonces Windows (UIPI) no deja que SendInput le
    entregue los atajos, y el editor lo avisa de forma discreta junto
    al programa detectado. False si no hay elevación; None fuera de
    Windows o si no se puede saber — el editor solo avisa con True.
    Caché de unos segundos: el aviso no necesita ser instantáneo."""
    global _fg_elev_cache
    if not ES_WINDOWS:
        return None
    ahora = time.time()
    if ahora - _fg_elev_cache["t"] < 3.0:
        return _fg_elev_cache["v"]
    programa_en_primer_plano()  # refresca _fg_cache (nombre y PID)
    valor = None
    pid_fg = _fg_cache.get("pid") or 0
    if pid_fg and pid_fg != os.getpid():
        suyo = _nivel_integridad_proceso(pid_fg)
        mio = _nivel_integridad_proceso(os.getpid())
        if suyo is not None and mio is not None:
            valor = bool(suyo > mio)
    elif pid_fg:
        valor = False  # el propio servidor en primer plano: misma integridad
    _fg_elev_cache["t"] = ahora
    _fg_elev_cache["v"] = valor
    return valor

def config_para_enviar():
    salida = dict(CONFIG)
    salida["_fg"] = programa_en_primer_plano()
    # v1.6.1: sin barras deslizantes — tampoco salen si la configuración
    # que hubiera guardada aún las trajera.
    paginas = []
    for pg in salida.get("pages", []):
        copia = dict(pg)
        copia.pop("sliders", None)
        paginas.append(copia)
    salida["pages"] = paginas
    return salida

# ---------------------------------------------------------------- ejecución
registro = []          # últimos movimientos, para verlos en el editor

_candado_registro = threading.Lock()

def anota(texto):
    # 1.9.1 (punto 7 de la revisión): el registro se muta desde
    # muchos hilos (HTTP, Bluetooth, el puente); con candado.
    with _candado_registro:
        registro.insert(0, {"hora": time.strftime("%H:%M:%S"), "texto": texto})
        del registro[40:]
    print("[iMandro]", texto, flush=True)

VK_ESPECIAL = {
    "SPACE": 0x20, "ENTER": 0x0D, "ESC": 0x1B, "ESCAPE": 0x1B, "TAB": 0x09,
    "BACKSPACE": 0x08, "DELETE": 0x2E, "SUPR": 0x2E, "INSERT": 0x2D,
    "HOME": 0x24, "END": 0x23, "PGUP": 0x21, "PGDN": 0x22,
    "LEFT": 0x25, "UP": 0x26, "RIGHT": 0x27, "DOWN": 0x28,
    "[": 0xDB, "]": 0xDD, ";": 0xBA, "'": 0xDE, ",": 0xBC, ".": 0xBE,
    "/": 0xBF, "-": 0xBD, "=": 0xBB, "`": 0xC0, "\\": 0xDC, "+": 0xBB,
}
VK_MEDIA = {"volup": 0xAF, "voldn": 0xAE, "mute": 0xAD, "playpause": 0xB3,
            "next": 0xB0, "prev": 0xB1, "stop": 0xB2}

def vk_de(tecla):
    t = tecla.strip().upper()
    if t in VK_ESPECIAL: return VK_ESPECIAL[t]
    if t.startswith("F") and t[1:].isdigit(): return 0x70 + int(t[1:]) - 1
    if len(t) == 1: return ord(t)
    return None

def pulsa(vk, bajar):
    # 1.9.1 (punto 8): SendInput en vez del keybd_event de siempre,
    # con la misma semántica (bajar/subir; los tiempos los ponen los
    # llamantes). En las pruebas vale también fuera de Windows si
    # hay un SendInput falso que capturar (SEND_INPUT_PRUEBA).
    if ES_WINDOWS or SEND_INPUT_PRUEBA is not None:
        _envia_tecla(vk, bajar)

# ---------- 1.7.7: caracteres sueltos con VkKeyScanW ----------
# En la 1.7.6, un carácter suelto se traducía con ord() (en vk_de),
# que solo acierta con A-Z y 0-9: la «Ñ» salía como VK 0xD1, que no
# es la tecla de la Ñ en el teclado español (la real es 0xBA), y no
# pasaba nada aunque el servidor contestara «ok». Y la tecla «+»
# metía un Shift que no se había pedido: en el teclado español el
# «+» es la tecla 0xBB SIN Shift (con Shift esa tecla da «*»), así
# que «Ctrl+Shift++» llegaba como otra cosa. Desde la 1.7.7, un
# carácter fuera del conjunto seguro se traduce con VkKeyScanW del
# diseño de teclado activo: devuelve el código de tecla real y si
# ESE carácter necesita las mayúsculas en ese diseño.
def _vk_key_scan_windows(caracter):
    """VkKeyScanW real (Windows). Devuelve (vk, necesita_shift) o None
    si el carácter no se puede teclear en este diseño.
    1.9.1 (el arreglo de la «Ñ»): la llamada va por _user32(), que
    declara VkKeyScanW con argtypes [c_wchar] y restype c_short.
    Antes se llamaba a pelo por ctypes.windll, sin prototipo: ctypes
    convertía el carácter a ANSI (un byte), Windows no lo reconocía
    y devolvía -1, y resolver_caracter caía en su red de seguridad
    ord('Ñ') = 0xD1 — que NO es la tecla de la Ñ en el teclado
    español (la real es 0xBA). El «+» sí funcionaba porque está en
    la tabla fija VK_ESPECIAL y nunca pasaba por esta llamada."""
    try:
        r = _user32().VkKeyScanW(caracter)
    except Exception:
        return None
    if r == -1 or (r & 0xFF) == 0xFF:
        return None
    return (r & 0xFF), bool(r & 0x100)

# El resolvedor activo: en Windows, VkKeyScanW. Las pruebas lo
# sustituyen por uno falso con el diseño español.
VK_KEY_SCAN = _vk_key_scan_windows if ES_WINDOWS else None

def resolver_caracter(caracter, vk_key_scan=None):
    """Traduce UN carácter suelto a (vk, necesita_shift):
    - A-Z y 0-9: como siempre (ord del carácter en mayúscula, sin
      Shift: las mayúsculas las ponen los modificadores pedidos).
    - Los caracteres de la tabla VK_ESPECIAL: la tecla de siempre,
      sin Shift.
    - Todo lo demás: VkKeyScanW, que conoce el diseño real del
      teclado. Si tampoco sabe (o no es Windows), queda el ord() de
      siempre como red de seguridad.
    «vk_key_scan» es inyectable para poder probarlo sin Windows."""
    if len(caracter) == 1 and ("A" <= caracter <= "Z" or "0" <= caracter <= "9"):
        return (ord(caracter), False)
    if caracter in VK_ESPECIAL:
        return (VK_ESPECIAL[caracter], False)
    if len(caracter) != 1:
        return (None, False)
    if vk_key_scan is None:
        vk_key_scan = VK_KEY_SCAN
    if vk_key_scan is not None:
        r = vk_key_scan(caracter)
        if r:
            return r
    return (ord(caracter.upper()), False)

def _dividir_atajo(combo):
    """Trocea una combinación («Ctrl+Shift+Ñ»): las partes son los
    modificadores y, al final, la tecla. Es el troceo de siempre,
    con su misma regla: una combinación que termina en «+» lleva la
    tecla «+» al final («Ctrl++» es Ctrl y la tecla «+»), porque al
    trocear el separador se la come."""
    partes = [p.strip() for p in (combo or "").split("+") if p.strip() != ""]
    if (combo or "").rstrip().endswith("+"):
        partes.append("+")
    return partes

def enviar_atajo(combo):
    """combo tipo 'Ctrl+Shift+Z'. Las combinaciones de siempre
    (letras, dígitos, F1-F12, caracteres de la tabla) producen
    exactamente las mismas pulsaciones que en la 1.7.6; solo cambia
    la tecla final cuando es UN carácter fuera del conjunto seguro,
    que pasa por VkKeyScanW (1.7.7), y la tecla «+», que ya no mete
    un Shift que no se pidió."""
    partes = [p.strip() for p in (combo or "").split("+") if p.strip() != ""]
    if not partes: return False, "atajo vacío"
    # '+' como tecla final (ej. 'Ctrl++')
    if (combo or "").rstrip().endswith("+"):
        partes.append("+")
    mods = {"CTRL": 0x11, "CONTROL": 0x11, "ALT": 0x12, "SHIFT": 0x10,
            "WIN": 0x5B, "CMD": 0x5B}
    bajados = []
    try:
        for p in partes[:-1]:
            vk = mods.get(p.upper())
            if vk is None: return False, "modificador no válido: " + p
            pulsa(vk, True); bajados.append(vk)
        ultima = partes[-1]
        if len(ultima) == 1 and ultima not in VK_ESPECIAL and \
                not ("A" <= ultima.upper() <= "Z" or ultima.isdigit()):
            # Carácter suelto fuera del conjunto seguro: VkKeyScanW.
            vk, necesita_shift = resolver_caracter(ultima)
            if vk is None: return False, "tecla no válida: " + ultima
            if necesita_shift and 0x10 not in bajados:
                pulsa(0x10, True); bajados.append(0x10)
        else:
            vk = vk_de(ultima)
            if vk is None: return False, "tecla no válida: " + ultima
        pulsa(vk, True); time.sleep(0.03); pulsa(vk, False)
        return True, ""
    finally:
        for vk in reversed(bajados):
            pulsa(vk, False)

def enviar_tecla_media(clave):
    vk = VK_MEDIA.get(clave)
    if vk is None: return False, "tecla multimedia no válida"
    pulsa(vk, True); time.sleep(0.03); pulsa(vk, False)
    return True, ""

def _clave_version(texto):
    """La versión como números: «28.0» → (28, 0); «Adobe Photoshop 9»
    → (9,). Comparar tuplas así elige 28 sobre 9, cosa que el orden
    de texto hacía al revés («9» gana a «28» como letra)."""
    nums = []
    for trozo in str(texto or "").replace(",", ".").split("."):
        digitos = ""
        for ch in trozo:
            if ch.isdigit():
                digitos += ch
            elif digitos:
                break
        if digitos:
            nums.append(int(digitos))
    return tuple(nums)

def _elegir_por_version(candidatos):
    """De [(versión, ruta)] devuelve la ruta de la versión
    numéricamente mayor; a igual versión, la última de la lista."""
    mejor, mejor_clave = "", ()
    for ver, ruta in candidatos:
        if not ruta:
            continue
        clave = _clave_version(ver)
        if not mejor or clave >= mejor_clave:
            mejor, mejor_clave = ruta, clave
    return mejor

def _rutas_desde_registro(nombre_exe, texto_producto):
    """Busca un programa de Adobe en el registro de Windows (1.9.2,
    punto 6): la ruta de App Paths y las claves de desinstalación
    (DisplayName + DisplayVersion + InstallLocation). Devuelve
    [(versión, ruta)]. Solo Windows; ante cualquier problema, lista
    vacía — la búsqueda sigue por las rutas conocidas. Los bancos la
    sustituyen por un registro falso inyectado."""
    if not ES_WINDOWS:
        return []
    try:
        import winreg
    except Exception:
        return []
    encontradas = []
    for raiz in (winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER):
        try:
            with winreg.OpenKey(raiz, r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths" + "\\" + nombre_exe) as k:
                ruta, _ = winreg.QueryValueEx(k, None)
            if ruta:
                encontradas.append(("", str(ruta)))
        except Exception:
            pass
    claves = (r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
              r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall")
    for raiz in (winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER):
        for clave in claves:
            try:
                with winreg.OpenKey(raiz, clave) as k:
                    i = 0
                    while True:
                        try:
                            sub = winreg.EnumKey(k, i)
                        except OSError:
                            break
                        i += 1
                        try:
                            with winreg.OpenKey(k, sub) as sk:
                                nombre, _ = winreg.QueryValueEx(sk, "DisplayName")
                                if texto_producto.lower() not in str(nombre).lower():
                                    continue
                                version, _ = winreg.QueryValueEx(sk, "DisplayVersion")
                                carpeta, _ = winreg.QueryValueEx(sk, "InstallLocation")
                        except Exception:
                            continue
                        if carpeta:
                            encontradas.append((str(version or ""),
                                                os.path.join(str(carpeta), nombre_exe)))
            except Exception:
                pass
    return encontradas

def _ruta_programa_adobe(nombre_exe, texto_producto, patron_glob, clave_config):
    """La ruta de un programa de Adobe, por este orden (1.9.2,
    punto 6): 1) la ruta propia guardada en la configuración, si
    existe de verdad; 2) el registro de Windows, eligiendo por
    número de versión; 3) las carpetas conocidas de siempre, también
    por número (ya no por orden de texto)."""
    cfg = globals().get("CONFIG") or {}
    propia = str(cfg.get(clave_config) or "").strip()
    if propia and os.path.exists(propia):
        return propia
    del_registro = _rutas_desde_registro(nombre_exe, texto_producto)
    if del_registro:
        elegida = _elegir_por_version(del_registro)
        if elegida:
            return elegida
    conocidas = []
    for ruta in glob.glob(patron_glob):
        partes = ruta.replace("/", "\\").split("\\")
        version = partes[-2] if len(partes) >= 2 else ""
        conocidas.append((version, ruta))
    return _elegir_por_version(conocidas)

def ruta_photoshop():
    return _ruta_programa_adobe("Photoshop.exe", "Photoshop",
                                r"C:\Program Files\Adobe\Adobe Photoshop *\Photoshop.exe",
                                "rutaPhotoshop")

def ruta_lightroom():
    return _ruta_programa_adobe("Lightroom.exe", "Lightroom",
                                r"C:\Program Files\Adobe\Adobe Lightroom Classic\Lightroom.exe",
                                "rutaLightroom")

def _ruta_powershell():
    raiz = os.environ.get("SystemRoot", r"C:\Windows")
    return os.path.join(raiz, "System32", "WindowsPowerShell", "v1.0", "powershell.exe")

CARPETA_PS = os.path.join(tempfile.gettempdir(), "iMandro")

# Cola de Photoshop (1.7): todas las ejecuciones JSX pasan por este candado,
# de una en una y en orden de llegada, para que dos toques a la vez (dos
# teléfonos, o teléfono + «Probar ahora») no se pisen. El resto del servidor
# no se bloquea: cada petición espera en su propio hilo.
cola_photoshop = threading.Lock()
_contador_jsx = [0]
_candado_contador_jsx = threading.Lock()

def _sufijo_jsx_unico():
    with _candado_contador_jsx:
        _contador_jsx[0] += 1
        n = _contador_jsx[0]
    return "-%d-%d-%d" % (os.getpid(), int(time.time() * 1000), n)

def _limpia_jsx_viejos():
    """Borra los .jsx temporales y los papelitos de resultado de hace más
    de una hora (los de esta ejecución no se tocan: Photoshop puede estar
    leyéndolos o escribiéndolos)."""
    try:
        limite = time.time() - 3600
        for nombre in os.listdir(CARPETA_PS):
            if (nombre.startswith("imandro-script") and nombre.endswith(".jsx")) or \
               (nombre.startswith("imandro-resultado") and nombre.endswith(".txt")):
                p = os.path.join(CARPETA_PS, nombre)
                try:
                    if os.path.getmtime(p) < limite:
                        os.remove(p)
                except Exception:
                    pass
    except Exception:
        pass

def _envuelve_jsx(jsx, ruta_resultado):
    """El «papelito de resultado» (1.7.6): envuelve el script que va a
    Photoshop SIN tocarlo — va entero dentro de un try — y al final el
    propio Photoshop escribe en un archivo si salió bien ('OK') o el
    error real ('ERROR: ...'). Hace falta porque Photoshop.exe, en la PC
    de Liesky, ejecuta el script pero devuelve un código de salida de
    error: el puente se lo creía, repetía la orden por la otra ruta y
    las acciones de Photoshop se hacían DOS veces. Desde la 1.7.6 el
    puente cree el papelito, no el código del lanzador."""
    ruta_js = ruta_resultado.replace("\\", "\\\\")
    return ("var __imandroRes='OK';try{\n" + jsx +
            "\n}catch(__imandroE){__imandroRes='ERROR: '+((__imandroE&&__imandroE.message)?__imandroE.message:__imandroE);}"
            "try{var __imandroF=new File('" + ruta_js + "');__imandroF.open('w');"
            "__imandroF.write(__imandroRes);__imandroF.close();}catch(__imandroE2){}")

def _lee_papelito(ruta_resultado, segundos):
    """Espera hasta `segundos` a que aparezca el papelito de resultado y
    devuelve su contenido ('OK' o 'ERROR: ...'); None si no aparece."""
    limite = time.time() + segundos
    while True:
        try:
            with open(ruta_resultado, "r", encoding="utf-8", errors="replace") as f:
                texto = f.read().strip()
            if texto:
                return texto
        except Exception:
            pass
        if time.time() >= limite:
            return None
        time.sleep(0.3)

def _veredicto_papelito(texto):
    """(hecho, mensaje) según el papelito: 'OK' es éxito y 'ERROR: x' es
    el fallo con las palabras del propio Photoshop."""
    if texto.startswith("OK"):
        return True, ""
    if texto.startswith("ERROR:"):
        return False, texto[len("ERROR:"):].strip() or "Photoshop devolvió un error"
    return False, texto[:200]

def _limpia_error_powershell(texto):
    """El error de PowerShell llega a veces «serializado» (CLIXML: la
    primera línea es '#< CLIXML' y el resto, palabrería XML ilegible —
    eso era lo que enseñaba el aviso en el teléfono). Se devuelve la
    primera línea legible; si no hay ninguna, se intenta sacar el texto
    del propio CLIXML quitándole las etiquetas."""
    lineas = [l.strip() for l in texto.splitlines()]
    # Legible = ni la cabecera del CLIXML ('#< ...') ni etiquetas XML
    # sueltas ('<Objs ...'): un error de verdad nunca empieza así.
    utiles = [l for l in lineas if l and not l.startswith("#<") and not l.startswith("<")]
    if utiles:
        return utiles[0][:200]
    import re
    trozos = re.findall(r'<S S="Error">(.*?)</S>', texto, re.S) or \
             re.findall(r"<S[^>]*>(.*?)</S>", texto, re.S)
    plano = " ".join(trozos)
    plano = plano.replace("_x000D_", " ").replace("_x000A_", " ").replace("_x0009_", " ")
    plano = (plano.replace("&lt;", "<").replace("&gt;", ">").replace("&quot;", '"')
                  .replace("&apos;", "'").replace("&amp;", "&"))
    plano = " ".join(plano.split())
    return plano[:200] if plano else "error sin detalle"

def _jsx_por_archivo(jsx, sufijo="", timeout=25, ruta_resultado=""):
    """Ruta principal desde la v1.6: el script viaja como archivo .jsx
    directo a Photoshop.exe. No depende de PowerShell ni del registro COM.
    Desde la 1.7 el archivo es ÚNICO por ejecución (sufijo con pid, hora
    y contador): dos ejecuciones nunca comparten archivo.
    Devuelve (hecho, mensaje, contesto). El caso bueno NO cambia: si
    Photoshop.exe sale con código 0, éxito inmediato, como siempre.
    Solo cuando el código es de error (o la espera vence) se consulta el
    papelito (1.7.6): si Photoshop lo dejó, su veredicto manda y
    «contesto» es True — la orden ya se hizo o ya falló dentro de
    Photoshop y NO se repite por la otra ruta."""
    ps = ruta_photoshop()
    if not ps:
        return False, "no encontré Photoshop en la ruta habitual (C:\\Program Files\\Adobe)", False
    try:
        os.makedirs(CARPETA_PS, exist_ok=True)
        _limpia_jsx_viejos()
        ruta = os.path.join(CARPETA_PS, "imandro-script%s.jsx" % (sufijo or _sufijo_jsx_unico()))
        with open(ruta, "w", encoding="utf-8") as f:
            f.write(jsx)
        proceso = subprocess.Popen([ps, ruta], stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE, creationflags=SIN_VENTANA)
        try:
            _, errb = proceso.communicate(timeout=timeout)
            codigo = proceso.returncode
        except subprocess.TimeoutExpired:
            # Sigue vivo y NO se mata: Photoshop puede estar arrancando
            # en frío o con un diálogo de la propia acción abierto.
            codigo, errb = None, b""
        if codigo == 0:
            return True, "", False
        if ruta_resultado:
            # Tras un timeout se espera más: el arranque en frío es lento.
            papelito = _lee_papelito(ruta_resultado, 15 if codigo is None else 6)
            if papelito is not None:
                ok, msg = _veredicto_papelito(papelito)
                return ok, msg, True
        if codigo is None:
            return False, "Photoshop no terminó de responder", False
        err = (errb or b"").decode("utf-8", "replace").strip()
        return False, "Photoshop devolvió un error" + ((": " + err[:200]) if err else ""), False
    except Exception as e:
        return False, str(e), False

def _jsx_por_powershell(jsx, ruta_resultado=""):
    """Ruta de reserva: PowerShell llamado por su ruta completa (la búsqueda
    por el nombre corto fallaba en la PC de Liesky con WinError 2) y el script
    codificado en Base64, para que las comillas no lo corten.
    Manda la MISMA envoltura que la ruta del archivo: al volver, si hay
    papelito, su veredicto manda también aquí (1.7.6). Sin papelito vale
    lo de siempre: código 0 es éxito y si no, el error — ya limpio del
    CLIXML — como mensaje."""
    try:
        b64jsx = base64.b64encode(jsx.encode("utf-8")).decode("ascii")
        orden = ("$jsx=[Text.Encoding]::UTF8.GetString([Convert]::FromBase64String('%s'));"
                 "$ps=New-Object -ComObject Photoshop.Application;$ps.DoJavaScript($jsx)") % b64jsx
        codificado = base64.b64encode(orden.encode("utf-16-le")).decode("ascii")
        r = subprocess.run([_ruta_powershell(), "-NoProfile", "-EncodedCommand", codificado],
                           capture_output=True, timeout=25, creationflags=SIN_VENTANA)
        if ruta_resultado:
            papelito = _lee_papelito(ruta_resultado, 3)
            if papelito is not None:
                ok, msg = _veredicto_papelito(papelito)
                return ok, msg, True
        if r.returncode == 0:
            return True, "", False
        err = _limpia_error_powershell((r.stderr or b"").decode("utf-8", "replace"))
        return False, "PowerShell: " + err, False
    except subprocess.TimeoutExpired:
        # 1.7.9 (auditoría C2): esta era la única vía del puente que no
        # consultaba el papelito al vencer su espera: Photoshop podía
        # completar la orden por COM un segundo después y el aviso
        # decía «falló» con la acción ya hecha. Ahora lo consulta unos
        # segundos, como las demás vías, antes de declarar el fallo.
        if ruta_resultado:
            papelito = _lee_papelito(ruta_resultado, 5)
            if papelito is not None:
                ok, msg = _veredicto_papelito(papelito)
                return ok, msg, True
        return False, "PowerShell no contestó a tiempo", False
    except Exception as e:
        return False, str(e), False

def ejecutar_jsx(jsx):
    """Manda un script (JSX) a Photoshop por la ruta del archivo y, solo
    si esa ruta no obtiene respuesta, por el puente de PowerShell con
    ruta completa.
    Desde la 1.7 todas las ejecuciones pasan por la cola (cola_photoshop):
    se hacen de una en una, en orden de llegada.
    Desde la 1.7.6 el script viaja envuelto con el papelito de resultado
    y con un sufijo único compartido por el .jsx y el papelito: si
    Photoshop ya contestó por el papelito (bien o mal), la orden NO se
    repite por la otra ruta."""
    if not jsx or not jsx.strip():
        return False, "el script está vacío"
    with cola_photoshop:
        sufijo = _sufijo_jsx_unico()
        ruta_resultado = os.path.join(CARPETA_PS, "imandro-resultado%s.txt" % sufijo)
        envuelto = _envuelve_jsx(jsx, ruta_resultado)
        try:
            try:
                os.makedirs(CARPETA_PS, exist_ok=True)
                if os.path.exists(ruta_resultado):
                    os.remove(ruta_resultado)
            except Exception:
                pass
            ok, msg, contesto = _jsx_por_archivo(envuelto, sufijo=sufijo,
                                                 ruta_resultado=ruta_resultado)
            if ok:
                return True, ""
            if contesto:
                return False, msg
            ok2, msg2, contesto2 = _jsx_por_powershell(envuelto, ruta_resultado=ruta_resultado)
            if ok2:
                return True, ""
            if contesto2:
                return False, msg2
            return False, "Photoshop no respondió. Por archivo: %s · Por el puente: %s" % (msg, msg2)
        finally:
            try:
                os.remove(ruta_resultado)
            except Exception:
                pass

def _guid(hexs):
    import uuid as _u
    class GUID(ctypes.Structure):
        _fields_ = [("d", ctypes.c_ubyte * 16)]
    g = GUID()
    ctypes.memmove(ctypes.byref(g), _u.UUID(hexs).bytes_le, 16)
    return g

def _volumen_endpoint():
    """IAudioEndpointVolume del altavoz por defecto, o None. Se crea en cada
    llamada: el servidor es multihilo y COM funciona por apartamentos."""
    ole32 = ctypes.windll.ole32
    ole32.CoInitialize(None)
    enum = ctypes.c_void_p()
    if ole32.CoCreateInstance(ctypes.byref(_guid("BCDE0395-E52F-467C-8E3D-C4579291692E")), None, 23,
                              ctypes.byref(_guid("A95664D2-9614-4F35-A746-DE8DB63617E6")),
                              ctypes.byref(enum)) != 0 or not enum:
        return None
    dev = ctypes.c_void_p()
    vtbl = ctypes.cast(enum, ctypes.POINTER(ctypes.c_void_p))[0]
    fn = ctypes.WINFUNCTYPE(ctypes.c_long, ctypes.c_void_p, ctypes.c_int, ctypes.c_int,
                            ctypes.POINTER(ctypes.c_void_p))
    getdef = ctypes.cast(ctypes.cast(vtbl, ctypes.POINTER(ctypes.c_void_p))[4], fn)
    if getdef(enum, 0, 0, ctypes.byref(dev)) != 0 or not dev:
        return None
    vol = ctypes.c_void_p()
    vtbl2 = ctypes.cast(dev, ctypes.POINTER(ctypes.c_void_p))[0]
    fn2 = ctypes.WINFUNCTYPE(ctypes.c_long, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_ulong,
                             ctypes.c_void_p, ctypes.POINTER(ctypes.c_void_p))
    act = ctypes.cast(ctypes.cast(vtbl2, ctypes.POINTER(ctypes.c_void_p))[3], fn2)
    if act(dev, ctypes.byref(_guid("5CDF2C82-841E-4546-9722-0CF74078229A")), 23, None,
           ctypes.byref(vol)) != 0 or not vol:
        return None
    return vol

def _llama_vtbl(obj, idx, prototipo):
    vtbl = ctypes.cast(obj, ctypes.POINTER(ctypes.c_void_p))[0]
    return ctypes.cast(ctypes.cast(vtbl, ctypes.POINTER(ctypes.c_void_p))[idx], prototipo)

def valor_volumen():
    """Volumen general real de Windows (0-100), o None si no se puede leer."""
    if not ES_WINDOWS:
        return None
    try:
        vol = _volumen_endpoint()
        if not vol:
            return None
        fn = ctypes.WINFUNCTYPE(ctypes.c_long, ctypes.c_void_p, ctypes.POINTER(ctypes.c_float))
        nivel = ctypes.c_float()
        if _llama_vtbl(vol, 9, fn)(vol, ctypes.byref(nivel)) != 0:
            return None
        return round(nivel.value * 100)
    except Exception:
        return None

def fijar_volumen(v):
    """Fija el volumen general de Windows al valor exacto (0-100)."""
    try:
        vol = _volumen_endpoint()
        if not vol:
            return False
        fn = ctypes.WINFUNCTYPE(ctypes.c_long, ctypes.c_void_p, ctypes.c_float, ctypes.c_void_p)
        return _llama_vtbl(vol, 7, fn)(vol, max(0.0, min(1.0, v / 100.0)), None) == 0
    except Exception:
        return False

def ejecutar_raton(btn, mods=""):
    """Clics y rueda del ratón donde esté el puntero (nuevo en la v1.6).
    «mods» puede traer teclas especiales («Ctrl+Alt») que se mantienen
    pulsadas durante el clic: Alt+clic del tampón de clonar, Ctrl+clic, etc."""
    u = ctypes.windll.user32
    ABAJO = {"left": 0x0002, "right": 0x0008, "middle": 0x0020}
    ARRIBA = {"left": 0x0004, "right": 0x0010, "middle": 0x0040}
    VK_MODS = {"CTRL": 0x11, "CONTROL": 0x11, "ALT": 0x12, "SHIFT": 0x10,
               "WIN": 0x5B, "CMD": 0x5B}
    def clic(b):
        u.mouse_event(ABAJO[b], 0, 0, 0, 0); time.sleep(0.05); u.mouse_event(ARRIBA[b], 0, 0, 0, 0)
    bajados = []
    try:
        for m in (mods or "").split("+"):
            vk = VK_MODS.get(m.strip().upper())
            if vk:
                pulsa(vk, True); bajados.append(vk)
        if bajados:
            time.sleep(0.03)
        if btn in ABAJO:
            clic(btn); return True, ""
        if btn == "dblclick":
            clic("left"); time.sleep(0.08); clic("left"); return True, ""
        if btn in ("wheelup", "wheeldown"):
            dato = 120 if btn == "wheelup" else -120
            u.mouse_event(0x0800, 0, 0, ctypes.c_ulong(dato & 0xFFFFFFFF), 0); return True, ""
        return False, "botón del ratón no válido"
    finally:
        for vk in reversed(bajados):
            pulsa(vk, False)

# ------------------------------------- selector de archivos (ctypes)
# 1.9.2 (punto 17 de la revisión): el selector de archivos deja de
# lanzarse con PowerShell -EncodedCommand (la vía de la 1.6.1) y pasa
# a ser el diálogo propio de Windows llamado por ctypes desde este
# mismo proceso: GetOpenFileNameW para programas y SHBrowseForFolderW
# para carpetas, con las estructuras declaradas enteras. El Python
# embebido del instalador sí trae ctypes y comdlg32/shell32 son DLL
# del sistema, así que la vía es viable sin tkinter (que era el
# muerto de la v1.6) y sin procesos extra. Los bancos sustituyen los
# cargadores de DLL por falsos y ejercitan la construcción real de
# las llamadas.

# Las estructuras van con tipos de tamaño fijo (no con wintypes, que
# en el ctypes de Linux cuenta DWORD como 8 bytes): así la
# disposición es la de Win64 en cualquier plataforma — OPENFILENAMEW
# 152 bytes y BROWSEINFOW 64 — y el banco lo puede asertar aquí igual
# que en Windows.
class _OPENFILENAMEW(ctypes.Structure):
    _fields_ = [("lStructSize", ctypes.c_uint32),
                ("hwndOwner", ctypes.c_void_p),
                ("hInstance", ctypes.c_void_p),
                ("lpstrFilter", ctypes.c_wchar_p),
                ("lpstrCustomFilter", ctypes.c_wchar_p),
                ("nMaxCustFilter", ctypes.c_uint32),
                ("nFilterIndex", ctypes.c_uint32),
                ("lpstrFile", ctypes.c_wchar_p),
                ("nMaxFile", ctypes.c_uint32),
                ("lpstrFileTitle", ctypes.c_wchar_p),
                ("nMaxFileTitle", ctypes.c_uint32),
                ("lpstrInitialDir", ctypes.c_wchar_p),
                ("lpstrTitle", ctypes.c_wchar_p),
                ("Flags", ctypes.c_uint32),
                ("nFileOffset", ctypes.c_uint16),
                ("nFileExtension", ctypes.c_uint16),
                ("lpstrDefExt", ctypes.c_wchar_p),
                ("lCustData", ctypes.c_ssize_t),
                ("lpfnHook", ctypes.c_void_p),
                ("lpTemplateName", ctypes.c_wchar_p),
                ("pvReserved", ctypes.c_void_p),
                ("dwReserved", ctypes.c_uint32),
                ("FlagsEx", ctypes.c_uint32)]

class _BROWSEINFOW(ctypes.Structure):
    _fields_ = [("hwndOwner", ctypes.c_void_p),
                ("pidlRoot", ctypes.c_void_p),
                ("pszDisplayName", ctypes.c_wchar_p),
                ("lpszTitle", ctypes.c_wchar_p),
                ("ulFlags", ctypes.c_uint32),
                ("lpfn", ctypes.c_void_p),
                ("lParam", ctypes.c_ssize_t),
                ("iImage", ctypes.c_int32)]

_comdlg32_c = None
def _comdlg32():
    global _comdlg32_c
    if _comdlg32_c is None:
        d = ctypes.WinDLL("comdlg32", use_last_error=True)
        d.GetOpenFileNameW.argtypes = [ctypes.POINTER(_OPENFILENAMEW)]
        d.GetOpenFileNameW.restype = ctypes.c_int
        _comdlg32_c = d
    return _comdlg32_c

_shell32_c = None
def _shell32():
    global _shell32_c
    if _shell32_c is None:
        d = ctypes.WinDLL("shell32", use_last_error=True)
        d.SHBrowseForFolderW.argtypes = [ctypes.POINTER(_BROWSEINFOW)]
        d.SHBrowseForFolderW.restype = ctypes.c_void_p
        d.SHGetPathFromIDListW.argtypes = [ctypes.c_void_p, ctypes.c_wchar_p]
        d.SHGetPathFromIDListW.restype = ctypes.c_int
        _shell32_c = d
    return _shell32_c

_ole32_c = None
def _ole32():
    global _ole32_c
    if _ole32_c is None:
        d = ctypes.WinDLL("ole32", use_last_error=True)
        d.CoInitialize.argtypes = [ctypes.c_void_p]
        d.CoInitialize.restype = ctypes.c_int32
        d.CoTaskMemFree.argtypes = [ctypes.c_void_p]
        d.CoTaskMemFree.restype = None
        _ole32_c = d
    return _ole32_c

def _dialogo_programa_ctypes():
    """GetOpenFileNameW con el filtro de programas de siempre.
    Devuelve la ruta escogida o «» si se canceló."""
    buf = ctypes.create_unicode_buffer(32768)
    ofn = _OPENFILENAMEW()
    ofn.lStructSize = ctypes.sizeof(_OPENFILENAMEW)
    ofn.lpstrFilter = "Programas (*.exe)\0*.exe\0Todos los archivos (*.*)\0*.*\0\0"
    # El campo es un puntero a texto: va un c_wchar_p con la
    # dirección del búfer (asignar el array a pelo lanza TypeError
    # en ctypes, y el entero suelto se lee como texto al volver).
    ofn.lpstrFile = ctypes.c_wchar_p(ctypes.addressof(buf))
    ofn.nMaxFile = 32768
    ofn.lpstrTitle = "Escoge el programa"
    # OFN_EXPLORER | OFN_FILEMUSTEXIST | OFN_PATHMUSTEXIST | OFN_NOCHANGEDIR
    ofn.Flags = 0x00080000 | 0x00001000 | 0x00000800 | 0x00000008
    if _comdlg32().GetOpenFileNameW(ctypes.byref(ofn)):
        return buf.value
    return ""

def _dialogo_carpeta_ctypes():
    """SHBrowseForFolderW con el estilo nuevo de diálogo. Devuelve la
    carpeta escogida o «» si se canceló."""
    try:
        _ole32().CoInitialize(None)
    except Exception:
        pass
    nombre = ctypes.create_unicode_buffer(32768)
    bi = _BROWSEINFOW()
    bi.pszDisplayName = ctypes.c_wchar_p(ctypes.addressof(nombre))
    bi.lpszTitle = "Escoge la carpeta"
    # BIF_RETURNONLYFSDIRS | BIF_NEWDIALOGSTYLE
    bi.ulFlags = 0x0001 | 0x0040
    pidl = _shell32().SHBrowseForFolderW(ctypes.byref(bi))
    if not pidl:
        return ""
    try:
        buf = ctypes.create_unicode_buffer(32768)
        if _shell32().SHGetPathFromIDListW(pidl, buf):
            return buf.value
        return ""
    finally:
        try:
            _ole32().CoTaskMemFree(pidl)
        except Exception:
            pass

def buscar_ruta(modo):
    """Abre el selector de archivos de Windows en esta PC (para los botones
    «Buscar…» del editor) y devuelve la ruta escogida.

    Historia: la v1.6 lo hacía con tkinter (el Python embebido no lo
    trae y el selector moría antes de abrirse); la v1.6.1 pasó al
    diálogo de Windows lanzado con PowerShell; la 1.9.2 (punto 17)
    llama al mismo diálogo por ctypes, sin procesos extra."""
    if not ES_WINDOWS:
        return False, "", "el selector de archivos solo funciona en la PC de Windows"
    # 1.7.4: UN SOLO diálogo por clic. Antes el modo «ruta» abría un
    # selector de archivos y, solo si se cancelaba, el de carpetas:
    # para escoger una carpeta había que cancelar el primero, y Liesky
    # lo reportó como «un explorador que no funciona y al cancelar
    # sale otro». El editor ahora manda «programa» o «carpeta» según
    # el botón que se toque; cualquier otro modo es un error.
    if modo not in ("programa", "carpeta"):
        return False, "", "modo de selector no válido: «%s»" % modo
    try:
        ruta = (_dialogo_programa_ctypes() if modo == "programa"
                else _dialogo_carpeta_ctypes())
    except Exception as e:
        return False, "", str(e)
    if ruta:
        return True, ruta, ""
    return False, "", "no escogiste nada"

def _escapa_jsx(texto):
    """Escapa un texto para meterlo entre comillas dobles en un script JSX:
    un nombre de acción con comillas o barras ya no puede romper el script."""
    return (texto or "").replace("\\", "\\\\").replace('"', '\\"').replace("\n", " ").replace("\r", " ")

def ejecutar_accion_ps(nombre, conjunto):
    if not nombre: return False, "la acción no tiene nombre"
    if not conjunto:
        return False, "a esta acción le falta el conjunto: escríbelo en el editor de la PC"
    return ejecutar_jsx('app.doAction("%s", "%s");' % (_escapa_jsx(nombre), _escapa_jsx(conjunto)))

def abrir_destino(destino):
    if not destino: return False, "este botón no tiene programa ni carpeta todavía"
    try:
        if destino.startswith("appid:"):
            # Aplicación de Microsoft Store (1.7.4): no tiene una ruta
            # que abrir; Windows la lanza por su identificador con
            # explorer.exe shell:AppsFolder\<AppID>.
            appid = destino[len("appid:"):].strip()
            if not appid: return False, "a este botón le falta el identificador de la aplicación"
            if not ES_WINDOWS: return False, "las aplicaciones de la Store solo se abren en Windows"
            subprocess.Popen(["explorer.exe", "shell:AppsFolder\\" + appid],
                             creationflags=SIN_VENTANA)
            return True, ""
        if destino == "fotos":
            destino = os.path.join(os.path.expanduser("~"), "Pictures")
        if destino == "photoshop":
            destino = ruta_photoshop()
            if not destino: return False, "no encontré Photoshop en la ruta habitual"
        elif destino == "lightroom":
            destino = ruta_lightroom()
            if not destino: return False, "no encontré Lightroom Classic en la ruta habitual"
        if ES_WINDOWS:
            os.startfile(destino)  # noqa: S606 - destino elegido por el propio usuario
        else:
            subprocess.Popen(["xdg-open", destino], creationflags=SIN_VENTANA)
        return True, ""
    except Exception as e:
        return False, str(e)

# ------------------------------------------------- aplicaciones instaladas
# «Elegir aplicación…» (1.7.4): el editor enseña la lista de aplicaciones
# de ESTA PC y el botón guarda la ruta del .exe (programas de siempre) o
# «appid:<AppID>» (aplicaciones de Microsoft Store, que abrir_destino
# lanza con explorer.exe shell:AppsFolder\<AppID>). La lista se lee una
# vez y se guarda en caché unos minutos: juntar Get-StartApps, el
# registro de programas instalados y los accesos del menú Inicio lleva
# unos segundos en una PC normal.
_cache_apps = {"t": 0.0, "lista": None}

def _apps_fuentes():
    """Los datos crudos de Windows, en un solo viaje de PowerShell:
    {start: [{Name, AppID}], uninst: [{DisplayName, DisplayIcon,
    InstallLocation}], lnks: [{Nombre, Destino}]} con los .lnk del menú
    Inicio ya resueltos a su destino. En pruebas se puede inyectar la
    misma forma con la variable IMANDRO_APPS_SIM (ruta a un JSON)."""
    sim = os.environ.get("IMANDRO_APPS_SIM")
    if sim:
        with open(sim, encoding="utf-8") as f:
            return json.load(f)
    if not ES_WINDOWS:
        return {"start": [], "uninst": [], "lnks": []}
    script = (
        "$ErrorActionPreference = 'SilentlyContinue'\n"
        "$start = @(Get-StartApps | ForEach-Object { [PSCustomObject]@{ Name = $_.Name; AppID = $_.AppID } })\n"
        "$uninst = @()\n"
        "foreach ($k in @('HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\*',"
        "'HKLM:\\SOFTWARE\\WOW6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\*',"
        "'HKCU:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\*')) {\n"
        "  $uninst += @(Get-ItemProperty $k | Where-Object { $_.DisplayName } | "
        "ForEach-Object { [PSCustomObject]@{ DisplayName = $_.DisplayName; DisplayIcon = $_.DisplayIcon; InstallLocation = $_.InstallLocation } })\n"
        "}\n"
        "$lnks = @()\n"
        "$sh = New-Object -ComObject WScript.Shell\n"
        "foreach ($dir in @(\"$env:ProgramData\\Microsoft\\Windows\\Start Menu\\Programs\", \"$env:APPDATA\\Microsoft\\Windows\\Start Menu\\Programs\")) {\n"
        "  foreach ($f in @(Get-ChildItem -Path $dir -Recurse -Filter *.lnk)) {\n"
        "    try { $t = $sh.CreateShortcut($f.FullName).TargetPath; if ($t) { $lnks += [PSCustomObject]@{ Nombre = $f.BaseName; Destino = $t } } } catch {}\n"
        "  }\n"
        "}\n"
        "[Console]::Out.Write(([PSCustomObject]@{ start = $start; uninst = $uninst; lnks = $lnks } | ConvertTo-Json -Depth 4 -Compress))\n"
    )
    codificado = base64.b64encode(script.encode("utf-16-le")).decode("ascii")
    r = subprocess.run([_ruta_powershell(), "-NoProfile", "-STA", "-WindowStyle", "Hidden",
                        "-EncodedCommand", codificado],
                       capture_output=True, text=True, timeout=120,
                       creationflags=SIN_VENTANA)
    salida = (r.stdout or "").strip()
    if not salida:
        raise ValueError("PowerShell no devolvió la lista de aplicaciones")
    return json.loads(salida)

def _fusiona_apps(fuentes):
    """Junta las tres fuentes en una lista limpia: una entrada por
    nombre (si un programa se puede abrir por su .exe, esa forma gana a
    la de la tienda), ordenada por nombre."""
    por_nombre = {}
    def mete(nombre, tipo, ruta="", appid=""):
        nombre = (nombre or "").strip()
        if not nombre:
            return
        clave = nombre.casefold()
        nuevo = {"nombre": nombre, "tipo": tipo, "ruta": ruta, "appid": appid,
                 "exe": ruta.replace("\\", "/").rsplit("/", 1)[-1] if ruta else ""}
        viejo = por_nombre.get(clave)
        if viejo is None or (viejo["tipo"] != "exe" and tipo == "exe"):
            por_nombre[clave] = nuevo
    # 1) Accesos del menú Inicio ya resueltos: la ruta .exe más fiable.
    for l in fuentes.get("lnks", []):
        destino = (l.get("Destino") or "").strip()
        if destino.lower().endswith(".exe"):
            mete(l.get("Nombre"), "exe", ruta=destino)
    # 2) Registro de programas instalados: su icono suele apuntar al .exe.
    for u in fuentes.get("uninst", []):
        icono = (u.get("DisplayIcon") or "").strip()
        if "," in icono:
            icono = icono.rsplit(",", 1)[0].strip()
        icono = icono.strip('"')
        if icono.lower().endswith(".exe"):
            mete(u.get("DisplayName"), "exe", ruta=icono)
    # 3) Get-StartApps: lo que falte; las de la Store entran por su AppID.
    for s in fuentes.get("start", []):
        appid = (s.get("AppID") or "").strip()
        if appid.lower().endswith(".exe"):
            mete(s.get("Name"), "exe", ruta=appid)
        elif appid:
            mete(s.get("Name"), "store", appid=appid)
    return sorted(por_nombre.values(), key=lambda a: a["nombre"].casefold())

def lista_aplicaciones(forzar=False):
    """(lista, mensaje_de_error). Con caché de 3 minutos."""
    ahora = time.time()
    if not forzar and _cache_apps["lista"] is not None and ahora - _cache_apps["t"] < 180:
        return _cache_apps["lista"], ""
    try:
        lista = _fusiona_apps(_apps_fuentes())
    except Exception as e:
        if _cache_apps["lista"] is not None:
            return _cache_apps["lista"], ""
        return [], "no se pudo leer la lista de aplicaciones: %s" % e
    _cache_apps.update({"t": ahora, "lista": lista})
    return lista, ""

def _ejecutar_multi(accion):
    # 1.9.1 (punto 5 de la revisión): cada paso se despacha por
    # LA MISMA lógica que un botón suelto — antes solo salían la
    # espera, los atajos y las acciones de Photoshop, y cualquier
    # otro paso (una herramienta, un script, abrir algo,
    # multimedia, el ratón, el sistema) se ignoraba EN SILENCIO y
    # la secuencia decía «ok» igual. Por eso ejecutar() despacha
    # el «multi» ANTES de su guarda de simulación: el despacho
    # aquí es explícito, tipo a tipo, llamando a la misma función
    # ejecutora de cada uno. Fuera de Windows, los pasos con
    # efectos reales (Photoshop, ratón, abrir) se simulan como
    # hace la guarda con un botón suelto, y atajos y multimedia
    # pasan por pulsa(), que fuera de Windows no actúa. Además:
    # - el atajo suelto {keys: …} es una acción hotkey;
    # - un paso que no se reconoce devuelve ERROR, en cualquier
    #   plataforma.
    for paso in accion.get("steps", []):
        if not isinstance(paso, dict):
            return False, ("un paso de la secuencia no se reconoce: "
                           "«%s»" % (paso,))
        if "delay" in paso:
            # 1.7.9 (auditoría C1): la espera se convierte con red
            # de seguridad y se acota entre 0 y 5 000 ms. Antes,
            # una espera no numérica o negativa lanzaba un error
            # dentro del manejador y la petición moría sin
            # respuesta: el teléfono enseñaba un fallo sin mensaje.
            try:
                espera = int(paso["delay"])
            except (TypeError, ValueError):
                return False, ("un paso de la secuencia lleva una "
                               "espera no válida: «%s»" % (paso.get("delay"),))
            time.sleep(max(0, min(espera, 5000)) / 1000.0)
            continue
        ptipo = paso.get("type") or ("hotkey" if paso.get("keys") else "")
        if ptipo == "hotkey":
            ok, msg = enviar_atajo(paso.get("keys", ""))
            anota(("Atajo " + paso.get("keys", "")) if ok else ("Fallo: " + msg))
        elif ptipo == "media":
            ok, msg = enviar_tecla_media(paso.get("key", ""))
            anota("Multimedia " + paso.get("key", "") if ok else "Fallo: " + msg)
        elif ptipo == "mouse":
            if not ES_WINDOWS:
                anota("SIMULADO (paso de ratón)"); ok, msg = True, ""
            else:
                ok, msg = ejecutar_raton(paso.get("btn", "left"), paso.get("mods", ""))
                anota(("Ratón: " + paso.get("btn", "left")) if ok else ("Fallo: " + msg))
        elif ptipo == "pstool":
            if not ES_WINDOWS:
                anota("SIMULADO (paso de herramienta de Photoshop)"); ok, msg = True, ""
            else:
                ok, msg = ejecutar_jsx(jsx_herramienta(paso.get("tool", "")))
                anota("Herramienta de Photoshop" if ok else ("Fallo: " + msg))
        elif ptipo == "psscript":
            if not ES_WINDOWS:
                anota("SIMULADO (paso de script de Photoshop)"); ok, msg = True, ""
            else:
                ok, msg = ejecutar_jsx(paso.get("script", ""))
                anota("Script de Photoshop" if ok else ("Fallo: " + msg))
        elif ptipo == "psaction":
            ok, msg = ejecutar_accion_ps(paso.get("name", ""), paso.get("set", ""))
            anota(("Acción de Photoshop: " + paso.get("name", "")) if ok else ("Fallo: " + msg))
        elif ptipo == "open":
            if not ES_WINDOWS:
                anota("SIMULADO (paso de abrir)"); ok, msg = True, ""
            else:
                ok, msg = abrir_destino(paso.get("target", ""))
                anota(("Abrir " + paso.get("target", "")) if ok else ("Fallo: " + msg))
        elif ptipo == "system":
            # La rama «system» de ejecutar() vive tras la guarda
            # de simulación, así que llamarla desde aquí en un
            # no-Windows devolvería el «ok» simulado sin tocar
            # nada: se reproduce su despacho a mano (en Windows
            # es literalmente lo mismo que hace su rama).
            cmd_s = paso.get("cmd", "")
            if cmd_s == "lock":
                if ES_WINDOWS:
                    ctypes.windll.user32.LockWorkStation()
                anota("PC bloqueada")
                ok, msg = True, ""
            elif cmd_s == "screenshot":
                ok, msg = enviar_atajo("Win+Shift+S")
            elif cmd_s == "explorer":
                ok, msg = enviar_atajo("Win+E")
            else:
                ok, msg = False, "orden del sistema no válida"
        elif ptipo == "multi":
            ok, msg = ejecutar(paso)
        elif ptipo == "page":
            ok, msg = True, ""  # el cambio de página lo hace el teléfono
        elif ptipo == "none":
            ok, msg = False, "este botón todavía no tiene función: asígnala en el editor de la PC"
        else:
            return False, ("un paso de la secuencia no se reconoce: "
                           "«%s»" % (json.dumps(paso, ensure_ascii=False)[:80],))
        if not ok: return ok, msg
    anota("Varios pasos seguidos")
    return True, ""

def ejecutar(accion):
    """Devuelve (ok, mensaje). En máquinas que no son Windows se simula."""
    tipo = (accion or {}).get("type", "none")
    if tipo == "none":
        return False, "este botón todavía no tiene función: asígnala en el editor de la PC"
    if tipo == "page":
        return True, ""  # el cambio de página lo hace el propio teléfono
    if tipo == "multi":
        return _ejecutar_multi(accion)
    if not ES_WINDOWS:
        anota("SIMULADO (esta no es la PC de Windows): " + json.dumps(accion, ensure_ascii=False))
        return True, ""
    if tipo == "hotkey":
        ok, msg = enviar_atajo(accion.get("keys", ""))
        anota(("Atajo " + accion.get("keys", "")) if ok else ("Fallo: " + msg))
        return ok, msg
    if tipo == "media":
        ok, msg = enviar_tecla_media(accion.get("key", ""))
        anota("Multimedia " + accion.get("key", "") if ok else "Fallo: " + msg)
        return ok, msg
    if tipo == "mouse":
        ok, msg = ejecutar_raton(accion.get("btn", "left"), accion.get("mods", ""))
        etq = "Ratón: " + accion.get("btn", "left") + ((" con " + accion.get("mods")) if accion.get("mods") else "")
        anota(etq if ok else ("Fallo: " + msg))
        return ok, msg
    if tipo == "pstool":
        ok, msg = ejecutar_jsx(jsx_herramienta(accion.get("tool", "")))
        anota("Herramienta de Photoshop" if ok else ("Fallo: " + msg))
        return ok, msg
    if tipo == "psscript":
        ok, msg = ejecutar_jsx(accion.get("script", ""))
        anota("Script de Photoshop" if ok else ("Fallo: " + msg))
        return ok, msg
    if tipo == "psaction":
        ok, msg = ejecutar_accion_ps(accion.get("name", ""), accion.get("set", ""))
        anota(("Acción de Photoshop: " + accion.get("name", "")) if ok else ("Fallo: " + msg))
        return ok, msg
    if tipo == "open":
        ok, msg = abrir_destino(accion.get("target", ""))
        anota(("Abrir " + accion.get("target", "")) if ok else ("Fallo: " + msg))
        return ok, msg
    if tipo == "system":
        cmd = accion.get("cmd", "")
        if cmd == "lock":
            ctypes.windll.user32.LockWorkStation(); anota("PC bloqueada"); return True, ""
        if cmd == "screenshot": return enviar_atajo("Win+Shift+S")
        if cmd == "explorer": return enviar_atajo("Win+E")
        return False, "orden del sistema no válida"
    return False, "tipo de acción no válido"

# ------------------------------------------------------- Bluetooth y cable USB
estado_bt = {"activo": False, "conectados": 0}
estado_usb = {"estado": "nodisponible", "detalle": "sin comprobar"}

# Tope de línea Bluetooth (1.7.9, auditoría D4): 8 MB, el triple de la
# configuración más pesada conocida (la que viaja por este canal con
# muchos iconos propios). Espejo del tope que pone el teléfono.
TOPE_LINEA_BT = 8 * 1024 * 1024

def atender_bt(conn):
    """Canal Bluetooth (1.7): igual que por HTTP, nadie ejecuta nada sin
    emparejarse. La conexión empieza sin autorizar: primero tiene que
    llegar un mensaje «auth» con el token del dispositivo (o «emparejar»
    con el código de 6 dígitos, que devuelve el token). El emparejamiento
    Bluetooth de Windows sigue existiendo, pero ya no es la única barrera.

    1.7.9: tres cuidados de la auditoría, sin tocar el protocolo.
    El emparejamiento por este canal comparte el freno de intentos
    con el de HTTP (B1). El token de la conexión se REVALIDA en cada
    mensaje: si el editor lo revoca con el Bluetooth conectado, la
    conexión recibe el «sinpermiso» de siempre y vuelve a emparejar
    (B2; por HTTP la revocación ya era inmediata). Y las líneas
    tienen el tope de arriba: una línea mayor se descarta entera
    como mensaje malformado y la conexión sigue escuchando (D4)."""
    estado_bt["conectados"] += 1
    anota("Bluetooth: un teléfono se conectó")
    token_conexion = ""
    try:
        f = conn.makefile("rb")
        while True:
            linea = f.readline(TOPE_LINEA_BT + 2)
            if not linea:
                break
            if len(linea) > TOPE_LINEA_BT and not linea.endswith(b"\n"):
                # Línea que pasa del tope: se vacía hasta su salto de
                # línea y se descarta como mensaje malformado.
                while linea and not linea.endswith(b"\n"):
                    linea = f.readline(TOPE_LINEA_BT + 2)
                continue
            try:
                pet = json.loads(linea.decode("utf-8"))
            except Exception:
                continue
            rid = pet.get("id", 0)
            tipo = pet.get("tipo", "")
            if tipo == "auth":
                if token_valido(pet.get("token", "")):
                    token_conexion = pet.get("token", "")
                    resp = {"id": rid, "ok": True, "msg": "", "protocolo": PROTOCOLO}
                else:
                    resp = {"id": rid, "ok": False, "msg": "hay que emparejar este teléfono primero"}
            elif tipo == "emparejar":
                if emparejar_quedan() <= 0:
                    # 1.9.2 (punto 2): sin ventana abierta desde el
                    # editor, emparejar está pausado también por aquí.
                    resp = {"id": rid, "ok": False, "pausado": True,
                            "msg": MSG_EMPAREJAR_PAUSADO}
                elif freno_activo() > 0:
                    resp = {"id": rid, "ok": False, "msg": msg_pausa_emparejar(freno_activo())}
                elif secrets.compare_digest(str(pet.get("codigo", "")).strip(),
                                            str(DISPOSITIVOS.get("codigo", ""))):
                    token = crear_token(pet.get("nombre", "Teléfono"))
                    token_conexion = token
                    freno_registra_acierto()
                    resp = {"id": rid, "ok": True, "token": token, "msg": ""}
                else:
                    freno_registra_fallo()
                    resp = {"id": rid, "ok": False, "msg": "código de emparejamiento incorrecto"}
            elif not token_conexion or not token_valido(token_conexion):
                if token_conexion:
                    token_conexion = ""
                    anota("Bluetooth: un permiso revocado dejó de valer con la conexión abierta")
                resp = {"id": rid, "ok": False, "sinpermiso": True,
                        "msg": "hay que emparejar este teléfono primero"}
            elif tipo == "config":
                resp = {"id": rid, "ok": True, "protocolo": PROTOCOLO, "config": config_para_enviar()}
            elif tipo == "tap":
                ok, msg = ejecutar(pet.get("action") or {})
                resp = {"id": rid, "ok": ok, "msg": msg}
            else:
                resp = {"id": rid, "ok": True, "msg": ""}
            conn.sendall((json.dumps(resp, ensure_ascii=False) + "\n").encode("utf-8"))
    except Exception:
        pass
    finally:
        estado_bt["conectados"] = max(0, estado_bt["conectados"] - 1)
        try: conn.close()
        except Exception: pass

def hilo_bluetooth():
    """Servidor Bluetooth clásico (SPP, canal 5) para el panel de Android."""
    try:
        import socket as _s
        familia = getattr(_s, "AF_BTH", None)
        proto = getattr(_s, "BTHPROTO_RFCOMM", None)
        if familia is None or proto is None or not ES_WINDOWS:
            return
        srv = _s.socket(familia, _s.SOCK_STREAM, proto)
        srv.bind((_s.BDADDR_ANY, 5))
        srv.listen(2)
        estado_bt["activo"] = True
        anota("Bluetooth: escuchando (canal 5)")
        while True:
            conn, _ = srv.accept()
            threading.Thread(target=atender_bt, args=(conn,), daemon=True).start()
    except Exception as e:
        estado_bt["activo"] = False
        print("[iMandro] Bluetooth no disponible:", e, flush=True)

def ruta_adb():
    p = os.path.join(BASE, "adb", "adb.exe")
    return p if os.path.exists(p) else None

def hilo_usb():
    """Si hay un Android con depuración USB, redirige el puerto por el cable."""
    adb = ruta_adb()
    if not ES_WINDOWS or not adb:
        estado_usb.update({"estado": "nodisponible",
                           "detalle": "la herramienta del cable no está en esta PC"})
        return
    while True:
        try:
            r = subprocess.run([adb, "devices"], capture_output=True, timeout=10,
                               creationflags=0x08000000)
            salida = r.stdout.decode("utf-8", "ignore")
            hay = any(l.strip().endswith("\tdevice") for l in salida.splitlines())
            if hay:
                subprocess.run([adb, "reverse", "tcp:%d" % PUERTO, "tcp:%d" % PUERTO],
                               capture_output=True, timeout=10, creationflags=0x08000000)
                estado_usb.update({"estado": "detectado",
                                   "detalle": "teléfono por cable listo"})
            else:
                estado_usb.update({"estado": "sin",
                                   "detalle": "ningún teléfono con depuración USB"})
        except Exception:
            estado_usb.update({"estado": "sin", "detalle": "sin respuesta del cable"})
        time.sleep(5)

# ---------------------------------------------------------------- red local
_ips_cache = {"t": 0.0, "v": []}
_candado_ips = threading.Lock()
IPS_TTL = 5.0  # segundos de caché de las IPs locales (1.9.1, punto 7)

def ips_locales():
    """Las IPv4 locales de esta PC. 1.9.1 (punto 7): con caché de
    unos segundos — antes cada llamada resolvía el nombre y abría
    un socket UDP, y la piden el sondeo, el descubrimiento (que
    anuncia cada 4 s), la lista blanca del token y la IP principal.
    Devuelve una COPIA: quien la recibe no puede mutar la caché."""
    ahora = time.time()
    with _candado_ips:
        if ahora - _ips_cache["t"] < IPS_TTL and _ips_cache["v"]:
            return list(_ips_cache["v"])
    ips = set()
    try:
        for info in socket.getaddrinfo(socket.gethostname(), None, socket.AF_INET):
            ip = info[4][0]
            if not ip.startswith("127."): ips.add(ip)
    except Exception:
        pass
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80)); ips.add(s.getsockname()[0]); s.close()
    except Exception:
        pass
    valor = sorted(ips)
    with _candado_ips:
        _ips_cache["t"] = ahora
        _ips_cache["v"] = valor
    return list(valor)

def ip_principal():
    """La IPv4 principal de esta PC en la red local: la que los
    teléfonos usan para encontrarla, y la que el editor enseña en
    su tarjeta CONEXIÓN («Dirección en tu red · IP y puerto»).
    Entre las de ips_locales() prefiere 192.168.*, luego 10.*,
    luego 172.16-31.*; si no hay ninguna privada, None (el editor
    enseña «sin red local»)."""
    def rango(ip):
        if ip.startswith("192.168."):
            return 0
        if ip.startswith("10."):
            return 1
        partes = ip.split(".")
        if len(partes) == 4 and partes[0] == "172":
            try:
                if 16 <= int(partes[1]) <= 31:
                    return 2
            except ValueError:
                pass
        return 3
    candidatas = [(rango(ip), ip) for ip in ips_locales()]
    candidatas = [c for c in candidatas if c[0] < 3]
    if not candidatas:
        return None
    return sorted(candidatas)[0][1]

def hilo_descubrimiento():
    """Responde a los teléfonos que buscan la PC y anuncia la PC cada 4 s."""
    try:
        srv = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        srv.bind(("", PUERTO_DESCUBRIR)); srv.settimeout(1.0)
    except Exception:
        srv = None
    aviso = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    aviso.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    nombre = (CONFIG or {}).get("pcName", socket.gethostname())
    ultimo_aviso = 0
    while True:
        ahora = time.time()
        if ahora - ultimo_aviso > 4:
            ultimo_aviso = ahora
            for ip in ips_locales():
                msg = ("IMANDRO_PC %s %d %s" % (ip, PUERTO, nombre)).encode("utf-8")
                try: aviso.sendto(msg, ("255.255.255.255", PUERTO_AVISO))
                except Exception: pass
        if srv is not None:
            try:
                datos, destino = srv.recvfrom(256)
                if datos.startswith(b"IMANDRO_BUSCA"):
                    for ip in ips_locales():
                        msg = ("IMANDRO_PC %s %d %s" % (ip, PUERTO, nombre)).encode("utf-8")
                        srv.sendto(msg, destino)
            except socket.timeout:
                pass
            except Exception:
                pass
        time.sleep(0.05)

# ---------------------------------------------------------------- HTTP
MAX_CUERPO = 16 * 1024 * 1024  # una configuración con iconos propios cabe de sobra

class Manejador(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def setup(self):
        super().setup()
        # Robustez (1.7.9, auditoría A3): el socket de cada conexión
        # aceptada tiene 60 s de paciencia: un cliente que abre la
        # conexión y no termina de hablar ya no deja su hilo colgado
        # para siempre. No afecta a /api/buscar-ruta (su espera de
        # hasta 300 s es del propio servidor, sin tráfico de red de
        # por medio) ni al sondeo del panel (peticiones cortas que ya
        # traen su propio límite).
        try:
            self.connection.settimeout(60)
        except Exception:
            pass

    def log_message(self, *a):  # silencio
        pass

    # ------------------------------------------------ seguridad (1.7)
    def _origen_permitido(self):
        """CORS cerrado: ya no hay «*». Solo se refleja el origen cuando es
        el propio servidor (el editor o el panel abiertos desde esta PC o
        desde el teléfono contra esta misma dirección) o cuando no hay
        origen (programas que no son navegadores). Una web cualquiera
        abierta en el navegador no recibe cabecera CORS y no puede leer
        las respuestas.
        Desde la 1.7.9 el origen «null» ya NO se refleja (auditoría
        A1): es el origen de cualquier iframe sandbox de cualquier web
        y de cualquier archivo HTML local, y reflejarlo era una de las
        dos mitades de la fuga del token del editor. Ningún cliente
        legítimo lo necesita: el panel servido por esta PC es del
        mismo origen, y el panel dentro de la aplicación Android lee
        las respuestas gracias al acceso universal desde archivos de
        su WebView, no a esta cabecera."""
        origen = self.headers.get("Origin")
        if not origen:
            return True
        if origen == "null":
            return False
        host = self.headers.get("Host") or ""
        return origen.split("://", 1)[-1].rstrip("/") == host

    def _es_propia_pc(self):
        """True si la petición viene de ESTA PC: bucle local (127.0.0.1,
        que es también como llega el cable USB por adb reverse) o una de
        las direcciones IP de la propia máquina."""
        ip = self.client_address[0] if self.client_address else ""
        return ip in ("127.0.0.1", "::1") or ip in ips_locales()

    def _token_local_permitido(self):
        """Lista blanca literal para /api/token-local (1.7.9): sin
        cabecera Origin pasa (no es un navegador: la ventana propia,
        un programa local); con Origin, este y el Host tienen que ser
        literalmente «localhost», «127.0.0.1» o una IP de esta PC, con
        el puerto del servidor — escrito así en la cabecera, sin
        comparar dos datos del visitante entre sí, que era lo que un
        dominio con DNS rebinding podía hacer coincidir. El origen
        «null» no pasa nunca: es indistinguible entre un panel por
        cable y una página hostil."""
        origen = self.headers.get("Origin")
        if not origen:
            return True
        if origen == "null":
            return False
        permitidos = {"localhost:%d" % PUERTO, "127.0.0.1:%d" % PUERTO}
        permitidos.update("%s:%d" % (ip, PUERTO) for ip in ips_locales())
        host = (self.headers.get("Host") or "").strip().lower()
        if host not in permitidos:
            return False
        destino = origen.split("://", 1)[-1].rstrip("/").strip().lower()
        return destino in permitidos

    def _autorizado(self):
        return token_valido(self.headers.get("X-iMandro-Token") or "") is not None

    def _es_editor(self):
        """True si el token de la petición es el del editor de esta PC
        (1.7.9, auditoría A2): los endpoints de administración exigen
        este token; un teléfono emparejado ya no puede usarlos. El
        panel nunca llama a esos endpoints (verificado en la
        auditoría): los teléfonos ni lo notan."""
        disp = token_valido(self.headers.get("X-iMandro-Token") or "")
        return disp is not None and bool(disp.get("editor"))

    def _sin_permiso(self):
        return self._envia_json(401, {"ok": False, "sinpermiso": True,
                                      "msg": "hay que emparejar este teléfono primero"})

    def _envia(self, codigo, cuerpo, tipo="application/json; charset=utf-8", etag=None):
        datos = cuerpo if isinstance(cuerpo, bytes) else cuerpo.encode("utf-8")
        self.send_response(codigo)
        self.send_header("Content-Type", tipo)
        self.send_header("Content-Length", str(len(datos)))
        origen = self.headers.get("Origin")
        if origen and self._origen_permitido():
            self.send_header("Access-Control-Allow-Origin", origen)
            self.send_header("Vary", "Origin")
        if etag is not None:
            # 1.9.1 (punto 11): los estáticos se cachean con ETag y
            # must-revalidate — el navegador pregunta antes de usar
            # su copia, así que una actualización llega al instante
            # (304 si no cambió, el archivo nuevo si cambió) sin
            # descargar megabytes en cada apertura. Todo lo demás
            # (las respuestas /api/*) sigue con no-store.
            self.send_header("Cache-Control", "must-revalidate")
            self.send_header("ETag", etag)
        else:
            self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(datos)

    def _envia_304(self, etag):
        """Respuesta «sin cambios» para un estático revalidado."""
        self.send_response(304)
        self.send_header("Cache-Control", "must-revalidate")
        self.send_header("ETag", etag)
        self.send_header("Content-Length", "0")
        origen = self.headers.get("Origin")
        if origen and self._origen_permitido():
            self.send_header("Access-Control-Allow-Origin", origen)
            self.send_header("Vary", "Origin")
        self.end_headers()

    def _envia_json(self, codigo, obj):
        self._envia(codigo, json.dumps(obj, ensure_ascii=False))

    def _lee_json(self):
        """Lee el cuerpo JSON de un POST con las reglas de la 1.7:
        Content-Type application/json obligatorio (si no, error 415) y
        tamaño máximo. Devuelve (datos, codigo_error, mensaje_error);
        si todo va bien, codigo_error es None."""
        tipo = (self.headers.get("Content-Type") or "").split(";")[0].strip().lower()
        if tipo != "application/json":
            return None, 415, "esta petición tiene que venir en formato JSON"
        try:
            largo = int(self.headers.get("Content-Length") or 0)
        except Exception:
            largo = 0
        if largo <= 0:
            return {}, None, ""
        if largo > MAX_CUERPO:
            return None, 413, "la petición es demasiado grande"
        try:
            datos = json.loads(self.rfile.read(largo).decode("utf-8"))
        except Exception:
            return None, 400, "el cuerpo de la petición no es un JSON válido"
        if not isinstance(datos, dict):
            return None, 400, "el cuerpo de la petición no es un JSON válido"
        return datos, None, ""

    def do_OPTIONS(self):
        self.send_response(204)
        origen = self.headers.get("Origin")
        if origen and self._origen_permitido():
            self.send_header("Access-Control-Allow-Origin", origen)
            self.send_header("Vary", "Origin")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type, X-iMandro-Token")
        self.send_header("Content-Length", "0")
        self.end_headers()

    def do_GET(self):
        ruta = urlparse(self.path).path
        if ruta == "/api/ping":
            # Abierto a propósito: es lo que el teléfono mira para encontrar
            # la PC antes de emparejarse. Solo lleva nombre y versión.
            return self._envia_json(200, {"ok": True, "app": "iMandro", "version": VERSION,
                                          "protocolo": PROTOCOLO,
                                          "pcName": CONFIG.get("pcName", ""), "rev": CONFIG.get("_rev", 1)})
        if ruta == "/api/token-local":
            # El editor de ESTA PC recibe aquí su token automáticamente.
            # 1.7.9 (auditoría A1, el hallazgo alto): la entrega queda
            # blindada. Hasta la 1.7.8 bastaba con que la petición
            # viniera de esta PC y el CORS reflejaba el origen «null»:
            # cualquier iframe sandbox de cualquier página web, o un
            # HTML local abierto en el navegador, podía leer el token
            # permanente del editor y tomar el control entero. Ahora
            # se exige, además de venir de esta PC, que no haya
            # cabecera Origin (la ventana propia y los programas
            # locales no la mandan) o que Origin y Host sean de la
            # lista blanca literal (localhost, 127.0.0.1, IPs propias
            # con su puerto). El editor no lo nota: se sirve desde
            # este mismo servidor y su origen es uno de los de la
            # lista. Quien sí lo nota es el panel por cable USB: llega
            # con origen «null», indistinguible de una página hostil,
            # así que por cable se escribe el código de
            # emparejamiento la primera vez, como por Wi-Fi, y el
            # token queda guardado en el teléfono.
            if not self._es_propia_pc():
                return self._envia_json(403, {"ok": False, "msg": "el token del editor solo se entrega en esta PC"})
            if not self._token_local_permitido():
                return self._envia_json(403, {"ok": False, "msg": "el token del editor no se entrega a este origen"})
            return self._envia_json(200, {"ok": True, "token": token_del_editor()})
        if ruta == "/api/dispositivos":
            # Administración (1.7.9): solo el editor ve la lista y el código.
            if not self._es_editor():
                return self._sin_permiso()
            lista = [{"id": d.get("id"), "nombre": d.get("nombre"),
                      "creado": d.get("creado"), "ultimo": d.get("ultimo"),
                      "editor": bool(d.get("editor"))}
                     for d in DISPOSITIVOS.get("lista", [])]
            return self._envia_json(200, {"ok": True, "codigo": DISPOSITIVOS.get("codigo", ""), "dispositivos": lista})
        if ruta == "/api/config":
            if not self._autorizado():
                return self._sin_permiso()
            return self._envia_json(200, config_para_enviar())
        if ruta == "/api/bt":
            # Estado interno (1.7.9): solo el editor.
            if not self._es_editor():
                return self._sin_permiso()
            return self._envia_json(200, estado_bt)
        if ruta == "/api/usb":
            if not self._es_editor():
                return self._sin_permiso()
            return self._envia_json(200, estado_usb)
        if ruta == "/api/registro":
            if not self._es_editor():
                return self._sin_permiso()
            with _candado_registro:
                copia = list(registro)
            return self._envia_json(200, {"registro": copia})
        if ruta == "/api/aplicaciones":
            if not self._es_editor():
                return self._sin_permiso()
            qs = parse_qs(urlparse(self.path).query)
            lista, msg = lista_aplicaciones(forzar=qs.get("forzar", [""])[0] == "1")
            if msg:
                return self._envia_json(500, {"ok": False, "msg": msg})
            return self._envia_json(200, {"ok": True, "aplicaciones": lista})
        if ruta == "/api/bandeja":
            if not self._es_editor():
                return self._sin_permiso()
            return self._envia_json(200, estado_bandeja())
        if ruta == "/api/estado":
            # Sondeo ligero del panel (1.7.7): solo la versión, la
            # revisión de la configuración y el programa en primer
            # plano — menos de 1 KB. La configuración entera (que con
            # los iconos propios en base64 puede pesar megabytes) solo
            # viaja cuando su _rev cambia. Mismo control de token que
            # /api/config.
            if not self._autorizado():
                return self._sin_permiso()
            return self._envia_json(200, {"ok": True, "version": VERSION,
                                          "protocolo": PROTOCOLO,
                                          "_rev": CONFIG.get("_rev", 0),
                                          "_fg": programa_en_primer_plano(),
                                          # 1.9.1: True si ese programa
                                          # corre como administrador y
                                          # los atajos no le llegarán;
                                          # el editor avisa junto a
                                          # «Ahora tienes delante».
                                          "_fgElevado": fg_elevado(),
                                          # La dirección de esta PC en la
                                          # red (IP principal y el puerto
                                          # propio): la enseña el editor en
                                          # su tarjeta CONEXIÓN.
                                          "ip": ip_principal(),
                                          "puerto": PUERTO,
                                          # 1.9.2 (punto 2): segundos
                                          # de ventana de emparejamiento
                                          # que quedan (0 = pausado); el
                                          # editor lo enseña en su
                                          # tarjeta EMPAREJAMIENTO.
                                          "_empQuedan": int(round(emparejar_quedan()))})
        if ruta == "/api/autoinicio":
            if not self._autorizado():
                return self._sin_permiso()
            return self._envia_json(200, {"ok": True, "activo": autoinicio_estado()})
        if ruta in ("/", "/editor"):
            return self._archivo("editor.html", "text/html; charset=utf-8")
        if ruta == "/panel":
            return self._archivo("panel.html", "text/html; charset=utf-8")
        if ruta == "/icons.js":
            return self._archivo("icons.js", "text/javascript; charset=utf-8")
        if ruta == "/packs.js":
            return self._archivo("packs.js", "text/javascript; charset=utf-8")
        if ruta.startswith("/static/"):
            nombre = os.path.basename(ruta)
            tipo = "text/javascript; charset=utf-8" if nombre.endswith(".js") else "text/plain"
            return self._archivo(nombre, tipo)
        return self._envia_json(404, {"ok": False, "msg": "no encontrado"})

    def _archivo(self, nombre, tipo):
        p = os.path.join(STATIC, nombre)
        if not os.path.exists(p):
            return self._envia_json(404, {"ok": False, "msg": "falta " + nombre})
        # 1.9.1 (punto 11): ETag fuerte = SHA-256 del contenido; si
        # el navegador revalida con el mismo, 304 sin cuerpo.
        with open(p, "rb") as f:
            contenido = f.read()
        etag = '"%s"' % hashlib.sha256(contenido).hexdigest()
        if (self.headers.get("If-None-Match") or "").strip() == etag:
            return self._envia_304(etag)
        return self._envia(200, contenido, tipo, etag=etag)

    # Endpoints de administración (1.7.9): exigen el token del editor.
    RUTAS_ADMIN = ("/api/dispositivos/revocar", "/api/dispositivos/regenerar-codigo",
                   "/api/autoinicio", "/api/config", "/api/buscar-ruta",
                   "/api/emparejar-ventana")

    def do_POST(self):
        ruta = urlparse(self.path).path
        if ruta == "/api/emparejar":
            datos, err, msg_err = self._lee_json()
            if err is not None:
                return self._envia_json(err, {"ok": False, "msg": msg_err})
            # La única puerta de entrada: el código de 6 dígitos que el
            # editor de la PC enseña. Desde la 1.7.9 (auditoría B1)
            # hay freno, compartido con el emparejamiento por
            # Bluetooth: a los 10 códigos fallidos seguidos, pausa de
            # 60 s que se dobla en cada ronda (durante la pausa ni el
            # código bueno entra). El código sigue siendo permanente:
            # ni caduca ni se regenera solo, y el editor puede
            # regenerarlo a mano cuando quiera, como siempre.
            # 1.9.2 (punto 2, modo emparejar): sin la ventana abierta
            # desde el editor, ni se mira el código: «pausado» claro.
            if emparejar_quedan() <= 0:
                return self._envia_json(403, {"ok": False, "pausado": True,
                                              "msg": MSG_EMPAREJAR_PAUSADO})
            quedan = freno_activo()
            if quedan > 0:
                return self._envia_json(403, {"ok": False, "msg": msg_pausa_emparejar(quedan)})
            # 1.9.1 (punto 2, solo esto): la comparación del código
            # va con compare_digest, como ya iban los hash de token;
            # por Bluetooth, lo mismo (en atender_bt).
            if not secrets.compare_digest(str(datos.get("codigo", "")).strip(),
                                          str(DISPOSITIVOS.get("codigo", ""))):
                freno_registra_fallo()
                return self._envia_json(403, {"ok": False, "msg": "código de emparejamiento incorrecto"})
            freno_registra_acierto()
            token = crear_token(datos.get("nombre", "Teléfono"))
            anota("Teléfono emparejado: " + str(datos.get("nombre", "Teléfono")))
            return self._envia_json(200, {"ok": True, "token": token})
        # 1.7.9 (auditoría A4): en las rutas con token, la autorización
        # se comprueba ANTES de leer el cuerpo: nadie sin permiso hace
        # que el servidor lea y descarte hasta 16 MB por petición.
        # Como el cuerpo no se consume en estos dos rechazos, la
        # conexión se cierra tras la respuesta para que los bytes que
        # queden no ensucien la siguiente petición de la misma
        # conexión.
        if not self._autorizado():
            self.close_connection = True
            return self._sin_permiso()
        if ruta in self.RUTAS_ADMIN and not self._es_editor():
            self.close_connection = True
            return self._envia_json(403, {"ok": False,
                                          "msg": "esa operación es solo del editor de esta PC"})
        datos, err, msg_err = self._lee_json()
        if err is not None:
            return self._envia_json(err, {"ok": False, "msg": msg_err})
        if ruta == "/api/dispositivos/revocar":
            objetivo = str(datos.get("id", ""))
            # 1.9.1 (punto 7): la sustitución de la lista también va
            # con el candado de dispositivos.
            with candado_dispositivos:
                antes = len(DISPOSITIVOS.get("lista", []))
                DISPOSITIVOS["lista"] = [d for d in DISPOSITIVOS.get("lista", [])
                                         if str(d.get("id")) != objetivo or d.get("editor")]
                cambio = len(DISPOSITIVOS["lista"]) != antes
            if cambio:
                guardar_dispositivos()
                anota("Dispositivo revocado desde el editor")
            return self._envia_json(200, {"ok": True})
        if ruta == "/api/dispositivos/regenerar-codigo":
            with candado_dispositivos:
                DISPOSITIVOS["codigo"] = "%06d" % secrets.randbelow(1000000)
            guardar_dispositivos()
            anota("Código de emparejamiento regenerado")
            return self._envia_json(200, {"ok": True, "codigo": DISPOSITIVOS["codigo"]})
        if ruta == "/api/emparejar-ventana":
            # 1.9.2 (punto 2): el botón «Permitir emparejar» del
            # editor abre la ventana (120 s por omisión); se cierra
            # sola al pasar el tiempo. Solo editor (RUTAS_ADMIN).
            quedan = abrir_ventana_emparejar(datos.get("segundos", VENTANA_EMPAREJAR_S))
            anota("Ventana de emparejamiento abierta desde el editor")
            return self._envia_json(200, {"ok": True, "quedan": quedan})
        if ruta == "/api/autoinicio":
            # Inicio con Windows (1.7.7): crea o quita el acceso
            # directo de la carpeta de Inicio. El estado que se
            # contesta es el real (si el acceso directo existe).
            activo = bool(datos.get("activo"))
            hecho, msg = autoinicio_fijar(activo)
            registra_servidor("Inicio con Windows %s%s" % (
                "activado" if activo else "desactivado",
                "" if hecho else " — no se pudo: " + msg))
            return self._envia_json(200, {"ok": hecho, "activo": autoinicio_estado(), "msg": msg})
        if ruta == "/api/config":
            global CONFIG
            nueva = datos.get("config") or datos
            if not isinstance(nueva, dict) or "pages" not in nueva:
                return self._envia_json(400, {"ok": False, "msg": "configuración no válida"})
            nueva.pop("_fg", None)  # dato en vivo, no se guarda
            nueva.pop("_vals", None)  # idem
            with candado_config:
                # Control de versiones (1.7): si quien guarda trae una _rev
                # más vieja que la del servidor, otro editor ya cambió la
                # configuración: se avisa con 409 en vez de pisarla en silencio.
                # Quien no manda _rev (una copia restaurada, un cliente viejo)
                # se acepta como hasta ahora.
                rev_cliente = nueva.get("_rev")
                rev_servidor = int(CONFIG.get("_rev", 1))
                if rev_cliente is not None:
                    try:
                        rev_cliente = int(rev_cliente)
                    except Exception:
                        rev_cliente = rev_servidor
                    if rev_cliente < rev_servidor:
                        return self._envia_json(409, {"ok": False, "conflicto": True, "rev": rev_servidor,
                                                      "msg": "otro editor cambió la configuración (rev %d); se recarga para no pisar su trabajo" % rev_servidor})
                CONFIG = nueva
                guardar_config(subir_rev=True)
                anota("Configuración guardada desde el editor (rev %d)" % CONFIG["_rev"])
                return self._envia_json(200, {"ok": True, "rev": CONFIG["_rev"]})
        if ruta == "/api/tap":
            ok, msg = ejecutar(datos.get("action") or {})
            return self._envia_json(200, {"ok": ok, "msg": msg})
        if ruta == "/api/buscar-ruta":
            ok, elegida, msg = buscar_ruta(datos.get("modo", "programa"))
            return self._envia_json(200, {"ok": ok, "ruta": elegida, "msg": msg})
        return self._envia_json(404, {"ok": False, "msg": "no encontrado"})

# ------------------------------------------------- control del servidor
# Desde la 1.7 el servidor HTTP se puede detener, iniciar y reiniciar sin
# cerrar el programa: lo pide la bandeja del sistema («Detener el
# servidor» deja iMandro en la bandeja sin servir; «Iniciar» lo levanta
# otra vez). El bucle supervisor vive en el hilo principal y el servidor
# en un hilo hijo; fuera de la bandeja nadie nota la diferencia.
estado_srv = {"servidor": None, "corriendo": False, "quiero": True, "salir": False,
              # 1.9.1: True solo cuando la salida la pidió «Cerrar
              # iMandro» de la bandeja (srv_cerrar): entonces, al
              # terminar el bucle, se cierra también la ventana del
              # editor. El puerto ocupado pone «salir» sin esto.
              "cerrar_todo": False}

def _bucle_servidor():
    while not estado_srv["salir"]:
        if estado_srv["quiero"]:
            try:
                srv = ThreadingHTTPServer(("0.0.0.0", PUERTO), Manejador)
            except OSError:
                # El puerto ya está ocupado: casi seguro hay otro iMandro
                # corriendo en esta PC. No se levanta un segundo servidor.
                print("[iMandro] El puerto %d ya está en uso: parece que iMandro "
                      "ya está abierto. No se abre otra copia." % PUERTO, flush=True)
                registra_servidor("El puerto %d ya está en uso; no se levanta "
                                  "un segundo servidor." % PUERTO)
                estado_srv["salir"] = True
                # 1.9.1 (punto 9a): la bandeja retira su icono
                # (NIM_DELETE) antes de que el proceso salga: no
                # queda un icono fantasma señalando a un iMandro
                # que no llegó a arrancar. La ventana del editor
                # NO se toca: puede ser de la copia que sigue viva.
                try:
                    import bandeja as _bandeja_mod
                    if _bandeja_mod.retirar_icono():
                        registra_servidor("Bandeja: el icono se retiró "
                                          "al terminar por el puerto ocupado.")
                except Exception:
                    pass
                break
            estado_srv["servidor"] = srv
            estado_srv["corriendo"] = True
            t = threading.Thread(target=srv.serve_forever, kwargs={"poll_interval": 0.25}, daemon=True)
            t.start()
            while not estado_srv["salir"] and estado_srv["quiero"]:
                time.sleep(0.2)
            try: srv.shutdown()
            except Exception: pass
            try: srv.server_close()
            except Exception: pass
            estado_srv["servidor"] = None
            estado_srv["corriendo"] = False
        else:
            time.sleep(0.2)

def srv_detener():
    estado_srv["quiero"] = False

def srv_iniciar():
    estado_srv["quiero"] = True

def srv_reiniciar():
    """Detiene y vuelve a levantar el servidor, sin bloquear a quien llama
    (la bandeja sigue atendiendo su menú mientras tanto)."""
    def pasos():
        estado_srv["quiero"] = False
        for _ in range(50):
            if estado_srv["servidor"] is None:
                break
            time.sleep(0.1)
        if not estado_srv["salir"]:
            estado_srv["quiero"] = True
    threading.Thread(target=pasos, daemon=True).start()

def srv_cerrar():
    estado_srv["quiero"] = False
    estado_srv["salir"] = True
    # 1.9.1 (punto 9b): esta salida es «Cerrar iMandro» de la bandeja:
    # al terminar el bucle se cierra también la ventana del editor.
    estado_srv["cerrar_todo"] = True

_mutex_unico = None  # se guarda para que Windows no lo libere al salir

def _instancia_unica():
    """Instancia única (1.7, solo Windows): un mutex con nombre hace de
    candado. Si ya existe, hay otro iMandro corriendo: se abre su editor
    en el navegador y esta copia se cierra sin levantar un segundo
    servidor en el mismo puerto. Fuera de Windows devuelve True siempre
    (el propio puerto ocupado hace de segunda barrera en el bucle).
    1.9.1 (punto 4 de la revisión): el kernel32 sale de _kernel32()
    (WinDLL con use_last_error=True y el prototipo de CreateMutexW
    declarado, con restype HANDLE de 64 bits). Antes era
    ctypes.windll sin firma: el error 183 se leía de un canal que no
    era fiable y el handle volvía como int de 32 bits. «Se abre su
    editor»: abrir_editor() enseña el editor DE LA COPIA QUE YA
    CORRE — esta copia no levanta servidor, así que la ventana o el
    navegador que se abren hablan con la primera."""
    global _mutex_unico
    if not ES_WINDOWS:
        return True
    try:
        kernel32 = _kernel32()
        kernel32.SetLastError(0)
        _mutex_unico = kernel32.CreateMutexW(None, False, "iMandro-Servidor-Unico")
        if not _mutex_unico:
            return True
        if ctypes.get_last_error() == 183:  # ERROR_ALREADY_EXISTS
            print("[iMandro] Ya hay un iMandro abierto en esta PC: se abre su editor.", flush=True)
            abrir_editor()
            return False
    except Exception:
        return True
    return True

def abrir_editor_navegador():
    try:
        if ES_WINDOWS: os.startfile("http://localhost:%d" % PUERTO)  # noqa: S606
    except Exception:
        pass

def abrir_editor():
    """Abre el editor en la VENTANA PROPIA de iMandro (aplicacion.py,
    1.7.4); si el lanzador no está o no arranca, cae al navegador de
    siempre. Lo usan el arranque, la instancia única y la bandeja
    («Abrir» y el doble clic)."""
    if ES_WINDOWS:
        lanzador = os.path.join(BASE, "aplicacion.py")
        if os.path.exists(lanzador):
            try:
                subprocess.Popen([sys.executable, lanzador], cwd=BASE,
                                 env=dict(os.environ, IMANDRO_DESDE_SERVIDOR="1"),
                                 creationflags=SIN_VENTANA)
                return
            except Exception:
                pass
    abrir_editor_navegador()

def estado_bandeja():
    """El estado real de la bandeja del sistema, que lleva bandeja.py:
    el editor lo enseña tal cual («Bandeja: activa» / «Bandeja: no
    disponible») en vez de prometerla a ciegas."""
    try:
        import bandeja
        estado = dict(bandeja.ESTADO)
        if not ES_WINDOWS and estado["detalle"] == "sin iniciar":
            estado["detalle"] = "la bandeja solo existe en Windows"
        return estado
    except Exception as e:
        return {"activa": False, "detalle": "no disponible (%s)" % e, "actualizado": ""}

# ---------- Inicio con Windows (1.7.7, opcional y apagado de fábrica) ----------
def _ruta_acceso_inicio():
    """El acceso directo «iMandro.lnk» en la carpeta de Inicio del
    usuario, o None fuera de Windows."""
    if not ES_WINDOWS:
        return None
    base = os.environ.get("APPDATA") or os.path.expanduser("~")
    return os.path.join(base, "Microsoft", "Windows", "Start Menu",
                        "Programs", "Startup", "iMandro.lnk")

def autoinicio_estado():
    """El estado real: si el acceso directo existe o no. En no-Windows
    siempre apagado."""
    ruta = _ruta_acceso_inicio()
    return bool(ruta and os.path.isfile(ruta))

def autoinicio_fijar(activo):
    """Crea o quita el acceso directo de la carpeta de Inicio: lanza
    «pythonw.exe servidor.py» de ESTA instalación, para que el
    servidor arranque con Windows sin abrir ninguna ventana. El .lnk
    se crea con PowerShell por su ruta completa y el script en
    Base64, como el resto del proyecto (WScript.Shell). Devuelve
    (hecho, mensaje). Fuera de Windows es un no-op seguro que
    contesta el estado como apagado."""
    if not ES_WINDOWS:
        return False, "solo funciona en Windows"
    ruta = _ruta_acceso_inicio()
    try:
        if not activo:
            if os.path.isfile(ruta):
                os.remove(ruta)
            return True, ""
        os.makedirs(os.path.dirname(ruta), exist_ok=True)
        pythonw = os.path.join(BASE, "python", "pythonw.exe")
        if not os.path.isfile(pythonw):
            pythonw = sys.executable
        servidor = os.path.join(BASE, "servidor.py")

        def esc(s):
            return s.replace("'", "''")
        script = ("$s = New-Object -ComObject WScript.Shell; "
                  "$l = $s.CreateShortcut('%s'); "
                  "$l.TargetPath = '%s'; "
                  "$l.Arguments = '\"%s\"'; "
                  "$l.WorkingDirectory = '%s'; "
                  "$l.Description = 'iMandro - servidor (arranque con Windows)'; "
                  "$l.Save()") % (esc(ruta), esc(pythonw), esc(servidor), esc(BASE))
        codificado = base64.b64encode(script.encode("utf-16-le")).decode("ascii")
        r = subprocess.run([_ruta_powershell(), "-NoProfile", "-EncodedCommand", codificado],
                           capture_output=True, timeout=20, creationflags=SIN_VENTANA)
        if r.returncode != 0:
            return False, "Windows no creó el acceso directo"
        if not os.path.isfile(ruta):
            return False, "no se creó el acceso directo"
        return True, ""
    except Exception as e:
        return False, str(e)

def _anotar_bandeja():
    """Escribe en servidor.log cómo quedó la bandeja al arrancar: es
    el dato que faltaba cuando el icono no aparecía y nadie sabía por
    qué (1.7.7). La bandeja corre en su propio hilo; se le dan unos
    segundos y se anota su estado real."""
    time.sleep(3)
    try:
        est = estado_bandeja()
        registra_servidor("Bandeja al arrancar: %s (%s)" % (
            "activa" if est.get("activa") else "no disponible",
            est.get("detalle", "")))
    except Exception:
        pass

def _acciones_bandeja():
    """Lo que la bandeja del sistema (bandeja.py) puede pedir y mirar."""
    def estado():
        detalle = "protocolo %d" % PROTOCOLO
        if estado_bt.get("activo"):
            detalle += " · Bluetooth: %d conectado(s)" % estado_bt.get("conectados", 0)
        return {"corriendo": bool(estado_srv["corriendo"]), "detalle": detalle}
    def dispositivos():
        salida = []
        ahora = time.time()
        # 1.9.1 (punto 7): foto de la lista bajo el candado; el bucle
        # de abajo lee campos que token_valido puede estar tocando.
        with candado_dispositivos:
            lista = list(DISPOSITIVOS.get("lista", []))
        for d in lista:
            if d.get("editor"):
                continue
            activo = False
            try:
                ult = time.mktime(time.strptime(d.get("ultimo", ""), "%Y-%m-%d %H:%M"))
                activo = (ahora - ult) < 600
            except Exception:
                pass
            salida.append({"nombre": d.get("nombre", "Teléfono"),
                           "detalle": "activo hace poco" if activo else ("último uso: " + (d.get("ultimo") or "—"))})
        return salida
    return {"abrir_editor": abrir_editor, "estado": estado,
            "dispositivos": dispositivos, "reiniciar": srv_reiniciar,
            "detener": srv_detener, "iniciar": srv_iniciar, "cerrar": srv_cerrar}

def main():
    if not _instancia_unica():
        registra_servidor("Arranque cancelado: ya hay un iMandro abierto "
                          "en esta PC.")
        return
    registra_servidor("Servidor iMandro v%s arrancando (puerto %d)." %
                      (VERSION, PUERTO))
    # 1.7.9: si los datos son de una versión anterior, antes de
    # cargarlos y migrarlos queda su copia con sello «pre-<versión>».
    _copias_previas_actualizacion()
    cargar_config()
    cargar_dispositivos()
    threading.Thread(target=hilo_descubrimiento, daemon=True).start()
    threading.Thread(target=hilo_bluetooth, daemon=True).start()
    threading.Thread(target=hilo_usb, daemon=True).start()
    ips = ips_locales()
    print("iMandro v%s · Creador: %s" % (VERSION, CREADOR), flush=True)
    print("Editor: http://localhost:%d  ·  En tu red: %s" %
          (PUERTO, ", ".join("http://%s:%d" % (ip, PUERTO) for ip in ips) or "—"), flush=True)
    if ES_WINDOWS:
        # Bandeja del sistema (1.7): si algo falla al crearla, el servidor
        # sigue igual; la bandeja nunca puede tumbar a iMandro.
        # 1.7.7: el import va DESPUÉS de meter BASE en sys.path (arriba):
        # con el Python embebido antes moría aquí en silencio.
        try:
            import bandeja
            # 1.9.1 (punto 9b): al salir del bucle por «Cerrar
            # iMandro», la bandeja dispara esta función registrada:
            # cerrar también la ventana del editor. La ventana es
            # otro proceso (aplicacion.py); se le pide que se cierre
            # mandándole WM_CLOSE a su ventana por el título. El
            # arranque normal no cambia: sin «Cerrar iMandro» esta
            # función nunca se invoca.
            def _al_cerrar_bandeja():
                if not estado_srv.get("cerrar_todo"):
                    return
                try:
                    user32 = _user32()
                    user32.FindWindowW.argtypes = [wintypes.LPCWSTR, wintypes.LPCWSTR]
                    user32.FindWindowW.restype = wintypes.HWND
                    user32.PostMessageW.argtypes = [wintypes.HWND, wintypes.UINT,
                                                    wintypes.WPARAM, wintypes.LPARAM]
                    user32.PostMessageW.restype = wintypes.BOOL
                    hwnd_ventana = user32.FindWindowW(None, "iMandro — Editor")
                    if hwnd_ventana:
                        user32.PostMessageW(hwnd_ventana, 0x0010, 0, 0)  # WM_CLOSE
                        registra_servidor("Bandeja: «Cerrar iMandro» cerró "
                                          "también la ventana del editor.")
                except Exception:
                    pass
            bandeja.registrar_al_cerrar(_al_cerrar_bandeja)
            threading.Thread(target=bandeja.iniciar, args=(_acciones_bandeja(),),
                             kwargs={"icono": os.path.join(BASE, "icono.ico")}, daemon=True).start()
            threading.Thread(target=_anotar_bandeja, daemon=True).start()
        except Exception as e:
            print("[iMandro] Bandeja no disponible:", e, flush=True)
            registra_servidor("Bandeja: el módulo no cargó: %s" % e)
    if os.environ.get("IMANDRO_NO_ABRIR") != "1":
        def abre():
            time.sleep(1.0)
            abrir_editor()
        threading.Thread(target=abre, daemon=True).start()
    registra_servidor("Servidor en marcha; editor en http://localhost:%d." % PUERTO)
    try:
        _bucle_servidor()
    except KeyboardInterrupt:
        srv_cerrar()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        registra_servidor("Fallo al arrancar: %r" % (e,))
        raise
