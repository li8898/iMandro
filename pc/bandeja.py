# -*- coding: utf-8 -*-
"""iMandro 1.7 — Bandeja del sistema de Windows.

Un icono de iMandro junto al reloj con un menú sencillo: abrir el editor,
ver el estado y los teléfonos autorizados, reiniciar o detener el
servidor y cerrar iMandro bien.

Está hecho SOLO con ctypes y las funciones de Windows (user32/shell32):
el Python que lleva el instalador no trae tkinter ni librerías de bandeja
(pystray), y aquí no se añade ninguna dependencia.

Fuera de Windows este módulo no hace nada: iniciar() devuelve False
enseguida y el servidor ni se entera. Dentro de Windows corre en su
propio hilo con su bucle de mensajes, sin tocar el servidor.

1.7.5 — bandeja endurecida, tras el reporte de Liesky (la aplicación
avisaba de un icono junto al reloj que en su PC no se veía):
- El estado real vive en ESTADO y el servidor lo enseña en el editor
  («Bandeja: activa» / «Bandeja: no disponible»), sin prometerla.
- Ningún fallo se traga en silencio: queda escrito, con fecha y
  motivo, en «bandeja.log», junto a la configuración.
- Si el Explorador de Windows renace (mensaje TaskbarCreated), el
  icono se vuelve a poner solo: Windows lo borra al reiniciar
  explorer.exe y antes no volvía hasta reiniciar iMandro.

1.7.10 — el menú, instrumentado. En la PC de Liesky la bandeja
arrancaba y trabajaba (el icono se registraba, el doble clic reabría
el editor) pero el clic secundario no mostraba nada, y no había
testigo: bandeja.log ni existía, porque la línea «activa» solo se
escribía cuando la bandeja ya se había cerrado. Ahora esa línea se
escribe al registrar el icono, con la bandeja viva, y mostrar el
menú (extraído a _mostrar_menu, probado con un user32 simulado)
anota cada paso: qué inserción devuelve falso, el resultado de
TrackPopupMenu con el último error de Windows y cualquier
excepción, sin propagarla jamás.

1.8 — el menú cambia cómo mete los textos. La prueba de la
1.7.10 en su PC cerró el diagnóstico: el menú se construía entero
(ni una inserción en falso, ni excepciones) y se abría con su
estructura — filas, separadores y la flecha del submenú — pero
SIN una sola letra, y ancho, como si las palabras estuvieran
medidas pero pintadas invisibles. Los menús de Windows (Papelera,
escritorio) sí enseñan sus letras en esa misma PC: el fallo está
en nuestro modo de meter los textos, que era AppendMenuW con
cadenas anchas vía ctypes. Desde esta versión el menú se arma
con InsertMenuItemW + MENUITEMINFOW, la vía que usan las
aplicaciones de verdad, y antes de enseñarlo se lee de vuelta su
primer texto (GetMenuStringW) y queda escrito en bandeja.log:
si el dato quedó bien puesto, el diario lo prueba.

1.9.1 — el menú se pinta él mismo. Las dos vías anteriores
(AppendMenuW, InsertMenuItemW) dejaban el texto bien guardado en
el menú y aun así Windows no lo dibujaba: lo que fallaba era el
PINTADO del texto del menú nativo en este proceso/PC, no el modo de
meterlo. Ahora cada opción es «de dibujo propio» (MFT_OWNERDRAW):
Windows sigue dando el marco, la navegación con teclado, el
submenú y la elección, pero el texto lo mide y lo pinta iMandro con
GDI, con colores y fuente fijados por nosotros (no los del tema de
Windows). Además: (a) DefWindowProcW ahora tiene prototipo (antes se
llamaba «a pelo» desde el wndproc y en 64 bits recortaba wParam y
lParam a 32 bits); (b) se usan WinDLL(use_last_error=True) para que
los «último error de Windows» del registro sean de verdad (con
ctypes.windll siempre salía 0); (c) bandeja.log anota un diagnóstico
de pintura (colores del menú del sistema, tema visual activo,
fuente que se usó y cuántos ítems se midieron/pintaron). Con
MENU_PROPIO = False se vuelve al menú nativo de la 1.8.

1.9.1 (añadidos de la integración, sobre el archivo de la revisión
externa): (i) MENSAJE_QUITAR + retirar_icono(): si el servidor
termina porque el puerto está ocupado, la bandeja retira su icono
(NIM_DELETE) y cierra su ventana antes de que el proceso salga,
en vez de dejar el icono fantasma junto al reloj; (ii) el dict
_CIERRE permite que la acción «Cerrar iMandro» del servidor registre
una función para cerrar también la ventana del editor
(aplicacion.py), que el propio servidor dispara desde su hilo tras
salir del bucle.

Creador: Liesky Vázquez.
"""
import ctypes
import os
import sys
import threading
import time
from ctypes import wintypes

ES_WINDOWS = sys.platform.startswith("win")

# En sistemas que no son Windows, ctypes.wintypes viene reducido (sin los
# tipos de ventana). Se definen alias equivalentes para que las
# estructuras de abajo se puedan declarar al importar el módulo en
# cualquier sitio; en la práctica solo se usan dentro de Windows.
HWND = getattr(wintypes, "HWND", ctypes.c_void_p)
HINSTANCE = getattr(wintypes, "HINSTANCE", ctypes.c_void_p)
HICON = getattr(wintypes, "HICON", ctypes.c_void_p)
HCURSOR = getattr(wintypes, "HCURSOR", ctypes.c_void_p)
HBRUSH = getattr(wintypes, "HBRUSH", ctypes.c_void_p)
HMENU = getattr(wintypes, "HMENU", ctypes.c_void_p)
HBITMAP = getattr(wintypes, "HBITMAP", ctypes.c_void_p)
HANDLE = getattr(wintypes, "HANDLE", ctypes.c_void_p)
HMODULE = getattr(wintypes, "HMODULE", ctypes.c_void_p)
LPCWSTR = getattr(wintypes, "LPCWSTR", ctypes.c_wchar_p)
LPVOID = getattr(wintypes, "LPVOID", ctypes.c_void_p)
WPARAM = getattr(wintypes, "WPARAM", ctypes.c_size_t)
LPARAM = getattr(wintypes, "LPARAM", ctypes.c_ssize_t)

