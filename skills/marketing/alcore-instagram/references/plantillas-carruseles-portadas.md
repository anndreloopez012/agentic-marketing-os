# GUIA DE DISEÑO: CARRUSELES (4:5) Y PORTADAS DESTACABLES (ALCORE INSTAGRAM)

Esta guía define la estructura de maquetación para carruseles de Instagram (1080x1350 px, proporción 4:5 vertical) y las directrices para que cada columna mantenga su identidad visual única a través de su mascota anfitriona.

---

## 1. Por qué la Portada Destacable es Mandatoria

En la vista de cuadrícula de Instagram, las publicaciones se visualizan como recortes cuadrados (1:1), mientras que en el feed principal se despliegan en 4:5 vertical.
Para que el perfil de `@alcore.gt` funcione como un sistema de 3 columnas verticales coherente:
- Cada portada debe situar a su mascota titular en el centro o tercio superior/medio.
- Ninguna portada de la Columna 1 puede omitir a Kivo.
- Ninguna portada de la Columna 2 puede omitir a Alki.
- Ninguna portada de la Columna 3 puede omitir a Kivi.
- Los fondos y colores de acento de la portada deben respetar la paleta oficial de la columna.

---

## 2. Plantilla de Estructura de Carrusel (5 a 7 Slides)

### Slide 1: Portada de Alto Impacto
- **Dimensiones**: 1080 x 1350 px (4:5).
- **Badge Superior**: `[COLUMNA X — PILAR]`.
- **Arte Principal**: Mascota en plano medio o entero, interactuando con el concepto del post.
- **Titular Principal**: Máximo 6 palabras, tipografía ExtraBold, alto contraste.
- **Subtítulo**: 1 línea que expande la promesa de valor.
- **Microindicador**: Flecha vectorial o texto discreto *"Desliza para auditar"* / *"Pasa la página"*.

### Slide 2: El Contexto o Problema Crítico
- **Objetivo**: Agitar el dolor del cliente o evidenciar la práctica obsoleta de la industria.
- **Estructura**: Un titular de impacto + 2 bloques comparativos (ej. *Método Tradicional vs Método ALCORE*).

### Slide 3: Desglose Técnico o Mecánica de la Solución
- **Objetivo**: Demostrar autoridad de ingeniería o funcionamiento del software.
- **Estructura**: Bloque de código en JetBrains Mono, diagrama de flujo o captura real de interfaz de Kinvo / Kinvo Express.

### Slide 4: Aplicación Práctica o Caso Real
- **Objetivo**: Mostrar el antes y después en métricas tangibles (tiempo, costos de servidores, facturación sin errores).
- **Estructura**: Cifras en fuente grande (ej. *"60% Ahorro"*, *"0.01% Error Rate"*).

### Slide 5: Checklist / Resumen Ejecutivo
- **Objetivo**: Dejar un contenido guardable y compartible.
- **Estructura**: 3 o 4 pasos numerados o viñetas geométricas (`▪`).

### Slide 6 (Slide Final): Cierre Institucional y Llamado a la Acción
- **Objetivo**: Conversión sin rodeos.
- **Estructura**:
  - Logotipo oficial de ALCORE o producto SaaS.
  - Frase de cierre institucional.
  - CTA unívoco: *"Comenta [PALABRA] para recibir la guía completa"* o *"Solicita tu demo en alcore-gt.com"*.
  - Firma: *"ALCORE Technologies Solutions — El Núcleo Tecnológico de tu Negocio"*.

---

## 3. Guía de Generación de Prompt para Portadas con Mascota

Cuando se requiera generar una portada nueva utilizando la herramienta `generate_image`, se debe aplicar la siguiente estructura:

```text
AspectRatio: '3:4' o '1:1'
Prompt: Full body or medium shot of [Nombre de Mascota], the official mascot of ALCORE, [descripción del personaje]. Standing in a [entorno institucional de la columna]. Confident, professional and welcoming expression. Minimalist composition with ample negative space at the top and bottom for typography overlay. Dark sleek corporate background in [color oficial de columna], cinematic softbox lighting, 3D animated film render, Pixar DreamWorks style, zero noise.
ImagePaths: [Ruta absoluta al render oficial de la mascota]
```
