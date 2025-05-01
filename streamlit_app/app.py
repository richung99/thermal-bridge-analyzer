import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
from parser.pdf_table import fetch_pdf_data as fetch_pdf
from regression.polynomial import fit_polynomial, evaluate_polynomial, plot_polynomial
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="Thermal Bridge Regression Tool", layout="centered")

st.title("📊 Thermal Envelope Detail Regression Tool")

# --- Input Section ---
st.markdown("**Select data source:**")
st.radio("Only PDF mode is supported on Streamlit Cloud:", ["PDF Thermal Sheet"], index=0, disabled=True)

detail_number = st.text_input("Enter detail number (e.g. 7.1.29):", value="7.1.29")
spacing = st.text_input("Vertical spacing (inches):", value="24")
degree = st.slider("Polynomial degree:", 1, 4, 2)
x_query = st.number_input("R-value to predict:", value=10.0)

# --- Run Button ---
if st.button("Run Regression"):
    with st.spinner("Fetching data..."):
        x_vals, y_vals = fetch_pdf(detail_number, spacing)

    if not x_vals:
        st.error("❌ No data found. Check detail number or spacing.")
    else:
        coeffs = fit_polynomial(x_vals, y_vals, degree)
        y_result = evaluate_polynomial(coeffs, x_query)
        y_pred = np.polyval(coeffs, x_vals)
        r2 = 1 - np.sum((np.array(y_vals) - y_pred) ** 2) / np.sum((np.array(y_vals) - np.mean(y_vals)) ** 2)

        eqn = "y = " + " + ".join(f"{round(c, 4)}x^{len(coeffs)-i-1}" for i, c in enumerate(coeffs))
        st.success("✅ Regression Complete")
        st.markdown(f"**Equation:** {eqn}")
        st.markdown(f"**R²:** {r2:.6f}")
        st.markdown(f"**Predicted y at x = {x_query}:** `{round(y_result, 3)}`")

        # Plotting
        fig, ax = plt.subplots()
        ax.scatter(x_vals, y_vals, color='blue', label='Data Points')
        x_range = np.linspace(min(x_vals), max(x_vals), 100)
        y_fit = np.polyval(coeffs, x_range)
        ax.plot(x_range, y_fit, color='orange', label='Fit')
        ax.set_xlabel("Exterior Insulation R-Value")
        ax.set_ylabel("Effective R-Value or Ro - R1D")
        ax.set_title("Polynomial Regression Fit")
        ax.legend()
        st.pyplot(fig)
