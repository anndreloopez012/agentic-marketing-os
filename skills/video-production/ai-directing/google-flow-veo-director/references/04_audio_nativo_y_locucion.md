# AUDIO NATIVO Y CALIBRACIÓN DE LOCUCIÓN

Las versiones avanzadas de **Google Veo** integran capacidades de generación nativa de audio (efectos de sonido foley, ambientes y tonalidades musicales). Al mismo tiempo, en producciones de video corporativo largo para redes sociales, el guion de locución en off (*voiceover*) debe coincidir exactamente con los cortes de video para que no sobre ni falte tiempo.

---

## 1. La Matemática de la Locución Corporativa

El ritmo estándar de locución corporativa profesional en español para negocios e ingeniería es de **135 palabras por minuto (PPM)**. Este ritmo garantiza dicción nítida, peso institucional y suficiente espacio para pausas de énfasis sin atropello verbal.

$$\text{Velocidad} = \frac{135 \text{ palabras}}{60 \text{ segundos}} = 2.25 \text{ palabras por segundo}$$

### Tabla de Calibración de Palabras según Duración:

| Duración del Bloque | Palabras Ideales (Español a 135 PPM) | Palabras Ideales (Inglés a 150 PPM) | Margen de Tolerancia |
| :--- | :--- | :--- | :--- |
| **5 Segundos** | 10 a 12 palabras | 12 a 14 palabras | $\pm 1$ palabra |
| **8 Segundos** | 17 a 19 palabras | 19 a 22 palabras | $\pm 1$ palabra |
| **10 Segundos (Flow)** | **22 a 25 palabras** | **25 a 28 palabras** | **21 mín — 26 máx** |
| **20 Segundos** | 44 a 50 palabras | 50 a 56 palabras | $\pm 2$ palabras |
| **30 Segundos** | 66 a 75 palabras | 75 a 84 palabras | $\pm 3$ palabras |
| **60 Segundos** | 132 a 150 palabras | 150 a 168 palabras | $\pm 5$ palabras |

### Consecuencias de Errores de Conteo:
* **Menos de 20 palabras en 10s**: Provoca silencios muertos incómodos donde el video sigue corriendo sin que nadie hable.
* **Más de 26 palabras en 10s**: Obliga al locutor a hablar apresuradamente, perdiendo la seriedad ejecutiva y saturando cognitivamente al espectador.

---

## 2. Directivas de Audio Nativo en Google Veo

En Google Veo 3 y 3.1, puedes incrustar directivas de audio dentro del prompt en inglés usando la cláusula `Native audio: [descripción]`:

```text
Native audio: crisp professional studio room tone, subtle mechanical clicks from keyboard, warm sub-bass synthesizer pad, zero vocal distortion.
```

### Catálogo de Entornos Sonoros Corporativos:
* **Entorno Cloud / Datacenter**:
  * `Native audio: low-frequency server fan hum in deep background, smooth robotic servo whirrs, crisp holographic chime on data load.`
* **Entorno FinTech / Retail / POS**:
  * `Native audio: lively modern boutique acoustic ambiance, crisp red laser barcode scanner beep, pleasant electronic confirmation chime.`
* **Entorno Ciberseguridad / Sala de Crisis**:
  * `Native audio: tense subtle bass drone, crisp tactile mechanical switch clicks, rhythmic electronic pinging, dry focused room acoustics.`
* **Entorno Sala de Juntas / Corporativo**:
  * `Native audio: spacious modern executive conference room acoustics, muted distant city murmur through thick glass, confident vocal cadence.`
