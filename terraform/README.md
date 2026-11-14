# Woche 7 – nginx mit Terraform

Terraform erstellt einen lokalen nginx-Container, der die eigene `index.html`
über einen schreibgeschützten Bind-Mount ausliefert.

---
## Voraussetzungen

- Terraform ab 1.5
- Docker läuft
- Host-Port 8080 ist frei
- Keine Python-`.venv` erforderlich

---
## Ausführen

Vom Projekt-Hauptverzeichnis:

```bash
cd terraform
terraform init          # provider laden und backend initialisieren
terraform fmt           # terraform-dateien einheitlich formatieren
terraform validate      # Success! The configuration is valid.
terraform plan          # Plan: 2 to add, 0 to change, 0 to destroy.
terraform apply         # Apply complete! Resources: 2 added, 0 changed, 0 destroyed. Outputs: web_url = "http://localhost:8080"
```

Den Plan prüfen und `apply` mit `yes` bestätigen.
Bei einer frischen Umgebung werden zwei Ressourcen angelegt.

```bash
curl -i http://localhost:8080/
```

Erwartet: HTTP 200 und die eigene HTML-Seite mit „Hausübung – Woche 7“.
Der Output `web_url` zeigt die Adresse. Sie kann auch im Browser geöffnet werden.

## Portvalidierung

```bash
terraform plan -var="host_port=80"
```

Erwartet: `Invalid value for variable` mit der Meldung
`host_port must be between 1025 and 65535.`

## Aufräumen

```bash
terraform destroy
```

Den Löschplan prüfen und mit `yes` bestätigen.
Erwartete Ausgabe: `Destroy complete! Resources: 2 destroyed.`

Container und Terraform-Image-Verwaltung werden entfernt;
das lokale Image bleibt wegen `keep_locally = true` erhalten.
Die eingebundene `index.html` bleibt ebenfalls erhalten.

## Git und Nachweis

State, `.terraform/` und echte `.tfvars` werden ignoriert.
Die `.terraform.lock.hcl` wird versioniert.

[Erstellungsplan](plan-screenshot.png)

> Grundlage: Kursmaterialien, Woche 7 – Infrastructure as Code.
