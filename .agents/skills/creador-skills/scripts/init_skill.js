#!/usr/bin/env node

/**
 * Script CLI para inicializar una nueva Skill en Antigravity
 * Uso: node init_skill.js --name <nombre-skill> --description "<descripcion>" [--scope workspace|global]
 */

const fs = require('fs');
const path = require('path');
const os = require('os');

function printHelp() {
  console.log(`
Uso:
  node init_skill.js --name <nombre-skill> --description "<descripcion>" [opciones]

Opciones:
  --name, -n          Nombre de la habilidad (ej: deploy-aws, analizador-logs) [Requerido]
  --description, -d   Descripción en 3ra persona y condiciones de activación [Requerido]
  --scope, -s         Alcance: 'workspace' (por defecto) o 'global'
  --help, -h          Muestra este mensaje de ayuda
`);
}

function parseArgs() {
  const args = process.argv.slice(2);
  const parsed = {
    name: '',
    description: '',
    scope: 'workspace'
  };

  for (let i = 0; i < args.length; i++) {
    const arg = args[i];
    if (arg === '--help' || arg === '-h') {
      printHelp();
      process.exit(0);
    } else if ((arg === '--name' || arg === '-n') && i + 1 < args.length) {
      parsed.name = args[++i];
    } else if ((arg === '--description' || arg === '-d') && i + 1 < args.length) {
      parsed.description = args[++i];
    } else if ((arg === '--scope' || arg === '-s') && i + 1 < args.length) {
      parsed.scope = args[++i].toLowerCase();
    }
  }

  return parsed;
}

function main() {
  const { name, description, scope } = parseArgs();

  if (!name) {
    console.error('Error: Debe especificar el nombre de la habilidad (--name <nombre>).');
    printHelp();
    process.exit(1);
  }

  const sanitizedName = name.toLowerCase().replace(/[^a-z0-9_-]/g, '-');
  const desc = description || `Asiste y ejecuta tareas relacionadas con ${sanitizedName}. Activa esta habilidad cuando el usuario lo solicite.`;

  let baseDir;
  if (scope === 'global') {
    baseDir = path.join(os.homedir(), '.gemini', 'config', 'skills', sanitizedName);
  } else {
    baseDir = path.join(process.cwd(), '.agents', 'skills', sanitizedName);
  }

  console.log(`Creando estructura para la habilidad '${sanitizedName}' en: ${baseDir}`);

  const dirs = [
    baseDir,
    path.join(baseDir, 'scripts'),
    path.join(baseDir, 'examples'),
    path.join(baseDir, 'resources'),
    path.join(baseDir, 'references')
  ];

  for (const dir of dirs) {
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }
  }

  const skillContent = `---
name: ${sanitizedName}
description: >-
  ${desc}
---

# ${sanitizedName}

Instrucciones detalladas para el agente sobre cómo abordar tareas relacionadas con ${sanitizedName}.

---

## Cuándo Usar Esta Habilidad

- Describe los casos de uso y prompts típicos donde esta habilidad debe activarse.

---

## Requisitos Previos

- Especifica herramientas, variables de entorno o dependencias requeridas.

---

## Procedimiento Paso a Paso

### 1. Preparación
Instrucciones iniciales de verificación o inspección.

### 2. Ejecución
Pasos concretos y comandos a ejecutar.

### 3. Verificación
Comandos o métodos para validar que la tarea finalizó correctamente.

---

## Buenas Prácticas

- Mantén las instrucciones concisas y enfocadas.
- Usa scripts auxiliares en \`scripts/\` para tareas complejas.
- Consulta [referencias](./references/) para documentación extendida.
`;

  const skillPath = path.join(baseDir, 'SKILL.md');
  if (!fs.existsSync(skillPath)) {
    fs.writeFileSync(skillPath, skillContent, 'utf8');
    console.log(`[OK] Creado: ${skillPath}`);
  } else {
    console.log(`[!] El archivo ${skillPath} ya existía.`);
  }

  console.log(`\n¡Habilidad '${sanitizedName}' inicializada exitosamente!`);
}

try {
  main();
} catch (err) {
  console.error('Error inicializando la habilidad:', err);
  process.exit(1);
}
