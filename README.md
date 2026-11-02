# DevOps Ausgabenverwaltung

Eine Webanwendung für Privatpersonen, um Ausgaben mit Betrag, Kategorie und
Datum zu erfassen und nach Monat und Kategorie auszuwerten.

**Warum dieses Projekt?** Das Semesterprojekt im Modul CDS212 weist eine
vollständige DevOps-Kette von der Versionsverwaltung über Tests und Deployment
bis zum Monitoring nach. Der fachliche Umfang bleibt bewusst klein.

**Stand: Woche 3 – in Arbeit.** Aktuell entsteht das Flask-Grundgerüst mit
`create_app()`, WSGI-Einstiegspunkt und `/health`. Danach folgen erste Tests
und die Ausgabenfunktionen. 

## Geplanter Funktionsumfang (MVP)

- Ausgaben mit Betrag, Kategorie und Datum erfassen.
- Gespeicherte Ausgaben auflisten.
- Ausgaben nach Kategorie summieren.
- Ausgaben nach Monat summieren.

Budget-Warnungen bleiben eine mögliche spätere Erweiterung und gehören nicht
zum MVP. Weitere fachliche Funktionen werden zunächst zurückgestellt.

## Schnellstart

### Voraussetzungen

- Git und Zugriff auf GitHub über HTTPS.
- Python 3.12; lokal verwende ich dafür Conda.
- Ab Woche 4: Docker und Docker Compose.

### Repository herunterladen

```bash
git clone https://github.com/nachbaisabel/devops-ausgabenverwaltung.git
cd devops-ausgabenverwaltung
```

### Anwendung starten

Das Grundgerüst wird gerade eingerichtet. Sobald `requirements.txt`,
`app/__init__.py` und `wsgi.py` vorhanden sind, erfolgt der lokale Start so:

```bash
conda activate devops-ausgabenverwaltung
python -m pip install -r requirements.txt
python wsgi.py
```

Prüfaufruf: `http://127.0.0.1:8000/health`; erwartet wird `{"status": "ok"}`.
Der erste Test für diesen Endpunkt folgt als nächster Schritt.
Docker Compose und Postgres folgen in Woche 4.

## Endpunkte

**Geplant, noch nicht implementiert.** Die fachlichen Pfade werden bei der
Implementierung verbindlich festgelegt.

| Methode | Pfad | Zweck |
|---|---|---|
| `GET` | `/` | Einfache HTML-Oberfläche |
| `GET` | `/health` | Liveness: läuft die App? Ohne Datenbankzugriff |
| `GET` | `/ready` | Readiness: ist die App bereit? Prüft bei konfigurierter Datenbank deren Erreichbarkeit |
| `GET` | `/metrics` | Metriken im Prometheus-Format |
| `GET` | `/api/expenses` | Gespeicherte Ausgaben auflisten |
| `POST` | `/api/expenses` | Ausgabe mit Betrag, Kategorie und Datum erfassen |


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

## Weiterführende Dokumentation

- [CONTRIBUTING.md](CONTRIBUTING.md): GitHub Flow, Commit-Regeln und PR-Selbstprüfung.
- `ToDo.md`: Projektfortschritt und Links zu den Ergebnissen aus Woche 2.

Im weiteren Kursverlauf entstehen:

- `docs/architektur.md`: C4-Architekturübersicht und Entscheidungen.
- `DEPLOYMENT.md`: Runbook für Deployment, Rollback und Störungen (Woche 6).
- `MONITORING.md`: Metriken, Dashboard und Schwellwerte (Woche 9).
- `docs/adr/`: begründete Architekturentscheidungen.
- `BEWERTUNG.md`: Selbsteinschätzung vor der Abgabe.

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

## Autorin

| Name | GitHub | Modul |
|---|---|---|
| Isabelle Nachbaur | [@nachbaisabel](https://github.com/nachbaisabel) | CDS212 – DevOps |

**Eingesetzte KI-Werkzeuge:** Codex zur Erklärung und Zusammenfassung der
Kursunterlagen, zur Lernplanung sowie als Formulierungshilfe und zur Anpassung
von `README.md` und `CONTRIBUTING.md`. In Woche 3 unterstützt Codex beim
Flask-Grundgerüst und erklärt die einzelnen Schritte.

**Vorlage:** Die README-Struktur stammt aus
`woche-10-abschlussprojekt/code/projekt-vorlage/README.md` der CDS212-Kursunterlagen.
Der WSGI-Einstiegspunkt wird aus `beispiel-app/wsgi.py` übernommen.

## Lizenz

MIT-Lizenz; siehe Datei `LICENSE` im Projekt-Repository.
