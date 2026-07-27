# Valores por defecto para el desarrollo local (Docker Desktop)

app_name          = "todo-api"
app_namespace     = "todo-app"
app_image         = "todo-api:latest"
app_port          = 8000

replicas          = 2
cpu_request       = "100m"
memory_request    = "128Mi"
cpu_limit         = "250m"
memory_limit      = "256Mi"

environment       = "development"
enable_monitoring = true
