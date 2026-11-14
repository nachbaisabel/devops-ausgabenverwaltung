# output uses the same port variable as the container
# ensure the url stays correct when the port changes

output "web_url" {
  description = "URL of the local nginx webserver."
  value       = "http://localhost:${var.host_port}"
}