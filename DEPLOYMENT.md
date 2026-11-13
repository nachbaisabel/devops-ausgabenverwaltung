# Deployment-Runbook

## Umgebungen

| Umgebung | Zweck | URL |
|---|---|---|
| lokal – Flask | Entwicklung mit In-Memory | http://127.0.0.1:8000 |
| lokal – Compose | Container mit Postgres | http://localhost:8000 |
| Render | Gehostete Kursinstanz | https://expenses-dsjj.onrender.com |

---
## A - Voraussetzungen

### Konten und Zugriffsrechte
- **GitHub-Konto** mit Zugriff auf das Repository https://github.com/nachbaisabel/devops-ausgabenverwaltung
   - Für Änderungen: Berechtigung, Feature-Branches zu pushen und Pull Requests zu erstellen, Änderungen an `main` werden über Pull Requests integriert
   - Für die CD-Einrichtung: Berechtigung, GitHub-Actions-Secrets und Repository-Variablen zu verwalten, GitHub Actions muss aktiviert sein

- **Render-Konto** mit Berechtigung, das Repository zu verbinden, einen
  Docker-Web-Service per Blueprint anzulegen und dessen Einstellungen,
  Deploy-Hook und Deployments zu verwalten

### Lokale Werkzeuge

> Stand 11.11.2026 macOS:

| Werkzeug | Getestete Version | Prüfbefehl | Zweck |
|---|---|---|---|
| Git | 2.54.0 (Apple Git-157) | `git --version` | Repository klonen und Änderungen verwalten |
| Python | 3.13.5 | `python --version` | App lokal starten und Tests ausführen |
| Docker | 29.9.2 | `docker --version` | Container lokal bauen und starten |
| Docker Compose | 5.6.0 | `docker compose version` | App mit lokaler Postgres-Datenbank starten |
| curl | 8.12.1 | `curl --version` | HTTP-Endpunkte prüfen |
| Bash | 3.2.57 | `bash --version` | Smoke-Test ausführen |

### Weitere Voraussetzungen
- Python muss das Erstellen einer virtuellen Umgebung mit `venv` unterstützen.
- Die Python-Abhängigkeiten werden in Abschnitt B installiert.

- Für lokale Container-Tests muss Docker Desktop bzw. die Docker Engine laufen.
- Mit `docker info` prüfen, ob die Engine erreichbar ist.
Docker Compose wird nur für den lokalen Betrieb mit Postgres benötigt; Render baut das Docker-Image selbst.

- Internetzugang zu GitHub und Render, ein Terminal und Browser
- Zugangsdaten und Deploy-Hook-URLs vertraulich behandeln und niemals im Repository speichern

---
## B - Lokale Installation
Die folgenden Befehle gelten für macOS/Linux. Der lokale Start verwendet
In-Memory-Speicherung und benötigt keine Datenbank oder `.env`-Datei.
Die Daten gehen beim Beenden der App verloren.

### Repository klonen und Umgebung einrichten
In einem Terminal ausführen:
```bash
git clone https://github.com/nachbaisabel/devops-ausgabenverwaltung.git
cd devops-ausgabenverwaltung

python3 -m venv .venv
source .venv/bin/activate

python -m pip install -r requirements-dev.txt
```
>`requirements-dev.txt` installiert auch die Laufzeitabhängigkeiten aus `requirements.txt` sowie die Werkzeuge für Tests und Lint.

### Anwendung starten
Im selben Terminal ausführen:
```bash
unset DATABASE_URL
export APP_VERSION=1.0.0-local
export LOG_LEVEL=INFO

python -m flask --app wsgi:app run --host 127.0.0.1 --port 8000
```

>`unset DATABASE_URL` stellt sicher, dass keine zuvor gesetzte Datenbankverbindung verwendet wird.

**Erwartete Startmeldung:** `Running on http://127.0.0.1:8000`
>Das Terminal geöffnet lassen. Der Flask-Entwicklungsserver dient dem lokalen Test; auf Render startet das Docker-Image Gunicorn.

**Falls Port 8000 bereits belegt ist**, erscheint folgende Fehlermeldung:

```text
Address already in use
Port 8000 is in use by another program. Either identify and stop that program, or start the server with a different port.
```

Mögliche Lösungen:
- **Zuvor gestartete Flask-App beenden:** Im zugehörigen Terminal mit `Ctrl+C` stoppen.
- **Prozess unter macOS finden und beenden:** Den Prozess, der Port 8000 belegt, findest du mit
  `lsof -nP -iTCP:8000 -sTCP:LISTEN`.
  Die Prozessnummer steht in der Spalte `PID`. Mit `kill <PID>` beendest du den Prozess.
