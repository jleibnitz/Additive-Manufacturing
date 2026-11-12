
# --- TO DO ---

Umgebung prüfen:
```
python --version
```
erwartet wird **3.15.2**


## Umgebung einrichten ohne Installationstool
das benötigte Installationstool (*pip*) wird nachträglich manuell installiert, somit kann die Installation sollständig von der Umgebung durchgeführt werden. 

- **Virtuelle Umgebung ohne Pip erstellen:**
    ```
    python -m venv --without-pip ~/python-env
    ```
    
- **Die Umgebung aktivieren:**
    ```
    source ~/python-env/bin/activate
    ```
    
- **Pip manuell in der aktivierten Umgebung installieren:** Lade das offizielle Installationsskript herunter und führe es aus:
    ```
    curl https://bootstrap.pypa.io/get-pip.py | python
    ```
    _(Alternativ, falls `curl` nicht vorhanden ist: `wget -O - [https://bootstrap.pypa.io/get-pip.py](https://bootstrap.pypa.io/get-pip.py) | python`)_

## Projektinstallation

