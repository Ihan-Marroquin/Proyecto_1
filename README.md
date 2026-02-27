# Proyecto: Simulador TM - Fibonacci (unary)

Entregables:
1. Convenciones.
2. Diagrama y descripción de la máquina.
3. Archivo con componentes (machines/fib_macro.json).
4. Código en Python:
   - tm_simulator.py
   - run_experiments.py
5. Análisis empírico (results.csv, time_vs_n.png)

Cómo ejecutar:
1. Instala dependencias:
   pip install numpy matplotlib

2. Simular un caso:
   python3 tm_simulator.py machines/fib_macro.json --input 1111

3. Ejecutar experimentos (n=1..10):
   python3 tm_simulator.py machines/fib_macro.json --run-experiments

   o usar:
   python3 run_experiments.py

Estructura sugerida:
- machines/
    - fib_macro.json
- tm_simulator.py
- run_experiments.py
- results.csv (generado)
- time_vs_n.png (generado)