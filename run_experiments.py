import numpy as np
import matplotlib.pyplot as plt
import csv
from tm_simulator import run_experiments
import subprocess
import json

def load_results(csvfile):
    xs = []
    ys = []
    with open(csvfile, newline='', encoding='utf-8') as f:
        r = csv.DictReader(f)
        for row in r:
            xs.append(int(row['n']))
            ys.append(float(row['time_seconds']))
    return np.array(xs), np.array(ys)

def best_poly_fit(xs, ys, max_degree=5):
    best = None
    best_deg = 0
    best_r2 = -1
    for d in range(1, max_degree+1):
        coeffs = np.polyfit(xs, ys, d)
        p = np.poly1d(coeffs)
        ypred = p(xs)
        ss_res = ((ys - ypred)**2).sum()
        ss_tot = ((ys - ys.mean())**2).sum()
        r2 = 1 - ss_res/ss_tot if ss_tot>0 else 0
        if r2 > best_r2:
            best_r2 = r2
            best = coeffs
            best_deg = d
    return best_deg, best, best_r2

if __name__ == "__main__":
    machine_file = "machines/fib_macro.json"
    csvfile = run_experiments(machine_file, list(range(1, 11)), out_csv="results.csv")
    xs, ys = load_results(csvfile)
    deg, coeffs, r2 = best_poly_fit(xs, ys, max_degree=4)
    print(f"Mejor ajuste polinomial: grado={deg} R^2={r2:.4f}")
    p = np.poly1d(coeffs)
    xp = np.linspace(xs.min(), xs.max(), 200)
    plt.figure(figsize=(8,5))
    plt.scatter(xs, ys, label='datos')
    plt.plot(xp, p(xp), label=f'ajuste polinomial grado {deg}')
    plt.xlabel('n (entrada unary)')
    plt.ylabel('time (s)')
    plt.title('Tiempos de ejecución vs n')
    plt.legend()
    plt.grid(True)
    plt.savefig("time_vs_n.png")
    print("Gráfica guardada en time_vs_n.png")
    # imprimir la expresión polinómica resultante
    print("Polinomio (coeficientes):", coeffs)