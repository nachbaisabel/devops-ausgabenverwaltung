# ToDo-Liste für alle Wochen

> Diese ToDo-Liste wurde mit Codex auf Grundlage der Kursunterlagen erstellt.

Mein Kurs: **CDS212 – DevOps** · Mein Projekt: **Ausgabenverwaltung**

**Nachweise Screenshots:** `/screenshots`
- [x] Woche 1
- [x] Woche 2
- [x] Woche 3
- [x] Woche 4
- [x] Woche 5
- [x] Woche 6
- [x] Woche 7
- [ ] Woche 8
- [ ] Woche 9
- [ ] Woche 10

**Aktuell: Woche 7 – Terraform-Dokumentation und PR abschliessen.**



## Hausübungen & Lernmaterialien

- https://github.com/nachbaisabel/devops-course/

---
## Offene ToDos aller Wochen

### Spätere ToDos:
- [ ] einfaches HTML-Frontend: `GET` `/`
- [ ] API Metriken ergänzen: `GET` `/metrics` 
- [ ] API Statistiken ergänzen: `GET` `/api/expenses/stats` 

### Noch offen W6

- [ ] Kubernetes-Platzhalter im Runbook bis Woche 8 durch einen kurzen Ausblick ersetzen.
- [ ] Abschliessenden CI/CD-Lauf zu PR #25 bestätigen; die zuvor erfolgreichen Läufe sind oben dokumentiert.
- [ ] Empfohlene Ergänzung: automatisierte `/ready`-Tests für verfügbares (200) und nicht verfügbares Repository (503).

### Optionale Erweiterungen W7

- [ ] Bonus der Hausübung: zwei nginx-Instanzen mit verschiedenen Ports über `for_each` (keine kopierten Ressourcenblöcke) erzeugen; beide URLs als Output ausgeben und prüfen.
- [ ] Optionales Projektziel später: Postgres über Terraform verwalten und echte Persistenz prüfen.


---
## Woche 01 – Vorbereitung

Noch keine Anwendung implementiert. Projektthema Ausgabenverwaltung gewählt
und Werkzeuge geprüft. Linux-Übungen und Reflexion liegen im Kurs-Repository.
Zunächst wurde Conda verwendet; inzwischen erfolgt die lokale Entwicklung in `.venv`.

---
## Woche 02 – Repository und Arbeitsweise

- [x] Öffentliches Projekt-Repository und GitHub-Profil eingerichtet; Dozent eingeladen.
- [x] README, Python-`.gitignore` und MIT-Lizenz vorbereitet.
- [x] GitHub Flow und Commit-/PR-Regeln in `CONTRIBUTING.md` dokumentiert.
- [x] `main` gegen direkte Pushes geschützt; Änderungen über Branches und PRs integriert.

### Git-Stand und Zugriff prüfen

```bash
git status
git branch --show-current
git remote -v
git log --oneline --no-merges
```

Der Remote verwendet HTTPS. Ein zusätzlicher SSH-Schlüssel war für die
vorhandene Git-/VS-Code-Anmeldung nicht nötig. Zugangsdaten gehören nicht ins Repository.

### Durchgeführter PR-Ablauf

Auf Branches wie `docs/project-setup` und `docs/project-scope` wurden Änderungen
vorgemerkt, geprüft, committed und gepusht. Beispiel aus dem Projektaufbau:

```bash
git add README.md CONTRIBUTING.md
git diff --staged
git commit -m "docs: define project scope and workflow"
git push -u origin docs/project-scope
```

Den PR auf GitHub prüfen und mergen; anschliessend den Stand lokal holen:

```bash
git switch main
git pull --ff-only
```

---
## Woche 03 – Flask-App und Tests

- [x] Flask-App mit `create_app()`, WSGI-Einstiegspunkt und `/health` aufgebaut.
- [x] Routen in einem Blueprint gebündelt und in der App registriert.
- [x] Expense-Modell, Validierung und In-Memory-Repository mit automatischen IDs erstellt.
- [x] Ausgaben erfassen, auflisten, ändern und löschen implementiert.
- [x] JSON-Fehlerantworten mit 400 und unbekannte IDs mit 404 geprüft.
- [x] Gemeinsamen Testclient in `tests/conftest.py` eingerichtet.
- [x] 13 Ausgabentests und ein Health-Test bestanden; 14 Tests insgesamt.

Die folgenden Befehle zeigen den aktuellen Stand: `.venv` statt der anfänglich
verwendeten Conda-Umgebung; 
Beträge seit Woche 4 als Dezimalstrings statt Float und Daten als Date statt Strings.

### Lokal einrichten und starten

