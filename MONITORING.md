# Monitoring - Expenses

> Monitoring-, Alarmierungs- und Sicherheitsnachweise für die Ausgabenverwaltung.

Autorin: Isabelle Nachbaur · Datum: 2026-11-22 · App-Version (`expenses_info`): `1.0.0`

---
## Überblick

Die Ausgabenverwaltung stellt Prometheus-Metriken bereit. Der lokale
Observability-Stack besteht aus der Flask-App, PostgreSQL, Prometheus und
Grafana. Prometheus sammelt die Metriken ein, Grafana visualisiert sie und
Prometheus bewertet Alert-Regeln.

---
## Was wird erhoben?

Die Anwendung stellt unter `/metrics` Metriken im Prometheus-Format bereit.
Der `prometheus-flask-exporter` erzeugt automatisch HTTP-Request-Zähler und
Antwortdauer-Metriken; zusätzlich liefert `expenses_info` die konfigurierte
App-Version.

| Metrik | Typ | Bedeutung |
|---|---|---|
| `flask_http_request_total` | Counter | Anzahl HTTP-Requests nach Methode und Statuscode |
| `flask_http_request_duration_seconds_bucket` | Histogram-Bucket | Grundlage für die Berechnung von Antwortzeit- bzw. Latenz-Quantilen wie p95 |
| `expenses_info` | Gauge | Version und Metadaten der laufenden Ausgabenverwaltung |

---
## Prometheus

- Scrape-Ziel: `web:8000/metrics`
- Scrape-Intervall: `15s`
- Konfiguration: `monitoring/prometheus/prometheus.yml`
- Kontrolle: Unter `http://localhost:9090/targets` steht der Job `expenses`
  mit Endpoint `http://web:8000/metrics` auf **UP**.

---
## 1 – Grafana-Dashboard-Dokumentation

### Panel: Request-Rate

| Feld | Inhalt |
|---|---|
| Metrik | `flask_http_request_total` |
| PromQL | `sum(rate(flask_http_request_total[5m]))` |
| Frage | Wie viele HTTP-Requests verarbeitet die Ausgabenverwaltung pro Sekunde? |
| Normalbereich | Im Leerlauf lag die Rate nahe `0 req/s`; während des eigenen Lasttests bei ungefähr `2,1–2,4 req/s`. |
| Eingriffsschwelle | Über `10 req/s` für mehr als fünf Minuten prüfen, da dies deutlich über dem beobachteten Testniveau liegt und auf ungewöhnliche Last oder Missbrauch hindeuten kann. |

### Panel: Fehlerrate 5xx

| Feld | Inhalt |
|---|---|
| Metrik | `flask_http_request_total` |
| PromQL | `sum(rate(flask_http_request_total{status=~"5.."}[5m])) / sum(rate(flask_http_request_total[5m]))` |
| Frage | Welcher Anteil aller Requests scheitert wegen eines Serverfehlers? |
| Normalbereich | Im eigenen Lasttest `0 %`, weil nur erfolgreiche Requests und gezielte `404`-Client-Fehler erzeugt wurden. |
| Eingriffsschwelle | Mehr als `5 %` über fünf Minuten. Dann Logs, letzten Deploy und Abhängigkeiten wie die Datenbank prüfen. |

### Panel: p95-Latenz

| Feld | Inhalt |
|---|---|
| Metrik | `flask_http_request_duration_seconds_bucket` |
| PromQL | `histogram_quantile(0.95, sum by (le) (rate(flask_http_request_duration_seconds_bucket[5m])))` |
| Frage | Wie schnell wurden 95 % aller Requests höchstens beantwortet? |
| Normalbereich | Im eigenen Lasttest ungefähr `4,75 ms`. |
| Eingriffsschwelle | Mehr als `1 s` über fünf Minuten. Dann Request-Rate, Datenbankverbindung, Logs und Ressourcen prüfen. |

### Panel: Version (expenses_info)

| Feld | Inhalt |
|---|---|
| Metrik | `expenses_info` |
| PromQL | `expenses_info` |
| Frage | Welche App-Version läuft aktuell im überwachten Container? |
| Normalbereich | `1.0.0`, entsprechend der gesetzten Umgebungsvariable `APP_VERSION`. |
| Eingriffsschwelle | Handeln, wenn die Metrik fehlt oder eine unerwartete Version erscheint. Dann Deploy-Stand und Compose-Konfiguration vergleichen. |