- **Bei Docker:** Hier nicht `kill` verwenden, sondern den Container ausfindig machen und stoppen:
  `docker ps --filter "publish=8000"`, danach `docker stop <container-id>` oder `docker stop <container-name>`.
- **Nach dem Freigeben von Port 8000:** Den Startbefehl aus diesem Abschnitt erneut ausführen. Flask und Docker Compose verwenden beide Host-Port 8000 und müssen daher abwechselnd betrieben werden.

Kontrolle, dass der Port frei ist - wenn keine Ausgabe kommt, ist 8000 frei:
```bash
lsof -nP -iTCP:8000 -sTCP:LISTEN
```

### Lokalen Healthcheck prüfen
In einem zweiten Terminal ausführen:
```bash
curl -i http://127.0.0.1:8000/health
```
**Erwartetes Ergebnis:** HTTP 200 und 
```json 
{"status":"ok","version":"1.0.0-local"}
```
Die App mit `Ctrl+C` im ersten Terminal beenden.

---
## C - Konfiguration und Secrets

### Anwendung und Container

| Variable | Standardwert | Geheim | Wo hinterlegt | Zweck |
|---|---|---|---|---|
| `DATABASE_URL` | Nicht gesetzt; bei Compose automatisch gesetzt | **Ja** | Lokal über Compose; bei Cloud-Postgres im Render-Environment | Postgres-Verbindung inklusive Zugangsdaten. Ohne Wert verwendet die App In-Memory. Auf Render aktuell nicht gesetzt. |
| `APP_VERSION` | App/Docker: `0.0.0-dev`; Compose: `1.0.0-local`; Render: `1.0.0` | Nein | Standard im App-Code und Dockerfile; Compose-Build-Argument; Render-Blueprint | Version, die `/health` ausgibt. |
| `LOG_LEVEL` | `INFO` | Nein | Standard im App-Code; Compose und Render-Blueprint | Logging-Level des Flask-App-Loggers, z. B. `DEBUG`, `INFO` oder `ERROR`. |
| `PORT` | Auf Render: `8000` | Nein | Render-Blueprint | Portkonfiguration der Plattform, passend zum Container. Gunicorn bindet im Dockerfile fest an Port 8000; eine Änderung dieser Variable allein ändert den Startbefehl nicht. |
| `GUNICORN_WORKERS` | `1` | Nein | Dockerfile, Compose und Render-Blueprint | Anzahl der Gunicorn-Worker. Bei In-Memory muss ein Worker verwendet werden, damit alle Anfragen denselben Datenbestand sehen. |
| `POSTGRES_PASSWORD` | Lokale Compose-Übungsvorgabe: `changeme` | **Ja** | Lokal in der ignorierten `.env`; Ersatzwert in Compose | Passwort der Compose-Datenbank; wird auch für deren `DATABASE_URL` verwendet. `changeme` ist ausschliesslich ein Übungswert. |
| `POSTGRES_USER` | `expenses` | Nein | Compose-Datei, Service `db` | Benutzername der lokalen Postgres-Datenbank. |
| `POSTGRES_DB` | `expenses` | Nein | Compose-Datei, Service `db` | Name der lokalen Postgres-Datenbank. |
| `PYTHONDONTWRITEBYTECODE` | `1` im Container | Nein | Dockerfile | Verhindert das Schreiben von Python-Bytecode-Dateien. |
| `PYTHONUNBUFFERED` | `1` im Container | Nein | Dockerfile | Gibt Python-Ausgaben ohne Pufferung aus, damit Logs zeitnah sichtbar sind. |

### Deployment und Smoke-Test

| Variable | Standardwert | Geheim | Wo hinterlegt | Zweck |
|---|---|---|---|---|
| `RENDER_DEPLOY_HOOK` | Kein Standardwert | **Ja** | GitHub Repository Secret | Vollständige Deploy-Hook-URL zum Auslösen eines Render-Deployments. |
| `APP_URL` | Kein Standardwert; gesetzt auf `https://expenses-dsjj.onrender.com` | Nein | GitHub Repository Variable | Öffentliche Zieladresse für den Smoke-Test im CD-Workflow. |
| `WAIT_SECONDS` | `90` | Nein | `.github/workflows/cd.yml` | Wartezeit in Sekunden nach dem Deploy-Aufruf, bevor der Smoke-Test beginnt. |
| `HEALTH_RETRIES` | `12` | Nein | Standard in `scripts/smoke-test.sh`; bei Bedarf beim Aufruf überschreibbar | Maximale Anzahl der Healthcheck-Versuche. |
| `BACKOFF_SECONDS` | `5` | Nein | Standard in `scripts/smoke-test.sh`; bei Bedarf beim Aufruf überschreibbar | Basis der steigenden Wartezeit zwischen Versuchen: 5, 10, 15 Sekunden usw. |

