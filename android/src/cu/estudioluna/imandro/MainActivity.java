package cu.estudioluna.imandro;

import android.Manifest;
import android.app.Activity;
import android.bluetooth.BluetoothAdapter;
import android.bluetooth.BluetoothDevice;
import android.bluetooth.BluetoothSocket;
import android.content.Context;
import android.content.SharedPreferences;
import android.content.pm.PackageManager;
import android.os.Build;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.os.VibrationEffect;
import android.os.Vibrator;
import android.view.WindowManager;
import android.webkit.JavascriptInterface;
import android.webkit.WebResourceRequest;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;

import org.json.JSONArray;
import org.json.JSONObject;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.lang.reflect.Method;
import java.net.DatagramPacket;
import java.net.DatagramSocket;
import java.net.InetAddress;
import java.nio.charset.StandardCharsets;
import java.security.KeyStore;
import java.util.Map;
import java.util.Set;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;

import javax.crypto.Cipher;
import javax.crypto.KeyGenerator;
import javax.crypto.SecretKey;
import javax.crypto.spec.GCMParameterSpec;

import android.security.keystore.KeyGenParameterSpec;
import android.security.keystore.KeyProperties;
import android.util.Base64;

/** iMandro v1.7.10 — Panel para Android. Creador: Liesky Vázquez.
 *  Muestra el panel (HTML en assets), descubre la PC por la red local,
 *  mantiene la pantalla encendida si así está marcado, vibra al tocar
 *  y puede hablar con la PC también por Bluetooth clásico (SPP).
 *
 *  1.7.9 (auditoría de la 1.7.8; por fuera, nada cambia):
 *  - Descubrimiento: la IP de la PC es la de ORIGEN del paquete, no la
 *    que el anuncio escribe (E1); los dos sockets UDP viven en campos
 *    y se cierran en onDestroy (D3).
 *  - WebView: la vista solo puede navegar dentro del panel
 *    empaquetado (file:///android_asset/) y el acceso a content://
 *    queda apagado (D1).
 *  - Bluetooth: las líneas que llegan tienen un tope generoso de
 *    8 MB (D4), igual que en el servidor. */
public class MainActivity extends Activity {
    public static final String VERSION_APP = "1.9.2";
    public static final String CREADOR = "Liesky Vázquez";
    private static final int PUERTO_AVISO = 8933;    // la PC anuncia aquí
    private static final int PUERTO_BUSCAR = 8932;  // aquí se le pregunta
    private static final UUID UUID_SPP = UUID.fromString("00001101-0000-1000-8000-00805F9B34FB");
    private static final int CANAL_BT = 5;           // el mismo canal que escucha la PC

    private WebView web;
    private SharedPreferences prefs;
    private final Map<String, JSONObject> pcs = new ConcurrentHashMap<>();
    private final Handler ui = new Handler(Looper.getMainLooper());
    private volatile boolean vivo = true;
    // Descubrimiento UDP (1.7.9, D3): los sockets viven en campos para
    // poder cerrarlos en onDestroy; antes eran variables locales que
    // nadie cerraba y su hilo quedaba bloqueado en receive().
    private DatagramSocket sockAvisos;
    private DatagramSocket sockBuscar;

    // ---- Bluetooth
    private BluetoothSocket btSocket;
    private OutputStream btOut;
    private volatile String btEstado = "no";   // no | conectando | conectado | error:...

    /** Puente general: descubrimiento, vibración y pantalla encendida. */
    public class Puente {
        @JavascriptInterface
        public String buscar() {
            JSONArray arr = new JSONArray();
            for (JSONObject p : pcs.values()) arr.put(p);
            return arr.toString();
        }

        @JavascriptInterface
        public void vibrar(int ms) {
            try {
                Vibrator v = (Vibrator) getSystemService(Context.VIBRATOR_SERVICE);
                if (v == null) return;
                if (Build.VERSION.SDK_INT >= 26) {
                    v.vibrate(VibrationEffect.createOneShot(ms, VibrationEffect.DEFAULT_AMPLITUDE));
                } else {
                    v.vibrate(ms);
                }
            } catch (Exception ignored) {}
        }

