#!/usr/bin/env node

/**
 * Script de Diagnóstico para Despliegues en AWS
 * Verifica disponibilidad de Docker, AWS CLI, autenticación y credenciales.
 */

const { execSync } = require('child_process');

function runCheck(name, cmd) {
  process.stdout.write(`Comprobando ${name}... `);
  try {
    const output = execSync(cmd, { stdio: ['pipe', 'pipe', 'pipe'], encoding: 'utf8' });
    console.log('OK');
    return { ok: true, output: output.trim() };
  } catch (err) {
    console.log('ERROR');
    return { ok: false, error: err.message || err.stderr || String(err) };
  }
}

function main() {
  console.log('==================================================');
  console.log(' Diagnóstico de Entorno para Despliegue en AWS');
  console.log('==================================================\n');

  let allOk = true;

  // 1. Docker CLI
  const dockerCheck = runCheck('Docker CLI', 'docker --version');
  if (dockerCheck.ok) {
    console.log(`   -> Versión: ${dockerCheck.output}`);
  } else {
    allOk = false;
    console.log('   [!] Docker no parece estar instalado o accesible en el PATH.');
  }

  // 2. Docker Daemon
  const dockerDaemonCheck = runCheck('Docker Daemon en ejecución', 'docker info');
  if (!dockerDaemonCheck.ok) {
    allOk = false;
    console.log('   [!] Docker Daemon no está corriendo. Inicia Docker Desktop o el servicio docker.');
  }

  // 3. AWS CLI
  const awsCliCheck = runCheck('AWS CLI', 'aws --version');
  if (awsCliCheck.ok) {
    console.log(`   -> Versión: ${awsCliCheck.output}`);
  } else {
    allOk = false;
    console.log('   [!] AWS CLI no está instalado. Descárgalo desde https://aws.amazon.com/cli/');
  }

  // 4. AWS Identity / Credentials
  const awsAuthCheck = runCheck('Credenciales de AWS (STS Identity)', 'aws sts get-caller-identity --output json');
  if (awsAuthCheck.ok) {
    try {
      const identity = JSON.parse(awsAuthCheck.output);
      console.log(`   -> Account ID: ${identity.Account}`);
      console.log(`   -> Arn: ${identity.Arn}`);
    } catch (e) {
      console.log(`   -> ${awsAuthCheck.output}`);
    }
  } else {
    allOk = false;
    console.log('   [!] Credenciales AWS no configuradas o expiradas. Ejecuta `aws configure` o exporta AWS_ACCESS_KEY_ID.');
  }

  // 5. Región AWS
  const awsRegionCheck = runCheck('Región AWS por defecto', 'aws configure get region');
  if (awsRegionCheck.ok && awsRegionCheck.output) {
    console.log(`   -> Región configurada: ${awsRegionCheck.output}`);
  } else {
    console.log('   [i] No se detectó región por defecto. Puedes definirla con `aws configure set region us-east-1`');
  }

  console.log('\n==================================================');
  if (allOk) {
    console.log('[OK] Todo el entorno está listo para compilar y desplegar en AWS.');
  } else {
    console.log('[ERROR] Se encontraron advertencias o errores. Revisa las notas anteriores.');
  }
  console.log('==================================================\n');
}

main();
