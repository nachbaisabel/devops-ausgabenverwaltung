# DevOps Ausgabenverwaltung
Ausgabenverwaltung - Semesterprojekt für CDS212

Aufgabenstellung: Ausgaben mit Betrag, Kategorie und Datum erfassen und
auswerten. Fachlicher Kern: Aggregationen (Summen je Kategorie und Monat) sowie
optionale Budget-Warnungen bei Überschreitung.

---

Eine Webanwendung für Privatpersonen, um Ausgaben mit Betrag, Kategorie und Datum zu erfassen und ihre Ausgaben nach Monat und Kategorie auszuwerten.

## Voraussetzungen

- [z. B. Python ≥ 3.12]
- [weitere Werkzeuge]

## Installation

```
git clone https://github.com/nachbaisabel/devops-ausgabenverwaltung.git
cd devops-ausgabenverwaltung
[Befehle zum Einrichten, z. B. python -m venv .venv && . .venv/bin/activate]
[z. B. pip install -r requirements.txt]
```

## Nutzung

```
[Beispielbefehl zum Starten]
```

Kurz erklären, was der Befehl bewirkt und was man erwarten darf.

## Projektstruktur

```
[devops-ausgabenverwaltung]/
├── README.md
├── ToDo.md
├── .gitignore
├── LICENSE
├── git-labor       [Hausübungen]
└── src/            [Quellcode]
```

## KI-Nutzung

Codex wurde zur Erklärung und Zusammenfassung der Kursunterlagen,
zur Lernplanung sowie als Formulierungshilfe für Dokumentation verwendet.
Weitere Einsätze werden hier ergänzt.

## Sicherheit

### Branch-Schutz

Für `main` ist eine Branch Protection Rule eingerichtet. Änderungen werden über Feature-Branches und Pull Requests integriert; direkte Pushes sind auch für mich als Administrator gesperrt. Force-Pushes und das Löschen von `main` sind deaktiviert.

Da das Projekt eine Einzelarbeit ist, sind keine fremden Review-Freigaben erforderlich. Verpflichtende CI-Checks werden in Woche 5 ergänzt.


### GitHub-Zugriff

Das Repository wird über HTTPS verwendet. Die Anmeldung erfolgt über
die vorhandene Git-/VS-Code-Anmeldung; ein SSH-Schlüssel ist dafür
nicht erforderlich. Zugangsdaten und Tokens werden nicht im Repository gespeichert.

## Lizenz

Veröffentlicht unter der MIT-Lizenz (Datei `LICENSE` im Projekt-Repository).