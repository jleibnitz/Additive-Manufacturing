import os
import re
import shutil
import subprocess
import zipfile
import trimesh
import xml.etree.ElementTree as ET


import os
import pyttsx3

import os
import pyttsx3

import matplotlib

matplotlib.use(
    "Agg"
)  # Wichtig für Prefect: Rendert im Hintergrund ohne Fenster
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import trimesh


def erstelle_vorschau_bild(
    stl_pfad: str, bild_pfad: str, farbe: str = "#2b7bba"
) -> str:
  """Erzeugt aus einer STL-Datei ein isometrisches Vorschaubild (PNG oder JPG)."""
  mesh = trimesh.load(stl_pfad, force="mesh")

  # Figur ohne störende Achsen anlegen
  fig = plt.figure(figsize=(8, 8), dpi=150)
  ax = fig.add_subplot(111, projection="3d")

  # Dreiecke des Meshes als 3D-Polygone hinzufügen
  poly = Poly3DCollection(
      mesh.triangles,
      facecolor=farbe,
      edgecolor="#1a4e7a",
      linewidths=0.15,
      alpha=0.95,
  )
  ax.add_collection3d(poly)

  
  # Skalierung für alle drei Achsen gleichmäßig setzen (verhindert Verzerrungen)
  min_b, max_b = mesh.bounds
  mitte_x, mitte_y, mitte_z = (min_b + max_b) / 2.0
  max_reichweite = float((max_b - min_b).max() / 2.0)

  ax.set_xlim(mitte_x - max_reichweite, mitte_x + max_reichweite)
  ax.set_ylim(mitte_y - max_reichweite, mitte_y + max_reichweite)
  ax.set_zlim(mitte_z - max_reichweite, mitte_z + max_reichweite)


  # Schöne isometrische Perspektive wählen und Achsen ausblenden
  ax.view_init(elev=30, azim=45)
  ax.set_axis_off()

  # Bild speichern (Format richtet sich automatisch nach Dateiendung .png oder .jpg)
  plt.savefig(bild_pfad, bbox_inches="tight", pad_inches=0.1, transparent=False)
  plt.close(fig)

  msg=(f"Vorschaubild gespeichert unter: {bild_pfad}")
  return msg



def formatiere_zeit_fuer_sprache(zeit_str: str) -> str:
  """Wandelt '4h 29m 30s' in natürlich sprechbaren Text um."""
  if not zeit_str:
    return "unbekannt"

  text = zeit_str
  text = text.replace("h", " Stunden,").replace("m", " Minuten und")
  if text.endswith("s"):
    text = text[:-1] + " Sekunden"
  return text


def erstelle_sprachnotiz(ergebnis: dict, base_name: str, wav_pfad: str) -> str:
  """Erzeugt aus dem Slicing-Ergebnis eine gesprochene WAV-Datei am übergebenen Zielpfad."""
  dx, dy, dz = ergebnis["dimensions_mm"]
  gramm = str(ergebnis["filament_used_g"]).replace(".", " Komma ")
  druckzeit_gesprochen = formatiere_zeit_fuer_sprache(ergebnis["print_time"])

  # Unterstriche für eine sauberere Aussprache durch Leerzeichen ersetzen (z. B. "halter 4711")
  bauteil_gesprochen = base_name.replace("_", " ")

  nachricht = (
      f"Das Slicing für das Bauteil {bauteil_gesprochen} ist abgeschlossen. "
      f"Die Abmessungen betragen {int(dx)} mal {int(dy)} mal {int(dz)}"
      " Millimeter. "
      f"Der geschätzte Materialverbrauch liegt bei {gramm} Gramm. "
      f"Die voraussichtliche Druckzeit beträgt {druckzeit_gesprochen}."
  )

  engine = pyttsx3.init()
  engine.setProperty("rate", 175)

  for voice in engine.getProperty("voices"):
    if "german" in voice.name.lower() or "de" in voice.id.lower():
      engine.setProperty("voice", voice.id)
      break

  engine.save_to_file(nachricht, wav_pfad)
  engine.runAndWait()

  msg=(f"Sprachnotiz gespeichert unter: {wav_pfad}")
  return msg