WM_USER = 0x0400
WM_NULL = 0x0000
WM_DESTROY = 0x0002
WM_TIMER = 0x0113
WM_LBUTTONUP = 0x0202
WM_LBUTTONDBLCLK = 0x0203
WM_RBUTTONUP = 0x0205
MENSAJE_BANDEJA = WM_USER + 20
# 1.9.1: mensaje propio para retirar el icono y cerrar la ventana
# desde otro hilo (el del servidor, cuando el puerto está ocupado):
# quien lo recibe (el hilo de la bandeja) hace el NIM_DELETE y el
# DestroyWindow, que son suyos.
MENSAJE_QUITAR = WM_USER + 21

NIM_ADD = 0x00000000
NIM_MODIFY = 0x00000001
NIM_DELETE = 0x00000002
NIF_MESSAGE = 0x00000001
NIF_ICON = 0x00000002
NIF_TIP = 0x00000004

MF_STRING = 0x00000000
MF_GRAYED = 0x00000001
MF_SEPARATOR = 0x00000800
MF_POPUP = 0x00000010
MF_BYPOSITION = 0x00000400
# 1.8: el menú se arma con InsertMenuItemW + MENUITEMINFOW.
MIIM_STATE = 0x00000001
MIIM_ID = 0x00000002
MIIM_SUBMENU = 0x00000004
MIIM_TYPE = 0x00000010
MIIM_STRING = 0x00000040
MFT_STRING = 0x00000000
MFT_SEPARATOR = 0x00000800
MFS_GRAYED = 0x00000003  # MF_GRAYED | MF_DISABLED
TPM_LEFTALIGN = 0x0000
TPM_BOTTOMALIGN = 0x0020
TPM_RETURNCMD = 0x0100
TPM_RIGHTBUTTON = 0x0002

# 1.9.1: menú de dibujo propio (owner-draw).
WM_DRAWITEM = 0x002B
WM_MEASUREITEM = 0x002C
MIIM_DATA = 0x00000020
MIIM_FTYPE = 0x00000100
MFT_OWNERDRAW = 0x00000100
ODT_MENU = 1
ODS_SELECTED = 0x0001
DT_LEFT = 0x0000
DT_VCENTER = 0x0004
DT_SINGLELINE = 0x0020
DT_NOPREFIX = 0x0800
DT_RIGHT = 0x0002
TRANSPARENT = 1
# True: el texto del menú lo pinta iMandro (recomendado en la PC de
# Liesky). False: menú nativo de Windows como en la 1.8.
MENU_PROPIO = True
# Si en el menú propio salieran DOS flechas en «Teléfonos conectados»,
# es que Windows también dibuja la suya: ponerlo en False.
DIBUJAR_FLECHA = True

IDI_ABRIR = 1001
IDI_REINICIAR = 1010
IDI_DETENER = 1011
IDI_CERRAR = 1012

# WINFUNCTYPE (stdcall) solo existe en Windows; fuera se define un tipo
# equivalente para que este módulo se pueda importar en cualquier sistema
# (la función iniciar() es la que decide si se usa o no).
_FABRICA_PROC = ctypes.WINFUNCTYPE if ES_WINDOWS else ctypes.CFUNCTYPE
WNDPROC = _FABRICA_PROC(ctypes.c_ssize_t, HWND, wintypes.UINT, WPARAM, LPARAM)


class WNDCLASSW(ctypes.Structure):
    _fields_ = [("style", wintypes.UINT),
                ("lpfnWndProc", WNDPROC),
                ("cbClsExtra", ctypes.c_int),
                ("cbWndExtra", ctypes.c_int),
                ("hInstance", HINSTANCE),
                ("hIcon", HICON),
                ("hCursor", HCURSOR),
                ("hbrBackground", HBRUSH),
                ("lpszMenuName", LPCWSTR),
                ("lpszClassName", LPCWSTR)]


class NOTIFYICONDATAW(ctypes.Structure):
    _fields_ = [("cbSize", wintypes.DWORD),
                ("hWnd", HWND),
                ("uID", wintypes.UINT),
                ("uFlags", wintypes.UINT),
                ("uCallbackMessage", wintypes.UINT),
                ("hIcon", HICON),
                ("szTip", wintypes.WCHAR * 128),
                ("dwState", wintypes.DWORD),
                ("dwStateMask", wintypes.DWORD),
                ("szInfo", wintypes.WCHAR * 256),
                ("uVersion", wintypes.UINT),
                ("szInfoTitle", wintypes.WCHAR * 64),
                ("dwInfoFlags", wintypes.DWORD)]


class PUNTO(ctypes.Structure):
    _fields_ = [("x", wintypes.LONG), ("y", wintypes.LONG)]


class MENUITEMINFOW(ctypes.Structure):
    # La ficha completa de cada opción del menú para InsertMenuItemW
    # (1.8). Los tipos son los de 64 bits: dwItemData es ULONG_PTR
    # (c_size_t), dwTypeData el puntero ancho del texto y hSubMenu el
    # HMENU del submenú. cbSize se rellena con sizeof al usarla.
    _fields_ = [("cbSize", wintypes.UINT),
                ("fMask", wintypes.UINT),
                ("fType", wintypes.UINT),
                ("fState", wintypes.UINT),
                ("wID", wintypes.UINT),
                ("hSubMenu", HMENU),
                ("hbmpChecked", HBITMAP),
                ("hbmpUnchecked", HBITMAP),
                ("dwItemData", ctypes.c_size_t),
                ("dwTypeData", LPCWSTR),
                ("cch", wintypes.UINT),
                ("hbmpItem", HBITMAP)]


HDC = getattr(wintypes, "HDC", ctypes.c_void_p)


class RECT(ctypes.Structure):
    _fields_ = [("left", wintypes.LONG), ("top", wintypes.LONG),
                ("right", wintypes.LONG), ("bottom", wintypes.LONG)]


class SIZE(ctypes.Structure):
    _fields_ = [("cx", wintypes.LONG), ("cy", wintypes.LONG)]


class MEASUREITEMSTRUCT(ctypes.Structure):
    _fields_ = [("CtlType", wintypes.UINT), ("CtlID", wintypes.UINT),
                ("itemID", wintypes.UINT), ("itemWidth", wintypes.UINT),
                ("itemHeight", wintypes.UINT), ("itemData", ctypes.c_size_t)]


