
## ...aus fachlicher Sicht
![Ablaufdiagramm](../Media/Ablaufdiagramm.jpg)

- Empfang der Sprachnachricht für einen Auftrag
	- *Beispiel:* `Benötige einen Schraubendreherhalter`
- Nachricht wird auf verwertbare Informationen geprüft.
- Suche wird im Internet gestartet:
	- *Beispiel:* `Suche mir eine STL Datei für einen Schraubendreherhalter`
- Auswahl einer beliebigen Anzahl von Beispielen (*z.B. drei*) aus dem Ergebnis
- Aus Beispielen die STL-Dateien nutzen um das Angebot und die Daten für Auftragsvorbereitung zu erstellen.
	- Ermittlung der Daten aus der technischen Datei (STL)
		- Maße des Werkstücks
		- Dauer der Fertigung
		- Materialverbrauch
		- Abbildung
		- Daten für die Fertigung (GCODE)
	- Erstellung eines Angebots
		- Zusammenfassen der Angebotsdaten in einem Dokument und einer Sprachnachricht
		- Speichern der Daten in ein zentrales Datensystem zur Nachbearbeitung des Auftrags
	- Bei Auftragserteilung Maschine mit den Fertigungsdaten (GCODE) bestücken und Werkstück erstellen.
## ...aus technischer Sicht

- Workflowsystem zur Abarbeitung der technischen Aufgaben
	- pythonbasiertes Framework [Prefect](https://www.prefect.io/)
- Anwendung für die Durchführung der technischen Anforderungen zur 3D-Verarbeitung 
	- [Orca Slicer](https://www.orcaslicer.com/)
- Datenbanksystem [SQL Lite](https://www.sqlite.org/)
- Sonstige Bibliotheken 
	- Erstellung Bilder [Matplotlib](https://matplotlib.org/)
	- Erstellung eines PDFs [FDF](https://fdf-doc.readthedocs.io/en/latest/DF])
	- Erzeugen von Sprachnachrichten [pttsx3](https://pypi.org/project/pyttsx3/)
	- Analysieren von Sprachnachrichten [Openai Whisper](https://pypi.org/project/whisper-openai/)
	- Analysieren von 3D Objekten [Trimesh](https://trimesh.org/)