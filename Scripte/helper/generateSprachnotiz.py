import pyttsx3

engine = pyttsx3.init()

# Optional: Sprechgeschwindigkeit anpassen (Standard ist ca. 200)
engine.setProperty("rate", 170)

text ="Das Bauteil zu dem Halter 4711 weist Maßabweichungen auf. Bitte prüfen Sie die Toleranzen und dokumentieren Sie die Ergebnisse."

engine.save_to_file(text, "sprachnotiz.wav")

# Führt die Speicherung aus und wartet, bis die Datei fertig ist
engine.runAndWait()
print("WAV-Datei erfolgreich erstellt!")