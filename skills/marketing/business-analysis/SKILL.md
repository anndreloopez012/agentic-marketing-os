---
name: business-analysis
description: Use when the user needs business analysis work — requirements gathering, process mapping, stakeholder analysis, use case documentation, gap analysis, user stories, acceptance criteria, business case writing, KPI definition, or translating business needs into technical requirements. Also use when the user says "levantamiento de requisitos", "análisis de negocio", "mapeo de procesos", "caso de uso", "requerimientos funcionales", or "traducir el negocio a tecnología".
metadata:
  short-description: Análisis de negocio — requisitos, procesos, casos de uso, KPIs y traducción a especificaciones técnicas.
---

# Business Analysis Expert

Levantamiento, documentación y traducción de necesidades de negocio a especificaciones claras para el equipo técnico.

---

## Proceso de levantamiento de requisitos

### Técnicas de elicitación

**Entrevistas estructuradas:** con stakeholders clave. Preguntas base:
```
¿Cuál es el problema principal que quieres resolver?
¿Cómo funciona el proceso hoy? ¿Qué está mal?
¿Quiénes son los usuarios del sistema?
¿Cuál sería el resultado ideal?
¿Qué no debe cambiar?
¿Cuáles son las restricciones (presupuesto, tiempo, tecnología)?
```

**Observación de proceso (As-Is):** documentar cómo funciona actualmente antes de proponer cambios.

**Workshops:** reunir múltiples stakeholders para alinear visiones conflictivas.

**Prototipos rápidos:** mostrar, no describir — reduce malentendidos.

---

## Tipos de requisitos

### Funcionales (qué debe hacer el sistema)
```
RF-001: El sistema debe permitir al usuario iniciar sesión con email y contraseña.
RF-002: El sistema debe enviar un email de confirmación al registrar una cuenta.
RF-003: El administrador debe poder exportar reportes en formato CSV y PDF.
```

### No funcionales (cómo debe comportarse)
```
RNF-001: El sistema debe cargar en menos de 3 segundos en conexión 4G.
RNF-002: El sistema debe soportar hasta 500 usuarios simultáneos.
RNF-003: Los datos del usuario deben cifrarse en reposo y en tránsito.
RNF-004: El sistema debe tener 99.5% de uptime mensual.
```

### De negocio (restricciones y objetivos del negocio)
```
RN-001: El sistema debe cumplir con la Ley de Protección de Datos de Guatemala.
RN-002: El proceso de aprobación de facturas no puede tomar más de 24h.
```

---

## Documentación de procesos

### Notación BPMN simplificada (para no-técnicos)
```
[Inicio] → [Tarea 1] → {¿Condición?}
                              ↓ Sí → [Tarea 2] → [Fin]
                              ↓ No → [Tarea 3] → [Fin]
```

### Tabla de proceso As-Is vs To-Be
| Paso | Proceso Actual (As-Is) | Proceso Propuesto (To-Be) | Mejora |
|---|---|---|---|
| 1 | Factura en papel → firma manual | Factura digital → aprobación en sistema | -2 días |
| 2 | Envío por correo físico | Notificación automática por email | Inmediato |

---

## Análisis de stakeholders

### Mapa de stakeholders
| Stakeholder | Rol | Interés | Influencia | Estrategia |
|---|---|---|---|---|
| CEO | Decisor | Alto | Alta | Mantener informado |
| Gerente operativo | Usuario power | Alto | Media | Involucrar activamente |
| Equipo de ventas | Usuario final | Medio | Baja | Capacitar y escuchar |
| IT | Técnico | Medio | Alta | Colaborar en diseño |
| Proveedor externo | Integración | Bajo | Media | Coordinar cuando necesario |

---

## Casos de uso

### Formato de caso de uso
```
ID: CU-001
Nombre: Aprobar factura
Actor principal: Gerente financiero
Actores secundarios: Sistema de notificaciones
Precondición: La factura fue ingresada y está en estado "pendiente"
Flujo principal:
  1. El gerente accede al módulo de facturas pendientes
  2. Selecciona la factura a revisar
  3. Revisa el detalle y los documentos adjuntos
  4. Hace clic en "Aprobar"
  5. El sistema actualiza el estado a "aprobado"
  6. El sistema notifica al proveedor por email
Flujo alternativo (rechazo):
  4a. El gerente hace clic en "Rechazar" e ingresa motivo
  5a. El sistema notifica al área solicitante con el motivo
Postcondición: La factura tiene estado "aprobado" o "rechazado"
```

---

## Definición de KPIs

### Framework SMART para KPIs
**Specific** — qué mido exactamente  
**Measurable** — cómo lo mido  
**Achievable** — es alcanzable  
**Relevant** — importa para el negocio  
**Time-bound** — en qué período  

### Tabla de KPIs por área
| Área | KPI | Fórmula | Meta | Frecuencia |
|---|---|---|---|---|
| Ventas | Tasa de cierre | Cierres / Leads × 100 | > 25% | Mensual |
| Soporte | Tiempo de respuesta | Promedio de horas hasta primera respuesta | < 4h | Semanal |
| Producto | NPS | % promotores − % detractores | > 50 | Trimestral |
| Operaciones | Costo por transacción | Costos operativos / N transacciones | Reducir 10% | Mensual |

---

## Análisis de brechas (Gap Analysis)

```
ESTADO ACTUAL (As-Is)
¿Qué tenemos hoy? ¿Cómo funciona? ¿Cuáles son las limitaciones?

ESTADO DESEADO (To-Be)
¿Dónde queremos estar? ¿Qué necesita funcionar diferente?

BRECHAS IDENTIFICADAS
Gap 1: [Lo que falta o no funciona bien]
Gap 2: [...]

ACCIONES PARA CERRAR BRECHAS
Acción 1: [Qué hacer] → Responsable: [X] → Fecha: [Y]
Acción 2: [...]
```

---

## Documento de especificación funcional (SRS simplificado)

Estructura mínima para proyectos medianos:
```
1. Propósito y alcance del sistema
2. Descripción general del negocio
3. Actores / usuarios del sistema
4. Requisitos funcionales (RF-XXX)
5. Requisitos no funcionales (RNF-XXX)
6. Flujos de proceso (As-Is y To-Be)
7. Casos de uso principales
8. Reglas de negocio
9. Restricciones e integraciones
10. Criterios de aceptación por módulo
```
