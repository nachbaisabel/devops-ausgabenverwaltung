# Analyse: Readiness und Rolling Updates

Die Readiness-Probe auf `/ready` prüft, ob ein Pod aktuell Anfragen bearbeiten kann. Erst wenn sie erfolgreich ist, nimmt der Service den Pod als Ziel für neue Anfragen auf. Während eines Rolling Updates startet Kubernetes zuerst einen neuen Pod mit der neuen Image-Version. Dieser erhält erst dann Verkehr, wenn Gunicorn läuft und die Readiness-Probe erfolgreich beantwortet wurde.

`maxUnavailable: 0` ergänzt dieses Verhalten: Die Anzahl verfügbarer Pods darf während des Updates nie unter die gewünschte Replikazahl von drei fallen. Zusammen mit `maxSurge: 1` kann Kubernetes kurzzeitig einen zusätzlichen Pod starten. Erst wenn der neue Pod mindestens fünf Sekunden bereit war (`minReadySeconds: 5`), wird ein alter Pod beendet. Dadurch bleiben immer genügend erreichbare Instanzen vorhanden.

Ohne Readiness-Probe wäre ein Container bereits direkt nach dem Start als verfügbar bewertet. Der Service könnte Anfragen an Gunicorn senden, obwohl die Anwendung noch nicht vollständig bereit ist. `maxUnavailable: 0` wäre dann keine zuverlässige Ausfallgarantie.

Die Anwendung hat deshalb zwei Endpunkte: `/health` prüft nur, ob der Prozess lebt, und ist für Liveness gedacht. Würde dieser Endpunkt die Datenbank prüfen, könnte eine kurzzeitig nicht erreichbare Datenbank alle Pods in eine Neustart-Schleife bringen. `/ready` darf Abhängigkeiten prüfen, weil Kubernetes den Pod dann nur aus dem Service entfernt, aber nicht neu startet.