Nur beim ersten Einrichten die Umgebung erstellen:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
python wsgi.py
```

Ohne `DATABASE_URL` verwendet die App In-Memory. In einem zweiten Terminal prüfen:

```bash
curl http://localhost:8000/health
curl -i -X POST http://localhost:8000/api/expenses \
  -H "Content-Type: application/json" \
  -d '{"title":"Mittagessen","amount":"12.50","date":"2026-11-06","category":"Food"}'
curl http://localhost:8000/api/expenses
```

Erwartet: Health 200, POST 201 mit ID, anschliessend die Ausgabe in der Liste.
Flask und Docker verwenden lokal Port 8000; immer nur eine der beiden Varianten starten.

### Automatisierte Tests

Im Projektordner mit aktivierter Umgebung ausführen; ein Server ist nicht nötig:

```bash
source .venv/bin/activate
python -m pytest tests/test_health.py -v
python -m pytest tests/test_expenses.py -v
python -m pytest tests/ -v
```

Geprüft: leere Liste, Anlegen und Auflisten, eindeutige IDs, optionale Beschreibung,
Ändern und Löschen, unbekannte IDs, ungültige Kategorie/JSON/Body und unveränderte
Daten nach einem abgelehnten Update. Der trotz seines Namens bestehende Test
`test_get_single_expense` prüft die Listenantwort, keinen Einzelabruf-Endpunkt.

Ergebnis: **14 passed** im In-Memory-Pfad. Postgres wurde erst in Woche 4 manuell
geprüft.

---
## Woche 04 – Die eigene Anwendung containerisieren

- [x] Multi-Stage-Dockerfile mit Slim-Basis und sinnvoller Cache-Reihenfolge erstellen.
- [x] `.dockerignore` ergänzen und Image erfolgreich bauen.
- [x] App mit Gunicorn als `appuser` starten; Healthcheck und API auf Host-Port 8000 prüfen.
- [x] Compose mit `web`, Postgres 16, DB-Healthcheck und benanntem Volume einrichten.
- [x] Postgres-Repository implementieren und anhand von `DATABASE_URL` auswählen.
- [x] Beträge auf `Decimal` und Datumswerte auf `date` umstellen; 14 lokale Tests bestanden.
- [x] Anlegen, Ändern und Löschen über die API mit Postgres prüfen.
- [x] Persistenz nach `down` und erneutem Start nachweisen; Unterschied zu `down -v` erklären.
- [x] README und Testabläufe dokumentieren; Optimierungen mit geschätzten Vergleichswerten begründen.


### Dockerfile schreiben & testen
```bash
docker build -t ausgabenverwaltung:local .
docker run -d -p 127.0.0.1:8000:8000 --name ausgabenverwaltung ausgabenverwaltung:local

curl -i -X POST http://localhost:8000/api/expenses \
  -H "Content-Type: application/json" \
  -d '{"title":"Mittagessen","amount":"12.50","date":"2026-11-06","category":"Food"}'

curl http://localhost:8000/api/expenses
```

Der Einzelcontainer verwendet ohne `DATABASE_URL` In-Memory. Vor dem Compose-Start
den Einzelcontainer stoppen und entfernen, falls er noch Port 8000 belegt:

```bash
docker stop ausgabenverwaltung
docker rm ausgabenverwaltung
```

### Compose-Stack starten

```bash
docker compose up --build -d
docker compose ps
docker compose logs --tail=30 web
```

### Datenbank testen
1) Ausgabe anlegen --> erwartete Ausgabe: 201 Created
```bash
curl -i -X POST http://localhost:8000/api/expenses \
  -H "Content-Type: application/json" \
  -d '{"title":"Postgres-Test","amount":"12.50","date":"2026-11-06","category":"Food"}'
```
2) Ausgabe in der Datenbank überprüfen
```bash
docker compose exec db psql -U expenses -d expenses \
  -c "SELECT id, title, amount, date FROM expenses ORDER BY id;"
```

3) Persistenz überprüfen
```bash
docker compose down
docker compose up -d
```

4) Datenbank erneut überprüfen – vorher auf einen gesunden Web-Container warten.
Die Ausgabe muss nach `down` und erneutem Start noch vorhanden sein.
```bash
curl http://localhost:8000/api/expenses
```

5) Testausgabe ändern
```bash
curl -i -X PUT http://localhost:8000/api/expenses/1 \
  -H "Content-Type: application/json" \
  -d '{"title":"Postgres-Test geändert","amount":"15.00","date":"2026-11-06","category":"Food","description":"Update getestet"}'
