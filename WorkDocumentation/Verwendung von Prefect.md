## Testprogramm Starten

#### testPrefect.py
```
	from prefect import flow, task
	import time
@task
def daten_laden():
    """Eine einfache Aufgabe, die Daten simuliert."""
    print("Lade Daten aus der Quelle...")
    time.sleep(1)
    return [1, 2, 3, 4, 5]
@task
def daten_verarbeiten(daten):
    """Eine Aufgabe, die die Daten transformiert."""
    print("Verarbeite Daten...")
    time.sleep(1)
    return [x * 2 for x in daten]
@flow(name="Mein Erster Prefect Workflow")
def haupt_workflow():
    """Der Haupt-Flow, der die Tasks koordiniert."""
    rohe_daten = daten_laden()
    ergebnis = daten_verarbeiten(rohe_daten)
    print(f"Workflow erfolgreich beendet! Ergebnis: {ergebnis}")
# Das Skript lokal ausführen
if __name__ == "__main__":
    haupt_workflow()
```
#### Start / Ausgabe des Test-Scripts (*testPrefect.py*)

```
(conda-env) D:\Projekte\AdditiveManufacturing\ProtoType>python testPrefect.py
15:05:50.866 | INFO    | prefect - Starting temporary server on http://127.0.0.1:8977
See https://www.prefect.io/docs/v3/concepts/server#how-to-guides for more information on running a dedicated Prefect server.
15:05:54.351 | INFO    | Flow run 'unstoppable-sunfish' - Beginning flow run 'unstoppable-sunfish' for flow 'Mein Erster Prefect Workflow'
Lade Daten aus der Quelle...
15:05:55.368 | INFO    | Task run 'daten_laden-d25' - Finished in state Completed()
Verarbeite Daten...
15:05:56.376 | INFO    | Task run 'daten_verarbeiten-038' - Finished in state Completed()
Workflow erfolgreich beendet! Ergebnis: [2, 4, 6, 8, 10]
15:05:56.393 | INFO    | Flow run 'unstoppable-sunfish' - Finished in state Completed()
15:05:56.400 | INFO    | prefect - Stopping temporary server on http://127.0.0.1:8977
```
## Das vorbereitete Pipeline - Script für die Aufgabe
#### pipeline.py
```
import os
import subprocess
from prefect import task, flow, get_run_logger

# --- TASK 1: Bauteilprüfung (Eingabe & Einordnung) ---
@task(retries=1, retry_delay_seconds=5)
def pruefe_bauteil(teilennummer: str, stl_pfad: str, material_vorgabe: str):
    logger = get_run_logger()
    logger.info(f"Starte Prüfung für Bauteil: {teilennummer}")
    if not os.path.exists(stl_pfad):
        raise FileNotFoundError(f"STL-Datei unter {stl_pfad} nicht gefunden!")
    
    # Hier würde später 'trimesh' die Außenmaße lesen
    # Für den Prototyp simulieren wir die erfolgreiche Einordnung
    
    logger.info(f"STL-Datei {stl_pfad} erfolgreich validiert.")
    # Vorschlag basierend auf Material (z.B. ASA -> FDM)
    verfahren_vorschlag = "FDM" if material_vorgabe.upper() in ["ASA", "PLA", "PETG"] else "Fremdfertigung"

    nacharbeit = "M4-Gewinde schneiden" if teilennummer == "4711" else "Keine"
    return {
        "status": "Erfolgreich eingepasst",
        "verfahren": verfahren_vorschlag,
        "nacharbeit": nacharbeit
    }

# --- TASK 2: Druckvorbereitung (OrcaSlicer CLI-Aufruf) ---
@task
def generiere_druckdatei(stl_pfad: str, verfahren: str):
    logger = get_run_logger()
    if verfahren != "FDM":
        logger.warning(f"Verfahren {verfahren} wird nicht lokal geslict. Überspringe Slicer.")
        return "Keine Druckdatei (Fremdfertigung oder SLA)"
    logger.info("Rufe Slicer über Kommandozeile auf...")

    # Beispiel für den OrcaSlicer CLI Aufruf (Simuliert als Dummy-Echo für Woche 1)
    # Später: ["orcaslicer", "--slice", stl_pfad, "--profile", "festes_profil.gcode"]

    cmd = ["echo", f"OrcaSlicer generiert G-Code für {stl_pfad}"]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    logger.info(f"Slicer-Output: {result.stdout.strip()}")
    return "ausgabe_profil.gcode"

# --- CORE FLOW: Die modulare Workflow-Pipeline ---

@flow(name="Mechatronik Musterbau Pipeline")
def musterbau_workflow(teilennummer: str, stl_pfad: str, material_vorgabe: str):
    logger = get_run_logger()
    logger.info("=== Start des Auftrags ===")

    # 1. Bauteilprüfung
    pruef_ergebnis = pruefe_bauteil(teilennummer, stl_pfad, material_vorgabe)
    logger.info(f"Vorgeschlagenes Verfahren: {pruef_ergebnis['verfahren']}")

    # 2. Druckvorbereitung
    gcode_pfad = generiere_druckdatei(stl_pfad, pruef_ergebnis['verfahren'])
    logger.info("=== Ablauf erfolgreich beendet ===")

    return {
        "auftrag": teilennummer,
        "ergebnis": pruef_ergebnis,
        "datei": gcode_pfad
    }

# --- Lokaler Testlauf ---
if __name__ == "__main__":
    # Erstellen einer Dummy-STL-Datei für den Testlauf
    with open("halter_4711.stl", "w") as f:
        f.write("solid dummy_stl ... endsolid")

    # Start des Flows (Entspricht einem Musterauftrag)
    ergebnis = musterbau_workflow(
        teilennummer="4711",
        stl_pfad="halter_4711.stl",
        material_vorgabe="ASA"
    )
    print("\nLokales Endergebnis des Kerns:", ergebnis)
```

