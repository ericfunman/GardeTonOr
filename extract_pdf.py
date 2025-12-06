import pdfplumber

pdf = pdfplumber.open("Contrats/TotalEnergies.pdf")
for i, page in enumerate(pdf.pages):
    text = page.extract_text()
    if text:
        print(f"\n=== PAGE {i+1} ===\n")
        print(text)
