# Ausgabenverwaltung mit Terraform (lokaler Docker-Provider)

Lauffähige Terraform-Konfiguration, die den Expenses-Stack auf dem **lokalen**
Docker-Daemon anlegt: Terraform verwaltet Netzwerk, Volume, Image und Container. 
Es werden **keine** Cloud, **kein** Konto und **keine** Python-`.venv` benötigt – der Provider ist `kreuzwerker/docker`.

> Grundlage: Kursvorlagen woche-07-infrastructure-as-code/code


## Voraussetzung

- Terraform ab Version 1.5: `terraform version`.
- Docker Desktop bzw. Docker Engine läuft: `docker info`.
- Das Image `expenses:local` muss vor `apply` lokal vorhanden sein, da die Konfiguration es nicht selbst baut. Ohne dieses Image versucht der Docker-Provider, `expenses:local` aus einer Registry zu laden, und bricht mit `pull access denied` ab.
- Host-Port 8000 ist frei; gegebenenfalls die lokale Flask-App oder andere
  Container auf diesem Port stoppen.

Aus dem Projekt-Hauptverzeichnis `devops-ausgabenverwaltung` ausführen:

```bash
docker info >/dev/null && echo "Docker läuft"
docker build -t expenses:local .
docker images expenses:local
```

**Erwartete Ausgabe:**
```text
Docker läuft

IMAGE            ID             DISK USAGE   CONTENT SIZE   EXTRA
expenses:local   6af1cdb51555        249MB         53.6MB        
```
> Image-ID, Grösse und Tabellenformat können abweichen.

## Dateien

| Datei | Inhalt |
|---|---|
| `main.tf` | `terraform`-Block, Provider, `docker_network`, `docker_volume`, `docker_image`, `docker_container` |
| `variables.tf` | `container_name`, `host_port` (mit `validation`), `image_tag`, `app_version` |
| `outputs.tf` | `container_id`, `container_name`, `app_url` |
| `terraform.tfvars.example` | Vorlage für eigene Werte (nach `terraform.tfvars` kopieren) |
| `.terraform.lock.hcl` | Gewählte Provider-Version und Prüfsummen; wird versioniert |
| `.gitignore` | schliesst State, `.terraform/` und `*.tfvars` aus |

## Ablauf

Befehle einzeln ausführen im Terraform-Folder `terraform-expenses`:
```bash
cd terraform-expenses
terraform init      # Provider laden, Lock-Datei schreiben
terraform fmt       # Formatierung prüfen/anwenden
terraform validate  # Syntax prüfen
terraform plan      # Vorschau: "Plan: 4 to add, 0 to change, 0 to destroy."
terraform apply     # anlegen (mit yes bestätigen)
```

Nach dem Start die HTTP-Bereitschaft prüfen. Ein erfolgreicher `apply` bedeutet
nicht, dass Gunicorn bereits Anfragen annimmt. Deshalb bei Startverzögerungen
kurz warten und den Aufruf wiederholen:

```bash
curl http://localhost:8000/health
bash ../scripts/smoke-test.sh http://localhost:8000
```

**Erwartete Ausgabe:**
```json
{"status":"ok","version":"1.0.0-iac"}
```

Der Smoke-Test endet nach erfolgreichen Prüfungen mit:

```text
SMOKE TEST PASSED
```
Das Volume ist unter `/data` eingehängt. Die App verwendet ohne `DATABASE_URL`
weiterhin In-Memory: Ein Volume allein macht ihre Ausgaben nicht persistent.

## State, Outputs und Idempotenz

```bash
terraform state list   # zeigt die vier verwalteten Ressourcenadressen
terraform output       # zeigt app_url, container_id, container_name
terraform plan         # `No changes. Your infrastructure matches the configuration.`
```

State-Dateien und echte Variablendateien gehören nicht ins Repository und werden
nicht von Hand bearbeitet. `.terraform.lock.hcl` gehört dagegen ins Repository.

Drift wurde durch manuelles Löschen des Containers `expenses` erzeugt.
Der anschliessende Plan erkannte den fehlenden Container: `1 to add, 0 to change, 0 to destroy`.
Nach `apply` wurde der Container wiederhergestellt; der Smoke-Test war erfolgreich.

## Werte anpassen

Defaults: 
- `container_name = "expenses"`
- `host_port = 8000`
- `image_tag = "local"`
- `app_version = "1.0.0-iac"`

Beispielsweise Port und sichtbare App-Version ändern:

```bash
terraform plan -var="host_port=8080" -var="app_version=1.1.0-iac"
terraform apply -var="host_port=8080" -var="app_version=1.1.0-iac"
curl -i http://localhost:8080/health
```

**Beispielausgabe:** `Apply complete! Resources: 1 added, 0 changed, 1 destroyed.`
`app_url = "http://localhost:8080"`

Der Container-Port bleibt 8000. Kommandozeilenwerte gelten nur für den jeweiligen
Aufruf. Für wiederkehrende eigene Werte kann eine ignorierte `terraform.tfvars`
angelegt werden; diese wird automatisch geladen.

Die angegebenen Ressourcenanzahlen gelten für den beschriebenen Ausgangszustand. Bei bereits vorhandenen Ressourcen können sie abweichen.
Vor jedem `apply` den tatsächlichen Plan prüfen.

### Eigene Werte über eine Variablendatei setzen
Im Ordner `terraform-expenses` die Vorlage kopieren:

```bash
cp terraform.tfvars.example terraform.tfvars
```
In `terraform.tfvars` die gewünschten Werte eintragen.
Danach ohne zusätzliche Flags ausführen:

```bash
terraform plan
terraform apply
```

Terraform liest `terraform.tfvars` automatisch ein.
Mit der unveränderten Vorlage ist die App unter `http://localhost:8000`
erreichbar. Bei einem anderen `host_port` die URL entsprechend anpassen.
Kommandozeilenwerte mit `-var` überschreiben Werte aus der Datei.

Die echte `terraform.tfvars` bleibt aus Git ausgeschlossen; nur die Vorlage `terraform.tfvars.example` wird versioniert.

### Portvalidierung prüfen
```bash
terraform plan -var="host_port=80"
```

**Erwartete Ausgabe:** `Invalid value for variable` und der Hinweis auf den erlaubten Bereich `host_port must be an unprivileged port between 1025 and 65535`. 
Es werden keine Infrastrukturänderungen ausgeführt.

## Aufräumen

```bash
terraform destroy
```
Den Löschplan prüfen und mit `yes` bestätigen.
Erwartet bei vier verwalteten Ressourcen:

```text
Destroy complete! Resources: 4 destroyed.
```

Container, Netzwerk und Volume werden entfernt; Daten im Volume gehen verloren.
Das Image bleibt dank
`keep_locally = true` erhalten (prüfbar mit `docker images expenses:local`).

## Nachweise

- [Plan – Teil 1](plan_screenshot1.png)
- [Plan – Teil 2](plan-screenshot2.png)

