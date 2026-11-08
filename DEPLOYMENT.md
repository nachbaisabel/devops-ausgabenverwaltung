# Deployment-Runbook

> **Vorlage - Anpassung ist in Arbeit!** Ein Runbook ist eine abarbeitbare Handlungsanweisung, kein
> Fliesstext. Schreiben Sie jeden Schritt so, dass eine fremde Person ihn unter
> Druck ohne Nachdenken ausführen kann. Ersetzen Sie alle `<…>`.

## Umgebungen

| Umgebung | Zweck | URL |
|---|---|---|
| lokal | Entwicklung via Docker Compose | http://localhost:8000 |
| Render | Produktion (Free Tier) | https://<dienst>.onrender.com |

## Voraussetzungen

- <Zugänge: GitHub, Render-Konto, benötigte Rechte>
- <Werkzeuge: docker, kubectl + kind, terraform – mit Mindestversion>

## Konfiguration und Secrets

| Variable | Wo hinterlegt | Zweck |
|---|---|---|
| `DATABASE_URL` | Render-Environment / K8s-Secret | Postgres-Verbindung |
| `APP_VERSION` | Build-Argument / Environment | Version in `/health` |
| `<weitere>` | `<Ort>` | `<Zweck>` |

Secrets stehen **nie** im Repository. <Wo werden sie verwaltet?>

## Deployment auf Render

1. <Schritt: was auslösen – z. B. Merge auf `main` startet Auto-Deploy via `render.yaml`>
2. <Schritt: Fortschritt beobachten – wo?>
3. **Kontrolle:** `curl https://<dienst>.onrender.com/health` liefert `200` und
   die erwartete Version.

## Deployment auf Kubernetes (lokal, kind)

```bash
kind load docker-image <image>:<tag>
kubectl apply -f k8s/
kubectl rollout status deployment/<name> -n <namespace>
```

**Kontrolle:** `kubectl get pods -n <namespace>` zeigt ≥ 2 Pods `Running` / `1/1`.

## Rollback

<Wie machen Sie ein fehlerhaftes Deployment rückgängig? Konkret:>

- Render: <z. B. im Dashboard „Rollback" auf das vorige Deploy, oder Revert-Commit>
- Kubernetes: `kubectl rollout undo deployment/<name> -n <namespace>`

## Störungsbehandlung

| Symptom | Erste Prüfung | Massnahme |
|---|---|---|
| `/ready` liefert `503` | Datenbank erreichbar? Logs? | <Massnahme> |
| Deployment hängt | `kubectl describe pod …` / Render-Logs | <Massnahme> |
| `/health` unerreichbar | Läuft der Prozess? Port? | <Massnahme> |