curl http://localhost:8000/api/expenses
```

6) Testausgabe löschen
```bash
curl -i -X DELETE http://localhost:8000/api/expenses/1
curl http://localhost:8000/api/expenses
```

7) Bereits gelöschte ID erneut löschen – erwartet: 404 mit `Expense not found`.
Die ID 1 stammt aus meinem Testlauf; beim Wiederholen die tatsächlich zurückgegebene ID verwenden.

```bash
curl -i -X DELETE http://localhost:8000/api/expenses/1
```

**Beobachtetes Ergebnis:** POST 201, Datensatz per SQL bestätigt, nach Compose-Neustart weiterhin vorhanden, PUT 200 mit gespeicherten Änderungen, DELETE 200 und danach leere Liste; erneutes Löschen liefert die Fehlermeldung für eine unbekannte ID.

### Persistenz mit benanntem Volume: `down` und `down -v` (vgl. 6)

Postgres speichert seine Daten im benannten Volume `db-data`, eingebunden unter
`/var/lib/postgresql/data` im Datenbankcontainer.

- **`docker compose down`:** Stoppt und entfernt die Container sowie das Compose-Netzwerk. Das benannte Volume bleibt erhalten. Nach `docker compose up -d` sind die gespeicherten Ausgaben weiterhin vorhanden.
- **`docker compose down -v`:** Entfernt zusätzlich das benannte Volume. Damit gehen die darin gespeicherten Daten verloren; beim nächsten Start entsteht eine neue, leere Datenbank.

**Mein Nachweis:** Die Ausgabe „Postgres-Test“ mit ID 1 und Betrag „12.50“ war
nach `down` und erneutem `up` weiterhin per GET abrufbar. Das Löschen des Volumes
mit `-v` wurde für diese Projektprüfung nicht ausgeführt.


### Optimierung begründen

- **Schlankes Basis-Image:** `python:3.12-slim` enthält weniger vorinstallierte Pakete; dadurch kleineres Image und geringere Angriffsfläche.
- **Multi-Stage-Build:** Abhängigkeiten werden im Builder installiert; das Runtime-Image übernimmt die benötigten Installationsergebnisse.
- **Layer-Reihenfolge:** Erst Abhängigkeiten, dann Anwendungscode kopieren. Bei reinen Codeänderungen bleibt die Installation im Cache; der Build wird schneller.
- **`.dockerignore`:** Schliesst `.git`, `.venv`, Tests und `.env` aus. Das reduziert den Build-Kontext und verhindert das versehentliche Kopieren dieser lokalen Dateien ins Image.
- **Unprivilegierter Benutzer:** Gunicorn läuft als `appuser` statt root; das begrenzt die Rechte bei einem Angriff.
- **Kein pip-Cache:** `--no-cache-dir` vermeidet zusätzliche Download-Dateien im Image.
- **Grössenvergleich:** Naives Image ca. **1,05 GB**, optimiertes Image ca. **230 MB**. Rechnerische Einsparung ca. **820 MB bzw. 78 %** (1 GB = 1000 MB).

--
## Woche 05 – Continuous Integration

- [x] Issue und Branch `ci/add-quality-gates` für die CI einrichten
- [x] Ruff und pytest-cov in den Entwicklungsabhängigkeiten ergänzen
- [x] Lint und Formatierung lokal bereinigen
- [x] Validierungstests ergänzen; 45 Tests bestanden
- [x] Coverage-Gate mit mindestens 80 % konfigurieren; lokal 82,56 % erreicht
- [x] Workflow mit Lint, Formatprüfung, Testmatrix, Docker-Build und Smoke-Test vorbereiten
- [x] Erfolgreiche CI-Läufe für alle Jobs auf GitHub prüfen
- [x] Erforderliche Status-Checks im Branch-Schutz von `main` festlegen
- [x] Absichtlichen Fehler im PR nachweisen: rot und Merge gesperrt, danach korrigiert und grün
- [x] Rote und grüne Checks mit Screenshots und PR-Link dokumentieren
- [x] CI-Badge in der README ergänzen

### 1 – Werkzeuge installieren und Ausgangszustand prüfen

- virtuelle Umgebung aktivieren
- `requirements-dev.txt` mit `ruff` und `pytest-cov` ergänzt

```bash
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
python -m ruff check .
python -m ruff format --check .
python -m pytest --cov=app --cov-report=term-missing
```

**Ergebnis:** 
- 14 passed, Total coverage: 75 %
- ruff meldet: unsortierte Imports und unbenutzter Import, 7 zu formatierende Dateien

### 2 – Lint und Formatierung bereinigen

```bash
python -m ruff check . --fix
python -m ruff format .
```
- erste Korrekturlauf behebt 7 von 8 Lint-Befunden, 1 Fehler wird behoben
- anschliessend erneut prüfen und den Diff kontrollieren:

```bash
python -m ruff check .
python -m ruff format --check .
git diff
```

**Ergebnis:** `All checks passed!`, elf Dateien bereits formatiert

### 3 – Validierungen direkt testen

- neue Datei: `tests/test_models.py` --> Tests rufen die Validierungsfunktionen
direkt auf
- `pytest.mark.parametrize` führt dieselbe Funktion für jeden Eingabewert aus
- `pytest.raises(ValidationError)` erwartet die Ablehnung einer ungültigen Eingabe

```bash
python -m pytest tests/test_models.py -v
python -m pytest --cov=app --cov-report=term-missing
```
**Ergebnis:** Total coverage: 82.56%, 45 passed


### 4 – Coverage-Gate konfigurieren

`pyproject.toml` liefert unter 80 % einen Fehlerstatus:

```toml
[tool.coverage.report]
fail_under = 80
show_missing = true
```

```bash
python -m ruff check .
python -m ruff format --check .
python -m pytest --cov=app --cov-report=term-missing
```

**Ergebnis:** All checks passed! · 45 passed · Total coverage: 82.56%

### 5 – GitHub-Actions-Workflow vorbereiten

Datei: `.github/workflows/ci.yml` im Repository-Hauptordner, angelehnt an den
Kurs-Workflow.

- Trigger: Push auf `main`, Pull Requests und manueller Start
- Lint: `ruff check .` und `ruff format --check .`
- Tests: Python 3.12 und 3.13, pytest mit Coverage-Gate
- Pip-Cache: Schlüssel berücksichtigt `requirements.txt` und `requirements-dev.txt`
- Build: wartet mit `needs: [lint, test]` auf erfolgreiche Prüfungen
- Docker-Image: `expenses:ci`; Smoke-Test ruft `/health` auf
- Ohne `DATABASE_URL` verwendet der Smoke-Test bewusst In-Memory

Lokale Abschlussprüfung:

```bash
python -m ruff check .
python -m ruff format --check .
python -m pytest --cov=app --cov-report=term-missing
```
**Ergebnis:** Total coverage: 82.56%, 45 passed

### 6 - CI nachweisen
- auf Github Pull-Request erstellen
- Python Checks fehlgeschlagen, Testbefehl anpassen: "run: python -m pytest --cov=app --cov-report=term-missing"
- alle 4 Checks grün --> Lint (ruff), Test (Python 3.12/13), Build image

### 7 - Merge-Schutz nachweisen
Branch protection rules für `main` in GitHub vollständig einrichten
- Require a pull request before merging
- Require status checks to pass before merging
- Require branches to be up to date before merging
  - Lint (ruff)
  - Test (Python 3.12)
  - Test (Python 3.13)
  - Build image
- Do not allow bypassing the above settings (= admin rights)

### 8 - absichtlichen Lint-/Formatfehler pushen
roten Check und gesperrten Merge sichern
- Fehler in `ci.yml` eingebaut, Lint Check failed
- Button `Merge pull request` nicht klickbar: "Merging is blocked due to failing merge requirements"

### 9 - Badge in README ergänzen
[![CI](https://github.com/nachbaisabel/devops-ausgabenverwaltung/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/nachbaisabel/devops-ausgabenverwaltung/actions/workflows/ci.yml)


### 10 - finaler Check der CI-Jobs
```bash
source .venv/bin/activate
ruff check . && ruff format --check . && python -m pytest --cov=app --cov-report=term-missing
```

**Zuletzt dokumentierter lokaler Stand (11.11.2026):** 45 Tests bestanden, Coverage 81,68 % (Vorgabe 80 % erfüllt); Ruff-Lint und Formatprüfung grün.


---
## Woche 06 – Continuous Deployment

Anleitung: [Deployment-Runbook](DEPLOYMENT.md) ·
Live-App: https://expenses-dsjj.onrender.com ·
Nachweise: [screenshots/](screenshots/)

- [x] Render-Blueprint mit Docker, Branch `main`, Port 8000 und Healthcheck `/health` eingerichtet.
- [x] In-Memory ohne `DATABASE_URL` und mit einem Gunicorn-Worker gewählt; Datenverlust bei Neustarts dokumentiert.
- [x] Render-Variablen `PORT`, `GUNICORN_WORKERS`, `APP_VERSION` und `LOG_LEVEL` gesetzt.
- [x] `/ready` implementiert; lokal und auf Render im Smoke-Test geprüft.
- [x] `APP_VERSION` in `/health` und `LOG_LEVEL` für den Flask-App-Logger ausgewertet; Health-Test angepasst.
- [x] Codeänderungen als `234d10f` committed und gepusht; laut eigener Rückmeldung per PR integriert, vier CI-Checks und CD #3 erfolgreich.
- [x] Smoke-Test an die Ausgaben-API angepasst; lokal und auf Render bestanden (Health, Readiness, Anlegen, Listenabruf, Löschen).
- [x] CD unter `.github/workflows/cd.yml` eingerichtet: nach erfolgreicher CI auf `main` bzw. manuell auslösbar.
- [x] Deploy-Hook als GitHub Secret und `APP_URL` als Variable hinterlegt; Render-Autodeploy deaktiviert.
- [x] Cold Start beobachtet und Rollback mit anschliessender Wiederherstellung geprüft (Ergebnisse unten).
- [x] `.env.example` mit Projektwerten angelegt und ergänzt; lokale `.env` ist ignoriert.
- [x] `DEPLOYMENT.md` mit Abschnitten A–H geschrieben; vier beobachtete Fehlerbilder sowie weitere mögliche Störungen dokumentiert.
- [x] Lokale Installation nach Abschnitt B in separatem Testordner durchlaufen; laut eigener Rückmeldung getestet.
- [x] Lokale Portangaben auf 8000 vereinheitlicht; Compose auf `8000:8000` umgestellt und laut eigener Rückmeldung getestet.
- [x] Öffentliche Versionsausgabe bestätigt: HTTP 200 mit `{"status":"ok","version":"1.0.0"}`.
- [x] Vier Screenshots gesichert; [Healthcheck-Nachweis](screenshots/w6_healthcheck.png) im Runbook verlinkt.
- [x] README für Woche 6 aktualisiert: Render-URL, CI/CD, Versionsausgabe und `.env.example` dokumentiert; `/ready` als implementiert gekennzeichnet.
- [x] `.env.example` um `PORT`, `GUNICORN_WORKERS` und Postgres-Beispiel für `expenses` ergänzt.

### 1 – Öffentliche Instanz prüfen

```bash
curl -i https://expenses-dsjj.onrender.com/health
curl -i https://expenses-dsjj.onrender.com/api/expenses
```

**Ergebnis:** HTTP 200 bei Healthcheck und Listenabruf; anfangs Status `ok` und leere Liste.

### 2 – Gültige Ausgabe anlegen und lesen

```bash
curl -i -X POST https://expenses-dsjj.onrender.com/api/expenses \
  -H "Content-Type: application/json" \
  -d '{"title":"Deployment-Test","amount":"12.50","date":"2026-11-08","category":"Other"}'
