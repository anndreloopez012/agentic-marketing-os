# MATRIZ DE CONSISTENCIA Y ANCLAJE DE PERSONAJES (CHARACTER ANCHOR MATRIX)

Para que un personaje (humano, avatar 3D o mascota tecnológica) no cambie de apariencia a lo largo de un video de 30 o 60 segundos, se debe aplicar una **Ficha Técnica Inmutable de Rasgos (Character Anchor Sheet)**.

---

## 1. Regla de los 5 Anclajes Físicos Inmutables

Toda solicitud a Google Flow y Veo debe contener las siguientes 5 dimensiones fijas:

1. **Rostro y Cabeza**:
   * Ojos (color exacto, si tiene visor AR/HUD y en qué ojo específico se sitúa).
   * Orejas, pelaje o peinado.
2. **Vestimenta Superior**:
   * Tipo de prenda (sudadera, chaqueta técnica, camisa con cuello).
   * Color institucional primario y color de acentos (cordones, cremalleras).
3. **Prótesis, Dispositivos o Herramientas Biónicas**:
   * Guantes biónicos, placas de titanio en articulaciones, collar o medallas.
4. **Calzado y Tren Inferior**:
   * Tipo de calzado (zapatillas high-top, botas tácticas).
5. **Paleta Hexadecimal de Referencia**:
   * Definir los colores clave en el prompt (ej. `Solar Amber (#F59E0B)`, `Hyper Cyan (#00C4FF)`).

---

## 2. Protocolo de Enlace con Bancos Locales de Imágenes

Cuando se trabaje en entornos de agentes con acceso al sistema de archivos:
* **Start Keyframe**: Se indica siempre la ruta absoluta a la imagen real (ej. `./marca/mascotas/nombre/01_frontal.jpg`).
* **Character Anchor**: Se provee la imagen frontal completa oficial en plano entero (`01_frontal_full.jpg`).
* **Logotipos de Empresa**:
  > **IMPORTANTE**: Ningún generador de video por IA dibuja con 100% de precisión vectorial el imagotipo complejo de una empresa.
  > La regla técnica recomendada es: generar el personaje con el espacio despejado en la prenda o fondo, y en postproducción (o overlay de render) aplicar el PNG transparente maestro del logotipo oficial.

---

## 3. Ejemplo de Ficha de Anclaje de Personaje (mascotas ficticias de ejemplo)

### ZORRO CINÉTICO (mascota de ejemplo)
* **Especie / Estilo**: Zorro Fénec cibernético 3D estilo Pixar/DreamWorks.
* **Pelaje**: Solar Amber (`#F59E0B`) con pecho y mejillas en blanco ártico.
* **Visor**: HUD cibernético cian **exclusivamente sobre el ojo izquierdo** (el ojo derecho es orgánico ámbar).
* **Orejas**: Grandes orejas de fénec con trazas de circuitos internos pulsando en neón cian.
* **Accesorios**: Collar de titanio con medalla 'K', guantes y botas biónicas blancas con suela cian.

### LOBO ÁRTICO (mascota de ejemplo)
* **Especie / Estilo**: Lobo ártico cibernético 3D.
* **Pelaje**: Azul cielo y blanco puro con circuitos luminiscentes en mejillas y cola tupida.
* **Visor**: Visor rectangular AR dual cian que cubre **ambos ojos** proyectando telemetría.
* **Vestimenta**: Sudadera hoodie azul marino (`#0A0F1D`) con cordones verde esmeralda (`#10B981`).
* **Calzado**: Zapatillas high-top con luces cian reactivas.
