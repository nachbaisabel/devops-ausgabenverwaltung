# DevOps Ausgabenverwaltung

[![CI](https://github.com/nachbaisabel/devops-ausgabenverwaltung/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/nachbaisabel/devops-ausgabenverwaltung/actions/workflows/ci.yml)

Eine Webanwendung für Privatpersonen, um Ausgaben mit Betrag, Kategorie und
Datum zu erfassen und nach Monat und Kategorie auszuwerten.

**Warum dieses Projekt?** Das Semesterprojekt im Modul CDS212 weist eine
vollständige DevOps-Kette von der Versionsverwaltung über Tests und Deployment
bis zum Monitoring nach. Der fachliche Umfang bleibt bewusst klein.
---
**Stand: Woche 7.** Zusätzlich lässt sich die lokale Infrastruktur mit
Terraform erstellen und entfernen. Image, Container, Netzwerk und Volume
werden über den Docker-Provider verwaltet. Healthcheck, Smoke-Test,
Idempotenz, Drift-Erkennung und Portvalidierung wurden geprüft.

---
## Geplanter Funktionsumfang (MVP)

- Ausgaben mit Titel, Betrag, Kategorie und Datum erfassen; Beschreibung optional.
- Gespeicherte Ausgaben auflisten, ändern und löschen.
- Ausgaben nach Kategorie summieren.
- Ausgaben nach Monat summieren.

Budget-Warnungen bleiben eine mögliche spätere Erweiterung und gehören nicht
zum MVP. Weitere fachliche Funktionen werden zunächst zurückgestellt.

---
## Schnellstart

### Voraussetzungen

- Git und Zugriff auf GitHub über HTTPS.
- Python ab 3.12; lokal verwende ich Python 3.13 mit einer `.venv`.
- Docker und Docker Compose für den Start mit Postgres; Docker Desktop muss laufen.
- Python ist für den reinen Docker-Start nicht auf dem Host erforderlich.

### Repository herunterladen

```bash
git clone https://github.com/nachbaisabel/devops-ausgabenverwaltung.git
cd devops-ausgabenverwaltung
```

### Anwendung mit Docker Compose starten

Im Projektordner ausführen; eine lokale `.venv` ist dafür nicht nötig:

```bash
docker compose up --build -d
docker compose ps
```

Die API ist unter `http://localhost:8000` erreichbar. Der App-Prozess läuft im
Container auf Port 8000. Compose wartet auf den Datenbank-Healthcheck; bei
`health: starting` kurz warten und den Status erneut prüfen.

```bash
curl http://localhost:8000/health
curl http://localhost:8000/api/expenses
docker compose logs --tail=30 web
```

Aktuell gibt es noch keine HTML-Oberfläche unter `/`.

```bash
docker compose down       # Container entfernen; Datenbank-Volume bleibt erhalten
docker compose up -d      # Erneut starten; gespeicherte Ausgaben bleiben vorhanden
```

**`docker compose down -v` löscht zusätzlich das Datenbank-Volume und dessen Daten.**

### Anwendung lokal ohne Datenbank starten

Beim ersten Einrichten im Projektordner eine virtuelle Umgebung erstellen:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt

unset DATABASE_URL
export APP_VERSION=1.0.0-local
export LOG_LEVEL=INFO

python -m flask --app wsgi:app run --host 127.0.0.1 --port 8000
```

Prüfaufruf im zweiten Terminal: `curl -i http://127.0.0.1:8000/health`.
Erwartet: HTTP 200 und `{"status":"ok","version":"1.0.0-local"}`.

Falls Port 8000 bereits belegt ist, zuerst die andere lokale Instanz beenden oder auf einen anderen Port ausweichen.
Die Schritte dazu stehen unter
[Lokale Installation im Runbook](DEPLOYMENT.md#b---lokale-installation).

Flask und Docker Compose verwenden beide Host-Port 8000 und müssen daher
abwechselnd betrieben werden.

Die Umgebung in jedem neuen Terminal mit `source .venv/bin/activate` aktivieren.
Mit `deactivate` wird sie wieder verlassen. `.venv` wird nicht in Git gespeichert.

Tests in einem separaten Terminal ausführen:

```bash
source .venv/bin/activate
python -m pytest tests/ -v
```

Der Server muss für die Tests nicht laufen. Ohne gesetzte `DATABASE_URL`
verwendet der lokale Start den In-Memory-Speicher. Dessen Daten gehen beim
Beenden verloren. Die lokalen Tests sind kein automatisierter Postgres-Test;
die manuellen Datenbankprüfungen stehen in [ToDo.md](ToDo.md).

---
## Projektstruktur

```text
devops-ausgabenverwaltung/
├── .github/workflows/
│   ├── ci.yml            # Lint, Formatierung, Tests und Docker-Build
│   └── cd.yml            # Render-Deployment und Smoke-Test
├── app/
│   ├── __init__.py       # Erstellt die Flask-App und verbindet die Bausteine
│   ├── routes.py         # HTTP-Endpunkte: Anfragen annehmen und beantworten
│   ├── models.py         # Expense-Datenmodell und Validierungsfunktionen
│   └── repository.py     # Ausgaben speichern, IDs vergeben und Daten abrufen
├── screenshots/          # Nachweise
├── scripts/
│   └── smoke-test.sh     # Prüft die laufende API
├── terraform-expenses/   # Lokale Infrastruktur mit Terraform und Anleitung
├── tests/
│   ├── conftest.py       # Gemeinsamer Testclient
│   ├── test_health.py    # Prüft /health
│   └── test_expenses.py  # Prüft Ausgaben und Fehlerfälle
│   └── test_models.py    # Tests der Eingabevalidierung
├── .dockerignore         # Schliesst lokale Dateien und Secrets vom Docker-Build-Kontext aus
├── .env.example          # Unkritische Beispielkonfiguration
├── .gitignore            # Verhindert das versehentliche Versionieren lokaler Dateien und Secrets
├── CONTRIBUTING.md       # Regelwerk & Arbeitsweise
├── DEPLOYMENT.md         # Installation, Deployment und Störungsbehandlung
├── docker-compose.yml    # App, Postgres, Netzwerk und Datenbank-Volume
├── Dockerfile            # Multi-Stage-Image mit Gunicorn und appuser
├── pyproject.toml        # Ruff-, pytest- und Coverage-Konfiguration
├── README.md
├── render.yaml           # Render-Blueprint
├── requirements.txt      # Abhängigkeiten der Anwendung
├── requirements-dev.txt  # Zusätzliche Entwicklungswerkzeuge, z.B. pytest
├── ToDo.md               # Wochenfortschritt und manuelle Prüfungen
└── wsgi.py               # Einstiegspunkt zum Starten der Anwendung
```

### Wie hängen die Dateien zusammen?

`wsgi.py` ruft `create_app()` aus `app/__init__.py` auf.
Diese Funktion erstellt die Flask-App, richtet einen gemeinsamen
Repository-Speicher ein und registriert den Blueprint aus `routes.py`.
Bei gesetzter `DATABASE_URL` verwendet sie `PostgresExpenseRepository`,
ansonsten `InMemoryExpenseRepository`.

`routes.py` verarbeitet die HTTP-Anfragen. Die POST-Route liest den
JSON-Body ein und ruft die Validierungsfunktionen aus `models.py` auf.
Anschließend übergibt sie die gültigen Werte an das Repository.

`repository.py` speichert die Ausgabe im ausgewählten Backend und liefert
ein `Expense`-Objekt mit ID zurück. In-Memory vergibt die App die ID; bei
Postgres übernimmt das die Datenbank. Die Klasse `Expense` ist in
`models.py` definiert. Ihre Methode `to_dict()` wandelt das Objekt
für die JSON-Antwort in ein Dictionary um.

Die GET-Route fragt dieselbe Repository-Instanz nach den gespeicherten
Ausgaben. Beim Neustart gehen die Daten des In-Memory-Speichers verloren.
Postgres speichert sie hingegen im benannten Compose-Volume `db-data`.
Beträge werden intern als `Decimal`, Datumswerte als `date` verarbeitet.

---

## Endpunkte

`/health`, `/ready` und die Ausgaben-Endpunkte sind implementiert.
`/`, `/metrics` und `/api/expenses/stats` sind noch geplant.

| Methode | Pfad | Zweck |
|---|---|---|
| `GET` | `/` | Geplant: Einfache HTML-Oberfläche |
| `GET` | `/health` | Liveness mit Versionsausgabe, ohne Datenbankzugriff |
| `GET` | `/ready` | Readiness: ist die App bereit? Prüft bei konfigurierter Datenbank deren Erreichbarkeit |
| `GET` | `/metrics` | Geplant: Metriken |
| `GET` | `/api/expenses` | Gespeicherte Ausgaben auflisten |
| `POST` | `/api/expenses` | Ausgabe mit Titel, Betrag, Kategorie und Datum erfassen; Beschreibung optional |
| `PUT` | `/api/expenses/<id>` | Ausgabe bearbeiten |
| `DELETE` | `/api/expenses/<id>` | Ausgabe löschen |
| `GET` | `/api/expenses/stats` | Geplant: Statistiken & Übersichten |

---

### Beispiel: Ausgabe erfassen

Beträge werden als Dezimalstrings mit höchstens zwei Nachkommastellen gesendet
und mit zwei Nachkommastellen zurückgegeben. Das Datum hat das Format `YYYY-MM-DD`.

```bash
curl -i -X POST http://localhost:8000/api/expenses \
  -H "Content-Type: application/json" \
  -d '{"title":"Mittagessen","amount":"12.50","date":"2026-11-06","category":"Food"}'
```

Erwartet: HTTP 201 und die Ausgabe inklusive automatisch erzeugter ID.
Ungültige Eingaben liefern JSON mit HTTP 400; unbekannte IDs bei PUT/DELETE
liefern 404. PUT ersetzt alle Pflichtfelder der Ausgabe. Die erlaubten
Kategorien stehen in `app/models.py`.

## Konfiguration

| Variable | Standard | Wirkung / Stand |
|---|---|---|
| `DATABASE_URL` | lokal leer; in Compose gesetzt | Leer: In-Memory; gesetzt: PostgreSQL |
| `POSTGRES_PASSWORD` | `changeme` als lokale Übungsvorgabe | Compose verwendet denselben Wert für Datenbank und Verbindungsadresse |
| `GUNICORN_WORKERS` | `1` | Anzahl der Gunicorn-Worker im Container |
| `APP_VERSION` | App/Docker: `0.0.0-dev`; Compose: `1.0.0-local`; Render: `1.0.0` | Versionsausgabe in `/health` |
| `LOG_LEVEL` | `INFO` | Steuert das Logging-Level des Flask-App-Loggers |
| `PORT` | Render: `8000` | Passend zum fest auf Port 8000 gestarteten Gunicorn gesetzt |

Die vorhandene `.env.example` enthält unkritische Beispielwerte.
Die lokale `.env` und echte Zugangsdaten gehören nie ins Repository.
Docker Compose liest `.env` automatisch; der direkte Flask-Start lädt sie im aktuellen Projekt nicht automatisch. `changeme` ist nur ein lokaler Übungswert.

Die vollständige Variablen- und Secrets-Tabelle steht in
[DEPLOYMENT.md](DEPLOYMENT.md#c---konfiguration-und-secrets).

---
## Lokale Infrastruktur mit Terraform

Alternativ zu Flask und Docker Compose kann Terraform die lokale Ausgabenverwaltung mit Container, Netzwerk und Volume bereitstellen.

Voraussetzungen, Befehle und Nachweise stehen in
[terraform-expenses/README.md](terraform-expenses/README.md).

Diese Variante verwendet In-Memory-Speicherung. Das eingebundene Volume macht die Ausgaben nicht persistent. Terraform, Compose und Flask verwenden standardmässig denselben Host-Port 8000 und müssen daher abwechselnd betrieben werden.

---
## Deployment auf Render

Öffentliche Instanz: https://expenses-dsjj.onrender.com

Die Einrichtung erfolgt über den Blueprint `render.yaml`.
Nach erfolgreicher CI auf `main` löst GitHub Actions das Deployment über einen geheimen Render-Deploy-Hook aus und führt den Smoke-Test aus.
Ein manueller Start des CD-Workflows ist ebenfalls möglich.

```bash
bash scripts/smoke-test.sh https://expenses-dsjj.onrender.com
```

Erwartet: `SMOKE TEST PASSED`.

Render verwendet aktuell In-Memory-Speicherung mit einem Worker.
Ausgaben gehen bei einem Neustart verloren. Nach längerer Inaktivität kann der erste Aufruf wegen eines Cold Starts länger dauern.

Einrichtung, Verifikation, Rollback und Troubleshooting:
[Deployment-Runbook](DEPLOYMENT.md).

---
## Weiterführende Dokumentation

- [CONTRIBUTING.md](CONTRIBUTING.md): GitHub Flow, Commit-Regeln und PR-Selbstprüfung.
- [DEPLOYMENT.md](DEPLOYMENT.md): Runbook für Installation, Konfiguration, Deployment, Rollback und Troubleshooting.

- [ToDo.md](ToDo.md): Projektfortschritt, Git-Ablauf sowie Start- und Testbefehle von allen Wochen.

Im weiteren Kursverlauf entstehen:

- `docs/architektur.md`: C4-Architekturübersicht und Entscheidungen.
- `MONITORING.md`: Metriken, Dashboard und Schwellwerte (Woche 9).
- `docs/adr/`: begründete Architekturentscheidungen.
- `BEWERTUNG.md`: Selbsteinschätzung vor der Abgabe.

---

## Sicherheit und Arbeitsweise

### Branch-Schutz

Für `main` ist eine Branch Protection Rule eingerichtet: Änderungen erfolgen
über Feature-Branches und Pull Requests; direkte Pushes sind auch für mich als
Administrator gesperrt. Force-Pushes und das Löschen von `main` sind deaktiviert.

Die folgenden Einstellungen verhindern einen Merge bei fehlgeschlagenen Pflichtprüfungen:
- **Require a pull request before merging** – kein direkter Push auf `main`;
  Änderungen laufen über einen PR.
- **Require status checks to pass before merging** – benannte Checks müssen grün sein, sonst ist der Merge-Knopf gesperrt:
  - Lint (ruff)
  - Test (Python 3.12)
  - Test (Python 3.13)
  - Build image
- **Require branches to be up to date before merging** – der PR muss den aktuellen
  Stand von `main` enthalten, damit nicht zwei einzeln grüne Änderungen zusammen
  rot ergeben.
- **Do not allow bypassing the above settings** – die Branch-Regeln gelten auch für mich als Administrator; kein Umgehen der PR-Pflicht oder erforderlichen Checks
- Force-Pushes und Löschen von `main` bleiben deaktiviert.


### GitHub-Zugriff

Das Repository wird über HTTPS verwendet. Die Anmeldung erfolgt über die
vorhandene Git-/VS-Code-Anmeldung; ein SSH-Schlüssel ist dafür nicht erforderlich.
Zugangsdaten werden nicht im Repository gespeichert.

**Eingesetzte KI-Werkzeuge:**
- Codex zur Erklärung und Zusammenfassung der Kursunterlagen, zur Lernplanung sowie als Formulierungshilfe und zur Anpassung von `README.md` und `CONTRIBUTING.md`; ausserdem Unterstützung bei der Fehlersuche und Code-Validierung.
- GitHub Copilot für Codevervollständigungen und Vorschläge für einzelne Zeilen und Funktionen. Übernommene Vorschläge werden geprüft und angepasst.

**Vorlagen:**
- Die md.Files-Strukturen stammen aus den CDS212-Kursunterlagen.
- Der WSGI-Einstiegspunkt wird aus `beispiel-app/wsgi.py` übernommen.
- Einzelne Funktionen oder Bausteine werden ebenfalls aus dem Folder `beispiel-app` übernommen, wobei dies jeweils direkt im File gekennzeichnet wird.

---
## Autorin

| Name | GitHub | Modul |
|---|---|---|
| Isabelle Nachbaur | [@nachbaisabel](https://github.com/nachbaisabel) | CDS212 – DevOps |

---
## Lizenz

MIT-Lizenz; siehe Datei `LICENSE` im Projekt-Repository.