### Panel: p95 latency (eigenes Panel)

| Feld | Inhalt |
|---|---|
| Metrik | `flask_http_request_duration_seconds_bucket` |
| PromQL | `histogram_quantile(0.95, sum by (le) (rate(flask_http_request_duration_seconds_bucket[5m])))` |
| Frage | Bestätigt das eigene Panel dieselbe p95-Latenz der Ausgabenverwaltung wie das vorgegebene Latenz-Panel? |
| Normalbereich | Im eigenen Lasttest ungefähr `4,75 ms`; die Kurve entsprach dem vorhandenen p95-Panel. |
| Eingriffsschwelle | Mehr als `1 s` über fünf Minuten. Dann die betroffenen Endpunkte, Datenbankverbindung, Logs und Ressourcen prüfen. |

---
## 2 – SLOs mit Error Budget

### SLO 1 – Verfügbarkeit

- SLI: Anteil erfolgreicher HTTP-Requests; gemessen als `1 -` 5xx-Fehlerrate aus `flask_http_request_total`.
- SLO: Über 30 Tage sollen mindestens `99,9 %` aller Requests ohne 5xx-Serverfehler beantwortet werden.
- Error Budget (Rechenweg): Das Fehlbudget beträgt `0,1 %` aller Requests. Bei einem vollständigen Ausfall über 30 Tage entspräche dies `0,1 %` von `43 200 min`, also `43,2 min`.
- Begründung: Die Ausgabenverwaltung soll zuverlässig verfügbar sein, aber geplante Deployments und seltene technische Störungen müssen möglich bleiben. Ein Ziel von 100 % wäre nicht realistisch.

### SLO 2 – Latenz

- SLI: Anteil der Requests, deren Antwortdauer höchstens `0,5 s` beträgt. Grundlage ist `flask_http_request_duration_seconds_bucket{le="0.5"}` im Verhältnis zu `flask_http_request_duration_seconds_count`.
- SLO: Über 30 Tage sollen mindestens `95 %` aller Requests innerhalb von `0,5 s` beantwortet werden.
- Error Budget (Rechenweg): Maximal `5 %` der Requests dürfen langsamer als `0,5 s` sein. Bei je 100 Requests sind also höchstens fünf langsame Requests zulässig.
- Begründung: Im eigenen Lasttest lag die p95-Latenz bei etwa `4,75 ms` und damit deutlich unter dem Ziel. `0,5 s` lässt dennoch Reserve für normale Last, Datenbankzugriffe oder kurze Schwankungen.

---
## 3 – Eigene Alarmregel

```yaml
- alert: HighClientErrorRate
  expr: |
    sum(rate(flask_http_request_total{status=~"4.."}[5m]))
      /
    sum(rate(flask_http_request_total[5m]))
      > 0.20
  for: 5m
  labels:
    severity: warning
  annotations:
    summary: "High 4xx error rate on Expenses API"
    description: "{{ $value | humanizePercentage }} of requests returned a 4xx status over the last 5 minutes."
```

- **Begründung:** Die Regel erkennt das nutzernahe Symptom vieler abgewiesener
  Requests. Mehr als 20 % 4xx-Antworten können auf einen fehlerhaften Client,
  falsche API-Nutzung oder Probleme bei der Eingabevalidierung hindeuten. Die
  Dauer `for: 5m` verhindert Warnungen durch einzelne falsche Eingaben oder
  kurze Lastspitzen.

- Runbook-Skizze:
  1. Prüfen, ob `HighClientErrorRate` aktiv ist und welcher Wert gemeldet wird.
  2. Im Grafana-Dashboard die Request-Rate und die Fehlerraten vergleichen.
  3. In den App-Logs prüfen, ob hauptsächlich `400`- oder `404`-Antworten auftreten.
  4. Letzte Änderungen an API, Formularen oder Client-Code prüfen.
  5. Falsche Request-Daten, Validierung oder API-Aufrufe korrigieren; bei auffälligem Fremdverkehr gegebenenfalls Rate-Limiting prüfen.
  6. Nach der Korrektur kontrollieren, dass die 4xx-Rate unter 20 % fällt und der Alarm wieder `Inactive` wird.

