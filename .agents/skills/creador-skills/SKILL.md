---
name: creador-skills
description: >-
  Guía, diseña y automatiza la creación y estructuración de nuevas Skills (habilidades) para el agente Antigravity en español.
  Activa esta habilidad cuando el usuario solicite crear una nueva skill, definir habilidades personalizadas, empaquetar procedimientos repetibles, o estructurar runbooks dentro de .agents/skills/ o .antigravity/skills/.
  Also use when the user asks to create, scaffold, or standardize new agent skills, workflows, or runbooks.
---

# Creador de Habilidades para Antigravity (Skill Creator)

Esta habilidad proporciona un marco estructurado y estandarizado para guiar al usuario y al agente en el diseño, scaffolding y redacción de nuevas **Skills** para Antigravity, siguiendo las directrices oficiales de la plataforma y el principio de *Progressive Disclosure*.

---

## Objetivo

Garantizar que toda nueva habilidad creada en el proyecto o a nivel global cuente con:
1. Un **YAML Frontmatter** preciso que permita una activación contextual óptima por parte del modelo.
2. Una estructura modular y limpia (`SKILL.md`, `scripts/`, `examples/`, `resources/`, `references/`).
3. Instrucciones paso a paso accionables, verificables y sin redundancia de conocimientos generales.
4. Automatización del scaffolding mediante scripts auxiliares.

---

## Cuándo Usar Esta Habilidad

- Cuando el usuario diga: *"Crea una nueva skill llamada X"*, *"Ayúdame a crear una habilidad para Y"*, o *"Genera una skill que haga Z"*.
- Cuando se detecte un flujo de trabajo recurrente que deba ser encapsulado en un paquete de instrucciones reutilizable.
- Cuando se necesite auditar, refactorizar o estandarizar una skill existente.

---

## Flujo de Trabajo Paso a Paso para Crear una Habilidad

Cuando se solicite la creación de una nueva habilidad, sigue estrictamente este procedimiento:

```
+-----------------------------------+
| 1. Definición de Alcance y Nombre |
+-----------------------------------+
                  |
                  v
+-----------------------------------+
| 2. Redacción de Frontmatter YAML  |
+-----------------------------------+
                  |
                  v
+-----------------------------------+
| 3. Scaffolding de Directorios     |
+-----------------------------------+
                  |
                  v
+-----------------------------------+
| 4. Redacción de SKILL.md y Código |
+-----------------------------------+
                  |
                  v
+-----------------------------------+
| 5. Verificación y Validación      |
+-----------------------------------+
```

### Paso 1: Definir el Nombre y Propósito
- **Formato del nombre:** Minúsculas, palabras separadas por guiones (`kebab-case`). Ejemplos: `deploy-aws`, `analizador-logs`, `code-review`.
- **Enfoque singular:** La habilidad debe resolver un problema o flujo específico, no intentar abarcarlo todo.
- **Ubicación (Scope):**
  - **Workspace (Proyecto):** `.agents/skills/<nombre-skill>/` (recomendado) o `.antigravity/skills/<nombre-skill>/`.
  - **Global (Todo el sistema):** `~/.gemini/config/skills/<nombre-skill>/`.

### Paso 2: Redactar el Frontmatter YAML
El frontmatter es lo único que el agente lee antes de decidir activar la habilidad. Debe ser ultra claro:
- `name`: Nombre de la skill (coincide con el nombre de la carpeta).
- `description`: Redactada en **tercera persona**, detallando **qué hace** la habilidad y **cuándo debe activarse**, incluyendo palabras clave en español e inglés.

```yaml
---
name: nombre-de-la-skill
description: >-
  Describe con precisión qué hace la habilidad y en qué situaciones exactas debe activarse.
  Incluye disparadores claros y términos de búsqueda relevantes.
---
```

### Paso 3: Generar la Estructura de Carpetas y Archivos
Crea la estructura de carpetas estándar. Puedes usar el script auxiliar incluido:
```bash
node .agents/skills/creador-skills/scripts/init_skill.js --name <nombre-skill> --description "<descripcion>"
```

Estructura generada:
```text
.agents/skills/<nombre-skill>/
├── SKILL.md                 # [Requerido] Instrucciones principales
├── scripts/                 # [Opcional] Scripts ejecutables y herramientas auxiliares
├── examples/                # [Opcional] Ejemplos de uso, código de referencia o mocks
├── resources/               # [Opcional] Plantillas, configuraciones base o assets
└── references/              # [Opcional] Manuales extensos y documentación de apoyo
```

