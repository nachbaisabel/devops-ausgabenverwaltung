# ToDo-Liste für alle Wochen

> Diese ToDo-Liste wurde mit Codex auf Grundlage der Kursunterlagen erstellt.

Mein Kurs: **CDS212 – DevOps** · Mein Projekt: **Ausgabenverwaltung**

- [x] Woche 1
- [x] Woche 2
- [x] Woche 3
- [x] Woche 4
- [x] Woche 5
- [ ] Woche 6
- [ ] Woche 7
- [ ] Woche 8
- [ ] Woche 9
- [ ] Woche 10

**Currently: Woche 6**

## Hausübungen & Lernmaterialien

- https://github.com/nachbaisabel/devops-course/

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
Port 8000 muss für den lokalen Server frei sein; Docker verwendet bei mir Host-Port 8002.

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
# Woche 04 – Die eigene Anwendung containerisieren

- [x] Multi-Stage-Dockerfile mit Slim-Basis und sinnvoller Cache-Reihenfolge erstellen.
- [x] `.dockerignore` ergänzen und Image erfolgreich bauen.
- [x] App mit Gunicorn als `appuser` starten; Healthcheck und API auf Host-Port 8002 prüfen.
- [x] Compose mit `web`, Postgres 16, DB-Healthcheck und benanntem Volume einrichten.
- [x] Postgres-Repository implementieren und anhand von `DATABASE_URL` auswählen.
- [x] Beträge auf `Decimal` und Datumswerte auf `date` umstellen; 14 lokale Tests bestanden.
- [x] Anlegen, Ändern und Löschen über die API mit Postgres prüfen.
- [x] Persistenz nach `down` und erneutem Start nachweisen; Unterschied zu `down -v` erklären.
- [x] README und Testabläufe dokumentieren; Optimierungen mit geschätzten Vergleichswerten begründen.
- [ ] Änderungen selbst committen, pushen und PR nach `main` mergen.


### Dockerfile schreiben & testen
```bash
docker build -t ausgabenverwaltung:local .
docker run -d -p 127.0.0.1:8002:8000 --name ausgabenverwaltung ausgabenverwaltung:local

curl -i -X POST http://localhost:8002/api/expenses \
  -H "Content-Type: application/json" \
  -d '{"title":"Mittagessen","amount":"12.50","date":"2026-11-06","category":"Food"}'

curl http://localhost:8002/api/expenses
```

Der Einzelcontainer verwendet ohne `DATABASE_URL` In-Memory. Vor dem Compose-Start
den Einzelcontainer stoppen und entfernen, falls er noch Port 8002 belegt:

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
curl -i -X POST http://localhost:8002/api/expenses \
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
curl http://localhost:8002/api/expenses
```

5) Testausgabe ändern
```bash
curl -i -X PUT http://localhost:8002/api/expenses/1 \
  -H "Content-Type: application/json" \
  -d '{"title":"Postgres-Test geändert","amount":"15.00","date":"2026-11-06","category":"Food","description":"Update getestet"}'
curl http://localhost:8002/api/expenses
```

6) Testausgabe löschen
```bash
curl -i -X DELETE http://localhost:8002/api/expenses/1
curl http://localhost:8002/api/expenses
```

7) Bereits gelöschte ID erneut löschen – erwartet: 404 mit `Expense not found`.
Die ID 1 stammt aus meinem Testlauf; beim Wiederholen die tatsächlich zurückgegebene ID verwenden.

```bash
curl -i -X DELETE http://localhost:8002/api/expenses/1
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
## Woche 5 – Continuous Integration