> Ein `runbook_url` lassen wir bewusst weg: Deine echte YAML-Regel enthält keines, und das Runbook steht hier direkt nachvollziehbar im Dokument.

---
## 4 – Trivy-Auswertung

Scan-Befehl:

```bash
trivy image expenses:local 2>&1 | tee monitoring/trivy/scan-expenses.txt
```

Der Scan vom `2026-11-21` fand im Image `expenses:local` insgesamt 234 Funde:
7 UNKNOWN, 78 LOW, 98 MEDIUM, 51 HIGH und 0 CRITICAL. Die Python-Abhängigkeiten
enthielten dagegen keine HIGH- oder CRITICAL-Funde. Die folgenden drei
unterschiedlichen HIGH-Funde wurden genauer bewertet.

### Fund 1 – util-linux / mount

- CVE / Paket / Severity / Fixed Version: `CVE-2026-76642`, `mount` bzw.
  `util-linux`, HIGH, aktuell keine Fixed Version angegeben.
- Ausnutzbarkeit in der Ausgabenverwaltung: Die Schwachstelle betrifft
  privilegierte Mount-Post-Hooks. Die Flask-App stellt keine Funktion zum Mounten
  von Dateisystemen bereit, verarbeitet keine Mount-Optionen und läuft als
  nicht privilegierter `appuser`. Über die vorhandenen API-Endpunkte ist der
  betroffene Aufrufpfad daher nicht direkt erreichbar.
- Empfehlung: Beobachten und das Basisimage regelmäßig mit
  `docker build --pull` aktualisieren. Sobald ein Update mit Fixed Version
  verfügbar ist, Image neu bauen und erneut mit Trivy scannen.

### Fund 2 – OpenSSL

- CVE / Paket / Severity / Fixed Version: `CVE-2026-124709`, `openssl`,
  HIGH, aktuell keine Fixed Version angegeben.
- Ausnutzbarkeit in der Ausgabenverwaltung: Die Schwachstelle betrifft
  QUIC-Stream-Verarbeitung. Die App läuft lokal hinter Gunicorn über normales
  HTTP und verwendet weder QUIC noch eigene TLS- oder Stream-Verarbeitung.
  Daher ist die Funktion über die vorhandenen API-Endpunkte voraussichtlich
  nicht direkt erreichbar.
- Empfehlung: Beobachten und das Python-Basisimage regelmäßig aktualisieren.
  Bei einer verfügbaren Fixed Version das Image neu bauen, den Stack neu
  starten und den Scan wiederholen.

### Fund 3 – zlib

- CVE / Paket / Severity / Fixed Version: `CVE-2026-85091`, `zlib1g`, HIGH,
  Fixed Version `1:1.3.dfsg+really1.3.1-1+deb13u1`.
- Ausnutzbarkeit in der Ausgabenverwaltung: Die Schwachstelle betrifft eine
  Heap-Buffer-Overflow-Situation beim Verarbeiten komprimierter Daten. Die
  Ausgabenverwaltung bietet keinen Datei-Upload, keine Archiv-Extraktion und
  keinen direkten zlib-Endpunkt. Eine Ausnutzung über die aktuelle API ist
  deshalb unwahrscheinlich; die Schwachstelle bleibt dennoch im Basisimage.
- Empfehlung: Zeitnah beheben. Das Basisimage mit `docker build --pull`
  aktualisieren, `expenses:local` neu bauen und anschließend erneut mit Trivy
  prüfen, ob die Fixed Version enthalten ist.

---
## Nachweise

- Dashboard-Export: `monitoring/grafana/dashboards/expenses-overview.json`
- Dashboard-Screenshot: `monitoring/screenshots/dashboard.png`
- Firing-Alarm: `monitoring/screenshots/alert-firing.png`
- Trivy-Rohbericht: `monitoring/trivy/scan-expenses.txt`
- Prometheus-Regeln: `monitoring/prometheus/alert.rules.yml`