### Verwaltung von Secrets

Echte Secrets stehen **nie** im Repository oder in diesem Dokument.

- **Lokal:** Zugangsdaten können in der durch `.gitignore` ausgeschlossenen
  `.env` gespeichert werden. Docker Compose liest diese Datei automatisch.
  Der direkte Flask-Start lädt sie im aktuellen Projekt nicht automatisch.
   - **Beispielkonfiguration:** `.env.example` enthält nur Platzhalter und unkritische Beispielwerte.
- Passwörter und vollständige Deploy-Hook-URLs dürfen nicht in Logs,
  Screenshots, Commits oder Pull-Request-Beschreibungen veröffentlicht werden.

Nicht geheime Render-Einstellungen werden im `render.yaml` versioniert.
In-Memory-Daten gehen beim Neustart, Deployment oder Einschlafen des
Render-Service verloren.

---
## D - Deployment auf Render

### Einmalige Einrichtung per Blueprint
1. Bei Render kostenlos anmelden: https://dashboard.render.com.
2. Sicherstellen, dass die folgenden Dateien im GitHub-Repository
   `nachbaisabel/devops-ausgabenverwaltung` im `main` Branch vorhanden sind:
   - `render.yaml`
   - `Dockerfile`
   - `.github/workflows/ci.yml`
   - `.github/workflows/cd.yml`
   - `scripts/smoke-test.sh`
3. In Render **New → Blueprint** wählen.
4. Das GitHub-Konto verbinden und Render Zugriff auf das Repository
   `devops-ausgabenverwaltung` geben. Beim Repository auf **Connect** klicken.
5. Einen Blueprint-Namen vergeben, den Branch `main` wählen und als
   Blueprint-Pfad `render.yaml` verwenden.
6. Die aus dem Blueprint gelesene Konfiguration kontrollieren:

   | Einstellung | Wert |
   |---|---|
   | Service-Name | `expenses` |
   | Service-Typ | Web Service |
   | Runtime | Docker |
   | Branch | `main` |
   | Root Directory | Leer lassen; Repository-Hauptverzeichnis |
   | Dockerfile-Pfad | `./Dockerfile` |
   | Docker-Build-Kontext | `./` |
   | Instance Type | Free |
   | Region | Frankfurt |
   | Health Check Path | `/health` |
   | Auto-Deploy | Off (`autoDeployTrigger: off`) |
   | `PORT` | `8000` |
   | `GUNICORN_WORKERS` | `1` |
   | `APP_VERSION` | `1.0.0` |
   | `LOG_LEVEL` | `INFO` |
   | `DATABASE_URL` | Nicht setzen; zunächst In-Memory |

   Den Startbefehl nicht überschreiben: Das Dockerfile startet Gunicorn
   bereits auf `0.0.0.0:8000`.

7. Mit **Deploy Blueprint** die Ressourcen erstellen und den ersten
   Build und Deploy starten.
8. Den erstellten Service öffnen. Unter **Events/Deploys** den Fortschritt
   und die Build- bzw. Laufzeit-Logs verfolgen. Warten, bis der Status
   **Live** angezeigt wird.
9. Die öffentliche Service-URL notieren. Für diese Instanz lautet sie:
   https://expenses-dsjj.onrender.com
   Bei einer neuen Instanz die dort angezeigte URL verwenden.

### GitHub Actions mit Render verbinden

1. Im Render-Service unter **Settings → Deploy Hook** die vollständige
   Deploy-Hook-URL kopieren. Diese URL ist geheim und darf **niemals** öffentlich abgelegt werden.
2. Im GitHub-Repository unter
   **Settings → Secrets and variables → Actions** folgende Werte anlegen:

   | Name | Ablage | Inhalt |
   |---|---|---|
   | `RENDER_DEPLOY_HOOK` | Repository Secret | Kopierte Deploy-Hook-URL |
   | `APP_URL` | Repository Variable | Öffentliche Render-Service-URL ohne abschliessenden Slash |

3. Im Render-Service unter **Settings** kontrollieren, dass
   **Auto-Deploy auf Off** steht. Reguläre Codeänderungen werden über den
   CD-Workflow deployt.

