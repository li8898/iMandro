; Instalador de iMandro v1.9.4 (PC) - Creador: Liesky Vazquez
Unicode true
!include "MUI2.nsh"

Name "iMandro"
OutFile "..\entrega\Instalar-iMandro-v1.9.4.exe"
InstallDir "$LOCALAPPDATA\iMandro"
RequestExecutionLevel user
SetCompressor /SOLID lzma
Icon "icono.ico"
UninstallIcon "icono.ico"
VIProductVersion "1.9.4.0"
VIAddVersionKey "ProductName" "iMandro"
VIAddVersionKey "FileDescription" "Panel de control para la PC desde el telefono (tipo Stream Deck)"
VIAddVersionKey "FileVersion" "1.9.4.0"
VIAddVersionKey "CompanyName" "Liesky Vazquez"
VIAddVersionKey "LegalCopyright" "(c) 2026 Liesky Vazquez"

!define MUI_ICON "icono.ico"
!define MUI_UNICON "icono.ico"
!define MUI_WELCOMEPAGE_TITLE "iMandro"
!define MUI_WELCOMEPAGE_TEXT "Este asistente instala iMandro en tu PC.$\r$\n$\r$\nCon iMandro conviertes tus telefonos en un panel de botones (tipo Stream Deck) para controlar esta PC y Photoshop por tu Wi-Fi local, sin internet.$\r$\n$\r$\nAl terminar, iMandro se abre en su propia ventana: ahi cambias los botones, los iconos y los colores, y todo llega solo a los telefonos. Cerrar la ventana no apaga iMandro: sigue en la bandeja, junto al reloj.$\r$\n$\r$\nPulsa Siguiente para continuar."
!define MUI_FINISHPAGE_RUN "$INSTDIR\python\pythonw.exe"
!define MUI_FINISHPAGE_RUN_PARAMETERS "$\"$INSTDIR\aplicacion.py$\""
!define MUI_FINISHPAGE_RUN_TEXT "Abrir iMandro ahora"
!define MUI_FINISHPAGE_TITLE "Instalación terminada"

!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

!insertmacro MUI_LANGUAGE "Spanish"

Section "Instalar"
    ; 1.7.7: antes de copiar, se detiene la copia anterior SI está
    ; corriendo. En la 1.7.6, instalar encima con iMandro abierto
    ; fallaba con «Error abriendo archivo para escritura», porque
    ; Windows no sobrescribe archivos en uso (el pythonw del servidor
    ; y el adb.exe quedan vivos aunque se cierre la ventana). El
    ; script de PowerShell (con -EncodedCommand, como el resto del
    ; proyecto) detiene SOLO los procesos cuyo ejecutable está dentro
    ; de la carpeta de instalación ($LOCALAPPDATA\iMandro, que es
    ; $INSTDIR): el python/pythonw de la instalación y su adb.exe.
    ; Nada de matar por nombre: los pythonw de otros programas no se
    ; tocan, y el propio instalador queda excluido por su nombre. Si
    ; no hay nada corriendo, no pasa nada y se sigue como siempre.
    ExecWait '"$WINDIR\System32\WindowsPowerShell\v1.0\powershell.exe" -NoProfile -WindowStyle Hidden -EncodedCommand JABkACAAPQAgACIAJABlAG4AdgA6AEwATwBDAEEATABBAFAAUABEAEEAVABBAFwAaQBNAGEAbgBkAHIAbwBcACIAOwAgAEcAZQB0AC0AQwBpAG0ASQBuAHMAdABhAG4AYwBlACAAVwBpAG4AMwAyAF8AUAByAG8AYwBlAHMAcwAgAHwAIABXAGgAZQByAGUALQBPAGIAagBlAGMAdAAgAHsAIAAkAF8ALgBFAHgAZQBjAHUAdABhAGIAbABlAFAAYQB0AGgAIAAtAGEAbgBkACAAJABfAC4ARQB4AGUAYwB1AHQAYQBiAGwAZQBQAGEAdABoACAALQBsAGkAawBlACAAKAAkAGQAIAArACAAIgAqACIAKQAgAC0AYQBuAGQAIAAkAF8ALgBFAHgAZQBjAHUAdABhAGIAbABlAFAAYQB0AGgAIAAtAG4AbwB0AGwAaQBrAGUAIAAiACoASQBuAHMAdABhAGwAYQByAC0AaQBNAGEAbgBkAHIAbwAqACIAIAB9ACAAfAAgAEYAbwByAEUAYQBjAGgALQBPAGIAagBlAGMAdAAgAHsAIABTAHQAbwBwAC0AUAByAG8AYwBlAHMAcwAgAC0ASQBkACAAJABfAC4AUAByAG8AYwBlAHMAcwBJAGQAIAAtAEYAbwByAGMAZQAgAC0ARQByAHIAbwByAEEAYwB0AGkAbwBuACAAUwBpAGwAZQBuAHQAbAB5AEMAbwBuAHQAaQBuAHUAZQAgAH0AOwAgAFMAdABhAHIAdAAtAFMAbABlAGUAcAAgAC0ATQBpAGwAbABpAHMAZQBjAG8AbgBkAHMAIAA3ADAAMAA='
    Sleep 600
    SetOutPath "$INSTDIR"
    File "build-installer\servidor.py"
    File "build-installer\aplicacion.py"
    File "build-installer\bandeja.py"
    File "build-installer\icono.ico"

    SetOutPath "$INSTDIR\static"
    File /r "build-installer\static\*.*"
    SetOutPath "$INSTDIR\adb"
    File "build-installer\adb\adb.exe"
    File "build-installer\adb\AdbWinApi.dll"
    File "build-installer\adb\AdbWinUsbApi.dll"

    SetOutPath "$INSTDIR\python"
    File /r "build-installer\python\*.*"

    SetOutPath "$INSTDIR"
    CreateShortcut "$DESKTOP\iMandro.lnk" "$INSTDIR\python\pythonw.exe" "$\"$INSTDIR\aplicacion.py$\"" "$INSTDIR\icono.ico"
    CreateDirectory "$SMPROGRAMS\iMandro"
    CreateShortcut "$SMPROGRAMS\iMandro\iMandro.lnk" "$INSTDIR\python\pythonw.exe" "$\"$INSTDIR\aplicacion.py$\"" "$INSTDIR\icono.ico"
    CreateShortcut "$SMPROGRAMS\iMandro\iMandro (navegador).lnk" "$INSTDIR\python\pythonw.exe" "$\"$INSTDIR\servidor.py$\"" "$INSTDIR\icono.ico"
    CreateShortcut "$SMPROGRAMS\iMandro\Desinstalar iMandro.lnk" "$INSTDIR\Desinstalar.exe"

    WriteUninstaller "$INSTDIR\Desinstalar.exe"
    WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\iMandro" "DisplayName" "iMandro"
    WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\iMandro" "UninstallString" "$\"$INSTDIR\Desinstalar.exe$\""
    WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\iMandro" "DisplayIcon" "$INSTDIR\icono.ico"
    WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\iMandro" "Publisher" "Liesky Vazquez"
    WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\iMandro" "DisplayVersion" "1.9.4"
