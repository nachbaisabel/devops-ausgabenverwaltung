# Code – Woche 9: Observability-Stack und Security-Scanning

Lauffähiger Startpunkt für Labor und Hausaufgabe: Expenses + Postgres +
Prometheus + Grafana, dazu die Trivy-Konfiguration.

## Inhalt

```
code/
├── docker-compose.observability.yml   web + db + prometheus + grafana
├── prometheus/
│   ├── prometheus.yml                  Scrape-Ziele und Regel-Einbindung
│   └── alert.rules.yml                 ExpensesDown, HighErrorRate, HighLatencyP95
├── grafana/
│   ├── provisioning/
│   │   ├── datasources/prometheus.yml  Datenquelle -> http://prometheus:9090
│   │   └── dashboards/dashboards.yml   lädt Dashboards aus /etc/grafana/dashboards
│   └── dashboards/expenses-overview.json
├── last-erzeugen.sh                    erzeugt HTTP-Last (inkl. 404er)
├── trivy-scan.yml                      GitHub-Actions-Workflow (Image-Scan-Gate)
└── trivy/README.md                     Trivy-Kurzanleitung
```

## Startreihenfolge

Alle Befehle aus dem Wochenordner `woche-09-monitoring-devsecops/` ausführen.

```
# 1. Stack bauen und starten
docker compose -f code/docker-compose.observability.yml up -d --build

# 2. Warten, bis alle Container laufen (db hat einen Healthcheck)
docker compose -f code/docker-compose.observability.yml ps

# 3. Last erzeugen, damit Metriken entstehen
./code/last-erzeugen.sh http://localhost:8000

# 4. Aufräumen
docker compose -f code/docker-compose.observability.yml down       # Container weg, Volumes bleiben
docker compose -f code/docker-compose.observability.yml down -v    # auch Volumes löschen
```

## URLs und Zugangsdaten

| Dienst | URL | Zugang |
| --- | --- | --- |
| Ausgaben | <http://localhost:8000> | – |
| Ausgaben-Metriken | <http://localhost:8000/metrics> | – |
| Prometheus | <http://localhost:9090> | – |
| Prometheus-Targets | <http://localhost:9090/targets> | – |
| Prometheus-Alerts | <http://localhost:9090/alerts> | – |
| Grafana | <http://localhost:3000> | `admin` / `admin` |

Grafana fragt beim ersten Login nach einem neuen Passwort – im Kurs kann man das
überspringen. Die Prometheus-Datenquelle und das Dashboard „Expenses Overview"
sind bereits vorprovisioniert; nichts muss von Hand angelegt werden.

## Trivy

Trivy wird lokal installiert (nicht Teil des Compose-Stacks). Siehe
[`trivy/README.md`](trivy/README.md). Nach `docker compose ... up --build`
existiert das Image `expenses:local` und kann gescannt werden:

```
trivy image expenses:local
```

## Hinweise

- Ports 8000, 9090 und 3000 müssen frei sein. Belegt? In der Compose-Datei das
  linke Port-Mapping ändern (z. B. `"3001:3000"`).
- Der Build-Kontext von `web` zeigt auf `../../beispiel-app` – die
  Referenzanwendung im Repo-Wurzelverzeichnis. Von hier aus nichts verschieben.