curl -i https://expenses-dsjj.onrender.com/api/expenses
```

**Ergebnis:** POST 201, GET 200; Ausgabe mit Kategorie `Other` in der Liste.

### 3 – Ungültige Kategorie testen

```bash
curl -i -X POST https://expenses-dsjj.onrender.com/api/expenses \
  -H "Content-Type: application/json" \
  -d '{"title":"Deployment-Test","amount":"12.50","date":"2026-11-08","category":"Test"}'
curl -i https://expenses-dsjj.onrender.com/api/expenses
```

**Ergebnis:** POST 400 bei Kategorie `Test`; kein neuer Eintrag gespeichert.

### 4 – Testausgabe löschen und Liste prüfen

```bash
curl -i -X DELETE https://expenses-dsjj.onrender.com/api/expenses/1
curl -i https://expenses-dsjj.onrender.com/api/expenses
```

**Ergebnis:** DELETE 200; anschliessend leere Liste. Die ID `1` stammt aus dem Testlauf; beim Wiederholen tatsächliche ID verwenden.

### 5 – Lokaler Server (Projektordner, aktive `.venv`)

```bash
python -m flask --app wsgi:app run --port 8000
```

**Ergebnis:** Flask läuft auf Port 8000; Terminal geöffnet lassen.

### 6 – Lokaler Smoke-Test (zweites Terminal im Projektordner)

```bash
bash scripts/smoke-test.sh http://127.0.0.1:8000
```

**Ergebnis:** `SMOKE TEST PASSED`.

### 7 – Öffentlicher Smoke-Test – direkter Skriptaufruf

```bash
./scripts/smoke-test.sh https://expenses-dsjj.onrender.com
```

**Ergebnis:** `SMOKE TEST PASSED`; direkter Aufruf setzt Ausführungsrechte voraus, alternativ den untenstehenden Bash-Aufruf nutzen.

### 8 – Cold Start – zweimal nach Inaktivität bzw. direkt danach (11.11.2026)

```bash
curl -sS -w '\nHTTP: %{http_code}\nDauer: %{time_total}s\n' \
  https://expenses-dsjj.onrender.com/health