        @JavascriptInterface
        public void pantallaSiempre(boolean on) {
            prefs.edit().putBoolean("siempre", on).apply();
            ui.post(() -> aplicarPantalla());
        }

        /** Nombre de este equipo, para enseñarlo en la PC al emparejar (1.7). */
        @JavascriptInterface
        public String nombreEquipo() {
            try {
                String n = android.provider.Settings.Global.getString(
                        getContentResolver(), "device_name");
                if (n != null && !n.trim().isEmpty()) return n.trim();
            } catch (Exception ignored) {}
            String m = Build.MODEL == null ? "" : Build.MODEL.trim();
            return m.isEmpty() ? "Teléfono Android" : m;
        }

        // ---- Tokens cifrados (1.9.2, punto 3 de la revisión) ----
        // El token de emparejamiento de cada PC se guarda cifrado con
        // AES-GCM y una llave que vive en el Android Keystore de este
        // teléfono (solo APIs de plataforma; minSdk 24 las trae). El
        // valor guardado es «v1:» + Base64([nº de bytes del IV][IV]
        // [cifrado]). Los tokens de versiones anteriores iban en
        // claro: al leerlos se devuelven tal cual y se re-guardan
        // cifrados (migración transparente, sin reemparejar). Si algo
        // del cifrado fallara, la aplicación NO se cierra: leer
        // devuelve «» y el panel pedirá emparejar de nuevo.
        private static final String PREFIJO_CIFRADO = "v1:";
        private static final String ALIAS_LLAVE = "imandro_tokens";

        private SecretKey llaveTokens() throws Exception {
            KeyStore ks = KeyStore.getInstance("AndroidKeyStore");
            ks.load(null);
            KeyStore.Entry entrada = ks.getEntry(ALIAS_LLAVE, null);
            if (entrada instanceof KeyStore.SecretKeyEntry) {
                return ((KeyStore.SecretKeyEntry) entrada).getSecretKey();
            }
            KeyGenerator g = KeyGenerator.getInstance(
                    KeyProperties.KEY_ALGORITHM_AES, "AndroidKeyStore");
            g.init(new KeyGenParameterSpec.Builder(ALIAS_LLAVE,
                    KeyProperties.PURPOSE_ENCRYPT | KeyProperties.PURPOSE_DECRYPT)
                    .setBlockModes(KeyProperties.BLOCK_MODE_GCM)
                    .setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_NONE)
                    .build());
            return g.generateKey();
        }

        private String cifrarToken(String token) {
            try {
                Cipher c = Cipher.getInstance("AES/GCM/NoPadding");
                c.init(Cipher.ENCRYPT_MODE, llaveTokens());
                byte[] iv = c.getIV();
                byte[] cifrado = c.doFinal(token.getBytes(StandardCharsets.UTF_8));
                byte[] todo = new byte[1 + iv.length + cifrado.length];
                todo[0] = (byte) iv.length;
                System.arraycopy(iv, 0, todo, 1, iv.length);
                System.arraycopy(cifrado, 0, todo, 1 + iv.length, cifrado.length);
                return PREFIJO_CIFRADO + Base64.encodeToString(todo, Base64.NO_WRAP);
            } catch (Exception e) {
                return null;
            }
        }

        private String descifrarToken(String guardado) {
            try {
                byte[] todo = Base64.decode(
                        guardado.substring(PREFIJO_CIFRADO.length()), Base64.NO_WRAP);
                if (todo.length < 2) return "";
                int nIv = todo[0] & 0xFF;
                if (nIv <= 0 || todo.length <= 1 + nIv) return "";
                byte[] iv = new byte[nIv];
                System.arraycopy(todo, 1, iv, 0, nIv);
                Cipher c = Cipher.getInstance("AES/GCM/NoPadding");
                c.init(Cipher.DECRYPT_MODE, llaveTokens(), new GCMParameterSpec(128, iv));
                byte[] plano = c.doFinal(todo, 1 + nIv, todo.length - 1 - nIv);
                return new String(plano, StandardCharsets.UTF_8);
            } catch (Exception e) {
                return "";
            }
        }

