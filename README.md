# Proyecto: Simulador TM - Fibonacci (unary)
---

## Resumen
Este repositorio contiene un **simulador de Máquina de Turing (TM) de una cinta** que permite:
- cargar la definición de la máquina desde un archivo JSON (dos tipos: `macro` y `lowlevel`),
- simular paso a paso (impresión de configuraciones),
- ejecutar experimentos (medir tiempos para diferentes entradas),
- generar un **diagrama visual (SVG y PNG)** de la máquina (automáticamente a partir del archivo JSON).

El ejemplo principal es una **máquina macro** que calcula la sucesión de Fibonacci usando entrada en **unario**.

---

## Convenciones
- **Alfabeto de la cinta**: `{1, #, _}`  
  - `1` = unidad (unary).  
  - `#` = separador / marcador de campos.  
  - `_` = blanco (blank).
- **Entrada (encoding)**: `n` en **unario** → cadena de `1` repetidos `n` veces.  
  Ejemplo: `n = 4` → `"1111"`.
- **Formato interno de la cinta (convención del proyecto)**:  
  Usamos el layout con campos separados por `#`:
  **#A#B#[input]#**
- Inicialmente A = `""` (F(0)=0), B = `"1"` (F(1)=1). Después de las iteraciones el resultado `F(n)` queda en el campo `B` como secuencia de `1`s.
- **Salida**: interpretar la secuencia de `1` en el campo `B` como el valor `F(n)` (en unary).
- **Medición experimental**: el script de experimentos ejecuta la máquina para entradas `n` pequeñas (por ejemplo `1..10`) y guarda `results.csv` con columnas `n, time_seconds, steps, result_length`.
- **Complejidad**: Dado el enfoque (cada iteración concatena cadenas en unary), el tiempo es **exponencial** en `n`: `T(n) = Θ(F(n)) ≈ Θ(φ^n)` con `φ ≈ 1.618`.

---

## Archivos principales
- `tm_simulator.py` — simulador (soporta `macro` y `lowlevel`).
- `machines/fib_macro.json` — definición macro de la máquina Fibonacci (ejemplo).
- `run_experiments.py` — ejecutar experimentos y ajustar polinomio.
- `diagram_generator.py` — **genera el diagrama visual (SVG y PNG)** a partir de un archivo JSON de máquina.
- `README.md`, `.gitignore`

---

## Dependencias para generar el diagrama
El generador de diagramas usa **Graphviz**. Hay dos pasos:

### 1 Python (recomendado ≥ 3.8)
Crea y activa virtualenv (opcional pero recomendado):
```bash
# Unix / macOS
python -m venv .venv
source .venv/bin/activate
# Windows (PowerShell)
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 2 Instalar paquetes Python:
   ```bash
   pip install --upgrade pip
   pip install numpy matplotlib graphviz
   ```
Descargar e instalar graphviz desde https://graphviz.org/download/

## Comandos: cómo ejecutar todo

### Simulador:

   ```bash
    python tm_simulator.py machines/fib_macro.json
   ```
### Ejecutar experimentos y generar gráfico:

   ```bash
    python run_experiments.py
   ```
### Generar diagrama (SVG y PNG) desde JSON:

   ```bash
    python diagram_generator.py machines/fib_macro.json --out machines/fib_macro_diagram --format svg,png
   ```

## Interpretación de los resultados de run_experiments.py

`results.csv` contiene por fila:
- `n` — tamaño de entrada (cantidad de 1 en unary)
- `time_seconds` — tiempo total medido (segundos)
- `steps` — contador de pasos según el simulador.
- `result_length` — longitud de B (cantidad de 1 = F(n))

`time_vs_n.png` — gráfico scatter con la curva polinómica que mejor se ajustó.