```

**Ergebnis:** HTTP 200; erster Aufruf 23,398553 s, zweiter 0,160756 s.

### 9 – Rollback und Wiederherstellung (11.11.2026)

```bash
bash scripts/smoke-test.sh https://expenses-dsjj.onrender.com
```

**Ergebnis:** In Render Rollback `b8b39ba` → `4c0a451`, danach Manual Deploy → Deploy latest commit zurück auf `b8b39ba`; Smoke-Test jeweils bestanden.

### 10 – Health-Erweiterung lokal prüfen (aktive `.venv`)

```bash
ruff check app/routes.py tests/test_health.py
ruff format app/routes.py tests/test_health.py
python -m pytest tests/test_health.py -v
```

**Ergebnis:** Lint und Formatierung erfolgreich; Health-Test: `1 passed`.

### 11 – LOG_LEVEL prüfen (aktive `.venv`)

```bash
LOG_LEVEL=DEBUG python -c 'from app import create_app; print(create_app().logger.getEffectiveLevel())'
```

**Ergebnis:** Ausgabe `10` entspricht `DEBUG` im Flask-App-Logger.

### 12 – Gesamtprüfung vor Commit (aktive `.venv`, 11.11.2026)

```bash
ruff check .
ruff format --check .
python -m pytest --cov=app --cov-report=term-missing
```

**Ergebnis:** Ruff-Lint und Formatprüfung grün; 45 Tests bestanden, Coverage 81,68 % bei Vorgabe 80 %.

### 13 – Runbook-Test vorbereiten (neues Terminal, bisherige `.venv` deaktivieren)

```bash
mkdir -p /tmp/devops-runbook-check
cd /tmp/devops-runbook-check
```

**Ergebnis:** Separates Testverzeichnis vorbereitet; Installation aus Teil B anschliessend laut eigener Rückmeldung erfolgreich getestet.

### 14 – Formatkorrektur nach Ruff-Meldung

```bash
ruff format app/__init__.py
ruff format --check .
```

**Ergebnis:** Datei korrigiert; `13 files already formatted`.

### 15 – Versionsausgabe nach Konfigurations-Deployment (13.11.2026)

```bash
curl -i --max-time 90 https://expenses-dsjj.onrender.com/health
```

**Ergebnis:** CD #3 erfolgreich nach 8 min 13 s; HTTP 200 mit `{"status":"ok","version":"1.0.0"}`.

### 16 – Codeänderungen veröffentlichen (Feature-Branch)

```bash
git add app/__init__.py app/routes.py tests/test_health.py
git diff --cached
git commit -m "feat: expose app version and configure log level"
git push -u origin feature/render-deployment
```

**Ergebnis:** Commit `234d10f`; anschliessend per PR integriert, vier CI-Checks und CD erfolgreich. Historischer Branch, für neue Arbeit aktuellen Branch verwenden.

**Betrieb:** Flask und Compose verwenden lokal beide Port 8000 und laufen daher abwechselnd. Render verwendet In-Memory mit einem Worker; eine Cloud-Datenbank ist aktuell nicht eingerichtet. Kubernetes folgt in Woche 8.

---
## Woche 7 – Infrastructure as Code (Terraform)

Anleitung: [Terraform-README](terraform-expenses/README.md) ·
Nachweise: [Plan 1](terraform-expenses/plan_screenshot1.png) /
[Plan 2](terraform-expenses/plan-screenshot2.png)

**Umfang:** Lokale Docker-Infrastruktur für die Ausgabenverwaltung. Der
Render-Service bleibt separat; keine Python-`.venv` erforderlich.

- [x] Terraform und Docker eingerichtet; Projektbranch `feature/terraform` angelegt.
- [x] `terraform-expenses/` mit `main.tf`, `variables.tf`, `outputs.tf`, README und `.gitignore` erstellt.
- [x] Terraform ab 1.5 und Provider `kreuzwerker/docker` mit `~> 3.0` konfiguriert; Lockdatei hält Provider 3.9.0 fest.
- [x] Eigenes Image `expenses:local` gebaut; Container über `docker_image.expenses.image_id` damit verbunden.
- [x] Container `expenses`, Netzwerk `expenses-net` und Volume `expenses-data` deklariert.
- [x] Host-Port mit Default 8000 und Validierung 1025–65535 definiert; Container-Port bleibt 8000.
- [x] `APP_VERSION`, `LOG_LEVEL` und leere `DATABASE_URL` gesetzt; Image-Standard ist ein Gunicorn-Worker.
- [x] In-Memory-Betrieb und Lern-Volume unter `/data` dokumentiert; Volume allein macht Ausgaben nicht persistent.
- [x] Outputs für URL, Containername und ID sowie unkritische `terraform.tfvars.example` ergänzt.
- [x] `init`, `fmt`, `validate`, `plan` und `apply` erfolgreich ausgeführt; API und Smoke-Test geprüft.
- [x] Idempotenz, Drift-Erkennung, Wiederherstellung und Portvalidierung nachgewiesen (Ergebnisse unten).
- [x] Testressourcen mit `destroy` entfernt; danach neuen Erstellungsplan für zwei Screenshots erzeugt. Keine Textdatei erforderlich.
- [x] Git-Ausschlüsse geprüft: State, `.terraform/` und echte `.tfvars` ignoriert; Lockdatei und Nachweise dürfen versioniert werden.
- [x] Projekt-README um Woche 7, Terraform-Verweis und Portkonflikt-Hinweis ergänzt.
- [x] Terraform-README abschliessend korrigieren

### 1 – Terraform installieren (macOS/Homebrew)

```bash
brew tap hashicorp/tap
brew install hashicorp/tap/terraform
terraform version
```

**Ergebnis:** Installation und Versionsprüfung durchgeführt.

### 2 – Arbeitsordner und Dateien vorbereiten (vom Projekt-Hauptordner)

```bash
mkdir -p terraform-expenses
cd terraform-expenses
touch main.tf variables.tf outputs.tf README.md
```

**Ergebnis:** Ordner und Dateien erstellt. Früheren Tippfehler `cd terraform` auf `cd terraform-expenses` korrigiert.

### 3 – Docker prüfen und Image bauen (vom Projekt-Hauptordner)

```bash
cd terraform-expenses
docker info >/dev/null && echo "Docker läuft"
docker build -t expenses:local ..
docker images expenses:local
```

**Ergebnis:** Docker läuft; `expenses:local` erfolgreich gebaut und lokal vorhanden.

### 4 – Initialisieren, formatieren und validieren (Terraform-Ordner)

```bash
terraform init
terraform fmt
terraform validate
```

**Ergebnis:** Provider 3.9.0 aus Lockdatei verwendet; `Success! The configuration is valid.`

### 5 – Erstellungsplan

```bash
terraform plan
```

**Ergebnis:** `Plan: 4 to add, 0 to change, 0 to destroy.`

### 6 – Plan anwenden (mit `yes` bestätigen)

```bash
terraform apply
```

**Ergebnis:** `4 added, 0 changed, 0 destroyed`; URL `http://localhost:8000`, Containername `expenses` und Container-ID ausgegeben.

