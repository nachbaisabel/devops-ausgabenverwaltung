# Trivy – Schwachstellen-Scanner

[Trivy](https://trivy.dev/) ist ein Open-Source-Scanner von Aqua Security. Er
findet bekannte Schwachstellen (CVEs) in Container-Images, im Dateisystem eines
Projekts (Abhängigkeiten), in IaC-Dateien und mehr – aus einer einzigen Quelle.

## Installation

| Plattform | Befehl |
| --- | --- |
| macOS (Homebrew) | `brew install trivy` |
| Ubuntu/Debian | siehe offizielle Anleitung (APT-Repo) unten |
| Docker (ohne Installation) | `docker run --rm aquasec/trivy:latest image expenses:local` |

Offizielle, stets aktuelle Installationsanleitung:
<https://trivy.dev/latest/getting-started/installation/>

Prüfen, dass Trivy läuft:

```
trivy --version
```

Beim ersten Lauf lädt Trivy seine Schwachstellendatenbank herunter (einige
Hundert MB). Das kann ein, zwei Minuten dauern; danach wird sie zwischengespeichert.

## Die vier wichtigen Aufrufe

| Befehl | Wirkung |
| --- | --- |
| `trivy image expenses:local` | Scannt ein gebautes Container-Image (Betriebssystempakete **und** Anwendungsabhängigkeiten im Image). |
| `trivy fs .` | Scannt das Dateisystem/Projekt: liest `requirements.txt` & Co. und meldet verwundbare Abhängigkeiten (SCA), noch bevor ein Image existiert. |
| `trivy image --severity HIGH,CRITICAL --exit-code 1 expenses:local` | Wie oben, aber als **Gate**: nur hohe/kritische Funde, Exit-Code 1 bei Treffern – bricht eine CI-Pipeline ab. |
| `trivy image --format cyclonedx --output sbom.json expenses:local` | Erzeugt eine SBOM (Stückliste aller enthaltenen Komponenten) im CycloneDX-Format. |

Nützliche Zusätze:

- `--ignore-unfixed` blendet Funde aus, für die es (noch) keinen Fix gibt. Für
  ein Gate sinnvoll: Man kann nur beheben, was behebbar ist.
- `--format json --output trivy.json` für maschinenlesbare Ausgabe.
- `--format sarif --output trivy.sarif` für den Upload in die GitHub-Security-Registerkarte.

## Ausgabe lesen

Für jeden Fund zeigt Trivy: **Library/Paket**, **installierte Version**,
**Severity** (CRITICAL/HIGH/MEDIUM/LOW/UNKNOWN), die **CVE-ID** und – am
wichtigsten für die Praxis – die **Fixed Version**. Existiert eine Fixed
Version, ist die Behebung meist ein simples Update (Basis-Image oder
Abhängigkeit anheben). Steht dort nichts, gibt es noch keinen Fix.

## `.trivyignore`

Manche Funde lassen sich nicht sofort beheben (kein Fix verfügbar) oder sind im
Kontext dieser App nicht ausnutzbar. Solche CVEs kann man **begründet und
befristet** ausnehmen. Eine Datei `.trivyignore` im Projektwurzelverzeichnis:

```
# CVE-2024-XXXX: nur ausnutzbar über ein CLI-Werkzeug, das dieses Image nie startet.
# Erneut prüfen bis: 2026-09-01
CVE-2024-XXXX
```

Regeln fürs Ignorieren: immer mit Kommentar (Begründung + Ablaufdatum), nie
pauschal ganze Severities stummschalten, und regelmässig aufräumen. Ein
`.trivyignore` ohne Begründung ist eine versteckte Sicherheitslücke.

## CI-Gate bauen

Das Muster: SARIF für die Sichtbarkeit erzeugen **und** bei hohen/kritischen,
behebbaren Funden abbrechen. Ein fertiger GitHub-Actions-Workflow liegt unter
[`../trivy-scan.yml`](../trivy-scan.yml). Kernidee:

```
trivy image \
  --severity CRITICAL,HIGH \
  --ignore-unfixed \
  --exit-code 1 \
  expenses:local
```

Exit-Code `1` lässt den Pipeline-Schritt fehlschlagen, sobald ein behebbarer
hoher oder kritischer Fund existiert. So verlässt kein bekannt verwundbares
Image die Pipeline.

## Weiterführend

- Trivy-Dokumentation: <https://trivy.dev/latest/docs/>
- `trivy-action` für GitHub Actions: <https://github.com/aquasecurity/trivy-action>