class DRAWITEMSTRUCT(ctypes.Structure):
    _fields_ = [("CtlType", wintypes.UINT), ("CtlID", wintypes.UINT),
                ("itemID", wintypes.UINT), ("itemAction", wintypes.UINT),
                ("itemState", wintypes.UINT), ("hwndItem", ctypes.c_void_p),
                ("hDC", HDC), ("rcItem", RECT),
                ("itemData", ctypes.c_size_t)]


class MSG(ctypes.Structure):
    _fields_ = [("hwnd", HWND),
                ("message", wintypes.UINT),
                ("wParam", WPARAM),
                ("lParam", LPARAM),
                ("time", wintypes.DWORD),
                ("pt", PUNTO),
                ("lPrivate", wintypes.DWORD)]


# Estado real de la bandeja, para que el servidor lo enseñe en el
# editor: {"activa": bool, "detalle": str, "actualizado": "HH:MM:SS"}.
ESTADO = {"activa": False, "detalle": "sin iniciar", "actualizado": ""}

# 1.9.1: lo que hace falta para retirar el icono desde otro hilo —
# se rellena en _iniciar_win tras el NIM_ADD: el shell32 y el hwnd
# propios, un duplicado de la ficha y el acontecimiento que confirma
# que el icono ya no está. Y el «al_cerrar» opcional del servidor
# (cerrar también la ventana del editor al pulsar «Cerrar iMandro»).
_ACTIVA = {"user32": None, "shell32": None, "hwnd": None, "nid": None,
           "retirado": threading.Event()}
_CIERRE = {"al_cerrar": None}


def retirar_icono(espera=1.5):
    """Pide a la bandeja que retire su icono (NIM_DELETE) y cierre su
    ventana, y espera a que lo confirme. Lo llama el servidor cuando
    termina porque el puerto está ocupado: el icono no debe quedarse
    junto al reloj señalando a un iMandro que ya no existe. La
    retirada la hace el hilo de la bandeja (MENSAJE_QUITAR), que es
    el dueño de la ventana. Devuelve True si el icono quedó retirado;
    False si la bandeja no estaba activa o no confirmó a tiempo (el
    proceso sale de todos modos y Windows limpia el resto)."""
    hwnd, user32 = _ACTIVA["hwnd"], _ACTIVA["user32"]
    if not hwnd or user32 is None:
        return False
    try:
        _ACTIVA["retirado"].clear()
        user32.PostMessageW(hwnd, MENSAJE_QUITAR, 0, 0)
    except Exception:
        return False
    return bool(_ACTIVA["retirado"].wait(espera))


def registrar_al_cerrar(fn):
    """El servidor deja aquí una función que la bandeja invoca tras
    «Cerrar iMandro» (p. ej. cerrar también la ventana del editor).
    Bandeja la guarda pero NO la llama: quien la dispara es el
    servidor al salir de su bucle, cuando el cierre ya es efectivo."""
    _CIERRE["al_cerrar"] = fn

ARCHIVO_LOG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bandeja.log")


def _registra(detalle, activa=None):
    """Anota el estado de la bandeja y lo deja escrito en bandeja.log
    (junto a la configuración), con fecha y motivo. Nunca lanza: si ni
    el registro se puede escribir, la bandeja sigue sin tumbar nada."""
    ESTADO["detalle"] = detalle
    if activa is not None:
        ESTADO["activa"] = activa
    ESTADO["actualizado"] = time.strftime("%H:%M:%S")
    try:
        with open(ARCHIVO_LOG, "a", encoding="utf-8") as f:
            f.write("%s · %s\n" % (time.strftime("%Y-%m-%d %H:%M:%S"), detalle))
    except Exception:
        pass


def _ultimo_error():
    """El último error de Windows (ctypes.get_last_error solo existe
    en Windows; fuera devuelve 0). Lo usa _mostrar_menu para que su
    registro se pueda probar también sin Windows."""
    g = getattr(ctypes, "get_last_error", None)
    return g() if g is not None else 0


def _texto_estado(acciones):
    try:
        est = acciones["estado"]()
        return bool(est.get("corriendo")), str(est.get("detalle", ""))
    except Exception:
        return False, ""


def _colorref(r, g, b):
    return r | (g << 8) | (b << 16)


def _tema_claro():
    """True si Windows usa el tema claro para las aplicaciones (el
    valor AppsUseLightTheme del registro). Ante cualquier duda, claro."""
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                            r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize") as k:
            valor, _ = winreg.QueryValueEx(k, "AppsUseLightTheme")
            return bool(valor)
    except Exception:
        return True


