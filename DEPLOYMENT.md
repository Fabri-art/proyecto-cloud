# 🚀 Guía de Despliegue en Producción (AWS Cloud)

Esta guía detalla el procedimiento paso a paso, la arquitectura recomendada y las mejores prácticas de seguridad para desplegar la plataforma **Nombre-Creativo** (Backend FastAPI + Frontend SvelteKit + Base de Datos PostgreSQL) en **Amazon Web Services (AWS)**.

---

## 🏛️ Arquitectura Recomendada

```
                                  [ INTERNET ]
                                        │
                    ┌───────────────────┴───────────────────┐
                    ▼                                       ▼
       [ Frontend: SvelteKit ]                 [ Backend: FastAPI ]
    (AWS App Runner o ECS Fargate)          (AWS App Runner o ECS Fargate)
            Puerto: 5173                            Puerto: 8000
                    │                                       │
                    │   CORS restringido                    ▼
                    └─── (PUBLIC_API_BASE_URL) ──►   [ Amazon RDS ]
                                                  PostgreSQL 16 (Multi-AZ)
                                                  (Subred Privada - VPC)
                                                            ▲
                                                            │
                                                [ AWS Secrets Manager ]
                                                (DATABASE_URL, SECRET_KEY)
```

| Componente | Servicio AWS Recomendado | Rol / Función |
| :--- | :--- | :--- |
| **Frontend** | AWS App Runner / Amazon ECS Fargate | Interfaz web para hinchas y panel de administración |
| **Backend API** | AWS App Runner / Amazon ECS Fargate | Lógica de negocio, torneos, fixture y cálculo de estadísticas |
| **Base de Datos** | Amazon RDS for PostgreSQL (v16) | Persistencia relacional, respaldos automáticos y alta disponibilidad |
| **Imágenes Docker** | Amazon ECR (Elastic Container Registry) | Almacenamiento seguro de imágenes con escaneo de vulnerabilidades |
| **Gestión de Secretos** | AWS Secrets Manager / Parameter Store | Inyección segura de credenciales sin archivos `.env` en código |
| **Monitoreo y Logs** | Amazon CloudWatch | Trazabilidad de logs de contenedores y métricas de salud |

---

## 🔐 1. Prácticas Críticas de Seguridad

### A. Gestión Segura de Secretos
* **Nunca comitees archivos `.env` reales:** El repositorio ya incluye [.gitignore](.gitignore), [backend/.dockerignore](backend/.dockerignore) y [frontend/.dockerignore](frontend/.dockerignore) para evitar que secretos locales o historiales de Git entren en las imágenes de Docker.
* **Inyección en tiempo de ejecución:** En AWS ECS o App Runner, los secretos (`DATABASE_URL`, `SECRET_KEY`) deben inyectarse directamente como referencias a **AWS Secrets Manager** o **SSM Parameter Store**.

### B. Aislamiento de Red de la Base de Datos
* La instancia de **Amazon RDS PostgreSQL** debe residir en **subredes privadas** de tu VPC (`Publicly Accessible = No`).
* Configura el **Security Group** de RDS para permitir tráfico en el puerto `5432` **únicamente** desde el Security Group del backend.

### C. Restricción de CORS
* En producción, restringe `CORS_ORIGINS` en el backend para admitir únicamente el dominio público de tu frontend:
  ```env
  CORS_ORIGINS=https://tu-dominio-frontend.awsapprunner.com
  ```

### D. PIN de Administrador
* El panel de administración utiliza la variable `PUBLIC_ADMIN_PIN`. En producción, asigna un valor seguro de al menos 6-8 dígitos en las variables de entorno del frontend.

---

## 📋 2. Matriz de Variables de Entorno en Producción

### Backend (FastAPI)
| Variable | Descripción | Ejemplo / Valor en Producción |
| :--- | :--- | :--- |
| `APP_NAME` | Nombre de la aplicación | `"Nombre-Creativo API"` |
| `APP_VERSION` | Versión del despliegue | `"1.0.0"` |
| `DEBUG` | Modo depuración (debe ser falso) | `false` |
| `DATABASE_URL` | Cadena de conexión asyncpg a RDS | `postgresql+asyncpg://appuser:SECRET_PASS@rds-endpoint.amazonaws.com:5432/nombre_creativo_db` |
| `SECRET_KEY` | Llave secreta criptográfica (32+ chars) | Inyectada desde Secrets Manager |
| `CORS_ORIGINS` | Orígenes permitidos separados por coma | `https://app.tudominio.com` |

### Frontend (SvelteKit)
| Variable | Descripción | Ejemplo / Valor en Producción |
| :--- | :--- | :--- |
| `PUBLIC_API_BASE_URL` | URL pública de la API backend | `https://api.tudominio.com/api/v1` |
| `PUBLIC_ADMIN_PIN` | PIN para autorizar mesa de control | `849201` |

---

## 🐳 3. Empaquetado de Contenedores con Docker

Tanto el backend como el frontend cuentan con `Dockerfile` optimizados para producción (Multi-stage build, usuario no-root por seguridad y health checks incorporados).

### Verificación Local previa al despliegue:

```bash
# 1. Probar build del Backend
docker build --target production -t backend-prod:latest ./backend

# 2. Probar build del Frontend
docker build -t frontend-prod:latest ./frontend
```

---

## ☁️ 4. Paso a Paso para Desplegar en AWS

### Paso 4.1: Autenticación en Amazon ECR

Define tus variables de cuenta y región de AWS:

```bash
AWS_REGION="us-east-1"
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
```

Autentica tu cliente Docker local contra el registro privado de ECR:

```bash
aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com
```

---

### Paso 4.2: Crear los Repositorios en ECR y Subir Imágenes

