---
name: email-marketing
description: Use when the user needs email marketing work — campaign strategy, email sequences (welcome, nurture, sales, re-engagement), newsletter design, subject lines, deliverability optimization, segmentation, automation flows, or analyzing email metrics. Also use when the user mentions "secuencia de emails", "newsletter", "email de bienvenida", "automatización de email", "drip campaign", or "email marketing".
metadata:
  short-description: Estrategia y producción de email marketing — secuencias, newsletters, deliverability y automatización.
---

# Email Marketing Expert

Estrategia y ejecución completa: listas, secuencias automáticas, deliverability y análisis de métricas.

---

## Segmentación de lista

| Segmento | Criterio | Comunicación |
|---|---|---|
| Nuevos suscriptores | < 7 días | Secuencia de bienvenida |
| Leads fríos | Sin actividad 30+ días | Re-engagement |
| Leads activos | Abrieron últimos 30 días | Nurture / educación |
| Clientes | Han comprado | Upsell / retención |
| VIP | Compradores frecuentes | Beneficios exclusivos |

**Higiene de lista:** limpiar bounces duros y 90-day inactivos cada trimestre. Nunca comprar listas.

---

## Secuencias esenciales

### Bienvenida (5 emails / 7 días)
```
Día 0  — Entrega del lead magnet + bienvenida
Día 2  — Tu historia + credibilidad
Día 4  — El problema que resuelves (agitación)
Día 6  — Tu solución + social proof
Día 7  — Oferta de entrada + urgencia real
```

### Re-engagement (3 emails)
```
Email 1 — "¿Sigues ahí?" tono casual
Email 2 — Nuevo recurso exclusivo
Email 3 — "Te doy de baja en 48h" (urgencia de pérdida)
→ Sin apertura en Email 3 → dar de baja automáticamente
```

### Carrito abandonado (ecommerce)
```
1h    — Recordatorio suave + foto del producto
24h   — Urgencia + reseñas
72h   — Descuento o envío gratis
```

### Post-compra
```
Inmediato  — Confirmación + próximos pasos
Día 3      — Onboarding / cómo sacar el máximo provecho
Día 7      — Pedir reseña / testimonio
Día 30     — Upsell complementario
```

---

## Subject lines que funcionan

| Tipo | Fórmula | Ejemplo |
|---|---|---|
| Curiosidad | "[Lo que nadie te dice sobre X]" | "Lo que nadie te dice sobre crecer en Instagram" |
| Urgencia | "Solo [X]h para [beneficio]" | "Solo 24h para el precio de lanzamiento" |
| Beneficio directo | "[Verbo] [resultado] en [tiempo]" | "Consigue 10 clientes nuevos este mes" |
| Pregunta | "¿[Problema del lector]?" | "¿Por qué tu sitio web no convierte?" |
| Lista | "[N] formas de [resultado]" | "7 formas de vender sin ads" |

**Reglas:** 40-50 chars, evitar MAYÚSCULAS / !!!, siempre hacer A/B test (20/20/60).

---

## Estructura de email de venta

```
ASUNTO + PREHEADER complementario

Hola [Nombre],

[GANCHO — primera línea que atrapa]

[CONTEXTO — 2-3 oraciones que llevan al punto]

[OFERTA — claro y directo]
[BENEFICIOS — 3-5 bullets con resultados, no features]
  ✓ Beneficio 1
  ✓ Beneficio 2
  ✓ Beneficio 3

[SOCIAL PROOF — testimonio real]

[BOTÓN CTA]

[CTA secundario en texto plano]

Saludos, [Nombre]
[Footer: unsubscribe | dirección | privacidad]
```

---

## Deliverability

**DNS requerido:**
```
SPF:   v=spf1 include:tu-esp.com ~all
DKIM:  clave de tu ESP (TXT record)
DMARC: v=DMARC1; p=quarantine; rua=mailto:dmarc@tudominio.com
```

**Warm-up de dominio nuevo:** 50/día → 200 → 500 → escalar. Nunca enviar lista completa desde dominio nuevo.

---

## Métricas y benchmarks

| Métrica | Bueno | Promedio | Crítico |
|---|---|---|---|
| Open Rate | > 25% | 15-25% | < 15% |
| CTR | > 3% | 1-3% | < 1% |
| Unsubscribe | < 0.2% | 0.2-0.5% | > 0.5% |
| Spam complaint | < 0.1% | — | > 0.1% |

**ESPs recomendados:** Brevo (pymes LATAM), ActiveCampaign (automatización avanzada), Klaviyo (ecommerce), ConvertKit (creadores).