#### Start / Ausgabe des Programms (*pipeline.py*)
```
(conda-env) D:\Projekte\AdditiveManufacturing\ProtoType>python pipeline.py

15:11:55.859 | INFO    | prefect - Starting temporary server on http://127.0.0.1:8444
See https://www.prefect.io/docs/v3/concepts/server#how-to-guides for more information on running a dedicated Prefect server.
15:11:59.356 | INFO    | Flow run 'ancient-moose' - Beginning flow run 'ancient-moose' for flow 'Mechatronik Musterbau Pipeline'
15:11:59.359 | INFO    | Flow run 'ancient-moose' - === Start des Auftrags ===
15:11:59.375 | INFO    | Task run 'pruefe_bauteil-b69' - Starte Prüfung für Bauteil: 4711
15:11:59.376 | INFO    | Task run 'pruefe_bauteil-b69' - STL-Datei halter_4711.stl erfolgreich validiert.
15:11:59.377 | INFO    | Task run 'pruefe_bauteil-b69' - Finished in state Completed()
15:11:59.377 | INFO    | Flow run 'ancient-moose' - Vorgeschlagenes Verfahren: FDM
15:11:59.379 | INFO    | Task run 'generiere_druckdatei-30f' - Rufe Slicer über Kommandozeile auf...
15:11:59.552 | ←[36mINFO←[0m    | Task run 'generiere_druckdatei-30f' - Slicer-Output: OrcaSlicer generiert G-Code fÃ¼r halter_4711.stl
15:11:59.557 | ←[36mINFO←[0m    | Task run 'generiere_druckdatei-30f' - Finished in state ←[32mCompleted←[0m()
15:11:59.559 | ←[36mINFO←[0m    | Flow run←[35m 'ancient-moose'←[0m - === Ablauf erfolgreich beendet ===
15:11:59.577 | ←[36mINFO←[0m    | Flow run←[35m 'ancient-moose'←[0m - Finished in state ←[32mCompleted←[0m()

Lokales Endergebnis des Kerns: {'auftrag': '4711', 'ergebnis': {'status': 'Erfolgreich eingepasst', 'verfahren': 'FDM', 'nacharbeit': 'M4-Gewinde schneiden'}, 'datei': 'ausgabe_profil.gcode'}
15:11:59.589 | ←[36mINFO←[0m    | prefect - Stopping temporary server on ←[94mhttp://127.0.0.1:8444←[0m
```
## Open Whisper installieren

	pip install openai-whisper