SectionEnd

Section "Uninstall"
    ; 1.7.9 (auditoría I2): antes de borrar, se detiene el servidor si
    ; está en marcha, con EL MISMO bloque de la instalación: solo los
    ; procesos cuyo ejecutable vive dentro de la carpeta de
    ; instalación. Desinstalar con iMandro abierto dejaba archivos en
    ; uso que no se podían borrar y la carpeta quedaba a medias.
    ExecWait '"$WINDIR\System32\WindowsPowerShell\v1.0\powershell.exe" -NoProfile -WindowStyle Hidden -EncodedCommand JABkACAAPQAgACIAJABlAG4AdgA6AEwATwBDAEEATABBAFAAUABEAEEAVABBAFwAaQBNAGEAbgBkAHIAbwBcACIAOwAgAEcAZQB0AC0AQwBpAG0ASQBuAHMAdABhAG4AYwBlACAAVwBpAG4AMwAyAF8AUAByAG8AYwBlAHMAcwAgAHwAIABXAGgAZQByAGUALQBPAGIAagBlAGMAdAAgAHsAIAAkAF8ALgBFAHgAZQBjAHUAdABhAGIAbABlAFAAYQB0AGgAIAAtAGEAbgBkACAAJABfAC4ARQB4AGUAYwB1AHQAYQBiAGwAZQBQAGEAdABoACAALQBsAGkAawBlACAAKAAkAGQAIAArACAAIgAqACIAKQAgAC0AYQBuAGQAIAAkAF8ALgBFAHgAZQBjAHUAdABhAGIAbABlAFAAYQB0AGgAIAAtAG4AbwB0AGwAaQBrAGUAIAAiACoASQBuAHMAdABhAGwAYQByAC0AaQBNAGEAbgBkAHIAbwAqACIAIAB9ACAAfAAgAEYAbwByAEUAYQBjAGgALQBPAGIAagBlAGMAdAAgAHsAIABTAHQAbwBwAC0AUAByAG8AYwBlAHMAcwAgAC0ASQBkACAAJABfAC4AUAByAG8AYwBlAHMAcwBJAGQAIAAtAEYAbwByAGMAZQAgAC0ARQByAHIAbwByAEEAYwB0AGkAbwBuACAAUwBpAGwAZQBuAHQAbAB5AEMAbwBuAHQAaQBuAHUAZQAgAH0AOwAgAFMAdABhAHIAdAAtAFMAbABlAGUAcAAgAC0ATQBpAGwAbABpAHMAZQBjAG8AbgBkAHMAIAA3ADAAMAA='
    Sleep 600
    Delete "$DESKTOP\iMandro.lnk"
    ; 1.7.9 (auditoría I1): el acceso de «Iniciar con Windows» también
    ; se quita: si quedaba, apuntaba a un programa ya borrado y podía
    ; revivir solo al reinstalar en la misma carpeta.
    Delete "$SMSTARTUP\iMandro.lnk"
    RMDir /r "$SMPROGRAMS\iMandro"
    Delete "$INSTDIR\servidor.py"
    Delete "$INSTDIR\aplicacion.py"
    Delete "$INSTDIR\ventana.log"
    Delete "$INSTDIR\bandeja.log"
    ; 1.7.9 (auditoría I3): el registro del servidor (nació en la
    ; 1.7.7, después de esta lista) también se borra.
    Delete "$INSTDIR\servidor.log"
    Delete "$INSTDIR\bandeja.py"
    Delete "$INSTDIR\icono.ico"
    RMDir /r "$INSTDIR\static"
    RMDir /r "$INSTDIR\adb"
    RMDir /r "$INSTDIR\python"
    Delete "$INSTDIR\Desinstalar.exe"
    DeleteRegKey HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\iMandro"
    ; La configuracion (imandro-config.json) y los dispositivos
    ; (imandro-dispositivos.json) se quedan a proposito, con sus
    ; copias (.bak, .corrupta-*, pre-*): si reinstala, sus botones y
    ; sus emparejamientos vuelven.
    RMDir "$INSTDIR"
SectionEnd
