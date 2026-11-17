# -*- coding: utf-8 -*-
"""iMandro 1.9.2 — ventana propia de la aplicación de PC.

Abre el editor de iMandro en su propia ventana de escritorio (con su
icono y su título, sin navegador), como un programa aparte. Por dentro
sigue siendo el mismo editor de siempre: esta ventana solo lo enseña.

Reglas fijadas con Liesky:
- Si el servidor no está en marcha, lo arranca en segundo plano
  (sin abrir el navegador: para eso está esta ventana).
- CERRAR LA VENTANA NO APAGA EL SERVIDOR: iMandro sigue vivo en la
  bandeja del sistema y los teléfonos siguen conectados. Para cerrar
  iMandro del todo se usa «Cerrar iMandro» en el menú de la bandeja.
- Si ya hay una ventana de iMandro abierta, no abre otra: la trae
  al frente.
- Si la ventana no puede abrirse (falta el runtime de WebView2 o lo
  que sea), se abre el navegador de siempre y el fallo queda escrito,
  con fecha y motivo, en «ventana.log», junto a la configuración.

La ventana usa pywebview con WebView2 (el mismo motor que el Cajalis
Contable, integrado en el Python del instalador). Si pywebview no
está, el camino de reserva es el navegador.

Creador: Liesky Vázquez.
"""
import os
import subprocess
import sys
import threading
import time
import urllib.request
import webbrowser

BASE = os.path.dirname(os.path.abspath(__file__))
# 1.7.7: la misma regla que en servidor.py — con el Python embebido,
# sys.path no trae esta carpeta; va la primera por si en el futuro se
# importa un módulo hermano desde aquí.
if BASE not in sys.path:
    sys.path.insert(0, BASE)
PUERTO = 8931
URL = "http://localhost:%d" % PUERTO
TITULO = "iMandro — Editor"
ARCHIVO_LOG = os.path.join(BASE, "ventana.log")


def registra(texto):
    """Deja constancia en ventana.log, con fecha. Nunca lanza."""
    try:
        with open(ARCHIVO_LOG, "a", encoding="utf-8") as f:
            f.write("%s · %s\n" % (time.strftime("%Y-%m-%d %H:%M:%S"), texto))
    except Exception:
        pass


def servidor_activo():
    try:
        with urllib.request.urlopen(URL + "/api/ping", timeout=1) as r:
            return r.status == 200
    except Exception:
        return False


def arranca_servidor():
    """Levanta servidor.py en segundo plano, sin consola y sin que
    abra nada por su cuenta (IMANDRO_NO_ABRIR): la ventana es esta."""
    env = dict(os.environ)
    env["IMANDRO_NO_ABRIR"] = "1"
    try:
        subprocess.Popen([sys.executable, os.path.join(BASE, "servidor.py")],
                         cwd=BASE, env=env,
                         creationflags=0x08000000 if sys.platform.startswith("win") else 0)
    except Exception as e:
        registra("no se pudo arrancar el servidor: %s" % e)
        return False
    for _ in range(60):  # hasta ~15 s
        if servidor_activo():
            return True
        time.sleep(0.25)
    registra("el servidor no respondió a tiempo tras arrancarlo")
    return False


def enfoca_ventana_existente():
    """Si ya hay una ventana de iMandro, la trae al frente y devuelve
    True (no se abre otra). Solo Windows: busca por el título exacto."""
    if not sys.platform.startswith("win"):
        return False
    try:
        import ctypes
        user32 = ctypes.windll.user32
        hwnd = user32.FindWindowW(None, TITULO)
        if hwnd:
            SW_RESTORE = 9
            user32.ShowWindow(hwnd, SW_RESTORE)
            user32.SetForegroundWindow(hwnd)
            return True
    except Exception:
        pass
    return False


def main():
    if enfoca_ventana_existente():
        return
    if not servidor_activo():
        arranca_servidor()
    try:
        import webview
        try:
            webview.settings["ALLOW_DOWNLOADS"] = True
        except Exception:
            pass
        icono = os.path.join(BASE, "icono.ico")
        ventana = webview.create_window(
            TITULO, URL,
            width=1360, height=900, min_size=(1000, 640),
        )
        # 1.9.1 (punto 9b): «Cerrar iMandro» en la bandeja cierra
        # también esta ventana — el servidor le manda WM_CLOSE por
        # su título. Al cerrarse, si el servidor ya no responde
        # (iMandro se cerró entero), este proceso termina del todo
        # en vez de quedarse colgado sin ventana.
        def al_cerrarse():
            if not servidor_activo():
                registra("la ventana se cierra con iMandro ya cerrado: "
                         "este proceso termina")
                threading.Timer(0.3, lambda: os._exit(0)).start()
        try:
            ventana.events.closing += al_cerrarse
        except Exception:
            pass
        webview.start(gui="edgechromium",
                      icon=icono if os.path.exists(icono) else None)
    except Exception as e:
        # Sin ventana (falta pywebview, falta WebView2…): queda escrito
        # el motivo y se abre el navegador de siempre. El servidor, si
        # se arrancó, se queda funcionando igual.
        registra("la ventana propia no se pudo abrir (%s): se usa el navegador" % e)
        try:
            webbrowser.open(URL)
        except Exception:
            pass
    # La ventana se cerró (o se fue al navegador): NO se toca el
    # servidor. Sigue en la bandeja, con los teléfonos conectados.


if __name__ == "__main__":
    main()
