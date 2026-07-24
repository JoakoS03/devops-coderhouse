variable "app_name" {
  description = "Nombre de la aplicación"
  type        = string
  default     = "todo-api"
}

variable "app_namespace" {
  description = "Namespace para la aplicación"
  type        = string
  default     = "todo-app"
}

variable "app_image" {
  description = "Imagen del contenedor de la aplicación"
  type        = string
  default     = "todo-api:latest"
}

variable "app_port" {
  description = "Puerto en el que escucha la aplicación"
  type        = number
  default     = 8000
}

variable "replicas" {
  description = "Número inicial de réplicas"
  type        = number
  default     = 2
}

variable "cpu_request" {
  description = "Petición de CPU"
  type        = string
  default     = "100m"
}

variable "memory_request" {
  description = "Petición de memoria"
  type        = string
  default     = "128Mi"
}

variable "cpu_limit" {
  description = "Límite de CPU"
  type        = string
  default     = "250m"
}

variable "memory_limit" {
  description = "Límite de memoria"
  type        = string
  default     = "256Mi"
}

variable "environment" {
  description = "Entorno de despliegue"
  type        = string
  default     = "development"
}

variable "enable_monitoring" {
  description = "Habilitar namespace de monitoreo"
  type        = bool
  default     = true
}