class _MenuPropio(object):
    """El texto del menú, medido y pintado por iMandro (1.9.1).

    Cada opción del menú se inserta como MFT_OWNERDRAW con un número
    en dwItemData; aquí se guarda a qué texto corresponde. Windows
    manda WM_MEASUREITEM (¿cuánto mide?) y WM_DRAWITEM (píntalo) a la
    ventana de la bandeja y las contestamos con GDI, con colores y
    fuente propios: no dependen del tema visual de Windows, de los
    colores del sistema ni del pintor de menús del proceso.
    Todo ocurre en el hilo de la bandeja, dentro de TrackPopupMenu."""

    def __init__(self, user32, gdi32):
        self.u = user32
        self.g = gdi32
        self.items = {}
        self.medidos = 0
        self.pintados = 0
        self.cara = ""
        self.fuente = None
        self.esc = 1.0
        self.claro = True
        self.col = {}
        self.pinceles = {}
        self.listo = False
        self.errores = 0

    def _declara(self):
        u, g = self.u, self.g
        u.GetDC.argtypes = [HWND]
        u.GetDC.restype = HDC
        u.ReleaseDC.argtypes = [HWND, HDC]
        u.ReleaseDC.restype = ctypes.c_int
        u.FillRect.argtypes = [HDC, ctypes.POINTER(RECT), HBRUSH]
        u.FillRect.restype = ctypes.c_int
        u.DrawTextW.argtypes = [HDC, LPCWSTR, ctypes.c_int,
                                ctypes.POINTER(RECT), wintypes.UINT]
        u.DrawTextW.restype = ctypes.c_int
        g.GetDeviceCaps.argtypes = [HDC, ctypes.c_int]
        g.GetDeviceCaps.restype = ctypes.c_int
        g.CreateSolidBrush.argtypes = [wintypes.DWORD]
        g.CreateSolidBrush.restype = HBRUSH
        g.CreateFontW.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_int,
                                  ctypes.c_int, ctypes.c_int, wintypes.DWORD,
                                  wintypes.DWORD, wintypes.DWORD, wintypes.DWORD,
                                  wintypes.DWORD, wintypes.DWORD, wintypes.DWORD,
                                  wintypes.DWORD, LPCWSTR]
        g.CreateFontW.restype = HANDLE
        g.GetStockObject.argtypes = [ctypes.c_int]
        g.GetStockObject.restype = HANDLE
        g.SelectObject.argtypes = [HDC, HANDLE]
        g.SelectObject.restype = HANDLE
        g.SetBkMode.argtypes = [HDC, ctypes.c_int]
        g.SetBkMode.restype = ctypes.c_int
        g.SetTextColor.argtypes = [HDC, wintypes.DWORD]
        g.SetTextColor.restype = wintypes.DWORD
        g.GetTextExtentPoint32W.argtypes = [HDC, LPCWSTR, ctypes.c_int,
                                            ctypes.POINTER(SIZE)]
        g.GetTextExtentPoint32W.restype = wintypes.BOOL
        g.GetTextFaceW.argtypes = [HDC, ctypes.c_int, LPVOID]
        g.GetTextFaceW.restype = ctypes.c_int

    def _prepara(self):
        if self.listo:
            return
        self._declara()
        hdc = self.u.GetDC(None)
        try:
            dpi = self.g.GetDeviceCaps(hdc, 90) or 96  # LOGPIXELSY
        finally:
            self.u.ReleaseDC(None, hdc)
        self.esc = max(dpi / 96.0, 1.0)
        self.claro = _tema_claro()
        if self.claro:
            paleta = {"fondo": (249, 249, 249), "texto": (0, 0, 0),
                      "sel": (229, 229, 229), "gris": (140, 140, 140),
                      "linea": (205, 205, 205)}
        else:
            paleta = {"fondo": (43, 43, 43), "texto": (255, 255, 255),
                      "sel": (68, 68, 68), "gris": (135, 135, 135),
                      "linea": (85, 85, 85)}
        for nombre, (r, gg, b) in paleta.items():
            self.col[nombre] = _colorref(r, gg, b)
        for nombre in ("fondo", "sel", "linea"):
            self.pinceles[nombre] = self.g.CreateSolidBrush(self.col[nombre])
        # 12 px a 96 ppp son unos 9 pt, el tamaño normal de los menús.
        self.fuente = self.g.CreateFontW(-int(round(12 * self.esc)), 0, 0, 0, 400,
                                         0, 0, 0, 1, 0, 0, 5, 0, "Segoe UI")
        if not self.fuente:
            self.fuente = self.g.GetStockObject(17)  # DEFAULT_GUI_FONT
        self.listo = True

    def registra(self, texto, separador, activo, submenu):
        idx = len(self.items) + 1
        self.items[idx] = (texto or "", bool(separador), bool(activo), bool(submenu))
        return idx

    def limpia(self):
        self.items = {}
        self.medidos = 0
        self.pintados = 0

    def resumen(self):
        return ("menú propio: %d ítems, %d medidos, %d pintados, fuente «%s», "
                "tema %s, escala %.2f, errores %d"
                % (len(self.items), self.medidos, self.pintados,
                   self.cara or "?", "claro" if self.claro else "oscuro",
                   self.esc, self.errores))

    def medir(self, hwnd, lparam):
        self._prepara()
        m = ctypes.cast(lparam, ctypes.POINTER(MEASUREITEMSTRUCT)).contents
        if m.CtlType != ODT_MENU:
            return 0
        texto, separador, activo, submenu = self.items.get(m.itemData, ("", False, True, False))
        esc = self.esc
        if separador:
            m.itemWidth = int(round(40 * esc))
            m.itemHeight = int(round(9 * esc))
            self.medidos += 1
            return 1
        hdc = self.u.GetDC(hwnd)
        if not hdc:
            hdc = self.u.GetDC(None)
            hwnd = None
        try:
            viejo = self.g.SelectObject(hdc, self.fuente)
            if not self.cara:
                bufer = ctypes.create_unicode_buffer(64)
                self.g.GetTextFaceW(hdc, 64, bufer)
                self.cara = bufer.value
            tam = SIZE()
            self.g.GetTextExtentPoint32W(hdc, texto, len(texto), ctypes.byref(tam))
            self.g.SelectObject(hdc, viejo)
        finally:
            self.u.ReleaseDC(hwnd, hdc)
        extra = int(round((12 + 12 + (16 if submenu else 0)) * esc))
        m.itemWidth = tam.cx + extra
        m.itemHeight = max(tam.cy + int(round(10 * esc)), int(round(24 * esc)))
        self.medidos += 1
        return 1

    def dibujar(self, lparam):
        self._prepara()
        d = ctypes.cast(lparam, ctypes.POINTER(DRAWITEMSTRUCT)).contents
        if d.CtlType != ODT_MENU:
            return 0
        texto, separador, activo, submenu = self.items.get(d.itemData, ("", False, True, False))
        hdc = d.hDC
        r = d.rcItem
        esc = self.esc
        resaltado = bool(d.itemState & ODS_SELECTED) and activo and not separador
        self.u.FillRect(hdc, ctypes.byref(r),
                        self.pinceles["sel" if resaltado else "fondo"])
        if separador:
            y = (r.top + r.bottom) // 2
            linea = RECT(r.left + int(round(8 * esc)), y, r.right - int(round(8 * esc)), y + 1)
            self.u.FillRect(hdc, ctypes.byref(linea), self.pinceles["linea"])
            self.pintados += 1
            return 1
        viejo = self.g.SelectObject(hdc, self.fuente)
        self.g.SetBkMode(hdc, TRANSPARENT)
        self.g.SetTextColor(hdc, self.col["texto"] if activo else self.col["gris"])
        margen = int(round(12 * esc))
        caja = RECT(r.left + margen, r.top, r.right - margen, r.bottom)
        self.u.DrawTextW(hdc, texto, -1, ctypes.byref(caja),
                         DT_LEFT | DT_VCENTER | DT_SINGLELINE | DT_NOPREFIX)
        if submenu and DIBUJAR_FLECHA:
            self.g.SetTextColor(hdc, self.col["texto"])
            self.u.DrawTextW(hdc, "\u203a", -1, ctypes.byref(caja),
                             DT_RIGHT | DT_VCENTER | DT_SINGLELINE | DT_NOPREFIX)
        self.g.SelectObject(hdc, viejo)
        self.pintados += 1
        return 1


