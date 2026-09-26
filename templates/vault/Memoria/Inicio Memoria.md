# Índice de Memoria Continua

Bienvenido al sistema de memoria viva compartida entre tus agentes de Inteligencia Artificial (**Claude Code**, **Codex**, y **Antigravity**) y tu baúl de **Obsidian**.

---

## 📌 Protocolo Operativo para Agentes IA

1. **Antes de empezar a trabajar en cualquier proyecto**:
   - Consultar la memoria del proyecto:
     ```bash
     memoria contexto <nombre-proyecto>
     memoria proyecto <nombre-proyecto>
     ```
   - O consultar la nota en `Memoria/Proyectos Git/<nombre-proyecto>.md`.
2. **Si el proyecto tiene grafo de Graphify (`graphify-out/graph.json`)**:
   - Consultar la arquitectura y flujo sin inflar tokens de contexto:
     ```bash
     graphify query "¿Cuál es la arquitectura de este proyecto?"
     graphify path "<ComponenteA>" "<ComponenteB>"
     graphify explain "<Modulo>"
     ```
3. **Al finalizar un cambio o sprint**:
   - Actualizar el grafo de dependencias:
     ```bash
     graphify update .
     ```
   - Exportar a Obsidian:
     ```bash
     graphify export obsidian --dir "$VAULT_ROOT/Memoria/Graphify/<nombre-proyecto>"
     ```
   - Registrar la decisión técnica o aprendizaje:
     ```bash
     memoria registrar <nombre-proyecto> --tipo [aprendizaje|decision|cambio|validacion] --titulo "<Título>" --texto "<Resumen>"
     ```
   - Refrescar índices:
     ```bash
     memoria refresh
     ```

---

## 📂 Estructura del Baúl

- [[Contexto Operativo]]: Estado actual de proyectos, prioridades y convenciones.
- `Bitacora/`: Registro cronológico y bitácora de trabajo de los agentes.
- `Graphify/`: Grafos exportados de cada proyecto con sus nodos y dependencias.
- `Proyectos Git/`: Fichas maestras de cada proyecto registrado.
- `Decisiones/`: Registro de decisiones de arquitectura y diseño.
- `Skills/`: Documentación y catálogo de habilidades disponibles en los agentes.
