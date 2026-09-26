# Guía Operativa para Google Antigravity & Gemini CLI

Este archivo define las directivas para **Google Antigravity** y **Gemini** dentro del entorno **Agentic Marketing OS**.

---

## 1. Integración con el Sistema de Memoria

- **Consulta Obligatoria de Inicio**:
  Antes de plantear soluciones, consulta la memoria del proyecto con `memoria contexto <proyecto>` y utiliza Graphify (`graphify query`) si existe `graphify-out/graph.json`.
- **Registro de Bitácora**:
  Al completar hitos relevantes, documenta en la bitácora con `memoria registrar <proyecto> --tipo [aprendizaje|decision|cambio|validacion] --titulo "..." --texto "..."`.

---

## 2. Ejecución Multimodal y Habilidades

- **Marketing y Campañas**: Emplea `copywriting-pro`, `content-strategy`, `paid-ads` y `brand-identity`.
- **Optimización de Búsqueda**: Aplica `seo-expert` y `geo-expert` para posicionamiento en motores tradicionales e IA.
- **Producción Audiovisual**: Utiliza `remotion` y el framework `hyperframes` para video programmatic, y `google-flow-veo-director` para video generativo.
- **Navegador Web**: Usa `agent-browser` para verificación en tiempo real y pruebas end-to-end.

---

## 3. Flujo Git y Control de Versiones

- Todo trabajo se realiza en ramas de funcionalidad (`feature/...`).
- Se integra en `dev` antes de la sincronización final con `main`.
- Nunca sobrescribir trabajo del usuario sin antes revisar `git status --short`.
