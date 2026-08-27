```markdown
# 🏆 Nombre-Creativo — Plataforma de Torneos Deportivos

Sistema integral para gestión de torneos deportivos, fixture round-robin, mesa de control en vivo y tablas de posiciones.

---

## 🛠️ Stack Tecnológico

- **Backend:** FastAPI, Python 3.12, SQLModel / SQLAlchemy, Alembic.
- **Base de Datos:** PostgreSQL 16.
- **Frontend:** SvelteKit + Tailwind CSS (Puerto `5173`).
- **Entorno Local:** Docker & Docker Compose.
- **Gestión de Tareas:** Linear vía MCP Server.

---

## 🚀 Puesta en Marcha Local (Backend & Base de Datos)

### Requisitos previos
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) instalado y en ejecución.
- Git.

### 1. Clonar el repositorio
```bash
git clone https://github.com/Fabri-art/proyecto-cloud.git
cd proyecto-cloud

```

### 2. Variables de Entorno

Asegúrate de contar con el archivo de variables en `backend/.env`:

```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=nombre_creativo_db
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5433/nombre_creativo_db

```

### 3. Levantar Contenedores con Hot-Reload

```bash
docker compose up -d --build

```

### 4. Aplicar Migraciones

```bash
docker compose exec backend alembic upgrade head

```

### 5. Servicios Disponibles

* **Swagger UI (Documentación API):** [http://localhost:8001/docs](http://localhost:8001/docs)
* **Base de Datos (DBeaver / DataGrip):** `localhost:5433` | Usuario: `postgres` | Clave: `postgres` | BD: `nombre_creativo_db`
* **Tests Automatizados:** `docker compose exec backend pytest`

---

## 🤖 Configuración para Agentes / IDE (Antigravity & MCP)

Si utilizas el editor **Antigravity**:

1. Abre la raíz del proyecto (`File -> Open Folder`).
2. Verifica que las **Skills** y Customizations se carguen desde `.antigravity/` o `.agent/`.
3. Para conectar **Linear MCP Server**:
* Configura tu `LINEAR_API_KEY`.
* Si el servidor se desconecta, recarga la ventana con `Ctrl + Shift + P` -> `Developer: Reload Window`.



---

## 🌿 Flujo de Trabajo con Git y Ramas (OBLIGATORIO)

Para mantener la estabilidad del código, **la rama `main` queda reservada exclusivamente para versiones estables**.

1. **Nunca trabajes directamente sobre `main`.**
2. Actualiza la rama principal antes de comenzar:
```bash
git checkout main
git pull origin main

```


3. Crea una rama descriptiva para tu tarea:
```bash
git checkout -b feat/frontend-vistas
# o
git checkout -b feat/devops-docker-ci

```


4. Guarda tus avances y sube tu rama:
```bash
git add .
git commit -m "feat(front): implementacion de vistas y consumo de api"
git push origin feat/frontend-vistas

```


5. Abre un **Pull Request (PR)** hacia `main` en GitHub para revisión e integración.

```

```