### 7 – Laufende API prüfen

```bash
curl -i http://localhost:8000/health
bash ../scripts/smoke-test.sh http://localhost:8000
```

**Ergebnis:** HTTP 200 mit Version `1.0.0-iac`; `SMOKE TEST PASSED`.

### 8 – Idempotenz

```bash
terraform plan
```

**Ergebnis:** `No changes. Your infrastructure matches the configuration.`

### 9 – Drift absichtlich erzeugen

```bash
docker rm -f expenses
terraform plan
```

**Ergebnis:** Container gelöscht; `Plan: 1 to add, 0 to change, 0 to destroy.`

### 10 – Sollzustand wiederherstellen (mit `yes` bestätigen)

```bash
terraform apply
```

**Ergebnis:** `1 added, 0 changed, 0 destroyed`.

### 11 – Wiederhergestellte App prüfen

```bash
bash ../scripts/smoke-test.sh http://localhost:8000
```

**Ergebnis:** `SMOKE TEST PASSED`.

### 12 – Portvalidierung

```bash
terraform plan -var="host_port=80"
```

**Ergebnis:** `Invalid value for variable`; erlaubter Bereich 1025–65535; keine Änderungen ausgeführt.

### 13 – Aufräumen (mit `yes` bestätigen)

```bash
terraform destroy
```

