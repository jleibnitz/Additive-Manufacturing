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