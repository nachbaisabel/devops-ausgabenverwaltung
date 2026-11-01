# Mitarbeit an der Ausgabenverwaltung

Das Projekt ist eine Einzelarbeit im Modul CDS212. Diese Regeln halten fest,
wie Änderungen nachvollziehbar entwickelt, geprüft und übernommen werden.

## Branching-Strategie: GitHub Flow

`main` bleibt der stabile Hauptbranch und soll mit der lauffähigen Anwendung
immer deploybar sein. Direkte Pushes auf `main` sind durch Branch-Schutz
gesperrt, auch für mich als Administrator. Einen dauerhaften `develop`-Branch
verwende ich nicht.

1. Den aktuellen Stand von `main` holen und pro Aufgabe einen kurzen Branch anlegen.
2. Änderungen in kleinen, thematisch getrennten Commits festhalten.
3. Den Feature-Branch pushen und einen Pull Request nach `main` öffnen.
4. Den eigenen Diff prüfen und Was, Warum und Prüfergebnis im PR dokumentieren.
5. Ab Woche 5 müssen die erforderlichen CI-Checks grün sein.
6. Den PR mergen, den Merge lokal holen und den erledigten Branch löschen.

Issues verwende ich bei Bedarf zur Aufgabenplanung. Ein PR kann ein zugehöriges
Issue mit `Closes #<nummer>` beim Merge automatisch schliessen.

### Branch-Namen

Englisch, Kleinbuchstaben und Bindestriche: `<typ>/<kurzbeschreibung>`.

| Typ | Zweck | Beispiel |
|---|---|---|
| `feature/` | Neue Funktion | `feature/add-expenses` |
| `fix/` | Fehlerbehebung | `fix/monthly-total` |
| `docs/` | Dokumentation | `docs/project-scope` |
| `chore/` | Wartung und Werkzeuge | `chore/update-gitignore` |

Keine Force-Pushes und kein Löschen von `main`. Rebase nutze ich entsprechend
der Kursregel nur für eigene, noch nicht veröffentlichte Commits.

## Commit-Konventionen

Ab jetzt verwende ich Conventional Commits: englische, kurze Nachrichten im
Imperativ, ohne Punkt am Ende. Jeder Commit behandelt ein Thema.

```text
<typ>(<optionaler bereich>): <kurze beschreibung>
```

Typen: `feat`, `fix`, `docs`, `test`, `refactor`, `chore`, `ci`.

Beispiele:

```text
docs: define project scope and workflow
feat(api): add expense creation
fix(api): correct monthly totals
```

Ein optionaler Body erklärt nach einer Leerzeile die Gründe der Änderung.

## Selbstprüfung im Pull Request

Da ich allein arbeite, ist keine fremde Review-Freigabe vorgeschrieben.
Stattdessen prüfe ich den Diff auf GitHub selbst und dokumentiere das Ergebnis.
Die folgende Vorlage passe ich an die tatsächliche Änderung an:

```markdown
## Was
Welche Änderung enthält der PR?

## Warum
Welches Problem oder welche Anforderung löst sie?

## Selbstprüfung
- [ ] Eigenen Diff geprüft; keine Zugangsdaten oder unerwünschten Dateien enthalten
- [ ] Tests durchgeführt oder begründet, warum sie nicht nötig bzw. noch nicht möglich sind
- [ ] Dokumentation angepasst oder nicht betroffen

## CI-Status und offene Punkte
Aktuell: CI noch nicht eingerichtet, folgt in Woche 5.
Ab Woche 5: Ergebnisse von Lint, Tests, Coverage-Gate und Build angeben.
Weitere Einschränkungen oder Folgeaufgaben hier festhalten.
```

Die Checkliste hake ich nur ab, wenn ich den jeweiligen Punkt tatsächlich
geprüft habe. Bei reinen Textänderungen reichen die inhaltliche Prüfung und die
Markdown-Vorschau; Anwendungstests sind dafür normalerweise nicht nötig.

## Lokale Prüfungen und CI – schrittweiser Aufbau

**Stand Woche 2:** Es sind noch keine Anwendungstests, Ruff-Prüfungen oder
CI-Workflows eingerichtet. Das ist kein bestandener Testlauf.

**Ab Woche 3:** Sobald Anwendung und Entwicklungsabhängigkeiten vorhanden sind,
führe ich die eingerichteten Prüfungen in der aktiven Python-3.12-Umgebung aus:

```bash
ruff check .
ruff format --check .
pytest --cov=app --cov-report=term-missing
```

Die Pfade passen wir beim Aufbau der Anwendung an die tatsächliche Struktur an.
Die Coverage-Schwelle beträgt mindestens 80 %.

**Ab Woche 5:** Die CI automatisiert Lint, Formatprüfung, Tests mit Coverage-Gate
und Docker-Build. Die erforderlichen grünen Status-Checks werden als
Merge-Voraussetzung im Branch-Schutz hinterlegt.

## Quellen und KI-Unterstützung

Angepasst aus der CDS212-Kursvorlage
`woche-10-abschlussprojekt/code/projekt-vorlage/CONTRIBUTING.md`.
Codex hat bei der Formulierung und Anpassung an die Ausgabenverwaltung und den
aktuellen Kursstand unterstützt.
