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
