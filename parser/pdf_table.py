import pdfplumber
import requests
import re
from io import BytesIO

def fetch_pdf_data(detail_number, spacing_inches):
    # Build URL and download PDF
    url = f"https://thermalenvelope.ca/pdf/thermal_data_sheet_{detail_number}.pdf?version=v1.7.3"
    print(f"[INFO] Downloading PDF from: {url}")
    response = requests.get(url)
    if response.status_code != 200:
        print(f"[ERROR] Failed to download PDF for detail {detail_number}")
        return [], []

    pdf = pdfplumber.open(BytesIO(response.content))
    tables = [table for page in pdf.pages for table in page.extract_tables()]

    # Step 1: Debug print all headers
    print("\n[DEBUG] Scanning table headers:")
    for table in tables:
        if table and table[0]:
            print(" -", table[0])

    # Step 2: Extract R1D from ANY table cell right next to one labeled "R1D"
    r1d = None
    for table in tables:
        for row in table:
            for i, cell in enumerate(row):
                if not isinstance(cell, str):
                    continue
                normalized = re.sub(r"\s+", "", cell).lower()
                if normalized == "r1d":
                    if i + 1 < len(row):
                        right_cell = row[i + 1]
                        if right_cell:
                            print(f"[DEBUG] Found R1D label → Right cell: {right_cell}")
                            match = re.search(r"R-?([0-9.]+)", right_cell)
                            if match:
                                r1d = float(match.group(1))
                                print(f"[INFO] R1D extracted from summary = {r1d}")
                                break
            if r1d is not None:
                break
        if r1d is not None:
            break

    if r1d is None:
        print("[ERROR] Failed to extract R1D from summary section.")
        return [], []

    # Step 3: Find table containing vertical spacing column
    pattern = re.compile(fr"{spacing_inches}\s*[\"′”“']?\s*vertical\s*clip\s*spacing", re.IGNORECASE)
    selected_table = None

    for table in tables:
        if not table or not table[0]:
            continue
        header_row = [" ".join(cell.split()) if isinstance(cell, str) else "" for cell in table[0]]
        if any(cell and pattern.search(cell.lower()) for cell in header_row):
            selected_table = table
            break

    if not selected_table:
        print(f"[ERROR] Could not find data table for vertical spacing {spacing_inches}\".")
        return [], []

    # Step 4: Normalize header and find Ro/Exterior Insulation columns
    header = [" ".join(cell.split()) if isinstance(cell, str) else "" for cell in selected_table[0]]
    try:
        ext_col = header.index("Exterior Insulation 1D R-Value")
        ro_col = next(i for i, cell in enumerate(header) if pattern.search(cell.lower()))
    except (ValueError, StopIteration):
        print("[ERROR] Could not find required columns.")
        return [], []

    # Step 5: Extract data rows
    x_vals = []
    y_vals = []

    for row in selected_table[1:]:
        try:
            ext_val = re.search(r"R-?([\d.]+)", row[ext_col])
            ro_val = re.search(r"R-?([\d.]+)", row[ro_col])
            if ext_val and ro_val:
                x = float(ext_val.group(1))
                ro = float(ro_val.group(1))
                x_vals.append(x)
                y_vals.append(ro - r1d)
        except Exception:
            continue

    return x_vals, y_vals
