# ToDo-Liste für alle Wochen

> Diese ToDo-Liste wurde mit Codex auf Grundlage der Kursunterlagen erstellt.

Mein Kurs: **CDS212 – DevOps** · Mein Projekt: **Ausgabenverwaltung**

**Nachweise Screenshots:** `/screenshots`
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

**Aktuell: Woche 6 – Dokumentation abschliessen.**

Spätere ToDos:
- [ ] minimales frontend

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
- [x] Änderungen committen, pushen und per PR #16 nach `main` mergen (Merge `a18ccfc`, Umsetzung `b36ae35`).


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
## Woche 5 – Continuous Integration

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
- [x] CI-Badge in der README ergänzen und PR mergen

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
## Woche 6 – Continuous Deployment

Anleitung: [Deployment-Runbook](DEPLOYMENT.md) ·
Live-App: https://expenses-dsjj.onrender.com ·
Nachweise: [screenshots/](screenshots/)

### Erledigt

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
- [x] `.env.example` angelegt; lokale `.env` ist ignoriert. Ergänzungen unten noch offen.
- [x] `DEPLOYMENT.md` mit Abschnitten A–H geschrieben; vier beobachtete Fehlerbilder sowie weitere mögliche Störungen dokumentiert.
- [x] Lokale Installation nach Abschnitt B in separatem Testordner durchlaufen; laut eigener Rückmeldung getestet.
- [x] Lokale Portangaben auf 8000 vereinheitlicht; Compose auf `8000:8000` umgestellt und laut eigener Rückmeldung getestet.
- [x] Öffentliche Versionsausgabe bestätigt: HTTP 200 mit `{"status":"ok","version":"1.0.0"}`.
- [x] Vier Screenshots gesichert; [Healthcheck-Nachweis](screenshots/w6_healthcheck.png) im Runbook verlinkt.

### Prüfergebnisse

| Prüfung | Ergebnis |
|---|---|
| Lokale Codeprüfung (11.11.2026) | Ruff-Lint und Formatierung grün, 45 Tests bestanden, Coverage 81,68 % (Vorgabe 80 %) |
| Cold Start (11.11.2026) | Erster Aufruf 23,398553 s, direkt danach 0,160756 s; beide HTTP 200 |
| Rollback (11.11.2026) | `b8b39ba` → `4c0a451` → `b8b39ba`; Smoke-Test nach Rollback und Wiederherstellung bestanden |
| Konfigurations-Deployment (13.11.2026) | CD #3 erfolgreich nach 8 min 13 s; anschliessend `/health` mit Version `1.0.0` bestätigt |

### Noch offen

- [ ] README aktualisieren: Render-URL, CI/CD-Ablauf, Versionsausgabe und vorhandene `.env.example` beschreiben; `/ready` nicht mehr als geplant aufführen.
- [ ] `.env.example` vervollständigen: `PORT`, `GUNICORN_WORKERS` und Postgres-Beispiel für `expenses` statt `taskboard`.
- [ ] Runbook bereinigen: übrige Voraussetzungen-Platzhalter entfernen; Kubernetes bis Woche 8 als Ausblick kennzeichnen; „still in progress“ entfernen.
- [ ] ToDo, README, Runbook, Portänderung und Screenshots committen und per PR integrieren; danach CI/CD prüfen. Runbook-Commit: `docs: add deployment runbook`.
- [ ] Empfohlene Ergänzung: automatisierte `/ready`-Tests für verfügbares (200) und nicht verfügbares Repository (503).

**Betrieb:** Flask und Compose verwenden lokal beide Port 8000 und laufen daher abwechselnd. Render verwendet In-Memory mit einem Worker; eine Cloud-Datenbank ist aktuell nicht eingerichtet. Kubernetes folgt in Woche 8.
