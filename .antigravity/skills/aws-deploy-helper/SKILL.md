---
name: aws-deploy-helper
description: >-
  Prepara contenedores Docker, optimiza imágenes multi-stage y guía el despliegue de aplicaciones en Amazon Web Services (AWS) utilizando ECR, ECS (Fargate/EC2), App Runner o Elastic Beanstalk.
  Activa esta habilidad cuando el usuario solicite desplegar en AWS, crear/optimizar Dockerfiles, subir imágenes a Amazon ECR, configurar tareas de ECS, o gestionar infraestructura de contenedores en la nube.
  Also use when the user asks to containerize apps or deploy to AWS Cloud.
---

# AWS Deploy Helper (Asistente de Contenedorización y Despliegue en AWS)

Esta habilidad proporciona una guía completa y estructurada para preparar contenedores Docker listos para producción y desplegar aplicaciones web y microservicios en **Amazon Web Services (AWS)** con alta disponibilidad, seguridad y rendimiento.

---

## Objetivo

1. Guiar la creación y optimización de **Dockerfiles** (multi-stage builds, usuario no-root, variables de entorno y caching eficiente).
2. Automatizar el diagnóstico del entorno local (Docker Daemon, AWS CLI y credenciales IAM).
3. Administrar el ciclo de vida de imágenes en **Amazon ECR** (autenticación, creación de repositorios, etiquetado semántico y push).
4. Configurar y orquestar el despliegue en servicios administrados de AWS como **AWS App Runner** o **Amazon ECS (Fargate)**.
5. Validar la salud del servicio (*health checks*) y proporcionar estrategias de rollback y diagnóstico de errores.

---

## Cuándo Usar Esta Habilidad

- *"Ayúdame a dockerizar este proyecto y subirlo a AWS."*
- *"Despliega esta aplicación en AWS ECS / App Runner."*
- *"Crea el Dockerfile y las instrucciones para ECR."*
- *"¿Cómo configuro la tarea de ECS Fargate para mi backend?"*
- *"Tengo un error de permisos o de red al desplegar en AWS."*

---

## Árbol de Decisión: Selección del Servicio AWS Adecuado

Utiliza este árbol para recomendar la mejor arquitectura según las necesidades del usuario:

```
¿Qué tipo de aplicación es y cuál es el nivel de control requerido?
│
├── Aplicación Web / API HTTP simple, rápida y sin gestión de VPC compleja
│   └── [RECOMENDACION] AWS App Runner (Serverless, TLS automático, escalado simple)
│
├── Microservicios, workers en segundo plano, control granular de red y VPC
│   └── [RECOMENDACION] Amazon ECS con AWS Fargate (Serverless, integración VPC, IAM por tarea)
│
├── Necesidad de control directo sobre instancias EC2 y optimización extrema de costos (Spot)
│   └── [RECOMENDACION] Amazon ECS con EC2 Launch Type
│
└── Clúster existente de Kubernetes o arquitectura multi-cloud
    └── [RECOMENDACION] Amazon EKS (Elastic Kubernetes Service)
```

---

## Procedimiento Paso a Paso de Despliegue

```
+------------------------------------+
| 1. Diagnóstico del Entorno Local   |
+------------------------------------+
                  │
                  ▼
+------------------------------------+
| 2. Preparación de Dockerfile       |
+------------------------------------+
                  │
                  ▼
+------------------------------------+
| 3. Build & Test Local              |
+------------------------------------+
                  │
                  ▼
+------------------------------------+
| 4. Autenticación y Push a ECR      |
+------------------------------------+
                  │
                  ▼
+------------------------------------+
| 5. Despliegue en ECS / App Runner  |
+------------------------------------+
                  │
                  ▼
+------------------------------------+
| 6. Verificación de Salud           |
+------------------------------------+
```

---

### Paso 1: Diagnóstico del Entorno Local

Verifica que Docker y el CLI de AWS estén instalados y configurados. Puedes ejecutar el script de verificación incluido:

```bash
node .agents/skills/aws-deploy-helper/scripts/check_aws_env.js
```

O manualmente:
```bash
# Verificar Docker
docker --version && docker ps

# Verificar AWS CLI y credenciales
aws sts get-caller-identity
aws configure get region
```

---

### Paso 2: Preparación del `Dockerfile` y `.dockerignore`

Genera un `Dockerfile` optimizado con **Multi-Stage Build** para minimizar el tamaño de la imagen y reducir vulnerabilidades de seguridad.

1. **Crear `.dockerignore`:**
   ```text
   node_modules
   .git
   .env
   .env.local
   dist
   build
   npm-debug.log*
   .DS_Store
   ```

2. **Estructura del `Dockerfile`:**
   - Consulta las plantillas listas para usar en [resources/](./resources/):
     - Node.js: [Dockerfile.node.template](./resources/Dockerfile.node.template)
     - Python: [Dockerfile.python.template](./resources/Dockerfile.python.template)

---

### Paso 3: Construcción y Testeo Local del Contenedor

Valida que el contenedor compile y responda localmente antes de subirlo a AWS:

