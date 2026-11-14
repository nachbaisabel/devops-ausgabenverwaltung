# basic framework (provider and image)
terraform {
  required_version = ">= 1.5.0"

  # declare the provider for local docker
  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "~> 3.0"
    }
  }
}

provider "docker" {}

# manages the nginx image, the provider downloads it, no manual docker build needed
resource "docker_image" "nginx" {
  name         = "nginx:alpine"
  keep_locally = true
}

resource "docker_container" "nginx" {
  name  = "nginx-week7"
  image = docker_image.nginx.image_id # link to nginx image, terraform recognizes the dependency

  # maps the host port (default 8080) to nginx port 80
  ports {
    internal = 80
    external = var.host_port
  }

  volumes {
    # absolute path to the local html file
    host_path      = "${abspath(path.module)}/index.html"
    container_path = "/usr/share/nginx/html/index.html"
    read_only      = true # prevent changes by the container
  }
}