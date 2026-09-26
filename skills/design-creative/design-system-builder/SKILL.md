---
name: design-system-builder
description: Use when the user needs to build, document, or maintain a design system — design tokens, component libraries, Figma component sets, Storybook setup, naming conventions, spacing scales, color systems, or creating consistency across a product or brand. Also use when the user says "sistema de diseño", "design tokens", "componentes reutilizables", "librería de componentes", "Storybook", or "consistencia visual entre pantallas".
metadata:
  short-description: Construye y documenta design systems — tokens, componentes, escalas y consistencia entre producto y diseño.
---

# Design System Builder

Guía completa para construir y mantener un design system: desde tokens hasta componentes documentados.

---

## ¿Cuándo necesitas un design system?

- El producto tiene más de 3 pantallas o vistas
- Más de 1 persona trabaja en el diseño o el frontend
- Hay inconsistencias visuales entre secciones del producto
- Se está migrando de diseño ad-hoc a diseño sistemático

---

## 1. Design Tokens

Los tokens son las variables del design system. Son la base de todo.

### Jerarquía de tokens (3 niveles)

```
NIVEL 1: Tokens primitivos (valores crudos)
  color.blue.500 = #3B82F6
  spacing.4 = 16px
  font.size.base = 16px

NIVEL 2: Tokens semánticos (significado)
  color.primary = {color.blue.500}
  color.background.default = {color.neutral.50}
  spacing.component.padding = {spacing.4}

NIVEL 3: Tokens de componente (específicos)
  button.primary.background = {color.primary}
  button.primary.padding = {spacing.component.padding}
```

### Categorías de tokens a definir

**Color:**
```
Marca: primary, secondary, accent
Semántico: success, warning, error, info
Neutrales: background, surface, border, text
Interacción: hover, focus, active, disabled
```

**Tipografía:**
```
font-family: sans, serif, mono
font-size: xs(12) sm(14) base(16) lg(18) xl(20) 2xl(24) 3xl(30) 4xl(36)
font-weight: regular(400) medium(500) semibold(600) bold(700)
line-height: tight(1.25) normal(1.5) relaxed(1.75)
letter-spacing: tight / normal / wide
```

**Espaciado (escala 4px):**
```
0: 0px | 1: 4px | 2: 8px | 3: 12px | 4: 16px
5: 20px | 6: 24px | 8: 32px | 10: 40px | 12: 48px
16: 64px | 20: 80px | 24: 96px
```

**Bordes:**
```
border-radius: none(0) sm(4px) md(8px) lg(12px) xl(16px) full(9999px)
border-width: 1px / 2px / 4px
```

**Sombras:**
```
shadow-sm: 0 1px 2px rgba(0,0,0,0.05)
shadow-md: 0 4px 6px rgba(0,0,0,0.07)
shadow-lg: 0 10px 15px rgba(0,0,0,0.1)
shadow-xl: 0 20px 25px rgba(0,0,0,0.1)
```

**Breakpoints:**
```
sm: 640px | md: 768px | lg: 1024px | xl: 1280px | 2xl: 1536px
```

---

## 2. Componentes: atomic design

```
Átomos       → elementos mínimos: Button, Input, Badge, Icon, Avatar
Moléculas    → combinación de átomos: SearchBar, Card, FormField
Organismos   → secciones complejas: Header, Sidebar, DataTable
Templates    → layouts sin contenido real
Páginas      → templates con contenido real
```

### Anatomía de un componente bien documentado

```
Nombre: Button
Variantes: primary | secondary | ghost | danger | link
Tamaños: sm | md | lg
Estados: default | hover | focus | active | disabled | loading
Props: label, onClick, disabled, loading, icon, variant, size
Uso correcto: ✅ ejemplos
Uso incorrecto: ❌ qué evitar
Accesibilidad: role="button", aria-label, keyboard nav
```

### Componentes mínimos para cualquier producto web

**Básicos:**
Button, Input, Textarea, Select, Checkbox, Radio, Toggle, Badge, Tag, Avatar, Icon

**Layout:**
Container, Grid, Stack, Divider, Spacer

**Feedback:**
Alert, Toast/Snackbar, Modal, Drawer, Tooltip, Skeleton, Spinner/Loader, EmptyState

**Navegación:**
Navbar, Sidebar, Tabs, Breadcrumb, Pagination, Dropdown

**Data:**
Table, Card, List, Stat/KPI card

---

## 3. Implementación en código (Tailwind + React)

### Tokens como variables CSS
```css
:root {
  --color-primary: #3B82F6;
  --color-primary-hover: #2563EB;
  --color-surface: #FFFFFF;
  --color-text: #111827;
  --radius-md: 8px;
  --shadow-md: 0 4px 6px rgba(0,0,0,0.07);
}
```

### Tailwind: extender el tema con los tokens
```js
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      colors: {
        primary: { DEFAULT: '#3B82F6', hover: '#2563EB' },
        surface: '#FFFFFF',
      },
      borderRadius: { brand: '8px' },
    },
  },
}
```

### Componente de referencia con variantes
```tsx
// Button.tsx
const variants = {
  primary: 'bg-primary text-white hover:bg-primary-hover',
  secondary: 'border border-primary text-primary hover:bg-primary/10',
  ghost: 'text-primary hover:bg-primary/10',
  danger: 'bg-red-600 text-white hover:bg-red-700',
}
const sizes = {
  sm: 'px-3 py-1.5 text-sm',
  md: 'px-4 py-2 text-base',
  lg: 'px-6 py-3 text-lg',
}
```

---

## 4. Documentación del design system

### Storybook (documentación de componentes)
```bash
npx storybook@latest init
# Genera historia por componente: Button.stories.tsx
```

### Estructura de carpetas recomendada
```
src/
  design-system/
    tokens/
      colors.ts
      typography.ts
      spacing.ts
    components/
      Button/
        Button.tsx
        Button.stories.tsx
        Button.test.tsx
        index.ts
      Input/
      ...
    index.ts    ← exporta todo
```

---

## 5. Mantenimiento y gobernanza

- **Versioning:** semver para el design system (major.minor.patch)
- **Changelog:** documentar cada cambio
- **Deprecation:** marcar componentes deprecados con tiempo suficiente antes de eliminar
- **Review process:** cambios al system requieren review de diseño Y frontend
- **Single source of truth:** Figma es la fuente de diseño, código es la implementación — deben estar sincronizados
