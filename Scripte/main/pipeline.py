import sys
import os
import subprocess
from comtypes import logger
import trimesh

from prefect import task, flow, get_run_logger

# Hier erfolgt das "Include" aus einer bestehenden Datei SliceOrca.py
from SliceOrca import erstelle_vorschau_bild, erstelle_sprachnotiz, slice_stl_with_orca

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Berechnet die Abmessungen eines 3D-Modells aus einer STL-Datei.
def calc_measure(stl_path: str):
  
    if not os.path.exists(stl_path):
        raise FileNotFoundError(f"STL-Datei unter {stl_path} nicht gefunden!")
    
    # STL-Datei laden (force='mesh' stellt sicher, dass auch Szenen als ein Mesh geladen werden)
    mesh = trimesh.load(stl_path, force="mesh")
    
    # Abmessungen (Länge in X, Y und Z) auslesen
    x_dim, y_dim, z_dim = mesh.extents
    
    return {
        "x_dim": x_dim,
        "y_dim": y_dim,
        "z_dim": z_dim,
        "min_bounds": mesh.bounds[0].tolist(),
        "max_bounds": mesh.bounds[1].tolist()
    }


# --- TASK 1: Bauteilprüfung (Eingabe & Einordnung) ---
@task(retries=1, retry_delay_seconds=5)

def pruefe_bauteil(teilennummer: str, stl_pfad: str, material_vorgabe: str):
    logger = get_run_logger()
    logger.info(f"Starte Prüfung für Bauteil: {teilennummer}")
    
    if not os.path.exists(stl_pfad):
        raise FileNotFoundError(f"STL-Datei unter {stl_pfad} nicht gefunden!")
        
    # Hier liest 'trimesh' die Außenmaße    
    abmessungen = calc_measure(stl_pfad)
    logger.info(f"Abmessungen (X x Y x Z): {abmessungen['x_dim']:.2f} x {abmessungen['y_dim']:.2f} x {abmessungen['z_dim']:.2f} mm")
    logger.info(f"STL-Datei {stl_pfad} erfolgreich validiert.")
    
    # Vorschlag basierend auf Material (z.B. ASA -> FDM) - Evtl aus einer Arbeitskarte lesen

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
    
    # OrcaSlicer CLI Aufruf
    cmd = ["echo", f"OrcaSlicer generiert G-Code für {stl_pfad}"]

    stl_vollpfad = os.path.abspath(stl_pfad)
    arbeitsverzeichnis = os.path.dirname(stl_vollpfad)
    base_name, _ = os.path.splitext(os.path.basename(stl_vollpfad))
    wav_datei = os.path.join(arbeitsverzeichnis, f"{base_name}.wav")
    bild_pfad = os.path.join(arbeitsverzeichnis, f"{base_name}.png")


    cmd = ["echo", f"eine Sprachnotiz für das Ergebnis zu {stl_pfad} wird erstellt..."]    
    ergebnis = slice_stl_with_orca(stl_pfad)  # Aufruf der Funktion aus SliceOrca.py  
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)

    logger.info(f"OrcaSlicer: {result.stdout.strip()}")

    logger.info(f"--- Slicing Ergebnis ---")
    logger.info(f"G-Code Datei:      {ergebnis['gcode_path']}")
    logger.info(f"Druckzeit:         {ergebnis['print_time']}")
    logger.info(f"Filament (Gramm):  {ergebnis['filament_used_g']} g")

    cmd = ["echo", f"eine Sprachnotiz für das Ergebnis zu {stl_pfad} wird erstellt..."]
    msg=erstelle_sprachnotiz(ergebnis, base_name=base_name, wav_pfad=wav_datei)
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    logger.info(f"Sprachnotiz: {result.stdout.strip()}")
    logger.info(f"{msg}")

    cmd = ["echo", f"ein Vorschaubild für das Bauteil {stl_pfad} wird erstellt..."]
    msg=erstelle_vorschau_bild(stl_pfad, bild_pfad)
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    logger.info(f"Vorschaubild: {result.stdout.strip()}")
    logger.info(f"{msg}")

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
    #with open("halter_4711.stl", "w") as f:
    #    f.write("solid dummy_stl ... endsolid")
    #         
    # Start des Flows (Entspricht einem Musterauftrag)
    
    ergebnis = musterbau_workflow(
        # Arbeitskarte: Bauteilnummer, STL-Dateipfad, Materialvorgabe
        teilennummer="4711", 
        stl_pfad="halter_4711.stl", 
        material_vorgabe="ASA"
    )
    logger.info("\nLokales Endergebnis des Kerns:", ergebnis)