```bash
# 1. Construir la imagen localmente
docker build -t app-local:latest .

# 2. Ejecutar contenedor de prueba
docker run -d -p 3000:3000 --name test-app app-local:latest

# 3. Comprobar logs y respuesta
docker logs test-app
curl http://localhost:3000/health || curl http://localhost:3000/

# 4. Detener y limpiar
docker stop test-app && docker rm test-app
```

---

### Paso 4: Autenticación y Subida a Amazon ECR

1. **Definir variables:**
   ```bash
   AWS_REGION="us-east-1"
   AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
   REPO_NAME="mi-proyecto-backend"
   IMAGE_TAG="v1.0.0"
   ECR_URI="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${REPO_NAME}"
   ```

2. **Crear el repositorio en ECR (si no existe):**
   ```bash
   aws ecr describe-repositories --repository-names ${REPO_NAME} --region ${AWS_REGION} || \
   aws ecr create-repository \
       --repository-name ${REPO_NAME} \
       --region ${AWS_REGION} \
       --image-scanning-configuration scanOnPush=true \
       --encryption-configuration encryptionType=AES256
   ```

3. **Autenticar Docker con Amazon ECR:**
   ```bash
   aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com
   ```

4. **Etiquetar y Subir la Imagen:**
   ```bash
   docker tag app-local:latest ${ECR_URI}:${IMAGE_TAG}
   docker tag app-local:latest ${ECR_URI}:latest

   docker push ${ECR_URI}:${IMAGE_TAG}
   docker push ${ECR_URI}:latest
   ```

---

### Paso 5: Despliegue del Servicio

#### Opción A: Despliegue con AWS App Runner (Recomendado para Web/API)
App Runner aprovisiona balanceadores, certificados SSL y auto-escalado automáticamente:
```bash
aws apprunner create-service \
    --service-name "${REPO_NAME}-service" \
    --source-configuration '{
        "ImageRepository": {
            "ImageIdentifier": "'"${ECR_URI}:latest"'",
            "ImageRepositoryType": "ECR",
            "ImageConfiguration": {
                "Port": "3000",
                "RuntimeEnvironmentVariables": {
                    "NODE_ENV": "production"
                }
            }
        },
        "AutoDeploymentsEnabled": true,
        "AuthenticationConfiguration": {
            "AccessRoleArn": "arn:aws:iam::'"${AWS_ACCOUNT_ID}"':role/AppRunnerECRAccessRole"
        }
    }'
```

#### Opción B: Despliegue con Amazon ECS (Fargate)
1. **Registrar definición de tarea (Task Definition):**
   - Usa la plantilla [ecs-task-definition.json.template](./resources/ecs-task-definition.json.template).
   ```bash
   aws ecs register-task-definition --cli-input-json file://task-definition.json
   ```
2. **Actualizar el servicio ECS:**
   ```bash
   aws ecs update-service \
       --cluster mi-cluster-ecs \
       --service mi-servicio-backend \
       --force-new-deployment
   ```

---

### Paso 6: Verificación y Health Check

1. **Consultar estado del servicio:**
   ```bash
   # Para App Runner
   aws apprunner describe-service --service-arn <SERVICE_ARN> --query "Service.Status"

   # Para ECS
   aws ecs describe-services --cluster mi-cluster-ecs --services mi-servicio-backend --query "services[0].deployments"
   ```

2. **Monitoreo de Logs en Amazon CloudWatch:**
   ```bash
   aws logs tail /ecs/mi-proyecto-backend --follow
   ```

3. **Prueba de Endpoint Público:**
   ```bash
   curl -I https://<URL_PROPORCIONADA_POR_AWS>/
   ```

---

## Buenas Prácticas de Seguridad y Operación en AWS

1. **Nunca incrustar credenciales en imágenes:** Usa **AWS Secrets Manager** o **AWS SSM Parameter Store** para inyectar variables de entorno en tiempo de ejecución.
2. **Principio de menor privilegio:** Crea roles de ejecución IAM dedicados (`ecsTaskExecutionRole` y `TaskRole`) con permisos mínimos estrictos.
3. **Escaneo de Vulnerabilidades:** Activa siempre `scanOnPush=true` en los repositorios de ECR.
4. **Imágenes Ligeras:** Usa imágenes base tipo `alpine` o `-slim` y evita instalar herramientas de desarrollo en la capa final de producción.
5. **Políticas de Ciclo de Vida en ECR:** Configura reglas para expirar imágenes sin etiquetar y conservar solo las últimas N versiones.

---

## Recursos y Referencias Incluidas

- [Script de Diagnóstico de Entorno AWS](./scripts/check_aws_env.js)
- [Plantilla Dockerfile Node.js](./resources/Dockerfile.node.template)
- [Plantilla Dockerfile Python](./resources/Dockerfile.python.template)
- [Plantilla ECS Task Definition](./resources/ecs-task-definition.json.template)
- [Guía Comparativa de Servicios de Contenedores en AWS](./references/aws_container_services.md)
- [Guía de Resolución de Errores Comunes (Troubleshooting)](./references/troubleshooting_aws.md)
