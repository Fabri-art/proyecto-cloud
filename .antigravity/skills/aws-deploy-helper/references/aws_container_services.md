# Comparativa de Servicios de Contenedores en AWS

Guía de referencia arquitectónica para seleccionar el servicio de despliegue de contenedores más adecuado en AWS.

---

## 1. Cuadro Comparativo

| Característica | AWS App Runner | Amazon ECS (Fargate) | Amazon ECS (EC2) | Amazon EKS (Kubernetes) |
| :--- | :--- | :--- | :--- | :--- |
| **Nivel de Abstracción** | Muy Alto (PaaS / Serverless) | Medio-Alto (CaaS Serverless) | Medio (CaaS con VMs) | Bajo-Medio (K8s gestionado) |
| **Gestión de Infraestructura** | Cero gestión de servidores | Cero servidores (solo tareas) | Gestión de instancias EC2 | Gestión de plano de control y nodes |
| **Configuración de Red / VPC** | Opcional (Egress a VPC) | Integración total con VPC | Integración total con VPC | Red CNI nativa en VPC |
| **Balanceador de Carga (ALB)** | Incluido y gestionado | Requiere configurar ALB/NLB | Requiere configurar ALB/NLB | Ingress Controller / ALB Ingress |
| **Certificados SSL / HTTPS** | Automático y gratuito | Gestionado vía AWS ACM + ALB | Gestionado vía AWS ACM + ALB | ACM / Let's Encrypt + Ingress |
| **Soporte para Tareas / Cron** | No (solo servicios web HTTP) | Sí (Scheduled Tasks / EventBridge)| Sí | Sí (CronJobs de K8s) |
| **Escalado a Cero** | Sí (pausa de cómputo) | No (mínimo 1 tarea activa) | Depende del Auto Scaling Group | Sí (con KEDA / Karpenter) |
| **Costo Base Inicial** | Muy bajo (pago por uso) | Bajo (pago por vCPU/GB-hora) | Costo de instancias EC2 fijas | ~$73/mes por cluster + nodos |

---

## 2. Recomendaciones de Uso

### Cuándo elegir **AWS App Runner**:
- Aplicaciones web monolíticas, APIs REST o GraphQL con tráfico HTTP/HTTPS.
- Equipos pequeños que quieren evitar la sobrecarga de configurar VPCs, subredes, ALBs y Target Groups.
- Proyectos donde se requiere CI/CD automático con cada push a ECR o GitHub.

### Cuándo elegir **Amazon ECS con Fargate**:
- Arquitecturas de microservicios con comunicación interna en VPC.
- Procesos en segundo plano (workers de colas SQS, jobs asíncronos, crons).
- Necesidad de asignación granular de políticas IAM por contenedor (`taskRoleArn`).

### Cuándo elegir **Amazon ECS con EC2**:
- Cargas de trabajo de alto volumen constante donde las instancias reservadas o Savings Plans en EC2 ofrecen mayor ahorro.
- Requerimientos de hardware especializado (GPUs para ML, almacenamiento NVMe local).

### Cuándo elegir **Amazon EKS**:
- Ecosistemas existentes que ya usan Helm, Istio, Prometheus, ArgoCD.
- Requisito estricto de portabilidad multi-cloud basada en Kubernetes.
