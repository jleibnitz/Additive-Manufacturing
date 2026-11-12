Es wird ein Paketmanager "CONDA" benötigt der holt die Binaries:

1. MIniforge installieren (enthält CONDA)
	1. https://conda-forge.org/download/
2. Aktivieren von CONDA
	1.  für Powershell (PS) in DOS Befehlszeile (CMD)
		1. `D:\ProgramData\miniforge3\Scripts\conda.exe init powershell`
		2. `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
3. Dann im Arbeitsverzeichnis eine CONDA Umgebung setzen
	1. `conda create --name conda-env
4.  Aktivieren der Umgebung
	1. `conda activate conda-env
5. Installieren der Binaries zu "Prefect" und "trimesh"
	1. `conda install -c conda-forge prefect trimesh -y
6. Test ob "prefect" installiert wurde
	1. `conda list prefect`
    		```
			# packages in environment at C:\Users\User\.conda\envs\conda-env:
			#
			# Name                     Version          Build            Channel
			prefect                    3.9.2            pypi_0           pypi ```
7. Abhängige Pakete aktualisieren
	1. `pip install "sqlalchemy<2.1.0"
	2. `pip install --upgrade prefect fastapi pydantic
8. Deaktivieren der Umgebung (wichtig wenn die Umgebungen gewechselt werden)
	1. `conda deactivate



