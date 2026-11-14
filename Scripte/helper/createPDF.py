from fpdf import FPDF
bauteil = "halter_4711"
# 1. Neues PDF-Objekt erstellen (Hochformat, Millimeter, A4)
pdf = FPDF(orientation="P", unit="mm", format="A4")
pdf.add_page()

# 2. Überschrift hinzufügen
pdf.set_font("Helvetica", style="B", size=18)
pdf.cell(w=0, h=15, text=f"Vorschlag für {bauteil}", new_x="LMARGIN", new_y="NEXT", align="C")

# Kleiner Abstand nach unten
pdf.ln(5)

# 3. Fließtext hinzufügen
pdf.set_font("Helvetica", size=12)
info_text = (
    f"Suche nach einem Halter für Schraubendreher, den ich in meiner Werkstatt anbringen kann. "
)
pdf.multi_cell(w=0, h=8, text=info_text)

# Kleiner Abstand vor dem Bild
pdf.ln(10)

# 4. Bild einfügen (Pfad zum Bild anpassen!)
# x und y bestimmen die Position, w legt die Breite in mm fest (Höhe skaliert automatisch)
pdf.image(f"{bauteil}.png", x=30, w=150)

# 5. PDF speichern
pdf.output(f"{bauteil}_vorschlag.pdf")
print("PDF wurde erfolgreich erstellt!")