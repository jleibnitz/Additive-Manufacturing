import os
import subprocess
from typing import Literal, Union
from pydantic import BaseModel, Field, FilePath, ValidationError
from prefect import task, flow, get_run_logger

# =====================================================================
# WOCHE 3: SCHNITTSTELLEN-DEFINITION (Datenmodelle)
# =====================================================================

class DruckAuftragModel(BaseModel):
    """Schnittstelle für den 3D-Druck Demonstrator 01"""
    auftrags_typ: Literal["3d_druck"] = "3d_druck"
    teilennummer: str = Field(..., min_length=1, description="Eindeutige ID des Bauteils")
    # FilePath validiert automatisch, ob die Datei auf dem Linux-System existiert!
    stl_pfad: FilePath = Field(..., description="Lokal existierender Pfad zur STL-Datei")
    material_vorgabe: Literal["ASA", "PLA", "PETG", "ABS"] = Field(..., description="Zulässige Materialien")
    toleranz_mm: float = Field(..., gt=0, lt=2.0, description="Toleranzvorgabe in mm")

class AudioAuftragModel(BaseModel):
    """Schnittstelle für das Transferbeispiel Whisper"""
    auftrags_typ: Literal["audio_transkript"] = "audio_transkript"
    # Validiert ebenfalls die Existenz der Audiodatei vorab
    audio_pfad: FilePath = Field(..., description="Lokal existierender Pfad zur Audiodatei")


# =====================================================================
# TOOL-MODULE (Bleiben funktional getrennt)
# =====================================================================

@task
def pruefe_bauteil(auftrag: DruckAuftragModel):
    logger = get_run_logger()
    logger.info(f"[3D-Druck] Verarbeite validierten Auftrag für Bauteil {auftrag.teilennummer}")
    
    verfahren = "FDM" if auftrag.material_vorgabe in ["ASA", "PLA"] else "Fremdfertigung"
    nacharbeit = "M4-Gewinde" if auftrag.teilennummer == "4711" else "Keine"
    
    return {"verfahren": verfahren, "nacharbeit": nacharbeit}

@task
def transkribiere_audio(auftrag: AudioAuftragModel):
    logger = get_run_logger()
    logger.info(f"[Whisper] Verarbeite validierte Audiodatei: {auftrag.audio_pfad}")
    return {"status": "Transkribiert", "text": "Mustertext aus Audiodatei..."}


# =====================================================================
# GEMEINSAMER ARCHITEKTUR-KERN (Mit automatisierter Eingangskontrolle)
# =====================================================================

@flow(name="Validierter Mechatronik Workflow")
def workflow_kern_mit_validierung(rohe_auftrags_daten: dict):
    logger = get_run_logger()
    logger.info("=== Neuer Auftrag an der Systemgrenze eingetroffen ===")
    
    ergebnis_bericht = {"erfolgreich": False, "fehler": None}
    
    # 1. Schritt: Eingangskontrolle & Validierung (Woche 3 Aufgabe)
    try:
        typ = rohe_auftrags_daten.get("auftrags_typ")
        
        if typ == "3d_druck":
            # Validiert alle Felder gegen das DruckAuftragModel
            validierter_auftrag = DruckAuftragModel(**rohe_auftrags_daten)
            logger.info("-> Validierung erfolgreich: Datentypen und Dateien korrekt.")
            
            # Ausführung des spezifischen Tasks
            ergebnis = pruefe_bauteil(validierter_auftrag)
            ergebnis_bericht.update({"daten": ergebnis, "erfolgreich": True})
            
        elif typ == "audio_transkript":
            # Validiert das Audio-Modell
            validierter_auftrag = AudioAuftragModel(**rohe_auftrags_daten)
            logger.info("-> Validierung erfolgreich: Audiodatei existiert.")
            
            ergebnis = transkribiere_audio(validierter_auftrag)
            ergebnis_bericht.update({"daten": ergebnis, "erfolgreich": True})
            
        else:
            raise ValueError(f"Unbekannter oder fehlender 'auftrags_typ': {typ}")
            
    # 2. Schritt: Lokale Protokollierung von Schnittstellenfehlern (Woche 4 Aufgabe)
    except ValidationError as ve:
        logger.error("-> VALIDIERUNGSFEHLER: Auftrag erfüllt die Schnittstellen-Kriterien nicht!")
        # Gibt dem Nutzer exakt aus, welches Feld fehlt oder falsch ist
        ergebnis_bericht["fehler"] = ve.errors()
    except Exception as e:
        logger.error(f"-> SYSTEMFEHLER: {str(e)}")
        ergebnis_bericht["fehler"] = str(e)
        
    logger.info("=== Auftrag abgearbeitet. Ergebnis protokolliert. ===\n")
    return ergebnis_bericht


# =====================================================================
# SIMULATION DER MUSTERAUFTRÄGE (Erprobung & Auswertung)
# =====================================================================
if __name__ == "__main__":
    # Vorbereitung der physischen Dummy-Dateien
    with open("bauteil.stl", "w") as f: f.write("stl data")
    with open("sprachnotiz.wav", "w") as f: f.write("audio data")

    print("--- TEST 1: Gültiger 3D-Druck Auftrag ---")
    gueltiger_druck = {
        "auftrags_typ": "3d_druck",
        "teilennummer": "4711",
        "stl_pfad": "bauteil.stl",         # Existiert physisch
        "material_vorgabe": "ASA",         # Ist im Literal erlaubt
        "toleranz_mm": 0.2                 # Liegt im erlaubten Bereich (0.0 bis 2.0)
    }
    print(workflow_kern_mit_validierung(gueltiger_druck))


    print("--- TEST 2: Ungültiger Auftrag (Falsches Material & fehlende Datei) ---")
    ungueltiger_druck = {
        "auftrags_typ": "3d_druck",
        "teilennummer": "9999",
        "stl_pfad": "nicht_existierende_datei.stl",  # FEHLER: Datei fehlt!
        "material_vorgabe": "HOLZ",                  # FEHLER: Nicht im Literal erlaubt!
        "toleranz_mm": 0.1
    }
    # Der Kern fängt den Fehler ab und gibt ein exaktes Fehler-JSON zurück
    fehler_bericht = workflow_kern_mit_validierung(ungueltiger_druck)
    
    print("Vom Kern generierter Fehlerbericht für die Auswertung:")
    for err in fehler_bericht["fehler"]:
        print(f" -> Feld '{err['loc'][0]}': {err['msg']}")