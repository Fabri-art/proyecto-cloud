# Resolución de Problemas Comunes en Despliegues de Contenedores en AWS

Guía rápida para diagnosticar y solucionar errores frecuentes en ECR, ECS y App Runner.

---

## 1. Errores en Amazon ECR

### `no basic auth credentials` o `denied: Your authorization token has expired`
- **Causa:** El token temporal de Docker emitido por `aws ecr get-login-password` expira a las 12 horas.
- **Solución:**
  ```bash
  aws ecr get-login-password --region <REGION> | docker login --username AWS --password-stdin <ACCOUNT_ID>.dkr.ecr.<REGION>.amazonaws.com
  ```

### `RepositoryNotFoundException`
- **Causa:** El nombre del repositorio no existe en la región seleccionada.
- **Solución:**
  ```bash
  aws ecr create-repository --repository-name <REPO_NAME> --region <REGION>
  ```

---

## 2. Errores en Amazon ECS Fargate

### `CannotPullContainerError: AccessDeniedException` o `pull access denied`
- **Causa:** El rol `executionRoleArn` (`ecsTaskExecutionRole`) no tiene asignada la política administrada `AmazonECSTaskExecutionRolePolicy` o falta permiso para desencriptar KMS/Secrets Manager.
- **Solución:**
  Verificar que el rol IAM tenga adjunta `arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy`.

### `ResourceInitializationError: unable to pull secrets or registry auth`
- **Causa:** La tarea intenta descargar secretos desde Secrets Manager o SSM Parameter Store pero el rol de ejecución no tiene permisos `secretsmanager:GetSecretValue` o `ssm:GetParameters`.

### Tarea ECS se detiene con `Essential container in task exited (Exit Code: 1 o 137)`
- **Exit Code 1:** Error en el código de la aplicación. Inspeccionar logs en CloudWatch (`/ecs/<app_name>`).
- **Exit Code 137 (OOMKilled):** El contenedor consumió más memoria RAM que el límite asignado en la Task Definition. Aumentar el valor de `memory` (ej. de `512` a `1024` o `2048`).

### Las tareas entran en un bucle continuo de reinicio (*CrashLoop / Flapping*)
- **Causa común:** El contenedor falla su propio `HEALTHCHECK` o el balanceador (ALB) no recibe respuesta en la ruta configurada (ej. `/health`) antes del timeout.
- **Solución:**
  1. Validar que la app escuche en `0.0.0.0` y no en `127.0.0.1`.
  2. Comprobar que el puerto expuesto en el `Dockerfile` (`EXPOSE 3000`) coincida con `containerPort` en la Task Definition y el Target Group del ALB.

---

## 3. Errores en AWS App Runner

### `Deployment failed: Health check failed on port X`
- **Causa:** App Runner realiza peticiones HTTP a la ruta raíz `/` o a la ruta de health check configurada. Si la app tarda demasiado en iniciar o devuelve un código HTTP diferente de `200-399`, el despliegue falla y hace rollback automático.
- **Solución:**
  1. Aumentar el `HealthCheckConfiguration.Timeout` o `Interval`.
  2. Asegurar que la ruta `/` o `/health` retorne status `200 OK`.