4. Zum ersten Test in GitHub unter
   **Actions → CD → Run workflow** den Branch `main` auswählen und den
   Workflow starten. Dieser manuelle Start prüft die CI nicht erneut;
   deshalb zuvor einen grünen CI-Lauf auf `main` sicherstellen.

### Wiederkehrendes Deployment

1. Änderungen auf einem Feature-Branch erstellen und einen Pull Request
   nach `main` öffnen.
2. Die CI-Prüfungen abwarten und den Pull Request nach erfolgreicher
   Prüfung mergen.
3. Nach erfolgreichem Abschluss des CI-Workflows auf `main` startet
   der CD-Workflow automatisch. Er ruft den Render-Deploy-Hook auf,
   wartet 90 Sekunden und führt den Smoke-Test gegen `APP_URL` aus.
4. Den Ablauf an beiden Stellen beobachten:
   - GitHub: **Actions → CD**
   - Render: **Events/Deploys**, Auslöser **Deploy Hook**
Änderungen an `render.yaml` können zusätzlich einen Blueprint-Sync mit
Deployment auslösen und müssen deshalb bewusst vorgenommen werden.

---
## E - Verifikation nach dem Deploy

### Healthcheck 
Im Terminal prüfen, ob die Anwendung erreichbar ist:
```bash
curl -i https://expenses-dsjj.onrender.com/health
```
**Erwartete Ausgabe:** HTTP 200 und bei `APP_VERSION=1.0.0`:
```json
{"status":"ok","version":"1.0.0"}
```

### Smoke-Test
Im lokalen Projekt-Hauptverzeichnis ausführen:
```bash
bash scripts/smoke-test.sh https://expenses-dsjj.onrender.com
```

**Erwartete Ausgabe:**
- `/health`: HTTP 200 und Status `ok`.
- `/ready`: HTTP 200 und Status `ready`.
- Ausgabe anlegen: HTTP 201.
- Ausgabenliste abrufen: HTTP 200; Testausgabe vorhanden.
- Testausgabe löschen: HTTP 200.
- Abschliessende Ausgabe: `SMOKE TEST PASSED`.

Bei einem Fehler endet das Skript mit einem Exit-Code ungleich 0.

### GitHub Actions und Logs
Im automatischen Deployment steht dasselbe Ergebnis in GitHub unter
**Repository → Actions → CD → deploy → Smoke-test the running service**:
- Der CD-Lauf muss grün sein und
- der Schritt **Smoke-test the running service** mit folgendem Text enden: `SMOKE TEST PASSED`

> Der Smoke-Test prüft die erreichbare Anwendung. Die feste Wartezeit garantiert allein noch nicht, dass der neueste Deploy abgeschlossen ist. Deshalb zusätzlich den Commit und den Status **Live** in Render prüfen.

### Render-Status und Logs
Unter **Render → Service expenses → Events/Deploys** prüfen:
- Das gewünschte Deployment hat den Status **Live**.
- Der angezeigte Commit stimmt mit dem vorgesehenen Stand von `main` überein.

In den Laufzeit-Logs sind beim Smoke-Test folgende Anfragen mit diesen
Statuscodes zu erwarten:
```text
GET /health          200
GET /ready           200
POST /api/expenses   201
GET /api/expenses    200
DELETE /api/expenses/<id>   200
```
>`<id>` ist die automatisch vergebene ID der Testausgabe.

**Nachweis der laufenden Render-Instanz:**
[Healthcheck mit sichtbarer URL und Versionsausgabe](screenshots/w6_healthcheck.png)

---
## Deployment auf Kubernetes (lokal, kind)

```bash
kind load docker-image <image>:<tag>
kubectl apply -f k8s/
kubectl rollout status deployment/<week8> -n <week8space>
```

**Kontrolle:** `kubectl get pods -n <week8space>` zeigt ≥ 2 Pods `Running` / `1/1`.

---
## F - Rollback

Wenn ein neues Deploy Fehler verursacht, kann man auf die vorherige funktionierende Version mit einem Rollback zurückkehren.

Der Ablauf hängt von der Deployment-Umgebung ab.
Die folgenden Abschnitte beschreiben den Ablauf für Render und in Woche 8 für Kubernetes. 
Anschliessend wird mit dem Smoke-Test geprüft, ob die Anwendung wieder funktioniert.

### Render

