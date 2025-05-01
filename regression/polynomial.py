import numpy as np
import matplotlib.pyplot as plt

def fit_polynomial(x_vals, y_vals, degree):
    return np.polyfit(x_vals, y_vals, degree)

def evaluate_polynomial(coeffs, x):
    return np.polyval(coeffs, x)

def plot_polynomial(x_vals, y_vals, coeffs):
    x_range = np.linspace(min(x_vals), max(x_vals), 100)
    y_fit = np.polyval(coeffs, x_range)

    plt.scatter(x_vals, y_vals, color='blue', label='Data Points')
    plt.plot(x_range, y_fit, color='red', label='Polynomial Fit')
    plt.xlabel('Exterior Insulation (R)')
    plt.ylabel('Effective R-Value')
    plt.title('Polynomial Regression')
    plt.legend()
    plt.grid(True)
    plt.show()