- [x] Issue und Branch `ci/add-quality-gates` für die CI einrichten
- [x] Ruff und pytest-cov in den Entwicklungsabhängigkeiten ergänzen
- [x] Lint und Formatierung lokal bereinigen
- [x] Validierungstests ergänzen; 45 Tests bestanden
- [x] Coverage-Gate mit mindestens 80 % konfigurieren; lokal 82,56 % erreicht
- [x] Workflow mit Lint, Formatprüfung, Testmatrix, Docker-Build und Smoke-Test vorbereiten
- [ ] Erfolgreiche CI-Läufe für alle Jobs auf GitHub prüfen
- [ ] Erforderliche Status-Checks im Branch-Schutz von `main` festlegen
- [ ] Absichtlichen Fehler im PR nachweisen: rot und Merge gesperrt, danach korrigiert und grün
- [ ] Rote und grüne Checks mit Screenshots und PR-Link dokumentieren
- [ ] CI-Badge in der README ergänzen und PR mergen

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

**Zuletzt dokumentierter lokaler Stand:** Total coverage: 82.56%, 45 passed


---
## Woche 6 – Continuous Deployment

- [x] `render.yaml` im Repo-Hauptordner anpassen: Service-Name, `./Dockerfile`, Build-Kontext `.`
- [ ] Render-Service für die Ausgabenverwaltung erstellen und Repository verbinden mit Blueprint-Import
    - Name: expense tracking
- [ ] Speicher für Render festlegen: In-Memory oder erreichbares Postgres; Compose-Datenbank läuft nicht automatisch auf Render
- [ ] Variablen setzen: `PORT`, `GUNICORN_WORKERS`, `APP_VERSION`, `LOG_LEVEL`; `DATABASE_URL` nur bei Cloud-Datenbank
- [ ] Konfiguration im Python-Code prüfen: `APP_VERSION` in `/health`, `LOG_LEVEL` auswerten; `config.py` optional als zentrale Ablage
- [ ] `/ready` passend zum Repository ergänzen und testen; Render-Healthcheck bleibt `/health`
- [ ] `.env.example` mit Variablennamen und unkritischen Beispielwerten anlegen; `.env` bleibt aus Git ausgeschlossen
- [ ] Erstes Deployment prüfen: öffentliche Render-URL, `/health`, API und Logs
- [ ] `smoke-test.sh` auf Ausgaben-Endpunkte und Dezimalstrings anpassen; gegen Render ausführen
- [ ] `.github/workflows/cd.yml` einrichten: Deployment nur nach erfolgreicher CI auf `main`
- [ ] GitHub konfigurieren: Render-Deploy-Hook als Secret, `APP_URL` als Variable; unbedingte Render-Autodeploys abschalten
- [ ] Grünen CD-Workflow und erfolgreichen Smoke-Test nachweisen
- [ ] Cold Start beobachten und Rollback samt Erfolgskontrolle durchführen
- [ ] `DEPLOYMENT.md` schreiben: A Voraussetzungen, B lokale Installation, C Variablen, D Deployment, E Verifikation, F Rollback, G mindestens vier Fehlerbilder, H Kontakt/Eskalation
- [ ] Render-URL mit sichtbarer URL festhalten; README aktualisieren
- [ ] Runbook anhand der eigenen Anleitung durchgehen; Tests und CI grün, PR prüfen und mergen

### Entscheidungen

- **Gunicorn:** zunächst ein Worker; bei In-Memory notwendig, mit Postgres sind mehrere möglich, aber keine Pflicht
- **Port:** Container lauscht aktuell auf 8000; Render passend konfigurieren, Host-Port 8002 betrifft nur lokales Compose
- **Feature Flags:** optional, aktuell keine erforderlich
- **`config.py`:** keine Pflicht; Umgebungsvariablen müssen im Code tatsächlich ausgewertet werden
- **`DATABASE_URL`:** Zugangsdaten nur in Render/GitHub-Secrets, keine echten Werte in `.env.example`


### Render 
- `render.yaml` im Repo-Hauptordner anpassen: Service-Name, `./Dockerfile`, Build-Kontext `.`
- Render-Service für die Ausgabenverwaltung erstellen und Repository verbinden mit Blueprint-Import
- Website

### Smoke-Test 

./scripts/smoke-test.sh https://taskboard-w8aq.onrender.com
