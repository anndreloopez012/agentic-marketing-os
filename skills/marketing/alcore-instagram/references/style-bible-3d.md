# STYLE BIBLE 3D Y DIRECCION TECNICA CINEMATOGRAFICA (ALCORE)

Esta biblia de estilo define los parámetros de iluminación, cámaras, shaders, colorimetría y diseño sonoro para las producciones de video 3D y renderizado de imágenes de ALCORE en **Google Flow**, **Google Veo** y motores afines.

---

## 1. Filosofía Visual: Pixar / DreamWorks Corporate Cinematic

ALCORE no utiliza renders fotorrealistas crudos ni ilustraciones planas 2D. El lenguaje visual es de **largometraje animado 3D de alta gama**:
- Personajes expresivos con articulación física creíble.
- Texturas táctiles con micro-relieve visible (tejidos de traje, metal cepillado, escamas individuales, pelaje suave).
- Iluminación volumétrica de estudio que transmite rigor corporativo y calidez tecnológica.

---

## 2. Parámetros de Cámara y Óptica

| Tipo de Plano | Lente Focal Recomendada | Profundidad de Campo (DoF) | Uso Estratégico |
| :--- | :--- | :--- | :--- |
| **Plano Entero / Establecimiento** | 35mm Anamórfico | f/4.0 a f/5.6 (Enfoque amplio de escenario) | Inicios de video, salas de servidores, campus y domos |
| **Plano Medio (Waist Up)** | 50mm Esférico | f/2.8 (Separación sutil de fondo) | Explicaciones didácticas de Alki, Kivo con tabletas |
| **Primer Plano Facial (Close-up)** | 85mm Retrato | f/1.8 a f/2.0 (Bokeh cremoso en fondo) | Monóculo HUD de Kivo, ojos de Kivi, visor AR de Alki |
| **Ángulo de Obturación (Shutter)** | 180° estándar | Desenfoque de movimiento natural | Evita efecto estroboscópico en saltos y giros de cola |
| **Velocidad de Cuadro (FPS)** | 24fps (Cinemático) / 60fps (Kinético) | 24fps para narrativa; 60fps para clips express |

---

## 3. Esquema de Iluminación de Estudio (Rig de 3 Puntos + Neón)

Toda escena debe emular un montaje de iluminación profesional de estudio cinematográfico:

```
                  [Rim Light / Neón Cian-Violeta (Contraluz)]
                                       |
                                       v
                             [PERSONAJE / MASCOTA]
                                 ^           ^
                                /             \
   [Key Light / Softbox Cálido 45°]         [Fill Light / Azul Frío 45°]
```

1. **Key Light (Luz Principal)**: Softbox difuso a 45 grados frontales, temperatura de color 5200K (luz blanca neutra ligeramente cálida). Genera reflejo especular suave en ojos (catchlight).
2. **Fill Light (Luz de Relleno)**: Luz de relleno lateral a -45 grados, temperatura 6500K (azul frío sutil), ratio 1:3 respecto a la luz principal. Mantiene legibles las sombras sin negros empastados.
3. **Rim Light / Kicker (Contraluz)**: Foco de contorno trasero potente a 120 grados que perfila la silueta de la cabeza, capucha de Alki, orejas de Kivo o cresta de Kivi, separándola nítidamente del fondo.
4. **Institutional Ambient Glow**: Luces de acento volumétricas en `Hyper Cyan` (`#00C4FF`) para Kivo/Alki y `Neon Purple` (`#A855F7`) para Kivi, integradas en interfaces o servidores.

---

## 4. Especificaciones de Shaders y Materiales por Personaje

### ALKI (Lobo Ártico Cibernético / Academia Tech)
- **Especie y Pelaje**: Lobo ártico cibernético con pelaje azul cielo y blanco ártico suave (Hair BSDF / SSS al 14%).
- **Circuitos Tácticos**: Trazas luminiscentes integradas en el pelaje de patas, brazos, orejas y cola tupida en `Hyper Cyan` (`#00C4FF`).
- **Visor AR Dual**: Gafas / visor cibernético rectangular de realidad aumentada que cubre **AMBOS ojos** con micro-lecturas holográficas transparentes de telemetría.
- **Sudadera Institucional**: Sudadera con capucha (hoodie) azul marino oscuro (`#0A0F1D`) con cordones verde lima (`#10B981`) y logotipo de nube ALCORE en el pecho.
- **Calzado**: Zapatillas high-top oscuras con logotipo 'A' y suelas con iluminación cian reactiva.

### KIVO (Zorro Cinético / Centinela de Datos)
- **Especie y Pelaje**: Zorro fénec biónico con pelaje Ámbar Solar (`#F59E0B`), pecho blanco esponjoso y cola de zorro tupida con punta blanca (SSS al 18%).
- **Monóculo HUD Exclusivo**: Lente HUD holográfica cian únicamente sobre el **OJO IZQUIERDO** (ojo derecho completamente descubierto).
- **Orejas Hiper-desarrolladas**: Grandes orejas fénec con circuitos de datos cian impresos en la cara interna.
- **Collar y Botas**: Collar rígido de titanio con medalla circular 'K' luminiscente y botas biónicas blanco perla con ribetes cian.

### KIVI (Camaleón Tecnológico / 2 Diseños Canónicos)
Kivi cuenta con dos encarnaciones canónicas oficiales según el contexto editorial:

1. **Diseño 1: Toy Vinilo / Retail POS (Imágenes 01 a 10)**:
   - Textura: Vinilo mate suave de juguete de colección 3D (Pixar/DreamWorks), piel bicolor violeta oscuro y verde menta pastel.
   - Ojos: Globos oculares esféricos independientes 360 grados sin monturas mecánicas.
   - Accesorios: Tableta táctil de punto de venta Kinvo Express con sello 'K'.
   - Cola: Estructura prensil lisa en espiral continua que dibuja la letra 'K'.
   - Uso: Demostraciones comerciales de mostrador, cobro express y facturación SAT FEL.

2. **Diseño 2: Cyber Mecha Biónico / DevOps & Cloud (Imágenes 11 a 20)**:
   - Textura: Placas articuladas de blindaje violeta y cian tornasolado, peto y abdomen de placas curvas de titanio cepillado con costuras horizontales y remaches sutiles (armadura sólida y cerrada, sin cables ni vientre expuesto).
   - Juntas y Brazos: Juntas esféricas de titanio, codos y muñecas mecánicas expuestas, dedos robóticos articulados.
   - Espina y Cola: Espina dorsal con circuitos luminosos y cola mecánica segmentada unida permanentemente a la columna con tubo de neón púrpura (`#A855F7`) en forma de 'K' estilizada integrada rígidamente dentro del lazo (nunca rueda suelta ni separada).
   - Referencia Canónica Maestra: `11_kivi_presenting_chart.jpg`.
   - Uso: Memes de programación, cultura DevOps, arquitectura cloud, alertas de sistemas y métricas complejas.

---

## 5. Diseño Acústico y Dirección de Locución

- **Perfil de Frecuencia**: Ecualización broadcast profesional (corte limpio en sub-graves <80Hz, realce sutil de presencia en 3.5kHz y brillo en 12kHz).
- **Acústica**: Habitación tratada acústicamente, sin eco, con calidez de micrófono condensador de gran diafragma.
- **Cadencia de Locución**: 130 a 140 palabras por minuto. Cada bloque de 10 segundos admite exactamente entre 20 y 25 palabras con pausas respiratorias de 0.5 segundos al inicio y final del bloque.
