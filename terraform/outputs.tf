output "namespace_name" {
  description = "Nombre del namespace donde se desplegó la aplicación"
  value       = kubernetes_namespace.app.metadata[0].name
}

output "service_name" {
  description = "Nombre del servicio de Kubernetes de la aplicación"
  value       = kubernetes_service.app.metadata[0].name
}

output "app_url" {
  description = "URL para acceder a la aplicación a través de Ingress"
  value       = "http://${kubernetes_ingress_v1.app.spec[0].rule[0].host}"
}

output "deployment_name" {
  description = "Nombre del deployment creado para la aplicación"
  value       = kubernetes_deployment.app.metadata[0].name
}