def parse_orca_gcode_stats(gcode_path: str) -> dict:
  """Durchsucht alle Kommentarzeilen der G-Code-Datei nach Druckzeit und Filamentverbrauch."""
  stats = {
      "print_time": None,
      "filament_used_mm": None,
      "filament_used_cm3": None,
      "filament_used_g": None,
  }

  with open(gcode_path, "r", encoding="utf-8", errors="ignore") as f:
    # Nur Kommentarzeilen (beginnen mit ;) einlesen – das geht in wenigen Millisekunden
    comment_lines = [line.strip() for line in f if line.lstrip().startswith(";")]

  comment_text = "\n".join(comment_lines)

  # 1. Druckzeit auslesen (alle bekannten Schreibweisen in OrcaSlicer)
  time_patterns = [
      r";\s*total estimated time:\s*([^\r\n;]+)",
      r";\s*estimated printing time.*?=\s*([^\r\n;]+)",
      r";\s*model printing time:\s*([^\r\n;]+)",
  ]
  for pattern in time_patterns:
    match = re.search(pattern, comment_text, re.IGNORECASE)
    if match:
      stats["print_time"] = match.group(1).strip()
      break

  # 2. Filament in mm
  mm_match = re.search(
      r";\s*filament used \[mm\]\s*=\s*([\d\.]+)", comment_text
  )
  if mm_match:
    stats["filament_used_mm"] = float(mm_match.group(1))

  # 3. Filament in cm³
  cm3_match = re.search(
      r";\s*filament used \[cm3\]\s*=\s*([\d\.]+)", comment_text
  )
  if cm3_match:
    stats["filament_used_cm3"] = float(cm3_match.group(1))

  # 4. Filament in Gramm
  g_match = re.search(
      r";\s*(?:total )?filament used \[g\]\s*=\s*([\d\.]+)", comment_text
  )
  if g_match:
    stats["filament_used_g"] = float(g_match.group(1))

  return stats


def slice_stl_with_orca(
    stl_file: str,
    template_3mf: str = (
        r"D:\Projekte\AdditiveManufacturing\ProtoType\vorlage_mit_modell.3mf"
    ),
    output_gcode: str = "",
    orca_exe: str = r"D:\Program Files\OrcaSlicer\orca-slicer.exe",
    timeout_seconds: int = 120,
) -> dict:
  stl_full = os.path.abspath(stl_file)
  tpl_full = os.path.abspath(template_3mf)

  if not os.path.isfile(stl_full):
    raise FileNotFoundError(f"STL-Datei nicht gefunden: {stl_full}")
  if not os.path.isfile(tpl_full):
    raise FileNotFoundError(f"3MF-Vorlage nicht gefunden: {tpl_full}")
  if not os.path.isfile(orca_exe):
    raise FileNotFoundError(f"OrcaSlicer nicht gefunden: {orca_exe}")

  work_dir = os.path.dirname(stl_full)
  stl_name = os.path.basename(stl_full)
  #base_name = os.path.splitext(stl_name)
  base_name, _ = os.path.splitext(stl_name)

  if not output_gcode:
    output_gcode = os.path.join(work_dir, f"{base_name}.gcode")
  elif not os.path.isabs(output_gcode):
    output_gcode = os.path.join(work_dir, output_gcode)

  temp_3mf = os.path.join(work_dir, "temp_job.3mf")
  sliced_3mf = os.path.join(work_dir, "temp_sliced.gcode.3mf")

  # 1. STL laden & Abmessungen ermitteln
  mesh = trimesh.load(stl_full, force="mesh")
  dim_x, dim_y, dim_z = mesh.extents

  (min_x, min_y, min_z), (max_x, max_y, max_z) = mesh.bounds
  shift_x = float(128.0 - ((min_x + max_x) / 2.0))
  shift_y = float(128.0 - ((min_y + max_y) / 2.0))
  shift_z = float(-min_z)
  mesh.apply_translation([shift_x, shift_y, shift_z])


      # 2. XML-Daten generieren (mit direktem Unpacking statt eckiger Klammern)
  vertices_xml = "\n".join(
        f'          <vertex x="{x:.6g}" y="{y:.6g}" z="{z:.6g}"/>'
        for x, y, z in mesh.vertices
    )
  triangles_xml = "\n".join(
        f'          <triangle v1="{v1}" v2="{v2}" v3="{v3}"/>'
        for v1, v2, v3 in mesh.faces
    )


  with zipfile.ZipFile(tpl_full, "r") as tpl_zip:
    tpl_main_text = tpl_zip.read("3D/3dmodel.model").decode("utf-8")
    ns_core_match = re.search(r'xmlns="([^"]+)"', tpl_main_text)
    ns_prod_match = re.search(r'xmlns:p="([^"]+)"', tpl_main_text)
    ns_core = (
        ns_core_match.group(1)
        if ns_core_match
        else "http://microsoft.com"
    )
    ns_prod = (
        ns_prod_match.group(1)
        if ns_prod_match
        else "http://microsoft.com"
    )

  obj_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<model unit="millimeter" xml:lang="en-US" xmlns="{ns_core}">
  <resources>
    <object id="1" type="model">
      <mesh>
        <vertices>
{vertices_xml}
        </vertices>
        <triangles>
{triangles_xml}
        </triangles>
      </mesh>
    </object>
  </resources>
  <build/>
