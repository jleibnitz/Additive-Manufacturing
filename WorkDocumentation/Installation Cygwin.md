Es wird ein Paketmanager "CONDA" benötigt der holt die Binaries:

1. Miniforge installieren (enthält CONDA)
	1. https://conda-forge.org/download/
2. Aktivieren von CONDA für Unix Befehlsumgebung (BASH)
	1. Shell (BASH) für CONDA initialisieren
		1. `/cygdrive/D/ProgramData/miniforge3/Scripts/conda.exe init bash`
	2. Alle Shell Dateien bereinigen und den Zeilenumbruch bei Shell in UNIX-Format
		1. `find /cygdrive/d/ProgramData/miniforge3/etc/conda/ -name "*.sh" -exec sed -i 's/\r$//' {} +`
	3. Startscript (*.bashrc*) anpassen
    
	   		# >>> conda initialize >>>
			# !! Contents within this block are managed by 'conda init' !!
			if [ -f '/cygdrive/d/ProgramData/miniforge3/Scripts/conda.exe' ]; then
			    #eval "$('/cygdrive/d/ProgramData/miniforge3/Scripts/conda.exe' 'shell.bash' 'hook')"
			    eval "$(/cygdrive/d/ProgramData/miniforge3/Scripts/conda.exe shell.bash hook | tr -d "\r")"
			
			fi
			# <<< conda initialize <<<
1. Dann im Arbeitsverzeichnis eine CONDA Umgebung setzen
	1. `conda create --name conda-env-bash`
2.  Aktivieren der Umgebung
	1. `conda activate conda-env-bash`
3. Installieren der Binaries zu "*prefect*" und "*trimesh*"
	1. `conda install -c conda-forge prefect trimesh -y`
4. Test ob "*prefect*" installiert wurde
	1. `conda list prefect`
    
			# packages in environment at C:\Users\User\.conda\envs\conda-env:
			#
			# Name                     Version          Build            Channel
			prefect                    3.9.2            pypi_0           pypi 
5. Abhängige Pakete aktualisieren
	1. `pip install "sqlalchemy<2.1.0"`
	2. `pip install --upgrade prefect fastapi pydantic`
6. Deaktivieren der Umgebung (wichtig wenn die Umgebungen gewechselt werden)
	1. `conda deactivate`