**Ergebnis:** `Destroy complete! Resources: 4 destroyed.`; Volume gelöscht, Image bleibt lokal.

### 14 – Git-Ausschlüsse prüfen

```bash
git status --short --untracked-files=all .
git check-ignore .terraform terraform.tfstate terraform.tfstate.backup terraform.tfvars
```

**Ergebnis:** State, Provider-Ordner und echte `.tfvars` ignoriert; Quelldateien, Lockdatei und Screenshots dürfen versioniert werden.

### 15 – State und Outputs nachschlagen (nach `apply`)

```bash
terraform state list
terraform output
```

**Ergebnis:** Zeigt verwaltete Ressourcenadressen bzw. URL, Containername und ID; zusätzliche Nachschlagebefehle, kein separater Testnachweis.

### 16 – Plan-Nachweis nach Aufräumen

```bash
terraform plan
```

**Ergebnis:** Vier neue Ressourcen geplant; zwei Screenshots gesichert, kein erneutes `apply` nötig.

**Merksatz:** Konfiguration beschreibt den Sollzustand, der Plan zeigt Änderungen,
`apply` setzt sie um. Der State ordnet Terraform-Ressourcen realen Docker-Objekten zu.


## Hausübung W7 – nginx-Webserver mit Terraform


### Erledigte Hausübungs-ToDos