Crea repositorios con escaneo automático de vulnerabilidades activado:

```bash
# Crear repositorio backend
aws ecr create-repository \
    --repository-name nombre-creativo-backend \
    --region ${AWS_REGION} \
    --image-scanning-configuration scanOnPush=true \
    --encryption-configuration encryptionType=AES256

# Crear repositorio frontend
aws ecr create-repository \
    --repository-name nombre-creativo-frontend \
    --region ${AWS_REGION} \
    --image-scanning-configuration scanOnPush=true \
    --encryption-configuration encryptionType=AES256
```

Etiqueta y sube las imágenes:

```bash
# Backend
BACKEND_ECR="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/nombre-creativo-backend"
docker tag backend-prod:latest ${BACKEND_ECR}:latest
docker tag backend-prod:latest ${BACKEND_ECR}:v1.0.0
docker push ${BACKEND_ECR}:latest
docker push ${BACKEND_ECR}:v1.0.0

# Frontend
FRONTEND_ECR="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/nombre-creativo-frontend"
docker tag frontend-prod:latest ${FRONTEND_ECR}:latest
docker tag frontend-prod:latest ${FRONTEND_ECR}:v1.0.0
docker push ${FRONTEND_ECR}:latest
docker push ${FRONTEND_ECR}:v1.0.0
```

---

### Paso 4.3: Configurar Secretos en AWS Secrets Manager

Crea el secreto con las credenciales de la base de datos:

```bash
aws secretsmanager create-secret \
    --name "nombre-creativo/prod/credentials" \
    --region ${AWS_REGION} \
    --secret-string '{"DATABASE_URL":"postgresql+asyncpg://postgres:TU_PASSWORD_SEGURO@tu-rds-endpoint.amazonaws.com:5432/nombre_creativo_db","SECRET_KEY":"TU_LLAVE_ALEATORIA_MUY_LARGA"}'
```

---

### Paso 4.4: Despliegue en AWS App Runner (Opción Rápida y Serverless)

**AWS App Runner** aprovisiona balanceadores de carga, certificados HTTPS y escalado automático sin gestionar clusters de servidores.

#### Desplegar Backend:
```bash
aws apprunner create-service \
    --service-name "nombre-creativo-backend-svc" \
    --source-configuration '{
        "ImageRepository": {
            "ImageIdentifier": "'"${BACKEND_ECR}:latest"'",
            "ImageRepositoryType": "ECR",
            "ImageConfiguration": {
                "Port": "8000",
                "RuntimeEnvironmentVariables": {
                    "DEBUG": "false",
                    "CORS_ORIGINS": "https://<URL_FRONTEND>"
                }
            }
        },
        "AutoDeploymentsEnabled": true,
        "AuthenticationConfiguration": {
            "AccessRoleArn": "arn:aws:iam::'"${AWS_ACCOUNT_ID}"':role/AppRunnerECRAccessRole"
        }
    }'
```

#### Desplegar Frontend:
Una vez obtenida la URL pública del backend (`https://<URL_BACKEND_APPRUNNER>`), crea el servicio del frontend:

```bash
aws apprunner create-service \
    --service-name "nombre-creativo-frontend-svc" \
    --source-configuration '{
        "ImageRepository": {
            "ImageIdentifier": "'"${FRONTEND_ECR}:latest"'",
            "ImageRepositoryType": "ECR",
            "ImageConfiguration": {
                "Port": "5173",
                "RuntimeEnvironmentVariables": {
                    "PUBLIC_API_BASE_URL": "https://<URL_BACKEND_APPRUNNER>/api/v1",
                    "PUBLIC_ADMIN_PIN": "753190"
                }
            }
        },
        "AutoDeploymentsEnabled": true,
        "AuthenticationConfiguration": {
            "AccessRoleArn": "arn:aws:iam::'"${AWS_ACCOUNT_ID}"':role/AppRunnerECRAccessRole"
        }
    }'
```

---

### Paso 4.5: Ejecutar Migraciones de Base de Datos en Producción

Antes de habilitar el tráfico de usuarios, aplica las migraciones de base de datos con **Alembic**:

```bash
# Opción 1: Tarea temporal ECS Run-Task
aws ecs run-task \
    --cluster nombre-creativo-cluster \
    --task-definition nombre-creativo-backend-task \
    --overrides '{"containerOverrides": [{"name": "backend", "command": ["alembic", "upgrade", "head"]}]}'

# Opción 2: Ejecución remota si tienes bastion host o VPN
DATABASE_URL="<CONEXION_RDS>" alembic upgrade head
```

---

## 🩺 5. Verificación de Salud y Monitoreo

1. **Health Check del Backend:**
   ```bash
   curl -i https://<URL_BACKEND>/api/v1/health
   # Respuesta esperada: HTTP 200 {"status":"ok","app":"Nombre-Creativo API","version":"0.1.0"}
   ```

2. **Inspección del Frontend:**
   ```bash
   curl -I https://<URL_FRONTEND>/
   # Respuesta esperada: HTTP 200 OK
   ```

3. **Ver logs en tiempo real con Amazon CloudWatch:**
   ```bash
   aws logs tail /aws/apprunner/nombre-creativo-backend-svc --follow
   ```

---

## 🔄 6. Estrategia de Rollback

Si una nueva versión genera problemas en producción:

1. **Reversión de Imagen:**
   Redespliega la versión previa etiquetada en ECR:
   ```bash
   # En App Runner o ECS, apunta a la versión estable anterior
   aws apprunner start-deployment --service-arn <SERVICE_ARN>
   ```
2. **Reversión de Base de Datos:**
   Si hubo una migración fallida:
   ```bash
   alembic downgrade -1
   ```
