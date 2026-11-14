# Woche 7 - Infrastructure as Code
#
# > References: Course material woche-07-infrastructure-as-code/code
#
# This configuration provisions the Expenses stack on the LOCAL Docker daemon
# through the kreuzwerker/docker provider: a network, a volume, the image and
# the container. No cloud account and no credit card are required.
#
# Prerequisite - build the application image from the parent directory:
#   docker build -t expenses:local ..
#
# The same Terraform building blocks (provider, resource, state, plan/apply)
# apply to AWS, Azure and GCP. Only the resource types change.

terraform {
  # Pin the Terraform CLI. Features used here work from 1.5 onwards.
  required_version = ">= 1.5.0"

  required_providers {
    docker = {
      source = "kreuzwerker/docker"
      # Pin the provider to major version 3. Never leave this unpinned:
      # a future 4.x could rename arguments and break `apply` without warning.
      version = "~> 3.0"
    }
  }
}

# The provider talks to the local Docker daemon over its default socket
# (unix:///var/run/docker.sock on macOS/Linux). Docker Desktop sets this up.
provider "docker" {}

# --- Network -----------------------------------------------------------------
# A user-defined bridge network. Cloud equivalent: a VPC (AWS) / VNet (Azure).
resource "docker_network" "expenses" {
  name = "${var.container_name}-net"
}

# --- Volume ------------------------------------------------------------------
# A named Docker volume - the local stand-in for a cloud storage resource
# (AWS EBS volume, Azure Managed Disk). It outlives the container.
resource "docker_volume" "expense_data" {
  name = "${var.container_name}-data"
}

# --- Image -------------------------------------------------------------------
# References the image that was built locally with `docker build`.
# keep_locally = true tells Terraform NOT to delete the image on `destroy`:
# we built it ourselves, so removing it would be surprising.
resource "docker_image" "expenses" {
  name         = "expenses:${var.image_tag}"
  keep_locally = true
}

# --- Container ---------------------------------------------------------------
# The Expenses container. Cloud equivalent: the compute resource, e.g.
# aws_instance / azurerm_linux_virtual_machine / google_compute_instance.
resource "docker_container" "expenses" {
  name = var.container_name

  # Implicit dependency: by referencing image_id, Terraform knows the image
  # must exist before the container is created. This builds the dependency
  # graph automatically - no `depends_on` needed.
  image = docker_image.expenses.image_id

  # Publish container port 8000 on the host. host_port is validated (> 1024).
  ports {
    internal = 8000
    external = var.host_port
  }

  # Configuration comes from the environment (twelve-factor). 
  # APP_VERSION shows up in GET /health (and GET /metrics - not implemented yet).
  env = [
    "APP_VERSION=${var.app_version}",
    # Empty DATABASE_URL keeps the app on its in-memory store - no database is
    # needed for this lab. The app treats "" the same as unset.
    "DATABASE_URL=",
    "LOG_LEVEL=INFO",
  ]

  # Attach the container to the user-defined network created above.
  networks_advanced {
    name = docker_network.expenses.name
  }

  # Mount the named volume. The default in-memory app does not write here yet;
  # the mount shows how a storage resource is attached to a compute resource.
  volumes {
    volume_name    = docker_volume.expense_data.name
    container_path = "/data"
  }

  # Restart policy, equivalent to `restart: unless-stopped` in docker-compose.
  restart = "unless-stopped"

  # Container-level health check. The slim image ships python but not curl,
  # so the probe is a small python one-liner against /health.
  healthcheck {
    test         = ["CMD", "python", "-c", "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/health').status == 200 else 1)"]
    interval     = "30s"
    timeout      = "3s"
    retries      = 3
    start_period = "5s"
  }
}