#### pipeline_modular.py
```
import os
import subprocess
from prefect import task, flow, get_run_logger

# =====================================================================
# MODUL-POOL (Die Werkzeuge / Tools)
# =====================================================================

# --- WERKZEUG A: 3D-Druck Bauteilprüfung ---
@task(retries=1, retry_delay_seconds=5)
def pruefe_bauteil(teilennummer: str, stl_pfad: str, material_vorgabe: str):
    logger = get_run_logger()
    logger.info(f"[3D-Druck] Prüfe Bauteil: {teilennummer}")
    if not os.path.exists(stl_pfad):
        raise FileNotFoundError(f"STL fehlt unter: {stl_pfad}")
    
    verfahren = "FDM" if material_vorgabe.upper() in ["ASA", "PLA"] else "Fremdfertigung"
    nacharbeit = "M4-Gewinde" if teilennummer == "4711" else "Keine"
    return {"status": "geprüft", "verfahren": verfahren, "nacharbeit": nacharbeit}

# --- WERKZEUG B: OrcaSlicer CLI ---
@task
def generiere_druckdatei(stl_pfad: str, verfahren: str):
    logger = get_run_logger()
    if verfahren != "FDM":
        return "Keine Druckdatei erforderlich"
        
    # OrcaSlicer CLI-Dummy-Aufruf
    cmd = ["echo", f"OrcaSlicer generiert G-Code für {stl_pfad}"]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return "ausgabe_profil.gcode"

# --- WERKZEUG C: Whisper (Das neue Transferbeispiel) ---
@task
def transkribiere_audio(audio_pfad: str):
    logger = get_run_logger()
    logger.info(f"[Whisper] Starte lokale Transkription für: {audio_pfad}")
    if not os.path.exists(audio_pfad):
        raise FileNotFoundError(f"Audiodatei fehlt unter: {audio_pfad}")
        
    # Hier wird das echte Whisper-Modul geladen
    # Um Rechenzeit beim Testen zu sparen, hier als strukturierter Platzhalter:
    import whisper
    # model = whisper.load_model("base") # Aktivieren für echten Test
    # result = model.transcribe(audio_pfad)
    
    logger.info("Whisper-Transkription erfolgreich abgeschlossen.")
    return {
        "status": "Transkribiert",
        "text_vorschau": "Mustertext: Bauteil 4711 weist Maßabweichungen auf...",
        "werkzeug": "Whisper-Base"
    }


# =====================================================================
# GEMEINSAMER ARCHITEKTUR-KERN (Bleibt unverändert bei neuen Tools)
# =====================================================================

@flow(name="Modulare Mechatronik Pipeline")
def modularer_workflow_kern(auftrags_typ: str, auftrags_daten: dict):
    """
    Der Kern liest nur den Typ und steuert die Module an. 
    Er protokolliert Ergebnisse und Fehler zentral lokal.
    """
    logger = get_run_logger()
    logger.info(f"=== Starte Auftrag vom Typ: {auftrags_typ} ===")
    
    ergebnis_bericht = {"typ": auftrags_typ, "erfolgreich": False}
    
    try:
        # Route 1: Klassischer 3D-Druck Workflow (Demonstrator 1)
        if auftrags_typ == "3d_druck":
            pruefung = pruefe_bauteil(
                teilennummer=auftrags_daten["teilennummer"],
                stl_pfad=auftrags_daten["stl_pfad"],
                material_vorgabe=auftrags_daten["material_vorgabe"]
            )
            gcode = generiere_druckdatei(auftrags_daten["stl_pfad"], pruefung["verfahren"])
            
            ergebnis_bericht.update({"pruefung": pruefung, "datei": gcode, "erfolgreich": True})
            
        # Route 2: Das Transferbeispiel (Whisper) ohne Änderung am Kern-Konstrukt
        elif auftrags_typ == "audio_transkript":
            transkript = transkribiere_audio(audio_pfad=auftrags_daten["audio_pfad"])
            
            ergebnis_bericht.update({"transkript": transkript, "erfolgreich": True})
            
        else:
            logger.error(f"Unbekannter Auftragstyp: {auftrags_typ}")
            
    except Exception as e:
        logger.error(f"Fehler im Workflow-Lauf: {str(e)}")
        ergebnis_bericht["fehler"] = str(e)
        
    logger.info(f"=== Ende des Auftrags {auftrags_typ} ===")
    return ergebnis_bericht


# =====================================================================
# SYSTEMTEST (Lokale Ausführung / Simulation der 8 Musteraufträge)
# =====================================================================
if __name__ == "__main__":
    # 0. Vorbereitung der Testdateien für Woche 1
    with open("halter_4711.stl", "w") as f: f.write("solid dummy")
    with open("notiz.wav", "w") as f: f.write("audio dummy")

    # --- LAUF 1: 3D-Druck Demonstrator ---
    auftrag_1 = {
        "teilennummer": "4711",
        "stl_pfad": "halter_4711.stl",
        "material_vorgabe": "ASA"
    }
    bericht_1 = modularer_workflow_kern(auftrags_typ="3d_druck", auftrags_daten=auftrag_1)
    print("\n[Protokoll Kern] Lauf 1:", bericht_1)

    # --- LAUF 2: Transferbeispiel Whisper (Modular hinzugefügt) ---
    auftrag_2 = {
        "audio_pfad": "notiz.wav"
    }
    bericht_2 = modularer_workflow_kern(auftrags_typ="audio_transkript", auftrags_daten=auftrag_2)
    print("\n[Protokoll Kern] Lauf 2:", bericht_2)
```
## Installieren die OrcaSlicer App
https://apps.microsoft.com/detail/9mv6gl23xm59?hl=de-DE&gl=DE
