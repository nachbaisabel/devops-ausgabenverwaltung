# DevOps Ausgabenverwaltung

Eine Webanwendung für Privatpersonen, um Ausgaben mit Betrag, Kategorie und
Datum zu erfassen und nach Monat und Kategorie auszuwerten.

**Warum dieses Projekt?** Das Semesterprojekt im Modul CDS212 weist eine
vollständige DevOps-Kette von der Versionsverwaltung über Tests und Deployment
bis zum Monitoring nach. Der fachliche Umfang bleibt bewusst klein.

**Stand: Woche 3.** Ausgaben lassen sich im Arbeitsspeicher erfassen, auflisten,
ändern und löschen. Alle 14 Tests bestehen; die Auswertungen folgen.

---
## Geplanter Funktionsumfang (MVP)

- Ausgaben mit Betrag, Kategorie und Datum erfassen.
- Gespeicherte Ausgaben auflisten.
- Ausgaben nach Kategorie summieren.
- Ausgaben nach Monat summieren.

Budget-Warnungen bleiben eine mögliche spätere Erweiterung und gehören nicht
zum MVP. Weitere fachliche Funktionen werden zunächst zurückgestellt.

---
## Schnellstart

### Voraussetzungen

- Git und Zugriff auf GitHub über HTTPS.
- Python ab 3.12; lokal verwende ich Python 3.13 mit einer `.venv`.
- Ab Woche 4: Docker und Docker Compose.

### Repository herunterladen

```bash
git clone https://github.com/nachbaisabel/devops-ausgabenverwaltung.git
cd devops-ausgabenverwaltung
```

### Anwendung starten

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

Der Server muss für die Tests nicht laufen. Docker Compose und Postgres folgen in Woche 4.

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

`routes.py` verarbeitet die HTTP-Anfragen. Die POST-Route liest den
JSON-Body ein und ruft die Validierungsfunktionen aus `models.py` auf.
Anschließend übergibt sie die gültigen Werte an das Repository.

`repository.py` erzeugt daraus ein `Expense`-Objekt, vergibt eine ID
und speichert es im Arbeitsspeicher. Die Klasse `Expense` ist in
`models.py` definiert. Ihre Methode `to_dict()` wandelt das Objekt
für die JSON-Antwort in ein Dictionary um.

Die GET-Route fragt dieselbe Repository-Instanz nach den gespeicherten
Ausgaben. Beim Neustart gehen die Daten des In-Memory-Speichers verloren.

---

## Endpunkte

`/health` und die Ausgaben-Endpunkte sind implementiert. `/`, `/ready`,
`/metrics` und `/api/expenses/stats` sind noch geplant.

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

## Konfiguration

**Geplante Umgebungsvariablen**, angelehnt an die Kursreferenz. Die tatsächliche
Implementierung und eine `.env.example` folgen beim Aufbau der Anwendung.

| Variable | Geplanter Standard | Wirkung |
|---|---|---|
| `DATABASE_URL` | leer | Leer: In-Memory-Speicher; gesetzt: PostgreSQL |
| `APP_VERSION` | `0.0.0-dev` | Versionsangabe in `/health` und den Metriken |
| `LOG_LEVEL` | `INFO` | Mindestlevel der Logausgaben |

Die Datei `.env` sowie Zugangsdaten und Tokens gehören nie ins Repository.
Eine versionierte `.env.example` enthält nur Platzhalter und unkritische Beispielwerte.

---

## Weiterführende Dokumentation

- [CONTRIBUTING.md](CONTRIBUTING.md): GitHub Flow, Commit-Regeln und PR-Selbstprüfung.
- `ToDo.md`: Projektfortschritt und Links zu den Ergebnissen aus Woche 2.

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

Das Projekt ist eine Einzelarbeit. Eine schriftliche Selbstprüfung im PR ersetzt
fremde Review-Freigaben. Verpflichtende CI-Checks werden in Woche 5 ergänzt.

### GitHub-Zugriff

Das Repository wird über HTTPS verwendet. Die Anmeldung erfolgt über die
vorhandene Git-/VS-Code-Anmeldung; ein SSH-Schlüssel ist dafür nicht erforderlich.
Zugangsdaten werden nicht im Repository gespeichert.

---
## Autorin

| Name | GitHub | Modul |
|---|---|---|
| Isabelle Nachbaur | [@nachbaisabel](https://github.com/nachbaisabel) | CDS212 – DevOps |

**Eingesetzte KI-Werkzeuge:**
- Codex zur Erklärung und Zusammenfassung der Kursunterlagen, zur Lernplanung sowie als Formulierungshilfe und zur Anpassung
von `README.md` und `CONTRIBUTING.md`; ausserdem Unterstützung beim App-Aufbau,
bei Tests und bei der Fehlersuche.
- GitHub Copilot für Codevervollständigungen und Vorschläge für einzelne Zeilen und Funktionen. Übernommene Vorschläge werden geprüft und angepasst.

**Vorlagen:**
- Die md.Files-Strukturen stammen aus den CDS212-Kursunterlagen.
- Der WSGI-Einstiegspunkt wird aus `beispiel-app/wsgi.py` übernommen.
- Einzelne Funktionen oder Bausteine werden ebenfalls aus dem Folder `beispiel-app` übernommen, wobei dies jeweils direkt im File gekennzeichnet wird.

---
## Lizenz

MIT-Lizenz; siehe Datei `LICENSE` im Projekt-Repository.
