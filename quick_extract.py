import pdfplumber

pdf_path = "Contrats/TotalEnergies.pdf"

with pdfplumber.open(pdf_path) as pdf:
    print(f"Pages: {len(pdf.pages)}\n")
    for i, page in enumerate(pdf.pages[:3], 1):  # Premières 3 pages
        print(f"=== PAGE {i} ===")
        text = page.extract_text()
        if text:
            print(text)
        print("\n")