Anleitung: [nginx-README](terraform/README.md) ·
Nachweis: [Erstellungsplan](terraform/plan_screenshot.png)

- [x] Separaten Ordner `terraform/` für die nginx-Hausübung anlegen; eigene `.tf`-Dateien, `index.html`, `.gitignore` und README darin ablegen.
- [x] Vor `init` die Ausschlüsse einrichten: `.terraform/`, `*.tfstate*`, echte `*.tfvars`; `*.tfvars.example` darf versioniert werden. `.terraform.lock.hcl` ebenfalls versionieren.
- [x] `terraform`-Block mit `required_version`, Provider `kreuzwerker/docker` mit `version = "~> 3.0"` und `provider "docker" {}` konfigurieren.
- [x] `docker_image` für `nginx:alpine` und `docker_container` mit Referenz auf dieses Image definieren.
- [x] Eigene `index.html` mit erkennbarem Text (Name / Woche 7) erstellen und nach `/usr/share/nginx/html/index.html` mounten; bei Bind-Mount absoluten Host-Pfad und `read_only = true` verwenden.
- [x] Host-Port als Variable mit `type = number` und Validierung `> 1024` und `<= 65535` definieren; nginx lauscht standardmässig intern auf Port 80.
- [x] Output für die vollständige URL aus Hostname und Host-Port ergänzen, z. B. `http://localhost:8080`.
- [x] `terraform init`, `terraform fmt` und `terraform validate` ausführen; Dateien formatiert und `Success!` nachgewiesen.
- [x] Erstellungsplan prüfen und Screenshot mit geplanten Ressourcen und `Plan: … to add …` als `terraform/plan_screenshot.png` sichern.
- [x] `terraform apply` ausführen und mit `curl http://localhost:<port>/` prüfen, dass die eigene HTML-Seite statt der nginx-Standardseite erscheint; Output-URL kontrollieren.
- [x] `terraform plan -var="host_port=80"` ausführen: Ablehnung mit der eigenen Validierungsmeldung nachweisen.
- [x] Kurze `terraform/README.md` mit Voraussetzung (Docker läuft), Arbeitsverzeichnis und `init`, `apply`, Prüfung sowie `destroy` schreiben.
- [x] Mit `terraform destroy` aufräumen; vor dem Commit prüfen, dass keine State-Dateien, Provider-Caches oder echten Secrets versioniert werden.

**Prüfstand:** Zwei Ressourcen erstellt, eigene HTML-Seite mit HTTP 200 geprüft,
Port 80 wie erwartet abgelehnt und Testumgebung wieder mit `destroy` aufgeräumt.
Dateien sind vorgemerkt; Commit, Push und PR-Abschluss bleiben oben offen.

### 1 – Ordner und Dateien vorbereiten

Im Projekt-Hauptverzeichnis:

```bash
mkdir -p terraform
cd terraform
```

`.gitignore` anlegen und die Dateien vorbereiten:

- `main.tf`: Terraform-Konfiguration, Provider, nginx-Image und Container
- `variables.tf`: Host-Port mit Standardwert und Validierung
- `index.html`: eigene Webseite
- `outputs.tf`: URL des Webservers

### 2 – Terraform vorbereiten und Dateien prüfen

Danach im Ordner `terraform/` ausführen:

```bash
terraform init
terraform fmt
terraform validate
```

**Ergebnis:** `Success! The configuration is valid.`

### 3 – Erstellungsplan prüfen

```bash
terraform plan
```

**Ergebnis:** `Plan: 2 to add, 0 to change, 0 to destroy.`

### 4 – Webserver erstellen

```bash
terraform apply
```

Mit `yes` bestätigen.

**Ergebnis:**

```text
Apply complete! Resources: 2 added, 0 changed, 0 destroyed.

Outputs:
web_url = "http://localhost:8080"
```

### 5 – Eigene HTML-Seite prüfen

```bash
curl -i http://localhost:8080/
```

**Ergebnis:** HTTP 200 und Inhalt der eigenen `index.html`.
Die Adresse kann auch im Browser geöffnet werden.

### 6 – Portvalidierung prüfen

```bash
terraform plan -var="host_port=80"
```

**Ergebnis:** Beabsichtigte Ablehnung:

```text
Error: Invalid value for variable
host_port must be between 1025 and 65535.
```

### 7 – Aufräumen

```bash
terraform destroy
```

>Container und Terraform-Image-Verwaltung werden entfernt. Das lokale Image bleibt wegen `keep_locally = true` erhalten. Die eingebundene `index.html` bleibt ebenfalls erhalten.
