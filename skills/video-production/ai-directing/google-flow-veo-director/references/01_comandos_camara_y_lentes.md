# DICCIONARIO MAESTRO: COMANDOS DE CÁMARA Y LENTES CINEMATOGRÁFICAS

Esta guía técnica compila todas las directivas de cámara y óptica reconocidas por Google Veo y Google Flow Studio para garantizar control milimétrico sobre el movimiento, ángulo y profundidad de campo.

---

## 1. Movimientos Físicos y Mecánicos de Cámara

| Comando en Prompt | Vector y Dinámica | Intención Cinemática / Efecto Psicológico |
| :--- | :--- | :--- |
| `slow smooth dolly-in at [X] m/s` | Avance frontal sobre rieles hacia el sujeto | Focaliza la atención, incrementa la empatía, seriedad o tensión dramática. |
| `measured slow dolly-out revealing [entorno]` | Retroceso frontal sobre rieles alejándose | Revela la escala monumental del entorno (centro de datos, rascacielos, almacén). |
| `dramatic vertigo dolly-zoom (push in while zooming out)` | Dolly hacia adelante + zoom óptico opuesto | Efecto Vértigo (Hitchcock). El fondo se deforma y expande mientras el personaje mantiene su tamaño. Ideal para alertas de seguridad o sorpresas. |
| `steady horizontal pan from left to right` | Rotación horizontal en trípode | Escaneo ambiental guiado, lectura de tableros o seguimiento de un flujo de información. |
| `rapid whip-pan with natural motion blur` | Latigazo horizontal veloz con barrido | Transición enérgica entre dos puntos de interés o escenas sin corte brusco visible. |
| `vertical tilt-up from [base] to [cima]` | Inclinación vertical ascendente | Revelación de monumentalidad corporativa, nubes de servidores o visión hacia el futuro. |
| `deliberate tilt-down descending to [objeto]` | Inclinación vertical descendente | Focalización hacia un detalle operativo (pantalla táctil POS, teclado, terminal). |
| `lateral tracking truck shot parallel to subject` | Desplazamiento lateral coordinado | Dinamismo y avance constante; acompaña al personaje en su recorrido por la empresa. |
| `smooth mechanical pedestal rise` | Elevación vertical en línea recta | Ascenso solemne y elegante sin alterar el ángulo horizontal del encuadre. |
| `sweeping crane shot swooping down from ceiling` | Descenso arqueado de grúa | Establece una vista general del espacio y concluye en un plano medio del protagonista. |
| `graceful 180-degree (or 360-degree) orbital arc shot` | Giro circular continuo alrededor del sujeto | Tomas épicas de revelación de producto, liderazgo ejecutivo o mascota oficial. |
| `cinematic high-altitude drone shot gliding forward` | Vuelo de dron hacia adelante | Visión macroscópica de arquitectura, complejos industriales y despliegues masivos. |
| `top-down 90-degree bird's-eye view` | Plano cenital perpendicular exacto | Visualización esquemática, planos arquitectónicos y distribución espacial analítica. |
| `subtle floating handheld camera drift` | Respiración orgánica de Steadicam | Aporta realismo documental, presencia humana e inmersión sin sacudidas caóticas. |
| `locked-off static tripod shot with zero camera drift` | Inmovilidad absoluta de trípode | Claridad analítica para demostraciones técnicas de software, código y datos duros. |

---

## 2. Tipos de Plano y Encuadres (Framing Directives)

* **`Extreme Wide Shot (EWS)`**: Establece el universo narrativo. El sujeto ocupa menos del 5% del encuadre.
* **`Wide Shot (WS)` / `Full Shot (FS)`**: El personaje aparece de cuerpo entero con margen de respiro superior e inferior.
* **`Medium Shot (MS)`**: Encuadre desde la cintura hacia arriba. Permite ver gesticulación manual y el entorno inmediato.
* **`Medium Close-Up (MCU)`**: Desde el centro del pecho hasta la cabeza. **Es el plano estándar de oro para locución**, entrevistas corporativas y generación de confianza.
* **`Close-Up (CU)`**: Rostro o cabeza en primer plano. Ideal para capturar expresiones de convicción, guiños o concentración.
* **`Extreme Close-Up (ECU)` / `Macro Shot`**: Detalle hiperenfocado sobre un circuito, sensor biónico, ojo o código en pantalla.
* **`Over-The-Shoulder (OTS)`**: La cámara se ubica detrás del hombro del interlocutor. Indispensable para interacción con pantallas táctiles, clientes o copilotos.
* **`Low-Angle Hero Shot` (Contrapicado)**: Cámara situada a baja altura mirando hacia arriba. Otorga poder, liderazgo y solidez a la figura corporativa.
* **`High-Angle Analytic Shot` (Picado)**: Cámara elevada mirando hacia abajo. Otorga perspectiva de supervisión y control de procesos.
* **`Canted Dutch Angle (10-15 degrees)`**: Inclinación lateral del horizonte. Comunica fallo crítico, hackeo, cuello de botella o alerta técnica inminente.

---

## 3. Lentes, Óptica y Profundidad de Campo

* **`35mm Anamorphic Prime Lens`**:
  * *Efecto*: Bokeh ovalado característico de cine de Hollywood, ligera compresión de bordes y destellos (*lens flares*) horizontales controlados.
* **`50mm f/1.4 Prime Lens`**:
  * *Efecto*: La perspectiva más fiel a la visión humana. Excelente separación del sujeto con un fondo desenfocado suave y natural (*creamy bokeh*).
* **`85mm Portrait / Macro Lens`**:
  * *Efecto*: Compresión espacial hermosa, aislamiento absoluto del personaje y detalle microscópico en texturas de piel, pelaje o metales biónicos.
* **`24mm Wide-Angle Cinema Lens`**:
  * *Efecto*: Campo de visión amplio sin distorsión ojo de pez (*zero barrel distortion*). Excelente para tomas interiores en centros de datos u oficinas boutique.
* **`Deep Focus (Panavision f/11)`**:
  * *Efecto*: Nitidez simultánea en el primer plano, plano medio y el fondo lejano.
