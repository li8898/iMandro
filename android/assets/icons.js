// iMandro v1.0 · Biblioteca de iconos dibujados (sin emojis)
// Cada icono es el interior de un SVG de 24x24 con trazo.
const ICONOS = {
deshacer:'<path d="M9 14 4 9l5-5"/><path d="M4 9h10a6 6 0 0 1 0 12h-3"/>',
rehacer:'<path d="m15 14 5-5-5-5"/><path d="M20 9H10a6 6 0 0 0 0 12h3"/>',
curita:'<g transform="rotate(-45 12 12)"><rect x="3" y="9" width="18" height="7" rx="3.5"/><circle cx="9" cy="12.5" r=".8" fill="currentColor" stroke="none"/><circle cx="12" cy="12.5" r=".8" fill="currentColor" stroke="none"/><circle cx="15" cy="12.5" r=".8" fill="currentColor" stroke="none"/></g>',
tampon:'<path d="M12 3.2c1.6 0 2.9 1.3 2.9 2.9 0 1.7-.8 2.5-.8 3.9h1.2a2.7 2.7 0 0 1 2.7 2.7V14H6v-1.3A2.7 2.7 0 0 1 8.7 10h1.2c0-1.4-.8-2.2-.8-3.9C9.1 4.5 10.4 3.2 12 3.2Z"/><path d="M4.5 17.5h15M6 21h12"/>',
pincel:'<path d="m14.5 4.5 5 5L11 18H6v-5l8.5-8.5Z"/><path d="M6 18c-1.2.6-2 1.6-2.3 3 1.4-.3 2.4-1.1 3-2.3"/>',
gota:'<path d="M12 3.8s6.3 6.9 6.3 11A6.3 6.3 0 0 1 12 21a6.3 6.3 0 0 1-6.3-6.2c0-4.1 6.3-11 6.3-11Z"/><path d="M9.4 14.2a2.8 2.8 0 0 0 2 3.4"/>',
cara:'<circle cx="12" cy="12" r="8.6"/><circle cx="9.3" cy="10.2" r=".7" fill="currentColor" stroke="none"/><circle cx="14.7" cy="10.2" r=".7" fill="currentColor" stroke="none"/><path d="M8.2 14.2a5 5 0 0 0 7.6 0"/>',
ojo:'<path d="M2.8 12S6 5.8 12 5.8 21.2 12 21.2 12 18 18.2 12 18.2 2.8 12 2.8 12Z"/><circle cx="12" cy="12" r="3"/>',
brillos:'<path d="M12 4.5 13.6 10 19 12l-5.4 2L12 19.5 10.4 14 5 12l5.4-2L12 4.5Z"/><path d="M18.5 3.5v3M17 5h3"/>',
capas:'<path d="m12 3.8 8.8 5-8.8 5-8.8-5 8.8-5Z"/><path d="m4.8 13.4 7.2 4 7.2-4"/><path d="m4.8 17.2 7.2 4 7.2-4"/>',
mitad:'<circle cx="12" cy="12" r="8.6"/><path d="M12 3.4a8.6 8.6 0 0 1 0 17.2Z" fill="currentColor" stroke="none"/>',
recortar:'<path d="M6.5 3.8v13M3.8 6.5h13M17.5 20.2v-13M20.2 17.5h-13"/><rect x="6.5" y="6.5" width="11" height="11"/>',
guardar:'<path d="M6 4.5h9.5L19 8v11.5H6z"/><path d="M15.5 4.5V9H19"/><rect x="9" y="13" width="6" height="6.5"/>',
exportar:'<path d="M12 15V4"/><path d="m6.8 9.5L12 4.3l5.2 5.2"/><path d="M4.5 15.5v4h15v-4"/>',
camara:'<rect x="3" y="7.5" width="18" height="12" rx="2.5"/><circle cx="12" cy="13.5" r="3.6"/><path d="M8.5 7.5 10 4.8h4l1.5 2.7"/>',
curvas:'<path d="M4 19.5v-15"/><path d="M4 19.5h16"/><path d="M4.5 16.5C8 16.5 9 6 12.5 6S17 14 20 9.5"/>',
deslizadores:'<path d="M5 8h14M5 16h14"/><circle cx="9.5" cy="8" r="2.1" fill="#171f30"/><circle cx="14.5" cy="16" r="2.1" fill="#171f30"/>',
sol:'<circle cx="12" cy="12" r="4"/><path d="M12 3v2.4M12 18.6V21M3 12h2.4M18.6 12H21M5.6 5.6l1.7 1.7M16.7 16.7l1.7 1.7M18.4 5.6l-1.7 1.7M7.3 16.7l-1.7 1.7"/>',
paleta:'<circle cx="12" cy="12" r="8.6"/><circle cx="8.6" cy="9.6" r="1.25" fill="currentColor" stroke="none"/><circle cx="15" cy="8.4" r="1.25" fill="currentColor" stroke="none"/><circle cx="15.6" cy="14.6" r="1.25" fill="currentColor" stroke="none"/><circle cx="9.4" cy="15.8" r="1.25" fill="currentColor" stroke="none"/>',
varita:'<path d="M6 4.5 4.5 3M6 4.5 7.6 3.2M6 4.5v15"/><path d="M6 5.5c3-2 6 2 9 0v7c-3 2-6-2-9 0"/><path d="M17.5 15.5l.9 2.1 2.1.9-2.1.9-.9 2.1-.9-2.1-2.1-.9 2.1-.9.9-2.1Z"/>',
intercambiar:'<path d="M4.5 8.5h13M14 5l3.5 3.5L14 12M19.5 15.5h-13M10 12.5 6.5 16 10 19.5"/>',
mas:'<path d="M12 5v14M5 12h14"/>',
copiar:'<rect x="8.5" y="8.5" width="11" height="11" rx="2"/><path d="M15.5 8.5v-3a2 2 0 0 0-2-2h-7a2 2 0 0 0-2 2v7a2 2 0 0 0 2 2h2"/>',
papelera:'<path d="M4.5 6.5h15M9 6V4.5A1.5 1.5 0 0 1 10.5 3h3A1.5 1.5 0 0 1 15 4.5V6M6.5 6.5l1 13a2 2 0 0 0 2 1.8h5a2 2 0 0 0 2-1.8l1-13"/><path d="M10 10.5v6M14 10.5v6"/>',
mascara:'<rect x="4" y="5" width="16" height="14" rx="2"/><circle cx="12" cy="12" r="3.4"/><path d="M4 9.5h5.5M14.5 9.5H20M4 14.5h5.5M14.5 14.5H20"/>',
carpeta:'<path d="M3.5 8A2.5 2.5 0 0 1 6 5.5h3L11 8h9.5v11h-17V8Z"/><path d="M3.5 8v11h17V9.5H10L8 6.5"/>',
subir:'<path d="M12 19V6"/><path d="m6 11.5L12 5.5l6 6"/><path d="M5 3.5h14"/>',
bajar:'<path d="M12 5v13"/><path d="m6 12.5 6 6 6-6"/><path d="M5 20.5h14"/>',
lapiz:'<path d="m15.5 4.8 4.7 4.7L9 20.7H4.3V16L15.5 4.8Z"/><path d="m13.8 6.5 4.7 4.7"/>',
candado:'<rect x="5" y="10.5" width="14" height="9.5" rx="2"/><path d="M8 10.5V8a4 4 0 0 1 8 0v2.5"/><circle cx="12" cy="15.2" r="1.3" fill="currentColor" stroke="none"/>',
cubo:'<path d="M12 3.5 20 8v8l-8 4.5L4 16V8l8-4.5Z"/><path d="M4 8l8 4.5L20 8M12 12.5v8"/>',
texto:'<path d="M5 5.5V4h14v1.5M12 4v16M9 20h6"/>',
volumen:'<path d="M4.5 10.5v3H8l5.5 4.5v-12L8 10.5H4.5Z"/><path d="M16.5 9.5a4 4 0 0 1 0 5M18.8 7a7.5 7.5 0 0 1 0 10"/>',
play:'<path d="M8 5.5v13l11-6.5-11-6.5Z"/>',
pagina:'<rect x="4" y="4" width="7" height="7" rx="1.8"/><rect x="13" y="4" width="7" height="7" rx="1.8"/><rect x="4" y="13" width="7" height="7" rx="1.8"/><rect x="13" y="13" width="7" height="7" rx="1.8"/>',
teclado:'<rect x="3" y="6" width="18" height="12" rx="2"/><path d="M6.5 9.5h.01M10 9.5h.01M13.5 9.5h.01M17 9.5h.01M6.5 14.5h.01M17 14.5h.01M9 14.5h6"/>',
reloj:'<circle cx="12" cy="12" r="8.6"/><path d="M12 7.5V12l3 2"/>',
rayo:'<path d="M13 3.5 5.5 13.5H11L9.8 20.5 18 10h-5.5L13 3.5Z"/>',
engranaje:'<circle cx="12" cy="12" r="3.2"/><path d="M12 3.5v3M12 17.5v3M3.5 12h3M17.5 12h3M6 6l2.1 2.1M15.9 15.9 18 18M18 6l-2.1 2.1M8.1 15.9 6 18"/>',
wifi:'<path d="M3 10a13 13 0 0 1 18 0M6 13.5a8.5 8.5 0 0 1 12 0M8.8 17a4.5 4.5 0 0 1 6.4 0"/><circle cx="12" cy="19.5" r="1" fill="currentColor" stroke="none"/>',
corona:'<path d="M4 17.5 3 7l5.2 3.4L12 4l3.8 6.4L21 7l-1 10.5H4Z"/><path d="M4 20.5h16"/>',
corazon:'<path d="M12 20.5s-7.5-4.6-7.5-10A4.3 4.3 0 0 1 12 7.4a4.3 4.3 0 0 1 7.5 3.1c0 5.4-7.5 10-7.5 10Z"/>',
cohete:'<path d="M12 3.5c3 2.2 4.5 5.4 4.5 9L12 15l-4.5-2.5c0-3.6 1.5-6.8 4.5-9Z"/><circle cx="12" cy="9" r="1.8"/><path d="M7.5 13.5 5 19l3.5-1M16.5 13.5 19 19l-3.5-1"/>'
};
// Paquetes de iconos que trae la aplicación
const PAQUETES = {
  "Retoque": ["deshacer","rehacer","curita","tampon","pincel","gota","cara","ojo","brillos","mitad","recortar","guardar"],
  "Photoshop": ["camara","curvas","deslizadores","sol","paleta","varita","capas","mascara","intercambiar","copiar","texto","rayo"],
  "Sistema": ["carpeta","volumen","play","teclado","reloj","engranaje","wifi","candado","pagina","exportar","papelera","mas"],
  "Multimedia": ["play","volumen","camara","corona","corazon","cohete","sol","brillos"]
};
const NOMBRES_ICONO = {deshacer:"Deshacer",rehacer:"Rehacer",curita:"Quitar manchas",tampon:"Tampón",pincel:"Pincel",gota:"Licuar",cara:"Rostro",ojo:"Ojo",brillos:"Brillos",capas:"Capas",mitad:"Mitad",recortar:"Recortar",guardar:"Guardar",exportar:"Exportar",camara:"Cámara",curvas:"Curvas",deslizadores:"Ajustes",sol:"Sol",paleta:"Color",varita:"Varita",intercambiar:"Invertir",mas:"Más",copiar:"Copiar",papelera:"Papelera",mascara:"Máscara",carpeta:"Carpeta",subir:"Subir",bajar:"Bajar",lapiz:"Lápiz",candado:"Candado",cubo:"Cubo",texto:"Texto",volumen:"Volumen",play:"Reproducir",pagina:"Página",teclado:"Teclado",reloj:"Reloj",rayo:"Acción",engranaje:"Engranaje",wifi:"Wi-Fi",corona:"Corona",corazon:"Corazón",cohete:"Cohete"};
function svgIcono(id, color, fondo){
  // fondo: color de fondo para los puntos de "deslizadores"
  let inner = ICONOS[id] || ICONOS.pagina;
  if(fondo) inner = inner.replaceAll('#171f30', fondo);
  return '<svg viewBox="0 0 24 24" fill="none" stroke="' + color + '" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">' + inner + '</svg>';
}