        /** Guarda el token de emparejamiento de una PC (1.7), cifrado
         *  desde la 1.9.2. Vive en las mismas SharedPreferences que el
         *  resto de ajustes de la app, para que no se pierda si se
         *  limpia la caché del WebView. */
        @JavascriptInterface
        public void guardarToken(String base, String token) {
            if (base == null) return;
            try {
                if (token == null || token.isEmpty()) {
                    prefs.edit().remove("token:" + base).apply();
                } else {
                    String cifrado = cifrarToken(token);
                    if (cifrado != null) {
                        prefs.edit().putString("token:" + base, cifrado).apply();
                    }
                }
            } catch (Exception ignored) {}
        }

        @JavascriptInterface
        public String leerToken(String base) {
            if (base == null) return "";
            try {
                String t = prefs.getString("token:" + base, "");
                if (t == null || t.isEmpty()) return "";
                if (t.startsWith(PREFIJO_CIFRADO)) {
                    String plano = descifrarToken(t);
                    if (plano.isEmpty()) {
                        // Cifrado ilegible (la llave se regeneró, el
                        // dato vino de otro teléfono…): se borra y el
                        // panel pedirá emparejar de nuevo.
                        prefs.edit().remove("token:" + base).apply();
                    }
                    return plano;
                }
                // Token en claro de una versión anterior: vale igual
                // (el emparejamiento no se rompe) y se re-guarda
                // cifrado en este mismo momento.
                guardarToken(base, t);
                return t;
            } catch (Exception e) {
                return "";
            }
        }
    }

    /** Puente Bluetooth: aparatos emparejados, conexión y peticiones. */
    public class PuenteBT {
        @JavascriptInterface
        public String disponibles() {
            BluetoothAdapter ad = BluetoothAdapter.getDefaultAdapter();
            if (ad == null) return "{\"error\":\"Este equipo no tiene Bluetooth.\"}";
            if (!ad.isEnabled()) return "{\"error\":\"Enciende el Bluetooth del teléfono y vuelve a buscar.\"}";
            if (Build.VERSION.SDK_INT >= 31
                    && checkSelfPermission(Manifest.permission.BLUETOOTH_CONNECT) != PackageManager.PERMISSION_GRANTED) {
                requestPermissions(new String[]{Manifest.permission.BLUETOOTH_CONNECT}, 7);
                return "{\"error\":\"Acepta el permiso de Bluetooth y vuelve a buscar.\"}";
            }
            try {
                JSONArray arr = new JSONArray();
                Set<BluetoothDevice> emparejados = ad.getBondedDevices();
                if (emparejados != null) {
                    for (BluetoothDevice d : emparejados) {
                        JSONObject o = new JSONObject();
                        o.put("name", d.getName() == null ? "Sin nombre" : d.getName());
                        o.put("mac", d.getAddress());
                        arr.put(o);
                    }
                }
                return arr.toString();
            } catch (Exception e) {
                return "{\"error\":\"Falta el permiso de Bluetooth.\"}";
            }
        }

        @JavascriptInterface
        public void conectar(String mac) {
            new Thread(() -> conectarBT(mac), "imandro-bt").start();
        }

        @JavascriptInterface
        public String estado() {
            return btEstado;
        }

        @JavascriptInterface
        public void peticion(String json, int id) {
            new Thread(() -> {
                try {
                    OutputStream out = btOut;
                    if (out == null) throw new IllegalStateException("sin conexión");
                    synchronized (out) {
                        out.write((json + "\n").getBytes("UTF-8"));
                        out.flush();
                    }
                } catch (Exception e) {
                    btEstado = "error:Se cortó la conexión Bluetooth.";
                }
            }, "imandro-bt-tx").start();
        }

        @JavascriptInterface
        public void desconectar() {
            cerrarBT();
            btEstado = "no";
        }
    }

    private void aplicarPantalla() {
        boolean on = prefs.getBoolean("siempre", true);
        if (on) {
            getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
        } else {
            getWindow().clearFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
        }
    }

    private void conectarBT(String mac) {
        BluetoothAdapter ad = BluetoothAdapter.getDefaultAdapter();
        if (ad == null) { btEstado = "error:Este equipo no tiene Bluetooth."; return; }
        if (!ad.isEnabled()) { btEstado = "error:Enciende el Bluetooth del teléfono."; return; }
        if (Build.VERSION.SDK_INT >= 31
                && checkSelfPermission(Manifest.permission.BLUETOOTH_CONNECT) != PackageManager.PERMISSION_GRANTED) {
            requestPermissions(new String[]{Manifest.permission.BLUETOOTH_CONNECT}, 7);
            btEstado = "error:Acepta el permiso de Bluetooth y vuelve a intentarlo.";
            return;
        }
        btEstado = "conectando";
        cerrarBT();
        try {
            BluetoothDevice dev = ad.getRemoteDevice(mac);
            BluetoothSocket sock = null;
            try {
                sock = dev.createRfcommSocketToServiceRecord(UUID_SPP);
                sock.connect();
            } catch (Exception e1) {
                // Sin registro SPP en la PC: conexión directa al canal, como hacen
                // las aplicaciones de puerto serie clásicas.
                try { if (sock != null) sock.close(); } catch (Exception ignored) {}
                Method m = dev.getClass().getMethod("createRfcommSocket", int.class);
                sock = (BluetoothSocket) m.invoke(dev, CANAL_BT);
                sock.connect();
            }
            btSocket = sock;
            btOut = sock.getOutputStream();
            btEstado = "conectado";
            escucharBT(sock);
        } catch (Exception e) {
            btEstado = "error:No se pudo conectar por Bluetooth. Revisa que la PC tenga Bluetooth y esté emparejada.";
            cerrarBT();
        }
    }

    // Tope de línea Bluetooth (1.7.9, D4): 8 MB, el triple de la
    // configuración más pesada conocida (la que viaja por este canal
    // con muchos iconos propios). Espejo del tope del servidor.
    private static final int TOPE_LINEA_BT = 8 * 1024 * 1024;

    /** Lee una línea con tope y devuelve su texto (sin el salto), o
     *  null si la conexión se cortó. Una línea que pasa del tope se
     *  descarta entera — se sigue leyendo hasta su salto y se entrega
     *  una línea vacía, que el panel descarta como mensaje malformado,
     *  camino que ya tiene — y la escucha sigue. Antes se leía con
     *  readLine() sin límite: un par que mandara datos sin saltos de
     *  línea hacía crecer la memoria sin fin. */
    private String leerLineaBT(BufferedReader lector) throws Exception {
        StringBuilder sb = new StringBuilder();
        boolean desbordada = false;
        int c;
        while ((c = lector.read()) != -1) {
            if (c == '\n') {
                if (desbordada) return "";
                int n = sb.length();
                if (n > 0 && sb.charAt(n - 1) == '\r') sb.setLength(n - 1);
                return sb.toString();
            }
            if (!desbordada) {
                sb.append((char) c);
                if (sb.length() > TOPE_LINEA_BT) {
                    desbordada = true;
                    sb.setLength(0);
                }
            }
        }
        if (desbordada) return "";
        return sb.length() > 0 ? sb.toString() : null;
    }

    private void escucharBT(BluetoothSocket sock) {
        new Thread(() -> {
            try {
                BufferedReader lector = new BufferedReader(
                        new InputStreamReader(sock.getInputStream(), "UTF-8"));
                String linea;
                while (vivo && (linea = leerLineaBT(lector)) != null) {
                    final String js = "window.__btRespuesta && window.__btRespuesta("
                            + JSONObject.quote(linea) + ")";
                    ui.post(() -> { if (web != null) web.evaluateJavascript(js, null); });
                }
            } catch (Exception ignored) {}
            if ("conectado".equals(btEstado)) btEstado = "error:Se cortó la conexión Bluetooth.";
        }, "imandro-bt-rx").start();
    }

    private void cerrarBT() {
        try { if (btOut != null) btOut.close(); } catch (Exception ignored) {}
        try { if (btSocket != null) btSocket.close(); } catch (Exception ignored) {}
        btOut = null; btSocket = null;
    }

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        prefs = getSharedPreferences("imandro", MODE_PRIVATE);
        aplicarPantalla();
        web = new WebView(this);
        WebSettings s = web.getSettings();
        s.setJavaScriptEnabled(true);
        s.setDomStorageEnabled(true);
        s.setAllowFileAccess(true);
        s.setAllowUniversalAccessFromFileURLs(true);
        // Nadie usa content:// dentro del panel (1.7.9, D1).
        s.setAllowContentAccess(false);
        s.setMediaPlaybackRequiresUserGesture(false);
        // 1.7.9 (auditoría D1): la vista solo puede navegar dentro del
        // panel empaquetado (file:///android_asset/). Cualquier otra
        // navegación — un enlace, una redirección, un contenido remoto
        // que llegara alguna vez a la vista — se bloquea: con los
        // puentes AndroPC/AndroBT montados (que guardan y leen los
        // tokens de emparejamiento), ningún contenido ajeno debe poder
        // vivir en esta vista. El panel nunca navega: habla con la PC
        // por fetch, que no es navegación y no se toca.
        web.setWebViewClient(new WebViewClient() {
            private boolean fueraDelPanel(String url) {
                return url == null || !url.startsWith("file:///android_asset/");
            }
            @Override
            public boolean shouldOverrideUrlLoading(WebView vista, WebResourceRequest pet) {
                return fueraDelPanel(pet.getUrl() == null ? null : pet.getUrl().toString());
            }
            @Override
            @SuppressWarnings("deprecation")
            public boolean shouldOverrideUrlLoading(WebView vista, String url) {
                return fueraDelPanel(url);
            }
        });
        web.addJavascriptInterface(new Puente(), "AndroPC");
        web.addJavascriptInterface(new PuenteBT(), "AndroBT");
        setContentView(web);
        web.loadUrl("file:///android_asset/panel.html");
        new Thread(this::escucharAvisos, "imandro-avisos").start();
        new Thread(this::preguntar, "imandro-buscar").start();
    }

    /** El botón Atrás vuelve a la primera página del panel; si ya está ahí, sale. */
    @Override
    public void onBackPressed() {
        if (web == null) { super.onBackPressed(); return; }
        web.evaluateJavascript(
            "(function(){try{return (window.__paginaActual && window.__primeraPagina"
            + " && window.__paginaActual!==window.__primeraPagina)"
            + " ? (window.__irPagina(window.__primeraPagina),'si') : 'no';}"
            + "catch(e){return 'no';}})()",
            value -> {
                if (!"\"si\"".equals(value)) MainActivity.super.onBackPressed();
            });
    }

    /** Escucha los anuncios de la PC: "IMANDRO_PC <ip> <puerto> <nombre>".
     *  Desde la 1.7.9 (auditoría E1) la IP que vale es la de ORIGEN del
     *  paquete (pkt.getAddress()), no la escrita dentro del anuncio:
     *  cualquiera en la red puede anunciar el nombre que quiera, pero el
     *  tráfico ya no se puede redirigir a una máquina que no sea la que
     *  anuncia de verdad. Del mensaje se conservan nombre y puerto; el
     *  formato "IMANDRO_PC …" no cambia y la PC no se toca. */
    private void escucharAvisos() {
        DatagramSocket sock;
        try {
            sock = new DatagramSocket(PUERTO_AVISO);
            sock.setBroadcast(true);
            sockAvisos = sock;
        } catch (Exception e) {
            // sin red o puerto ocupado: el panel permite escribir la IP a mano
            return;
        }
        byte[] buf = new byte[512];
        while (vivo) {
            // El try va POR PAQUETE (1.7): un datagrama mal formado (puerto que
            // no es un número, texto cortado, JSON que falla) se descarta y la
            // escucha sigue viva. Antes el try envolvía todo el bucle y un solo
            // paquete malo mataba el hilo de descubrimiento hasta reiniciar
            // la app. El paquete se crea dentro del bucle para que su longitud
            // no quede recortada por el datagrama anterior.
            try {
                DatagramPacket pkt = new DatagramPacket(buf, buf.length);
                sock.receive(pkt);
                String msg = new String(pkt.getData(), 0, pkt.getLength(), "UTF-8").trim();
                if (msg.startsWith("IMANDRO_PC ")) {
                    String[] partes = msg.split(" ", 4);
                    if (partes.length >= 4) {
                        // La IP de origen manda; la del texto solo es la
                        // reserva si el paquete no trajera dirección.
                        String ip = pkt.getAddress() != null
                                ? pkt.getAddress().getHostAddress() : partes[1];
                        int puerto = Integer.parseInt(partes[2]);
                        String nombre = partes[3];
                        JSONObject p = new JSONObject();
                        p.put("ip", ip); p.put("port", puerto); p.put("name", nombre);
                        pcs.put(ip, p);
                        final String js = "window.__pcEncontrada && window.__pcEncontrada("
                                + JSONObject.quote(ip) + "," + puerto + "," + JSONObject.quote(nombre) + ")";
                        ui.post(() -> { if (web != null) web.evaluateJavascript(js, null); });
                    }
                }
            } catch (Exception e) {
                // paquete descartado: la escucha continúa con el siguiente
            }
        }
        try { sock.close(); } catch (Exception ignored) {}
    }

    /** Respuesta del sistema a los permisos pedidos en tiempo de ejecución.
     *  Hoy solo se pide BLUETOOTH_CONNECT (código 7, desde disponibles() y
     *  conectarBT()). Se avisa al panel: si se aceptó, su lista de aparatos
     *  se refresca sola sin volver a tocar «Buscar»; si se denegó, el panel
     *  enseña el aviso y la app no se cierra. */
    @Override
    public void onRequestPermissionsResult(int requestCode, String[] permissions, int[] grantResults) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);
        if (requestCode == 7) {
            boolean concedido = grantResults.length > 0
                    && grantResults[0] == PackageManager.PERMISSION_GRANTED;
            final String js = "window.__permisoBT && window.__permisoBT(" + concedido + ")";
            ui.post(() -> { if (web != null) web.evaluateJavascript(js, null); });
        }
    }

    /** Pregunta periódicamente si hay una PC con iMandro en la red. */
    private void preguntar() {
        try {
            DatagramSocket sock = new DatagramSocket();
            sock.setBroadcast(true);
            sockBuscar = sock;
            byte[] datos = "IMANDRO_BUSCA".getBytes("UTF-8");
            InetAddress destino = InetAddress.getByName("255.255.255.255");
            while (vivo) {
                try { sock.send(new DatagramPacket(datos, datos.length, destino, PUERTO_BUSCAR)); }
                catch (Exception ignored) {}
                Thread.sleep(4000);
            }
            try { sock.close(); } catch (Exception ignored) {}
        } catch (Exception e) {
            // la escucha de anuncios sigue funcionando por su cuenta
        }
    }

    @Override
    protected void onDestroy() {
        vivo = false;
        // 1.7.9 (auditoría D3): los dos sockets UDP del descubrimiento
        // se cierran aquí. Cerrar el de avisos despierta su receive()
        // bloqueado (la excepción ya está tragada paquete a paquete) y
        // su hilo termina; antes los dos quedaban abiertos con la
        // actividad ya destruida.
        try { if (sockAvisos != null) sockAvisos.close(); } catch (Exception ignored) {}
        try { if (sockBuscar != null) sockBuscar.close(); } catch (Exception ignored) {}
        cerrarBT();
        if (web != null) { web.destroy(); web = null; }
        super.onDestroy();
    }
}
