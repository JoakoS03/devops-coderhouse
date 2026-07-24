# Informe Final - Trabajo Práctico DevOps

**Alumno:** Joaquín S.  
**Curso:** DevOps  
**Fecha:** Julio 2026  
**Repositorio:** [https://github.com/JoakoS03/devops-coderhouse](https://github.com/JoakoS03/devops-coderhouse)

---

## 1. Descripción del Proyecto

Este proyecto implementa un pipeline DevOps completo para una **API REST de gestión de tareas (To-Do API)** construida con Python y FastAPI. El objetivo es demostrar el dominio de las herramientas y prácticas fundamentales de infraestructura cloud y automatización, cubriendo desde la contenedorización hasta el monitoreo y la optimización de costos.

### Tecnologías utilizadas

| Categoría | Tecnología |
|---|---|
| Aplicación | Python 3.12, FastAPI, Uvicorn |
| Contenedores | Docker (Multi-stage build) |
| IaC | Terraform (Kubernetes Provider) |
| Orquestación | Kubernetes (Docker Desktop) |
| CI/CD | GitHub Actions (6 etapas) |
| Seguridad | Bandit (SAST), Trivy (Scanner), OWASP ZAP (DAST) |
| Monitoreo | Prometheus, Grafana |
| FinOps | HPA, Resource Limits/Requests |

---

## 2. Estructura del Repositorio

```
.
├── .github/workflows/
│   └── ci-cd.yml              # Pipeline CI/CD completo
├── app/
│   ├── main.py                # Código fuente FastAPI
│   ├── test_main.py           # Tests automatizados (Pytest)
│   ├── requirements.txt       # Dependencias Python
│   ├── Dockerfile             # Multi-stage build optimizado
│   └── .dockerignore          # Exclusiones Docker
├── k8s/
│   ├── 00-namespace.yaml      # Namespace todo-app
│   ├── deployment.yaml        # Deployment con probes y limits
│   ├── service.yaml           # Service ClusterIP
│   ├── ingress.yaml           # Ingress Controller nginx
│   └── hpa.yaml               # HorizontalPodAutoscaler
├── terraform/
│   ├── providers.tf           # Proveedores K8s y Helm
│   ├── variables.tf           # Variables configurables
│   ├── main.tf                # Recursos de infraestructura
│   ├── outputs.tf             # Salidas del módulo
│   └── terraform.tfvars       # Valores para entorno local
├── monitoring/
│   ├── prometheus-config.yaml # Prometheus: ConfigMap + RBAC + Deploy
│   ├── grafana-deployment.yaml# Grafana: Deploy + Service
│   └── grafana-dashboard.json # Dashboard pre-configurado
├── .gitignore
└── README.md                  # Documentación completa
```

---

## 3. Docker - Dockerfile Optimizado (Multi-Stage Build)

Se implementó un **Dockerfile multi-stage** para optimizar el tamaño de la imagen y seguir buenas prácticas de seguridad:

### Stage 1 - Builder
- Base: `python:3.12-slim`
- Se crea un virtual environment (`/opt/venv`)
- Se instalan las dependencias desde `requirements.txt`

### Stage 2 - Runtime
- Base: `python:3.12-slim` (imagen liviana)
- Se copia **solo** el virtual environment del stage anterior (sin herramientas de build)
- Se crea un **usuario no-root** (`appuser`) para mayor seguridad
- Se incluye un `HEALTHCHECK` que valida el endpoint `/health`
- Puerto expuesto: `8000`

**Beneficios:**
- Imagen más pequeña (sin dependencias de build)
- Ejecución como usuario sin privilegios (seguridad)
- Health check integrado en la imagen

### Comando de build:
```bash
docker build -t todo-api:v2 ./app
```

---

## 4. Terraform - Infraestructura como Código

Se utilizó Terraform con el **Kubernetes Provider** para gestionar la infraestructura del cluster local (Docker Desktop con Kubernetes habilitado).

### Recursos definidos:
- **Namespace** (`todo-app`): Aislamiento lógico de recursos
- **Deployment**: Con réplicas, probes y resource limits configurables
- **Service** (ClusterIP): Exposición interna de la aplicación
- **Ingress**: Routing HTTP externo
- **HorizontalPodAutoscaler**: Auto-escalado basado en métricas
- **Namespace de monitoreo** (condicional): Habilitado/deshabilitado via variable

### Variables configurables:
- `app_name`, `app_namespace`, `app_image`, `app_port`
- `replicas` (cantidad inicial de réplicas)
- `cpu_request`, `memory_request`, `cpu_limit`, `memory_limit`
- `enable_monitoring` (booleano)

### Ejecución:
```bash
cd terraform
terraform init
terraform plan
terraform apply -auto-approve
```

---

## 5. Pipeline CI/CD - GitHub Actions

Se implementó un workflow completo en `.github/workflows/ci-cd.yml` con **6 jobs secuenciales**:

### Job 1: Test
- Setup Python 3.12
- Instalación de dependencias
- Ejecución de `pytest` con output verboso

### Job 2: SAST (Análisis Estático de Seguridad)
- **Bandit**: Escaneo del código Python buscando vulnerabilidades comunes
- **Trivy**: Escaneo del filesystem buscando dependencias vulnerables
- Los reportes se suben como artifacts del workflow

### Job 3: Build & Push
- Build de la imagen Docker con tag `SHA` y `latest`
- Login a **GitHub Container Registry (GHCR)**
- Push de la imagen al registry
- Escaneo de la imagen final con **Trivy**

### Job 4: Terraform Validate
- `terraform init`
- `terraform validate` (validación de sintaxis)
- `terraform plan` (plan de ejecución)

### Job 5: Deploy
- Solo se ejecuta en la rama `main`
- Aplica los manifiestos con `kubectl apply`
- Espera al rollout del deployment
- Verifica que los pods estén running

### Job 6: DAST (Análisis Dinámico de Seguridad)
- Ejecuta **OWASP ZAP** contra la URL de la API desplegada
- Genera un reporte HTML con los hallazgos
- Sube el reporte como artifact

---

## 6. Kubernetes - Manifiestos

### Deployment (`k8s/deployment.yaml`)
- **2 réplicas** para alta disponibilidad
- **Resource Requests**: CPU 100m, Memory 128Mi
- **Resource Limits**: CPU 250m, Memory 256Mi
- **Liveness Probe**: `GET /health` cada 10s (inicio: 10s)
- **Readiness Probe**: `GET /health` cada 10s (inicio: 5s)
- `imagePullPolicy: IfNotPresent` (optimizado para desarrollo local)

### Service (`k8s/service.yaml`)
- Tipo **ClusterIP** para comunicación interna
- Puerto 8000 → targetPort 8000
- Alternativa NodePort disponible (comentada)

### Ingress (`k8s/ingress.yaml`)
- Host: `todo-api.local`
- Anotación para **nginx ingress controller**
- Path `/` → Service `todo-api-service:8000`

### HPA (`k8s/hpa.yaml`)
- Min réplicas: **2**
- Max réplicas: **6**
- Target CPU: **70%**
- Target Memory: **80%**
- Estabilización de scale-down: **300s** (evita thrashing)

---

## 7. Monitoreo - Prometheus + Grafana

### Prometheus
- **ConfigMap** con configuración de scraping:
  - Job `todo-api`: Descubre pods automáticamente via `kubernetes_sd_configs`
  - Scrape interval: 15 segundos
  - Endpoint: `/metrics` en puerto 8000
- **RBAC**: ServiceAccount, ClusterRole y ClusterRoleBinding para permisos de lectura de pods/services
- **Deployment**: 1 réplica con la imagen `prom/prometheus:latest`
- **Service**: NodePort en puerto 30090

### Grafana
- **Deployment**: 1 réplica con `grafana/grafana:latest`
- **Service**: NodePort en puerto 30000
- **Dashboard pre-configurado** (`grafana-dashboard.json`) con paneles:
  - Tasa de requests HTTP por segundo
  - Duración de requests HTTP
  - Uso de CPU por pod
  - Uso de Memoria por pod

### Métricas exportadas por la API
La aplicación usa `prometheus-fastapi-instrumentator` que expone automáticamente:
- `http_requests_total` - Total de requests por método/endpoint/status
- `http_request_duration_seconds` - Histograma de latencias
- `http_requests_in_progress` - Requests en curso

### Acceso local:
```bash
# Prometheus
kubectl port-forward -n monitoring svc/prometheus-service 9090:9090
# → http://localhost:9090

# Grafana
kubectl port-forward -n monitoring svc/grafana-service 3000:3000
# → http://localhost:3000 (admin/admin)
```

---

## 8. FinOps - Optimización de Costos

Se aplicaron las siguientes estrategias para optimizar el uso de recursos:

### Resource Requests & Limits
Cada pod tiene configurados recursos mínimos (`requests`) y máximos (`limits`):
- Garantiza que los pods solo consumen lo necesario
- Protege al cluster de pods que consuman recursos excesivos (OOM Kill)
- Permite al scheduler de K8s distribuir pods eficientemente

### Horizontal Pod Autoscaler (HPA)
- Escala automáticamente entre 2 y 6 réplicas
- Se activa cuando el uso de CPU supera el 70% o memoria el 80%
- **Scale-down stabilization de 300s**: Evita oscilaciones rápidas (thrashing) que desperdiciarían recursos al crear/destruir pods constantemente
- En períodos de bajo tráfico, se mantiene el mínimo (2 réplicas) reduciendo costos

### Beneficios
- No se mantienen pods ociosos en períodos de bajo tráfico
- Se escala automáticamente ante picos de demanda
- El scale-down gradual evita disrupciones del servicio

---

## 9. Seguridad

### SAST (Static Application Security Testing)
- **Bandit**: Analiza el código Python en busca de vulnerabilidades comunes (ej: SQL injection, uso inseguro de crypto, hardcoded passwords)
- **Trivy FS**: Escanea el filesystem buscando dependencias con CVEs conocidos

### DAST (Dynamic Application Security Testing)
- **OWASP ZAP**: Ejecuta un scan baseline contra la API desplegada, probando vulnerabilidades en runtime como XSS, CSRF, headers de seguridad faltantes

### Buenas prácticas implementadas
- Ejecución como usuario **non-root** en Docker
- No se exponen credenciales en el código (uso de `secrets` en GitHub Actions)
- Imagen base **slim** (superficie de ataque reducida)
- `.dockerignore` para evitar filtrar archivos sensibles

---

## 10. Pasos para Replicar el Proyecto

### Requisitos previos
- Python 3.12+
- Docker Desktop con Kubernetes habilitado
- kubectl
- Terraform
- Git

### Ejecución local

```bash
# 1. Clonar el repositorio
git clone https://github.com/JoakoS03/devops-coderhouse.git
cd devops-coderhouse

# 2. Ejecutar la app localmente
cd app
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
# Abrir http://localhost:8000/docs

# 3. Construir imagen Docker
docker build -t todo-api:v2 ./app
docker run -p 8000:8000 todo-api:v2

# 4. Verificar Kubernetes
kubectl cluster-info
kubectl get nodes

# 5. Desplegar en Kubernetes
kubectl apply -f k8s/
kubectl get pods -n todo-app

# 6. Desplegar monitoreo
kubectl apply -f monitoring/prometheus-config.yaml
kubectl apply -f monitoring/grafana-deployment.yaml
kubectl get pods -n monitoring

# 7. Acceder a los servicios
kubectl port-forward -n todo-app svc/todo-api-service 8000:8000
kubectl port-forward -n monitoring svc/prometheus-service 9090:9090
kubectl port-forward -n monitoring svc/grafana-service 3000:3000

# 8. Ejecutar tests
cd app
pytest -v test_main.py
```

### Validación del despliegue
- API Swagger UI: http://localhost:8000/docs
- Health check: http://localhost:8000/health
- Métricas: http://localhost:8000/metrics
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000

---

## 11. Evidencias

### Pods corriendo exitosamente
```
kubectl get pods -n todo-app
NAME                       READY   STATUS    RESTARTS   AGE
todo-api-bfbb6c6c6-8zppb   1/1     Running   0          16s
todo-api-bfbb6c6c6-zxtpt   1/1     Running   0          16s
```

### Monitoreo activo
```
kubectl get pods -n monitoring
NAME                         READY   STATUS    RESTARTS   AGE
grafana-567857c7d-sbrx4      1/1     Running   0          5m42s
prometheus-7c5fc88f4-m82ks   1/1     Running   0          5m49s
```

### Todos los recursos del namespace
```
kubectl get all -n todo-app
NAME                           READY   STATUS    RESTARTS   AGE
pod/todo-api-bfbb6c6c6-8zppb   1/1     Running   0          23s
pod/todo-api-bfbb6c6c6-zxtpt   1/1     Running   0          23s

NAME                       TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)    AGE
service/todo-api-service   ClusterIP   10.96.203.152   <none>        8000/TCP   7m13s

NAME                       READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/todo-api   2/2     2            2           23s

NAME                                               REFERENCE             TARGETS         MINPODS   MAXPODS   REPLICAS
horizontalpodautoscaler.autoscaling/todo-api-hpa   Deployment/todo-api   cpu/mem: 70%/80%   2         6         2
```

*(Agregar capturas de pantalla de Swagger UI, Grafana Dashboard, Prometheus Targets y el pipeline de GitHub Actions corriendo exitosamente)*

---

## 12. Conclusiones

Este proyecto demuestra la implementación exitosa de un pipeline DevOps completo que abarca:

1. **Desarrollo**: API funcional con tests automatizados
2. **Contenedorización**: Dockerfile optimizado con multi-stage build y seguridad
3. **IaC**: Infraestructura reproducible con Terraform
4. **CI/CD**: Pipeline automatizado de 6 etapas con análisis de seguridad
5. **Orquestación**: Despliegue en Kubernetes con alta disponibilidad
6. **Monitoreo**: Observabilidad completa con Prometheus y Grafana
7. **FinOps**: Optimización de recursos con HPA y limits

La arquitectura implementada es escalable, segura y reproducible, permitiendo que cualquier desarrollador pueda replicar el entorno completo siguiendo la documentación proporcionada.
