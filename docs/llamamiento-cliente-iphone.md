# Se busca colaborador: cliente de iMandro para iPhone

_Este llamamiento está preparado para publicarse como «issue» destacado el día en que el repositorio se haga público._

## Español

iMandro convierte un teléfono o tableta Android en un panel de control tipo Stream Deck para una PC con Windows, pensado ante todo para Adobe Photoshop. El servidor (la PC) y el panel ya existen y funcionan; falta una pieza: **un cliente para iPhone**.

**En qué consiste el trabajo**

- El panel de iMandro ya es una página web: el cliente de Android es una cáscara WebView que la carga y le añade la conexión. El cliente de iPhone sería el equivalente en iOS: una aplicación en Swift que envuelva el mismo panel y hable con el servidor de la PC por la red local (el protocolo está implementado en `pc/servidor.py` y en el cliente Android, que sirven de referencia).
- La conexión en iPhone sería **solo por Wi-Fi**: iOS no permite el Bluetooth clásico ni el USB que usa Android.
- Todo el código nuevo se publica bajo la misma licencia del proyecto, **GPLv3**.

**Qué hace falta**

- Una Mac con Xcode y conocimientos de Swift.
- Para distribuir la aplicación hará falta una cuenta del Apple Developer Program; ese paso se coordina con el autor del proyecto.

Si te interesa, abre un comentario en este issue contando tu experiencia con iOS. ¡Gracias!

## English

iMandro turns an Android phone or tablet into a Stream Deck-style control panel for a Windows PC, designed above all for Adobe Photoshop. The server (the PC) and the panel already exist and work; one piece is missing: **an iPhone client**.

**What the work involves**

- The iMandro panel is already a web page: the Android client is a WebView shell that loads it and adds the connection. The iPhone client would be the iOS equivalent: a Swift app that wraps the same panel and talks to the PC server over the local network (the protocol is implemented in `pc/servidor.py` and in the Android client, which serve as reference).
- On iPhone the connection would be **Wi-Fi only**: iOS does not allow the classic Bluetooth or the USB link used on Android.
- All new code is published under the project's license, **GPLv3**.

**What you need**

- A Mac with Xcode and Swift skills.
- Distributing the app will require an Apple Developer Program account; that step will be coordinated with the project author.

If you are interested, leave a comment on this issue telling us about your iOS experience. Thank you!