_DIAG_HECHO = {"ya": False}


def _diagnostico_pintura(user32):
    """Una sola vez por ejecución: anota en bandeja.log con qué colores
    y tema pinta Windows los menús en ESTE proceso. Si COLOR_MENU y
    COLOR_MENUTEXT salen iguales (o casi), esa es la causa."""
    if _DIAG_HECHO["ya"] or not ES_WINDOWS:
        return
    _DIAG_HECHO["ya"] = True
    try:
        user32.GetSysColor.argtypes = [ctypes.c_int]
        user32.GetSysColor.restype = wintypes.DWORD

        def hexa(c):
            return "#%02X%02X%02X" % (c & 0xFF, (c >> 8) & 0xFF, (c >> 16) & 0xFF)
        tema = ctypes.WinDLL("uxtheme").IsThemeActive()
        _registra("menú: diagnóstico de pintura · COLOR_MENU=%s · COLOR_MENUTEXT=%s · "
                  "COLOR_MENUHILIGHT=%s · tema visual activo=%s · AppsUseLightTheme claro=%s"
                  % (hexa(user32.GetSysColor(4)), hexa(user32.GetSysColor(7)),
                     hexa(user32.GetSysColor(29)), bool(tema), _tema_claro()))
    except Exception as e:
        _registra("menú: el diagnóstico de pintura falló: %r" % e)


def _mostrar_menu(user32, acciones, hwnd, shell32=None, nid=None, poner_punta=None,
                  propio=None):
    """Enseña el menú de la bandeja y atiende la opción elegida.

    Vive a nivel de módulo (1.7.10) para poder probarla con un user32
    simulado, sin Windows; _iniciar_win solo la enlaza con su ventana.
    La estructura, el orden y los textos del menú son los de siempre.

    1.8: el menú se arma con InsertMenuItemW + MENUITEMINFOW, la
    vía que usan las aplicaciones de verdad. Era AppendMenuW con
    cadenas anchas vía ctypes y en la PC de Liesky el menú se abría
    con toda su estructura pero sin pintar ni una letra, mientras
    los menús de Windows sí enseñaban las suyas — el fallo estaba
    en ese modo de meter los textos, no en los textos.

    Y ya nada falla en silencio — todo queda en bandeja.log:
    - cada InsertMenuItemW que devuelve falso queda anotado por
      su nombre;
    - tras armar el menú, se lee de vuelta su primer texto
      (GetMenuStringW) y queda anotado con el número de ítems:
      la prueba escrita de que el dato quedó bien puesto;
    - si GetCursorPos devuelve falso, el menú se aborta y queda
      anotado; si SetForegroundWindow devuelve falso, se anota
      y se sigue;
    - el resultado bruto de TrackPopupMenu se anota una vez por
      clic, con el último error de Windows si devolvió 0 y con
      los milisegundos que el menú estuvo abierto;
    - cualquier excepción queda anotada («menú: error al mostrarlo»)
      y NO se propaga: el menú nunca puede tumbar la bandeja.
    shell32/nid/poner_punta solo hacen falta al final (quitar el icono
    al cerrar y repintar la punta al detener/iniciar); sin ellos —las
    pruebas— el menú se enseña igual."""
    try:
        corriendo, detalle = _texto_estado(acciones)
        _diagnostico_pintura(user32)
        if propio is not None:
            propio.limpia()
        menu = user32.CreatePopupMenu()
        fallos = []
        vivas = []  # las MENUITEMINFOW, vivas hasta que el menú se cierra

        def pon(menu_, pos, nombre, mascara, tipo=0, estado=0, wid=0,
                texto=None, sub=None):
            it = MENUITEMINFOW()
            it.cbSize = ctypes.sizeof(MENUITEMINFOW)
            if propio is not None:
                # 1.9.1: opción de dibujo propio. El texto NO viaja a
                # Windows: se guarda en «propio» y dwItemData lleva su
                # número; Windows pregunta (WM_MEASUREITEM) y pide
                # pintar (WM_DRAWITEM) y lo hace iMandro.
                separador = (tipo == MFT_SEPARATOR)
                sin_uso = bool(separador or estado)
                it.fMask = MIIM_FTYPE | MIIM_DATA | MIIM_ID | MIIM_STATE
                it.fType = MFT_OWNERDRAW
                it.fState = MFS_GRAYED if sin_uso else 0
                it.wID = wid
                it.dwItemData = propio.registra(texto, separador, not sin_uso,
                                                sub is not None)
                if sub is not None:
                    it.fMask |= MIIM_SUBMENU
                    it.hSubMenu = sub
            else:
                it.fMask = mascara
                it.fType = tipo
                it.fState = estado
                it.wID = wid
                if sub is not None:
                    it.hSubMenu = sub
                if texto is not None:
                    it.dwTypeData = texto
                    it.cch = len(texto)
            vivas.append(it)
            if not user32.InsertMenuItemW(menu_, pos, True, ctypes.byref(it)):
                fallos.append(nombre)

        pon(menu, 0, "«Abrir»", MIIM_STRING | MIIM_ID, wid=IDI_ABRIR,
            texto="Abrir iMandro")
        pon(menu, 1, "separador 1", MIIM_TYPE, tipo=MFT_SEPARATOR)
        texto = "Estado: funcionando" if corriendo else "Estado: detenido"
        if detalle:
            texto += " · " + detalle
        pon(menu, 2, "el estado", MIIM_STRING | MIIM_STATE,
            estado=MFS_GRAYED, texto=texto)
        # Submenú con los teléfonos autorizados en esta PC.
        sub = user32.CreatePopupMenu()
        try:
            tels = acciones["dispositivos"]() or []
        except Exception:
            tels = []
        if tels:
            for i, t in enumerate(tels):
                linea = "%s — %s" % (t.get("nombre", "Teléfono"), t.get("detalle", ""))
                pon(sub, i, "ítem del submenú «%s»" % linea,
                    MIIM_STRING | MIIM_STATE, estado=MFS_GRAYED, texto=linea)
        else:
            pon(sub, 0, "ítem del submenú (ningún teléfono)",
                MIIM_STRING | MIIM_STATE, estado=MFS_GRAYED,
                texto="Ningún teléfono autorizado todavía")
        pon(menu, 3, "«Teléfonos conectados»", MIIM_STRING | MIIM_SUBMENU,
            texto="Teléfonos conectados", sub=sub)
        pon(menu, 4, "separador 2", MIIM_TYPE, tipo=MFT_SEPARATOR)
        pon(menu, 5, "«Reiniciar»", MIIM_STRING | MIIM_ID, wid=IDI_REINICIAR,
            texto="Reiniciar el servidor")
        if corriendo:
            pon(menu, 6, "«Detener/Iniciar»", MIIM_STRING | MIIM_ID,
                wid=IDI_DETENER, texto="Detener el servidor")
        else:
            pon(menu, 6, "«Detener/Iniciar»", MIIM_STRING | MIIM_ID,
                wid=IDI_DETENER, texto="Iniciar el servidor")
        pon(menu, 7, "separador 3", MIIM_TYPE, tipo=MFT_SEPARATOR)
        pon(menu, 8, "«Cerrar»", MIIM_STRING | MIIM_ID, wid=IDI_CERRAR,
            texto="Cerrar iMandro")
        if fallos:
            _registra("menú: InsertMenuItemW devolvió falso en: %s" % "; ".join(fallos))
        # Lectura de vuelta (1.8): antes de enseñar el menú, se le
        # pregunta a Windows por el texto de su primera opción y el
        # número de ítems, y queda escrito. Es el testigo de que los
        # textos quedaron dentro — si un día el menú volviera a salir
        # sin letras, esta línea diría de qué lado está el fallo. El
        # testigo nunca bloquea el menú: si la lectura misma falla,
        # se anota y se sigue.
        try:
            bufer = ctypes.create_unicode_buffer(256)
            if propio is not None:
                _registra("menú propio: armado con %d ítems de dibujo propio"
                          % user32.GetMenuItemCount(menu))
                leidos = None
                total = 0
            else:
                leidos = user32.GetMenuStringW(menu, 0, bufer, 256, MF_BYPOSITION)
                total = user32.GetMenuItemCount(menu)
            if leidos is None:
                pass
            elif leidos:
                _registra("menú: lectura de vuelta del primer texto: '%s' (%d ítems)"
                          % (bufer.value, total))
            else:
                _registra("menú: lectura de vuelta VACÍA/falló (%d ítems)" % total)
        except Exception:
            _registra("menú: lectura de vuelta VACÍA/falló")
        pt = PUNTO()
        if not user32.GetCursorPos(ctypes.byref(pt)):
            _registra("menú: GetCursorPos devolvió falso · último error de Windows: %d"
                      % _ultimo_error())
            user32.DestroyMenu(menu)
            return
        if not user32.SetForegroundWindow(hwnd):
            _registra("menú: SetForegroundWindow devolvió falso · último error de Windows: %d"
                      % _ultimo_error())
        t0 = time.monotonic()
        cmd = user32.TrackPopupMenu(menu, TPM_LEFTALIGN | TPM_BOTTOMALIGN | TPM_RETURNCMD | TPM_RIGHTBUTTON,
                                    pt.x, pt.y, 0, hwnd, None)
        abierto_ms = int(round((time.monotonic() - t0) * 1000))
        error = _ultimo_error()
        if cmd == 0:
            _registra("menú: TrackPopupMenu devolvió 0 · último error de Windows: %d · abierto %d ms"
                      % (error, abierto_ms))
        else:
            _registra("menú: TrackPopupMenu devolvió %d · abierto %d ms"
                      % (cmd, abierto_ms))
        if propio is not None:
            _registra("menú: " + propio.resumen())
        user32.PostMessageW(hwnd, WM_NULL, 0, 0)
        user32.DestroyMenu(menu)
        if propio is not None:
            propio.limpia()
        if cmd == IDI_ABRIR:
            try: acciones["abrir_editor"]()
            except Exception: pass
        elif cmd == IDI_REINICIAR:
            try: acciones["reiniciar"]()
            except Exception: pass
        elif cmd == IDI_DETENER:
            try:
                if corriendo: acciones["detener"]()
                else: acciones["iniciar"]()
            except Exception: pass
            if poner_punta is not None:
                poner_punta()
        elif cmd == IDI_CERRAR:
            try: acciones["cerrar"]()
            except Exception: pass
            if shell32 is not None and nid is not None:
                shell32.Shell_NotifyIconW(NIM_DELETE, ctypes.byref(nid))
            user32.DestroyWindow(hwnd)
    except Exception as e:
        _registra("menú: error al mostrarlo: %r" % e)


