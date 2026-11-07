# DevOps Ausgabenverwaltung

Eine Webanwendung für Privatpersonen, um Ausgaben mit Betrag, Kategorie und
Datum zu erfassen und nach Monat und Kategorie auszuwerten.

**Warum dieses Projekt?** Das Semesterprojekt im Modul CDS212 weist eine
vollständige DevOps-Kette von der Versionsverwaltung über Tests und Deployment
bis zum Monitoring nach. Der fachliche Umfang bleibt bewusst klein.

**Stand: Woche 4.** Die App läuft mit Gunicorn als Nicht-root-Benutzer im
Container. Docker Compose startet App und Postgres; Ausgaben lassen sich
erfassen, auflisten, ändern und löschen. Die Speicherung über einen
Compose-Neustart wurde geprüft. Alle 14 lokalen Tests bestehen; sie verwenden
den In-Memory-Speicher. Die Auswertungen folgen.

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

Die API ist unter `http://localhost:8002` erreichbar. Der App-Prozess läuft im
Container auf Port 8000. Compose wartet auf den Datenbank-Healthcheck; bei
`health: starting` kurz warten und den Status erneut prüfen.

```bash
curl http://localhost:8002/health
curl http://localhost:8002/api/expenses
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
python wsgi.py
```

Prüfaufruf: `http://127.0.0.1:8000/health`; erwartet wird `{"status": "ok"}`.
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
├── app/
│   ├── __init__.py       # Erstellt die Flask-App und verbindet die Bausteine
│   ├── routes.py         # HTTP-Endpunkte: Anfragen annehmen und beantworten
│   ├── models.py         # Expense-Datenmodell und Validierungsfunktionen
│   └── repository.py     # Ausgaben speichern, IDs vergeben und Daten abrufen
├── tests/
│   ├── conftest.py       # Gemeinsamer Testclient
│   ├── test_health.py    # Prüft /health
│   └── test_expenses.py  # Prüft Ausgaben und Fehlerfälle
├── Dockerfile            # Multi-Stage-Image mit Gunicorn und appuser
├── .dockerignore         # Schliesst lokale Dateien vom Build-Kontext aus
├── docker-compose.yml    # App, Postgres, Netzwerk und Datenbank-Volume
├── ToDo.md               # Wochenfortschritt und manuelle Prüfungen
├── wsgi.py               # Einstiegspunkt zum Starten der Anwendung
├── requirements.txt      # Abhängigkeiten der Anwendung
├── requirements-dev.txt  # Zusätzliche Entwicklungswerkzeuge, z.B. pytest
├── README.md
└── CONTRIBUTING.md       # Regelwerk & Arbeitsweise
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

`/health` und die Ausgaben-Endpunkte sind implementiert. 
`/`, `/ready`,`/metrics` und `/api/expenses/stats` sind noch geplant.

| Methode | Pfad | Zweck |
|---|---|---|
| `GET` | `/` | Einfache HTML-Oberfläche |
| `GET` | `/health` | Liveness: läuft die App? Ohne Datenbankzugriff |
| `GET` | `/ready` | Readiness: ist die App bereit? Prüft bei konfigurierter Datenbank deren Erreichbarkeit |
| `GET` | `/metrics` | Metriken |
| `GET` | `/api/expenses` | Gespeicherte Ausgaben auflisten |
| `POST` | `/api/expenses` | Ausgabe mit Titel, Betrag, Kategorie und Datum erfassen; Beschreibung optional |
| `PUT` | `/api/expenses/<id>` | Ausgabe bearbeiten |
| `DELETE` | `/api/expenses/<id>` | Ausgabe löschen |
| `GET` | `/api/expenses/stats` | Statistiken & Übersichten |

---

### Beispiel: Ausgabe erfassen

Beträge werden als Dezimalstrings mit höchstens zwei Nachkommastellen gesendet
und mit zwei Nachkommastellen zurückgegeben. Das Datum hat das Format `YYYY-MM-DD`.

```bash
curl -i -X POST http://localhost:8002/api/expenses \
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
| `APP_VERSION` | Dockerfile: `0.0.0-dev`; Compose-Build: `1.0.0-local` | Im Image gesetzt; Ausgabe in `/health` und Metriken noch geplant |
| `LOG_LEVEL` | in Compose `INFO` | Auswertung durch den Anwendungscode noch geplant |

Die Datei `.env` sowie Zugangsdaten und Tokens gehören nie ins Repository.
Eine `.env.example` ist noch geplant und soll nur Platzhalter und unkritische
Beispielwerte enthalten. `changeme` ist nur für die lokale Übung vorgesehen.

---

## Weiterführende Dokumentation

- [CONTRIBUTING.md](CONTRIBUTING.md): GitHub Flow, Commit-Regeln und PR-Selbstprüfung.
- [ToDo.md](ToDo.md): Projektfortschritt, Git-Ablauf sowie Start- und Testbefehle aus Woche 2–4.

Im weiteren Kursverlauf entstehen:

- `docs/architektur.md`: C4-Architekturübersicht und Entscheidungen.
- `DEPLOYMENT.md`: Runbook für Deployment, Rollback und Störungen (Woche 6).
- `MONITORING.md`: Metriken, Dashboard und Schwellwerte (Woche 9).
- `docs/adr/`: begründete Architekturentscheidungen.
- `BEWERTUNG.md`: Selbsteinschätzung vor der Abgabe.

---

## Sicherheit und Arbeitsweise

### Branch-Schutz

Für `main` ist eine Branch Protection Rule eingerichtet: Änderungen erfolgen
über Feature-Branches und Pull Requests; direkte Pushes sind auch für mich als
Administrator gesperrt. Force-Pushes und das Löschen von `main` sind deaktiviert.

Mit den folgenden Einstellungen wird sichergestellt, dass kein fehlerhafter Code in den Hauptzweig gelangt:
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
- **Do not allow bypassing the above settings** - Branch Rules dürfen nur von mir geändert werden.


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