### Paso 4: Redactar el Archivo `SKILL.md`
El archivo `SKILL.md` debe estructurarse con las siguientes secciones:
1. **Título y Resumen:** Nombre y breve descripción del propósito.
2. **Requisitos Previos / Dependencias:** Herramientas, CLI o paquetes necesarios.
3. **Instrucciones Paso a Paso:** Procedimiento accionable numerado con ejemplos concretos.
4. **Verificación / Validación:** Comandos o pasos para comprobar que la tarea se completó con éxito.
5. **Resolución de Problemas / Árbol de Decisiones:** Qué hacer si un paso falla.

### Paso 5: Crear Scripts y Recursos Auxiliares
- Si la habilidad requiere automatizar comandos complejos, crea scripts en `scripts/` (ej. `.js`, `.py`, `.sh`, `.ps1`).
- Los scripts deben admitir flags como `--help` para que el agente pueda consultar su uso sin leer todo el código fuente.

### Paso 6: Validación
Revisar que:
- El archivo `SKILL.md` tiene el frontmatter YAML correctamente cerrado con `---`.
- Los enlaces relativos a `scripts/`, `resources/` o `references/` funcionen.
- No existan instrucciones redundantes sobre conocimientos generales de programación.

---

## Plantilla Oficial de `SKILL.md`

```markdown
---
name: mi-nueva-habilidad
description: >-
  Breve descripción en tercera persona de la habilidad.
  Explica qué resuelve y en qué situaciones exactas debe activarse.
---

# Nombre de la Habilidad

Descripción general del objetivo de esta habilidad y el resultado esperado tras su ejecución.

---

## Cuándo Usar

- Situación o prompt 1.
- Situación o prompt 2.

---

## Requisitos y Dependencias

- Herramienta X instalada (\`node\`, \`python\`, \`uv\`, etc.).
- Variables de entorno o credenciales requeridas.

---

## Procedimiento Paso a Paso

### 1. Preparación e Inspección
Explicación de qué inspeccionar o configurar primero.
\\\`\\\`\\\`bash
# Comando de ejemplo
\\\`\\\`\\\`

### 2. Ejecución Principal
Acciones y comandos para ejecutar la tarea.
- Si se usa un script auxiliar: \\\`node scripts/helper.js --flag valor\\\`

### 3. Verificación
Cómo validar que el procedimiento fue exitoso.
\\\`\\\`\\\`bash
# Comando de validación
\\\`\\\`\\\`

---

## Árbol de Decisiones / Casos Especiales

- **Si ocurre el error A:** Ejecutar solución X.
- **Si el entorno es Windows vs Linux:** Aplicar ajuste Y.

---

## Referencias
- [Documentación Adicional](./references/guia_detallada.md)
```

---

## Buenas Prácticas Oficiales

1. **Progressive Disclosure (Divulgación Progresiva):** Mantén `SKILL.md` conciso y enfocado en el flujo operativo. Si hay manuales extensos o tablas gigantes, colócalos en `references/` y vincúlalos con enlaces Markdown relativos.
2. **Scripts como Cajas Negras:** Diseña scripts auxiliares con interfaces de línea de comandos limpias y soporte para `--help`.
3. **Evitar Redundancias:** No enseñes al agente conceptos básicos que ya conoce (por ejemplo, cómo funciona un bucle `for` o qué es un JSON). Enfócate en las especificidades de tu proyecto o flujo de trabajo.
4. **Validación Explícita:** Cada flujo debe tener un criterio claro de finalización o validación.
5. **Nombres Descriptivos:** Usa identificadores que expresen la acción o el dominio con claridad.

---

## Herramientas de Apoyo en Esta Skill

- **Inicializador de Skills:** [init_skill.js](./scripts/init_skill.js) - Script en Node.js para crear la estructura completa de una nueva skill con un solo comando.
- **Plantilla Base:** [template_skill.md](./resources/template_skill.md) - Archivo base listo para duplicar y personalizar.
- **Directrices Oficiales de Antigravity:** [directrices_antigravity.md](./references/directrices_antigravity.md) - Documentación de referencia técnica sobre el ecosistema de extensiones.
