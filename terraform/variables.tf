# define the host port

# nginx runs internally on port 80, default host port 8080 avoids a conflict with the expenses app on port 8000
variable "host_port" {
  type        = number
  description = "Host port for the nginx webserver."
  default     = 8080

  # check that the port is between 1025 and 65535
  validation {
    condition     = var.host_port > 1024 && var.host_port <= 65535
    error_message = "host_port must be between 1025 and 65535."
  }
}