def iniciar(acciones, icono=None):
    """Pone el icono en la bandeja y atiende su menú hasta que se cierra.

    «acciones» es un diccionario de funciones que da el servidor:
    abrir_editor(), estado() -> {"corriendo": bool, "detalle": str},
    dispositivos() -> [{"nombre": str, "detalle": str}], reiniciar(),
    detener(), iniciar() y cerrar().
    Devuelve True si la bandeja llegó a funcionar; False si no (otro
    sistema, falta de icono, cualquier error de Windows). Nunca lanza:
    la bandeja es un adorno, no puede tumbar el servidor. El motivo de
    cada fallo queda en ESTADO y en bandeja.log."""
    if not ES_WINDOWS:
        _registra("la bandeja solo existe en Windows; en este sistema no se crea", activa=False)
        return False
    try:
        ok, motivo = _iniciar_win(acciones, icono)
    except Exception as e:
        _registra("la bandeja no pudo arrancar: %s" % e, activa=False)
        return False
    if ok:
        _registra("activa: el icono está junto al reloj (o en la flecha ^ de iconos ocultos)", activa=True)
    else:
        _registra("no disponible: %s" % motivo, activa=False)
    return ok


def _iniciar_win(acciones, icono):
    # 1.9.1: instancias propias con use_last_error=True. Con
    # ctypes.windll, get_last_error() devolvía SIEMPRE 0 y los «último
    # error de Windows» del registro no decían nada; además así los
    # prototipos de abajo no tocan la copia global de ctypes.windll.
    user32 = ctypes.WinDLL("user32", use_last_error=True)
    shell32 = ctypes.WinDLL("shell32", use_last_error=True)
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    gdi32 = ctypes.WinDLL("gdi32", use_last_error=True)

    user32.CreateWindowExW.restype = HWND
    user32.CreateWindowExW.argtypes = [wintypes.DWORD, LPCWSTR, LPCWSTR,
                                       wintypes.DWORD, ctypes.c_int, ctypes.c_int, ctypes.c_int,
                                       ctypes.c_int, HWND, HMENU, HINSTANCE, LPVOID]
    user32.CreatePopupMenu.restype = HMENU
    user32.LoadImageW.restype = HANDLE
    user32.DefWindowProcW.restype = ctypes.c_ssize_t
    shell32.Shell_NotifyIconW.argtypes = [wintypes.DWORD, ctypes.POINTER(NOTIFYICONDATAW)]
    shell32.Shell_NotifyIconW.restype = wintypes.BOOL
    kernel32.GetModuleHandleW.restype = HMODULE

    # 1.7.8: la familia del menú, CON prototipos. Era la única ruta de
    # texto del módulo que se llamaba «a pelo», sin argtypes: sin la
    # firma declarada, ctypes improvisa la conversión de cada
    # argumento y en AppendMenuW eso se comía el texto (el 3.er
    # parámetro es de tamaño puntero — UINT_PTR — y el 4.º, el
    # LPCWSTR del que cuelga cada etiqueta): el menú se abría con su
    # estructura y todas las etiquetas en blanco. Diagnóstico completo
    # en NOTA-menu-bandeja-1.7.8.md. Las llamadas de mostrar_menu no
    # cambian: con el prototipo, pasar la str de Python es lo correcto.
    user32.CreatePopupMenu.argtypes = []
    user32.AppendMenuW.argtypes = [HMENU, wintypes.UINT, ctypes.c_size_t, LPCWSTR]
    user32.AppendMenuW.restype = wintypes.BOOL
    # 1.8: el menú se arma con InsertMenuItemW + MENUITEMINFOW (la
    # vía de las aplicaciones de verdad) y se lee de vuelta su primer
    # texto antes de enseñarlo. AppendMenuW ya no se usa para meter
    # los textos — su prototipo se queda declarado arriba, sin uso.
    # En GetMenuStringW el búfer va declarado LPVOID: lo que viaja es
    # su dirección (ctypes convierte el búfer al pasar), así la firma
    # sirve igual en Windows y en el user32 simulado de las pruebas.
    user32.InsertMenuItemW.argtypes = [HMENU, wintypes.UINT, wintypes.BOOL,
                                       ctypes.POINTER(MENUITEMINFOW)]
    user32.InsertMenuItemW.restype = wintypes.BOOL
    user32.GetMenuStringW.argtypes = [HMENU, wintypes.UINT, LPVOID,
                                      ctypes.c_int, wintypes.UINT]
    user32.GetMenuStringW.restype = wintypes.UINT
    user32.GetMenuItemCount.argtypes = [HMENU]
    user32.GetMenuItemCount.restype = ctypes.c_int
    user32.TrackPopupMenu.argtypes = [HMENU, wintypes.UINT, ctypes.c_int, ctypes.c_int,
                                      ctypes.c_int, HWND, LPVOID]
    user32.TrackPopupMenu.restype = wintypes.UINT
    user32.DestroyMenu.argtypes = [HMENU]
    user32.DestroyMenu.restype = wintypes.BOOL
    user32.GetCursorPos.argtypes = [ctypes.POINTER(PUNTO)]
    user32.GetCursorPos.restype = wintypes.BOOL
    user32.SetForegroundWindow.argtypes = [HWND]
    user32.SetForegroundWindow.restype = wintypes.BOOL
    user32.PostMessageW.argtypes = [HWND, wintypes.UINT, WPARAM, LPARAM]
    user32.PostMessageW.restype = wintypes.BOOL
    # 1.9.1: DefWindowProcW se llamaba SIN prototipo desde el wndproc.
    # En 64 bits ctypes pasa los enteros de Python como int de 32
    # bits (o falla con «int too long to convert» si no caben), así
    # que wParam/lParam con punteros (WM_NCCREATE, WM_GETMINMAXINFO,
    # WM_WINDOWPOSCHANGING, WM_INITMENUPOPUP... todos ocurren al
    # mostrar un menú) no llegaban enteros al procesamiento por
    # defecto de Windows.
    user32.DefWindowProcW.argtypes = [HWND, wintypes.UINT, WPARAM, LPARAM]
    user32.DefWindowProcW.restype = ctypes.c_ssize_t
    user32.DestroyWindow.argtypes = [HWND]
    user32.DestroyWindow.restype = wintypes.BOOL
    user32.PostQuitMessage.argtypes = [ctypes.c_int]
    user32.PostQuitMessage.restype = None

    propio = _MenuPropio(user32, gdi32) if MENU_PROPIO else None
    # 1.9.1: la vía para que el servidor pida retirar el icono desde
    # otro hilo (MENSAJE_QUITAR), con la ficha propia de este hilo.
    _ACTIVA["user32"] = user32
    _ACTIVA["shell32"] = shell32

    hinst = kernel32.GetModuleHandleW(None)

    # Si el Explorador de Windows renace (se cae o se reinicia), borra
    # los iconos de la bandeja y avisa con este mensaje; su número no es
    # fijo, se pide al arrancar. Al recibirlo, el icono se repone solo.
    WM_TASKBARCREATED = user32.RegisterWindowMessageW("TaskbarCreated")

    # El icono de iMandro: el .ico de la aplicación si se pudo cargar.
    hicono = None
    if icono:
        LR_LOADFROMFILE = 0x0010
        LR_DEFAULTSIZE = 0x0040
        IMAGE_ICON = 1
        hicono = user32.LoadImageW(None, icono, IMAGE_ICON, 0, 0, LR_LOADFROMFILE | LR_DEFAULTSIZE)
    if not hicono:
        IDI_APPLICATION = 32512
        hicono = user32.LoadIconW(None, ctypes.cast(IDI_APPLICATION, LPCWSTR))

    nid = NOTIFYICONDATAW()
    nid.cbSize = ctypes.sizeof(NOTIFYICONDATAW)
    nid.uID = 1
    nid.uFlags = NIF_MESSAGE | NIF_ICON | NIF_TIP
    nid.uCallbackMessage = MENSAJE_BANDEJA
    nid.hIcon = hicono

    estado = {"punta": ""}

    def poner_punta():
        corriendo, _ = _texto_estado(acciones)
        punta = "iMandro · funcionando" if corriendo else "iMandro · detenido"
        if punta != estado["punta"]:
            estado["punta"] = punta
            nid.szTip = punta
            try:
                shell32.Shell_NotifyIconW(NIM_MODIFY, ctypes.byref(nid))
            except Exception:
                pass

    def mostrar_menu(hwnd):
        # 1.7.10: la lógica vive en _mostrar_menu (a nivel de módulo,
        # probada con un user32 simulado); aquí solo se enlaza con lo
        # de esta ventana. El wndproc la sigue llamando igual.
        _mostrar_menu(user32, acciones, hwnd, shell32, nid, poner_punta, propio)

    def wndproc(hwnd, msg, wparam, lparam):
        if msg == WM_TASKBARCREATED:
            # El Explorador renació y el icono desapareció: se repone.
            try:
                if shell32.Shell_NotifyIconW(NIM_ADD, ctypes.byref(nid)):
                    estado["punta"] = None
                    poner_punta()
                    _registra("activa: el icono se repuso porque el Explorador de Windows reinició", activa=True)
                else:
                    _registra("Windows rechazó reponer el icono tras el reinicio del Explorador")
            except Exception as e:
                _registra("no se pudo reponer el icono tras el reinicio del Explorador: %s" % e)
            return 0
        if msg == MENSAJE_BANDEJA:
            if lparam in (WM_RBUTTONUP,):
                mostrar_menu(hwnd)
            elif lparam in (WM_LBUTTONDBLCLK,):
                try: acciones["abrir_editor"]()
                except Exception: pass
            return 0
        if propio is not None and msg in (WM_MEASUREITEM, WM_DRAWITEM):
            try:
                if msg == WM_MEASUREITEM:
                    return propio.medir(hwnd, lparam)
                return propio.dibujar(lparam)
            except Exception as e:
                propio.errores += 1
                if propio.errores <= 3:
                    _registra("menú propio: error al %s: %r"
                              % ("medir" if msg == WM_MEASUREITEM else "pintar", e))
                return 0
        if msg == WM_TIMER:
            poner_punta()
            return 0
        if msg == WM_DESTROY:
            user32.PostQuitMessage(0)
            return 0
        return user32.DefWindowProcW(hwnd, msg, wparam, lparam)

    # 1.9.1: el mensaje QUITAR llega desde otro hilo (retirar_icono,
    # cuando el servidor termina por puerto ocupado): el icono se
    # retira y la ventana se cierra aquí, en su hilo, y quien pidió
    # la retirada queda avisado por el acontecimiento.
    wndproc_original = wndproc

    def wndproc_con_quitar(hwnd, msg, wparam, lparam):
        if msg == MENSAJE_QUITAR:
            try:
                shell32.Shell_NotifyIconW(NIM_DELETE, ctypes.byref(nid))
            except Exception:
                pass
            _ACTIVA["hwnd"] = None
            _ACTIVA["retirado"].set()
            _ACTIVA["sin_cierre_editor"] = True
            _registra("el icono se retiró de la bandeja (el servidor terminó)", activa=False)
            user32.DestroyWindow(hwnd)
            return 0
        return wndproc_original(hwnd, msg, wparam, lparam)

    proc = WNDPROC(wndproc_con_quitar)  # se guarda la referencia: si se recoge, la ventana muere

    clase = WNDCLASSW()
    clase.lpfnWndProc = proc
    clase.hInstance = hinst
    clase.hIcon = hicono
    clase.lpszClassName = "iMandroBandeja"
    if not user32.RegisterClassW(ctypes.byref(clase)):
        # Puede estar ya registrada si se reintenta: no es un fallo.
        if ctypes.get_last_error() != 1410:  # ERROR_CLASS_ALREADY_EXISTS
            return False, "Windows no dejó registrar la ventana de la bandeja (error %d)" % ctypes.get_last_error()

    hwnd = user32.CreateWindowExW(0, "iMandroBandeja", "iMandro", 0,
                                  0, 0, 0, 0, None, None, hinst, None)
    if not hwnd:
        return False, "no se pudo crear la ventana de la bandeja (error %d)" % ctypes.get_last_error()
    nid.hWnd = hwnd
    # 1.9.1: el hwnd y la ficha propios quedan a mano para
    # retirar_icono() (el mensaje QUITAR usa esta misma ficha).
    _ACTIVA["hwnd"] = hwnd
    _ACTIVA["nid"] = nid

    if not shell32.Shell_NotifyIconW(NIM_ADD, ctypes.byref(nid)):
        motivo = "Windows rechazó el icono de la bandeja (Shell_NotifyIcon, error %d)" % ctypes.get_last_error()
        user32.DestroyWindow(hwnd)
        return False, motivo
    # 1.7.10: la línea «activa» se escribe AHORA, con la bandeja viva.
    # Antes solo la escribía iniciar() cuando _iniciar_win retornaba
    # (la bandeja ya muerta): en una bandeja sana bandeja.log ni
    # existía, y el registro tenía un punto ciego justo donde hacía
    # falta mirar. La llamada de iniciar() tras el retorno se queda.
    _registra("activa: el icono está junto al reloj (o en la flecha ^ de iconos ocultos)", activa=True)
    estado["punta"] = None
    poner_punta()
    user32.SetTimer(hwnd, 1, 5000, None)

    mensaje = MSG()
    while user32.GetMessageW(ctypes.byref(mensaje), None, 0, 0) > 0:
        user32.TranslateMessage(ctypes.byref(mensaje))
        user32.DispatchMessageW(ctypes.byref(mensaje))
    try:
        shell32.Shell_NotifyIconW(NIM_DELETE, ctypes.byref(nid))
    except Exception:
        pass
    _ACTIVA["hwnd"] = None
    _ACTIVA["retirado"].set()
    # 1.9.1: si el servidor dejó una función «al_cerrar» (cerrar
    # también la ventana del editor), se dispara al salir del bucle,
    # pero SOLO en el camino de «Cerrar iMandro»: en el de puerto
    # ocupado (MENSAJE_QUITAR) la ventana del editor puede ser de la
    # otra copia que sigue viva, y no se toca.
    al_cerrar = _CIERRE["al_cerrar"]
    if al_cerrar is not None and not _ACTIVA.pop("sin_cierre_editor", False):
        try:
            al_cerrar()
        except Exception:
            pass
    return True, ""
