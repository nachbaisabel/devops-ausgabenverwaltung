# Outputs are printed after `apply` and can be queried with `terraform output`.
# They are the documented interface of this configuration.

# > References: Course material woche-07-infrastructure-as-code/code


output "container_id" {
  description = "Full ID of the running Expenses container."
  value       = docker_container.expenses.id
}

output "container_name" {
  description = "Name of the running Expenses container."
  value       = docker_container.expenses.name
}

output "app_url" {
  description = "URL to reach the Expenses (UI and ) API on the host."
  value       = "http://localhost:${var.host_port}"
}
