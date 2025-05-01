from playwright.sync_api import sync_playwright, TimeoutError
from bs4 import BeautifulSoup
import time
import re

def fetch_table_data(detail_number, spacing_filter):
    print("[INFO] Launching browser and navigating to main catalogue...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto("https://thermalenvelope.ca/catalogue/", timeout=60000)

        # STEP 1: Toggle US Customary units only
        try:
            page.wait_for_selector("text=Settings", timeout=10000)
            page.click("text=Settings")
            page.wait_for_selector("label:has-text('Show US Customary units')", timeout=5000)
            page.click("label:has-text('Show US Customary units')")
            time.sleep(0.5)
            page.click("label:has-text('Show Metric (SI) units')")  # uncheck SI
            print("[INFO] Units switched to US Customary only.")
            time.sleep(1)
        except TimeoutError:
            print("[WARNING] Unit toggle failed. Defaulting to SI.")

        # STEP 2: Search for the detail
        try:
            print(f"[INFO] Searching for detail: {detail_number}")
            search_input = page.wait_for_selector("input[placeholder='Search detail text']", timeout=5000)
            search_input.fill(detail_number)
            time.sleep(1)  # Wait for results to populate
            page.keyboard.press("Enter")
            time.sleep(2)
            page.click(f"text={detail_number}", timeout=5000)
            print("[INFO] Detail modal opened.")
        except TimeoutError:
            print(f"[ERROR] Could not find detail: {detail_number}")
            browser.close()
            return [], []

        # STEP 3: Wait for the modal table
        try:
            page.wait_for_selector("table.variant-table-2", timeout=10000)
            time.sleep(1)
        except TimeoutError:
            print("[ERROR] Modal table never appeared.")
            browser.close()
            return [], []

        # STEP 4: Extract HTML and close
        html = page.content()
        browser.close()

    # STEP 5: Parse HTML with BeautifulSoup
    soup = BeautifulSoup(html, "html.parser")
    table = soup.find("table", {"class": "variant-table-2"})
    if not table:
        print("[ERROR] Table not found.")
        return [], []

    x_vals, y_vals = [], []
    rows = table.find_all("tr")[1:]  # skip header

    for row in rows:
        cols = row.find_all("td")
        if not cols or len(cols) < 4:
            continue

        # Normalize spacing string
        raw_spacing = cols[1].get_text(strip=True).lower()
        # Remove all non-alphanumeric characters except letters and digits
        spacing_clean = re.sub(r"[^a-zA-Z0-9]", "", raw_spacing)
        target_clean = re.sub(r"[^a-zA-Z0-9]", "", f"{spacing_filter} in".lower())

        print(f"[DEBUG] Found spacing: {spacing_clean}")

        if spacing_clean == target_clean:
            try:
            	x = float(re.sub(r"[^\d.]", "", cols[2].get_text(strip=True)))
            	y = float(re.sub(r"[^\d.]", "", cols[3].get_text(strip=True)))
            	x_vals.append(x)
            	y_vals.append(y)
            except ValueError as e:
            	print(f"[SKIP] Failed to parse R-values: {e}")
            	continue

        
        if spacing_clean != target_clean:
        	print(f"[SKIP] Spacing did not match: '{spacing_clean}' ≠ '{target_clean}'")


    return x_vals, y_vals