</model>"""

  main_model_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<model unit="millimeter" xml:lang="en-US" xmlns="{ns_core}" xmlns:p="{ns_prod}">
  <resources>
    <object id="2" type="model">
      <components>
        <component p:path="/3D/Objects/object_1.model" objectid="1" p:UUID="00010001-81cb-4c03-9d28-80fed5dfa1dc" transform="1 0 0 0 1 0 0 0 1 0 0 0"/>
      </components>
    </object>
  </resources>
  <build>
    <item objectid="2" p:UUID="00010000-81cb-4c03-9d28-80fed5dfa1dc" transform="1 0 0 0 1 0 0 0 1 0 0 0" printable="1"/>
  </build>
</model>"""

  model_settings_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<config>
  <object id="2">
    <metadata key="name" value="{stl_name}"/>
    <metadata key="extruder" value="1"/>
    <part id="1" subtype="normal_part">
      <metadata key="name" value="{stl_name}"/>
      <metadata key="matrix" value="1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1"/>
      <metadata key="source_file" value="{stl_name}"/>
      <metadata key="source_object_id" value="0"/>
      <metadata key="source_volume_id" value="0"/>
    </part>
  </object>
  <plate>
    <metadata key="plater_id" value="1"/>
    <metadata key="plater_name" value=""/>
    <metadata key="locked" value="false"/>
    <model_instance>
      <metadata key="object_id" value="2"/>
      <metadata key="instance_id" value="0"/>
      <metadata key="identify_id" value="1"/>
    </model_instance>
  </plate>
</config>"""

  # 3. 3MF zusammenbauen
  with (
      zipfile.ZipFile(tpl_full, "r") as zin,
      zipfile.ZipFile(temp_3mf, "w", zipfile.ZIP_DEFLATED) as zout,
  ):
    for item in zin.infolist():
      if (
          item.filename.startswith("3D/Objects/")
          or item.filename == "3D/3dmodel.model"
          or item.filename == "Metadata/model_settings.config"
      ):
        continue

      content = zin.read(item.filename)
      if item.filename == "3D/_rels/3dmodel.model.rels":
        rels_text = content.decode("utf-8")
        rels_text = re.sub(
            r'Target="[^"]+"', 'Target="/3D/Objects/object_1.model"', rels_text
        )
        content = rels_text.encode("utf-8")

      zout.writestr(item, content)

    zout.writestr("3D/Objects/object_1.model", obj_xml.encode("utf-8"))
    zout.writestr("3D/3dmodel.model", main_model_xml.encode("utf-8"))
    zout.writestr(
        "Metadata/model_settings.config", model_settings_xml.encode("utf-8")
    )

  # 4. OrcaSlicer ausführen
  if os.path.exists(sliced_3mf):
    os.remove(sliced_3mf)

  cmd = [
      orca_exe,
      "--debug",
      "2",
      "--arrange",
      "1",
      "--slice",
      "0",
      "--export-3mf",
      sliced_3mf,
      temp_3mf,
  ]

  process = subprocess.Popen(
      cmd, stdin=subprocess.DEVNULL, stdout=None, stderr=None
  )

  try:
    returncode = process.wait(timeout=timeout_seconds)
  except subprocess.TimeoutExpired:
    subprocess.run(
        ["taskkill", "/F", "/T", "/PID", str(process.pid)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    raise TimeoutError(
        f"OrcaSlicer hat nach {timeout_seconds} Sekunden nicht reagiert."
    )

  if returncode != 0 or not os.path.isfile(sliced_3mf):
    raise RuntimeError(f"OrcaSlicer Fehler (Code {returncode}).")

  # 5. G-Code extrahieren & Kennzahlen auslesen
  with zipfile.ZipFile(sliced_3mf, "r") as zsliced:
    with (
        zsliced.open("Metadata/plate_1.gcode") as src,
        open(output_gcode, "wb") as dst,
    ):
      shutil.copyfileobj(src, dst)

  for tmp in (temp_3mf, sliced_3mf):
    if os.path.exists(tmp):
      os.remove(tmp)

  gcode_stats = parse_orca_gcode_stats(output_gcode)

  return {
      "gcode_path": output_gcode,
      "dimensions_mm": (round(dim_x, 2), round(dim_y, 2), round(dim_z, 2)),
      **gcode_stats,
  }


if __name__ == "__main__":

  stl_datei = "halter_4711.stl"

  # 1. Basename und Zielpfad für die WAV-Datei direkt aus der STL-Datei ableiten
  stl_vollpfad = os.path.abspath(stl_datei)
  arbeitsverzeichnis = os.path.dirname(stl_vollpfad)
  base_name, _ = os.path.splitext(os.path.basename(stl_vollpfad))
  wav_datei = os.path.join(arbeitsverzeichnis, f"{base_name}.wav")
  png_datei = os.path.join(arbeitsverzeichnis, f"{base_name}.png")

  # 2. Slicing durchführen
  ergebnis = slice_stl_with_orca(stl_vollpfad)

  print("\n--- Slicing Ergebnis ---")
  print(f"G-Code Datei:      {ergebnis['gcode_path']}")
  print(f"Druckzeit:         {ergebnis['print_time']}")
  print(f"Filament (Gramm):  {ergebnis['filament_used_g']} g")

  # 3. Basename und den fertigen WAV-Dateipfad an die Sprachausgabe übergeben
  erstelle_sprachnotiz(ergebnis, base_name=base_name, wav_pfad=wav_datei)

  # 4. Basename und den fertigen PNG-Dateipfad an die Vorschauübergeben
  erstelle_vorschau_bild(stl_vollpfad, png_datei)