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