# Code – Woche 08: Kubernetes-Manifeste

Alle Manifeste für das Expenses-Deployment in Kubernetes. 

---
## Inhalt

| Datei | Zweck |
|---|---|
| `manifeste/` | Deklarative Kubernetes-Manifeste für die Ausgabenverwaltung |
| `manifeste/kind-config.yaml` | kind-Cluster: 1 Control-Plane, 2 Worker, Portweiterleitung 30080 |
| `manifeste/namespace.yaml` | Namespace `expenses` |
| `manifeste/configmap.yaml` | Nicht-geheime Konfiguration (`APP_VERSION`, `LOG_LEVEL`) |
| `manifeste/secret.example.yaml` | **Beispiel** für ein Datenbank-Secret (nie mit echten Werten committen) |
| `manifeste/deployment.yaml` | Deployment mit Probes, `resources`, `securityContext`, Rolling-Update-Strategie |
| `manifeste/service.yaml` | ClusterIP-Service, Port 80 → targetPort 8000 |
| `manifeste/service-nodeport.yaml` | NodePort 30080 (Zugriff vom Host über `localhost:30080`) |
| `manifeste/hpa.yaml` | HorizontalPodAutoscaler (min 2 / max 5, CPU 70 %) – benötigt metrics-server |
| `manifeste/Makefile` | Kurzbefehle (`make cluster`, `load`, `deploy`, …) |
| `protokolle/` | Durchsuchbare Textnachweise für Skalierung, Rollout, Rollback und HPA |
| `analyse.md` | Analyse zu Readiness, Liveness und `maxUnavailable: 0` |

---
## Voraussetzungen

- Docker (läuft und ist erreichbar)
- [`kind`](https://kind.sigs.k8s.io/docs/user/quick-start/) und
  [`kubectl`](https://kubernetes.io/docs/tasks/tools/) installiert

---
## Reihenfolge der Befehle

Alle Befehle aus dem Verzeichnis `kubernetes/manifeste/` ausführen.

```bash
cd kubernetes/manifeste

# 1. Cluster erzeugen (1 Control-Plane + 2 Worker)
kind create cluster --config kind-config.yaml

# 2. Image bauen und ins Cluster laden – OHNE diesen Schritt: ErrImagePull
docker build -t expenses:local --build-arg APP_VERSION=1.0.0 ../..
kind load docker-image expenses:local --name expenses

# 3. Manifeste anwenden
kubectl apply -f namespace.yaml
kubectl apply -f configmap.yaml
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
kubectl -n expenses rollout status deployment/expenses

# 4. Temporären Zugriff prüfen (läuft im Vordergrund)
kubectl -n expenses port-forward service/expenses 8080:80
# In einer zweiten Shell: curl -i http://localhost:8080/health
# Danach den port-forward mit Ctrl+C beenden.

# 5. Externen NodePort-Service ergänzen (nach Ctrl+C)
kubectl apply -f service-nodeport.yaml
curl -i http://localhost:30080/health
curl -i http://localhost:30080/ready

# 6. Aufräumen
kind delete cluster --name expenses
```

Kürzer mit dem Makefile:

```bash
cd kubernetes/manifeste
make            # Liste aller Ziele
make cluster    # Cluster erzeugen
make load       # Image bauen + laden
make deploy     # Manifeste anwenden
make status     # Pods, Deployment, Service
make forward    # port-forward auf localhost:8080
make scale      # auf 3 Replikate
make update     # Rolling Update auf expenses:v2
make rollback   # letztes Rollout zurücknehmen
make clean      # Cluster löschen
```

---
## Hinweise

- **Namespace bei jedem Befehl:** `-n expenses` (oder Kontext dauerhaft setzen:
  `kubectl config set-context --current --namespace=expenses`).
- **`secret.example.yaml`** ist bewusst nicht Teil von `make deploy`. Die App
  läuft im Labor ohne Datenbank (In-Memory). Ein Verweis auf eine fehlende
  Datenbank liesse die Readiness-Probe `/ready` fehlschlagen.
- **Liveness und Readiness:** `/health` prüft nur den Prozess. `/ready` prüft,
  ob die Instanz Anfragen bedienen kann. Ein nicht bereiter Pod wird aus dem
  Service genommen, aber nicht neu gestartet.
- **Ausfallarmes Update:** `maxSurge: 1`, `maxUnavailable: 0` und
  `minReadySeconds: 5` sorgen dafür, dass ein neuer Pod stabil bereit ist,
  bevor ein alter Pod ersetzt wird.
- **Sicherheit:** Der Container läuft als UID 10001 ohne Root-Rechte und mit
  schreibgeschütztem Root-Dateisystem. Ein `emptyDir` stellt nur `/tmp` für
  gunicorn bereit.

---
## Nachweise

| Nachweis | Datei | Ergebnis |
|---|---|---|
| Skalierung | [protokoll-scale.txt](protokolle/protokoll-scale.txt) | Drei Pods `1/1 Running` inklusive Spalte `NODE` |
| Rolling Update | [protokoll-rollout.txt](protokolle/protokoll-rollout.txt) | Zeitstempel, keine fehlgeschlagene Anfrage und erfolgreicher Rollout auf Version 3.0.0 |
| Rollback | [protokoll-rollback.txt](protokolle/protokoll-rollback.txt) | `history`, `undo` und erfolgreicher Status |
| Analyse | [analyse.md](analyse.md) | Readiness, Liveness und `maxUnavailable: 0` erklärt |
| HPA-Bonus | [protokoll-hpa.txt](protokolle/protokoll-hpa.txt) | Skalierung unter Last von 3 auf 4 und nach Lastende zurück auf 2 |

---
## Optional: Horizontal Pod Autoscaler

Für den HPA muss der metrics-server im lokalen kind-Cluster laufen:

```bash
kubectl apply -f \
  https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml

kubectl -n kube-system patch deployment metrics-server --type=json \
  -p='[{"op":"add","path":"/spec/template/spec/containers/0/args/-","value":"--kubelet-insecure-tls"}]'

kubectl -n kube-system rollout status deployment/metrics-server
kubectl apply -f kubernetes/manifeste/hpa.yaml
kubectl -n expenses get hpa
```

`--kubelet-insecure-tls` dient ausschliesslich dem lokalen kind-Test und gehört
nicht in einen Produktionscluster.

## Aufräumen

```bash
kind delete cluster --name expenses
```

Dadurch werden Cluster, Pods, Services und metrics-server entfernt. Die
Manifeste und Textprotokolle bleiben im Repository.
