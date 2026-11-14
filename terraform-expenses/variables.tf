# Input variables. Values come (in order of precedence) from -var flags,
# *.tfvars files, TF_VAR_* environment variables and finally these defaults.

# > References: Course material woche-07-infrastructure-as-code/code


variable "container_name" {
  type        = string
  description = "Name of the Expenses container and prefix for its network and volume."
  default     = "expenses"
}

variable "host_port" {
  type        = number
  description = "Host port that is mapped to the container's port 8000."
  default     = 8000

  validation {
    # Ports 0-1024 are privileged. Keep the lab on an unprivileged port.
    condition     = var.host_port > 1024 && var.host_port <= 65535
    error_message = "host_port must be an unprivileged port between 1025 and 65535."
  }
}

variable "image_tag" {
  type        = string
  description = "Tag of the locally built image (expenses:<image_tag>)."
  default     = "local"
}

variable "app_version" {
  type        = string
  description = "Value of APP_VERSION inside the container; appears at GET /health."
  default     = "1.0.0-iac"
}
