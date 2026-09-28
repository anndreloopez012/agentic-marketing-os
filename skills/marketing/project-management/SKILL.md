---
name: project-management
description: Use when the user needs project management help — breaking down work, estimating effort, sprint planning, backlog management, status tracking, risk management, client communication on project status, or choosing between Agile/Scrum/Kanban. Also use when the user says "planificar el proyecto", "desglosar tareas", "sprint", "roadmap", "cronograma", "gestión de proyecto", or "cómo organizo este trabajo".
metadata:
  short-description: Gestión de proyectos — planificación, sprints, backlogs, estimación y seguimiento de entregables.
---

# Project Management Expert

Metodologías, herramientas y flujos de trabajo para entregar proyectos a tiempo y con calidad.

---

## Metodologías: cuándo usar cada una

| Metodología | Cuándo | Características |
|---|---|---|
| **Scrum** | Producto iterativo, equipo estable | Sprints de 1-2 semanas, daily standups, retrospectivas |
| **Kanban** | Flujo continuo, soporte, mantenimiento | Sin sprints, límite de WIP, flujo visible |
| **Waterfall** | Proyectos con requisitos fijos y fechas duras | Fases secuenciales, entrega única al final |
| **Híbrido** | Proyectos de cliente con entregables fijos | Planificación waterfall, ejecución ágil |

**Para proyectos de software con cliente (el caso más común):**
Usa híbrido: define fases y entregables con el cliente (waterfall), ejecuta internamente en sprints (ágil).

---

## Estructura de proyecto completa

### Fase 0: Discovery / Levantamiento
- [ ] Entender el negocio del cliente y su problema real
- [ ] Definir alcance exacto (qué SÍ incluye y qué NO incluye)
- [ ] Identificar stakeholders y tomadores de decisión
- [ ] Validar restricciones: presupuesto, tiempo, tecnología
- [ ] Documentar en: Brief de Proyecto o Statement of Work (SOW)

### Fase 1: Planificación
- [ ] Desglosar en épicas → user stories → tareas
- [ ] Estimar esfuerzo (story points o horas)
- [ ] Priorizar con cliente (MoSCoW: Must/Should/Could/Won't)
- [ ] Armar cronograma o roadmap
- [ ] Identificar dependencias y cuellos de botella
- [ ] Definir Definition of Done (DoD) por entregable

### Fase 2: Ejecución
- Sprint planning → daily standup → sprint review → retrospectiva
- Actualizar tablero (Kanban/Jira/Linear/Notion) diariamente
- Comunicar avances al cliente semanalmente
- Gestionar cambios de alcance formalmente (no informalmente)

### Fase 3: Entrega y Cierre
- [ ] QA y pruebas de aceptación del cliente
- [ ] Documentación técnica y de usuario
- [ ] Handoff / capacitación si aplica
- [ ] Retrospectiva interna del proyecto
- [ ] Lecciones aprendidas documentadas

---

## Desglose de trabajo (WBS)

### Jerarquía
```
Proyecto
  └── Épica (funcionalidad grande: "Sistema de autenticación")
        └── Historia de usuario ("Como usuario, quiero iniciar sesión con email")
              └── Tarea ("Crear endpoint POST /auth/login")
              └── Tarea ("Diseñar pantalla de login")
              └── Tarea ("Implementar validación de formulario")
```

### Formato de User Story
```
Como [tipo de usuario]
Quiero [acción/funcionalidad]
Para [beneficio/razón]

Criterios de aceptación:
- Dado [contexto], cuando [acción], entonces [resultado]
- Dado [contexto], cuando [acción], entonces [resultado]
```

---

## Estimación de esfuerzo

### Story Points (Fibonacci: 1, 2, 3, 5, 8, 13, 21)
| Points | Esfuerzo | Ejemplo |
|---|---|---|
| 1 | Trivial, <2h | Cambiar texto de un botón |
| 2 | Simple, 2-4h | Agregar un campo a un formulario |
| 3 | Pequeño, 4-8h | CRUD completo simple |
| 5 | Mediano, 1-2 días | Feature completa con UI |
| 8 | Grande, 2-4 días | Feature compleja con integraciones |
| 13 | Muy grande | Épica — debe dividirse |
| 21 | Indefinido | Requiere discovery antes de estimar |

### Buffer de estimación
- Para clientes: agregar 20-30% de buffer al tiempo estimado
- Para tecnología nueva: agregar 40-50% (la curva de aprendizaje siempre es mayor)
- Bugs e imprevistos: reservar 15% del sprint para esto

---

## Gestión de riesgos

### Registro de riesgos
| Riesgo | Probabilidad | Impacto | Mitigación |
|---|---|---|---|
| Cambio de alcance del cliente | Alta | Alto | SOW firmado + proceso de change request |
| Dependencia de tercero (API) | Media | Alto | Identificar alternativas, mockups |
| Recurso clave indisponible | Baja | Alto | Documentación, pair programming |
| Requisitos ambiguos | Alta | Medio | Discovery detallado + prototipos |

---

## Comunicación con cliente

### Update semanal (formato)
```
SEMANA [N] — [NOMBRE DEL PROYECTO]
📅 Fecha: [DD/MM/YYYY]

✅ COMPLETADO ESTA SEMANA
- [Entregable 1]
- [Entregable 2]

🔄 EN PROGRESO
- [Tarea en curso — % estimado]
- [Tarea en curso]

📋 PRÓXIMA SEMANA
- [Lo que se entregará]
- [Hito importante si aplica]

⚠️ BLOQUEADORES / PENDIENTES DEL CLIENTE
- [Si necesitas feedback, aprobación o info del cliente]

📊 ESTADO GENERAL: 🟢 En tiempo / 🟡 En riesgo / 🔴 Retrasado
```

### Gestión de cambios de alcance
Nunca aceptar cambios de alcance verbalmente. Siempre:
1. Documentar el cambio solicitado
2. Estimar el impacto en tiempo y costo
3. Obtener aprobación escrita del cliente
4. Ajustar el cronograma formalmente

---

## Herramientas recomendadas

| Herramienta | Mejor para |
|---|---|
| **Linear** | Equipos de software, integración con GitHub |
| **Notion** | Documentación + project tracking combinado |
| **Jira** | Equipos grandes, enterprise |
| **Trello** | Kanban simple, proyectos pequeños |
| **ClickUp** | Todo en uno, flexible |
| **GitHub Projects** | Open source, integración nativa con repos |