1. Im Render-Service `expenses` unter **Events/Deploys** ein vorheriges erfolgreiches Deployment auswählen und **Rollback** bestätigen.
2. Auf Status **Live** warten und den angezeigten Commit kontrollieren.
3. Im lokalen Projektverzeichnis den Smoke-Test ausführen:
   ```bash
   bash scripts/smoke-test.sh https://expenses-dsjj.onrender.com
   ```
   **Erwartete Ausgabe:** `/health` und `/ready` liefern HTTP 200; Anlegen, Abrufen und Löschen funktionieren. Abschliessend steht `SMOKE TEST PASSED`.

4. Nach Behebung des Fehlers die aktuelle Version mit **Manual Deploy → Deploy latest commit** wiederherstellen. Zuvor sicherstellen, dass der neueste Stand auf `main` funktioniert.
5. Auf **Live** warten und denselben Smoke-Test erneut ausführen.

**Grenzen:**
- In-Memory-Ausgaben gehen beim Neustart verloren.
- Eine externe Datenbank und deren Schema werden nicht zurückgesetzt.
- GitHub-Branch `main` bleibt unverändert. Ein erneutes CD-Deployment
  kann deshalb den fehlerhaften Stand wieder einspielen.
- Das frühere Build-Artefakt muss auf Render noch verfügbar sein.

### Kubernetes

`kubectl rollout undo deployment/<week8> -n <week8space>`

--- 
## G - Störungsbehandlung / Troubleshooting

### Bereits beobachtete Fehlerbilder

| Symptom | Erste Prüfung | Ursache | Massnahme |
|---|---|---|---|
| `/ready`: auf Render 404, lokal 200 | Live-Commit mit `main` vergleichen | Alte Version ohne `/ready` läuft | Aktuellen Stand deployen und Smoke-Test ausführen |
| CD-Workflow nicht sichtbar | Dateipfad prüfen | `cd.yml` im falschen Ordner | Nach `.github/workflows/cd.yml` verschieben und per PR integrieren |
| CI-Formatprüfung schlägt fehl | Datei laut Fehlermeldung prüfen | Zusätzliche Leerzeilen oder Leerzeichen | `ruff format <Datei>` ausführen, erneut prüfen und committen |
| Erster Aufruf nach Pause langsam | Status und Dauer zweier Aufrufe vergleichen | Render-Free-Cold-Start | Auf Aufwachen warten; Smoke-Test mit Wiederholungen nutzen. Gemessen: 23,40 s → 0,16 s, beide HTTP 200 |

### Weitere mögliche Störungen

| Symptom | Erste Prüfung | Mögliche Ursache | Massnahme |
|---|---|---|---|
| `/ready` liefert 503 | Bei Postgres-Betrieb Datenbankstatus und App-Logs prüfen | Repository meldet nicht verfügbar, z. B. durch unterbrochene DB-Verbindung | Datenbankverfügbarkeit und `DATABASE_URL` prüfen, Verbindung korrigieren und Smoke-Test wiederholen |
| Deployment hängt oder scheitert | Render-Build- und Laufzeit-Logs prüfen | Fehler beim Image-Build oder App-Start | Erste konkrete Fehlermeldung beheben; z. B. Dockerfile-Pfade oder Abhängigkeiten korrigieren und erneut deployen |
| `/health` unerreichbar | Render-Status, Logs und Port prüfen | App läuft nicht oder lauscht auf falschem Port bzw. Interface | Gunicorn-Bindung auf `0.0.0.0:8000` und Render-Variable `PORT=8000` prüfen; korrigieren und erneut testen |

---
## H – Kontakt und Eskalation

| Rolle | Zuständigkeit | Kommunikationsweg |
|---|---|---|
| Service-Owner: Isabelle Nachbaur | Fehler prüfen, Logs auswerten, Deployment oder Rollback durchführen | GitHub-Issue im Projekt-Repository |
| Kursleitung | Unterstützung bei ungelösten technischen Problemen | Moodle oder E-Mail |
| Render-Support | Unterstützung bei Problemen der Hosting-Plattform | Render-Supportkanal |

Kann eine Störung nach 30 Minuten eigener Fehlersuche nicht behoben werden,
wird die Kursleitung kontaktiert. Bei einem vermuteten Plattformproblem
wird zusätzlich der Render-Support einbezogen.

Die Meldung enthält:
- betroffene URL und Zeitpunkt,
- Symptom und Fehlermeldung,
- deployten Commit,
- bereits durchgeführte Prüfungen und Massnahmen.

>Logs und Screenshots nur ohne Passwörter oder Deploy-Hook-URLs weitergeben.
