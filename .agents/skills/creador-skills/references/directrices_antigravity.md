# Directrices y Estándares Oficiales de Skills en Antigravity

Documento de referencia técnica compilado a partir de la documentación oficial de Google Antigravity ([https://antigravity.google/docs/skills/](https://antigravity.google/docs/skills/)) y el sistema de personalización `agy-customizations`.

---

## 1. ¿Qué es una Skill (Habilidad)?

Una **Skill** es un paquete modular y reutilizable de conocimiento e instrucciones operativas que extiende las capacidades del agente de Antigravity para resolver flujos de trabajo especializados.

Cada skill contiene:
- Instrucciones detalladas de procedimiento (*runbooks* o guías paso a paso).
- Buenas prácticas y convenciones específicas de un proyecto o tecnología.
- Scripts ejecutables, recursos y referencias auxiliares.

---

## 2. Ubicaciones y Alcance (Scopes)

Antigravity busca y carga habilidades desde dos ubicaciones principales:

| Tipo de Alcance | Ruta | Propósito |
| :--- | :--- | :--- |
| **Workspace (Proyecto)** | `<workspace-root>/.agents/skills/<skill-folder>/` *(o `.antigravity/skills/`)* | Específico para el repositorio/proyecto actual. Se versiona en Git. |
| **Global (Sistema)** | `~/.gemini/config/skills/<skill-folder>/` | Disponible transversalmente en todos los proyectos del desarrollador. |

---

## 3. Estructura de Directorios de una Skill

```text
skills/<skill_name>/
├── SKILL.md                 # [Obligatorio] Archivo principal con frontmatter YAML
├── scripts/                 # [Opcional] Herramientas, CLI o scripts ejecutables
├── examples/                # [Opcional] Implementaciones y ejemplos de referencia
├── resources/               # [Opcional] Plantillas, esquemas o assets estáticos
└── references/              # [Opcional] Documentación extensa o manuales detallados
```

---

## 4. Ciclo de Vida: Progressive Disclosure

Para optimizar el uso de la ventana de contexto del modelo, Antigravity implementa **divulgación progresiva**:

1. **Discovery (Descubrimiento):** Al inicio de la conversación, el agente sólo conoce el `name` y `description` declarados en el YAML frontmatter de todas las skills disponibles.
2. **Activation (Activación):** Si el prompt del usuario o el contexto coinciden con la descripción, el agente lee el contenido completo de `SKILL.md`.
3. **Execution (Ejecución):** El agente sigue las instrucciones del `SKILL.md`, llamando a scripts o consultando archivos en `references/` únicamente si es necesario.

---

## 5. Especificación del YAML Frontmatter

```yaml
---
name: nombre-de-la-skill       # Obligatorio/Recomendado: kebab-case único
description: >-                # Obligatorio: En tercera persona, describe QUÉ hace y CUÁNDO activarse
  Proporciona instrucciones para ejecutar X tarea en el proyecto Y.
  Activa esta habilidad cuando el usuario solicite Z.
---
```

### Reglas de Oro para la Descripción:
- Redactar siempre en **tercera persona** (*"Genera...", "Ejecuta...", "Asiste en..."*).
- Incluir palabras clave específicas y disparadores (*triggers*) en español e inglés.
- Especificar con claridad el contexto y los casos de uso donde la habilidad aporta valor.

---

## 6. Buenas Prácticas de Diseño

1. **Enfoque Singular:** Cada habilidad debe resolver un dominio o procedimiento concreto.
2. **Scripts como Cajas Negras:** Los scripts auxiliares deben admitir `--help` y ser autodescriptivos.
3. **Enlaces Relativos:** Usar siempre enlaces Markdown estándar tipo `[script](./scripts/mi_script.js)` para que el agente pueda navegar entre archivos sin depender de rutas absolutas.
4. **Verificación Sistemática:** Incluir siempre un paso de validación post-ejecución.
