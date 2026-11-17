# iMandro Android — compilación y firma

- Paquete: `cu.estudioluna.imandro` · minSdk 24 / targetSdk 34.
- Toolchain: JDK 17 en `~/jdk/jdk-17.0.21+9`, SDK en `~/android-sdk` (build-tools 34.0.0, platform android-34).

## Firma (NO cambiar nunca)

- Keystore: `imandro.keystore` (en esta carpeta). Alias: `imandro`.
- Contraseña del almacén y de la clave: `CONTRASEÑA-OCULTA`.
- Certificado SHA-256: `b7e10b07f807d24789ca72a39b53c052d510a8a07ea44a22e94b8973aec80f3f` (CN=Liesky Vazquez, O=Estudio Luna).
- Todas las versiones se firman con este mismo keystore para que se instalen encima sin perder datos.

## Pipeline manual (sin Gradle)

Con `JAVA_HOME` exportado y `PATH=$JAVA_HOME/bin:$PATH`, `BT=~/android-sdk/build-tools/34.0.0`,
`AJ=~/android-sdk/platforms/android-34/android.jar`, desde esta carpeta:

1. `aapt2 compile --dir res -o build/res.zip`
2. `aapt2 link -o build/imandro-unsigned.apk -I $AJ --manifest AndroidManifest.xml -A assets --version-code N --version-name X.Y build/res.zip`
3. `javac -encoding UTF-8 -cp $AJ -d build/classes src/cu/estudioluna/imandro/MainActivity.java`
   (sin `-source 8 -target 8`)
4. `(cd build/classes && jar cf ../classes.jar .)` — d8 necesita un JAR, no la carpeta.
5. `d8 --output build/dex build/classes.jar` (la carpeta `build/dex` debe existir antes).
6. `(cd build/dex && zip ../imandro-unsigned.apk classes.dex)` — el dex entra en la raíz del APK.
7. `zipalign -f 4 build/imandro-unsigned.apk build/imandro-aligned.apk`
8. `apksigner sign --ks imandro.keystore --ks-key-alias imandro --ks-pass pass:******** --key-pass pass:******** --out ../entrega/iMandro-Android-vX.Y.apk build/imandro-aligned.apk`
9. Verificar: `apksigner verify --print-certs` (SHA-256 de arriba), `aapt2 dump badging` (versionCode/Name)
   y `unzip -l` (classes.dex y resources.arsc en la raíz, assets dentro).

Versiones: v1.0 vc1 · v1.1 vc2 · v1.2 vc3 · v1.3 vc4 · v1.3.1 vc5 · v1.4 vc6 · v1.4.1 vc7 · v1.5 vc8 · v1.7 vc12 · v1.7.1 vc13 · v1.7.2 vc14 · v1.7.3 vc15 · v1.7.4 vc16 · v1.7.5 vc17 · v1.7.6 vc18 · v1.7.7 vc19 · v1.7.8 vc20 · v1.7.9 vc21 · v1.7.10 vc22 · v1.8 vc23 · v1.9 vc24 · v1.9.1 vc25 · v1.9.2 vc26.
La versión visible dentro de la aplicación sale de `VERSION_APP` en `MainActivity.java` y del panel
(`assets/panel.html`, tarjeta Información): ambas deben coincidir con el nombre del archivo.
