# DevOps Ausgabenverwaltung
Ausgabenverwaltung - Semesterprojekt für CDS212

Ausgabenverwaltung. Ausgaben mit Betrag, Kategorie und Datum erfassen und
auswerten. Fachlicher Kern: Aggregationen (Summen je Kategorie und Monat) sowie
optionale Budget-Warnungen bei Überschreitung.

---
KI-Verwendung
Ordner-Struktur


## Sicherheit

### Branch-Schutz

Für `main` ist eine Branch Protection Rule eingerichtet. Änderungen werden über Feature-Branches und Pull Requests integriert; direkte Pushes sind auch für mich als Administrator gesperrt. Force-Pushes und das Löschen von `main` sind deaktiviert.

Da das Projekt eine Einzelarbeit ist, sind keine fremden Review-Freigaben erforderlich. Verpflichtende CI-Checks werden in Woche 5 ergänzt.


### GitHub-Zugriff

Das Repository wird über HTTPS verwendet. Die Anmeldung erfolgt über
die vorhandene Git-/VS-Code-Anmeldung; ein SSH-Schlüssel ist dafür
nicht erforderlich. Zugangsdaten und Tokens werden nicht im Repository gespeichert.


