from parser.html_table import fetch_table_data as fetch_html_data
from parser.pdf_table import fetch_pdf_data
from regression.polynomial import fit_polynomial, evaluate_polynomial, plot_polynomial
import numpy as np

def main():
    print("=== Thermal Envelope Detail Regression Tool ===\n")

    # Choose data source
    source = input("Use HTML table or PDF? (enter 'html' or 'pdf'): ").strip().lower()
    detail_number = input("Enter detail number (e.g. 7.1.29): ").strip()
    spacing = input("Enter vertical spacing (e.g. 24): ").strip()
    degree = int(input("Enter polynomial degree (e.g. 2): ").strip())
    x_query = float(input("Enter an exterior insulation R-value to evaluate (e.g. 10.5): ").strip())

    # Fetch data
    if source == "html":
        x_vals, y_vals = fetch_html_data(detail_number, spacing)
    elif source == "pdf":
        x_vals, y_vals = fetch_pdf_data(detail_number, spacing)
    else:
        print("[ERROR] Invalid source type.")
        return

    if not x_vals:
        print("\n[ERROR] No matching data found.")
        return

    # Fit polynomial and predict
    coeffs = fit_polynomial(x_vals, y_vals, degree)
    y_result = evaluate_polynomial(coeffs, x_query)
    y_pred = np.polyval(coeffs, x_vals)

    # Calculate R²
    ss_res = np.sum((np.array(y_vals) - y_pred) ** 2)
    ss_tot = np.sum((np.array(y_vals) - np.mean(y_vals)) ** 2)
    r_squared = 1 - (ss_res / ss_tot)

    # Display results
    print("\n=== Polynomial Equation ===")
    equation = "y = " + " + ".join(f"{round(c, 4)}x^{len(coeffs)-i-1}" for i, c in enumerate(coeffs))
    print(equation)
    print(f"\nR² = {r_squared:.6f}")
    print(f"\nPredicted y = {round(y_result, 2)} at x = {x_query}")

    if input("Show polynomial fit plot? (y/n): ").lower() == "y":
        plot_polynomial(x_vals, y_vals, coeffs)

if __name__ == "__main__":
    main()
