# Estrategias de Ruleta Europea

Este proyecto implementa un simulador de ruleta europea con capacidades de análisis y visualización estadística para comparar diferentes estrategias de apuestas progresivas.

## Características Principales

- **Ruleta Europea**: Números del 0 al 36.
- **Tres Estrategias de Progresión**: Martingala, D'Alembert y Fibonacci.
- **Gestión de Capital Flexible**:
  - **Capital Infinito**: Sin restricciones.
  - **Capital Finito**: Detecta bancarrotas (capital llegando a 0).
- **Apuestas Personalizables**:
  - **Apuesta a Pleno**: Elegir un número específico.
  - **Apuesta Sencilla**: Apuesta automática a números pares (excluyendo 0).
- **Análisis Estadístico Profundo**:
  - **Rendimiento de Capital**: Ganancia/Pérdida neta, capital final, picos.
  - **Ratios de Éxito**: Frecuencia de resultados positivos, negativos y nulos.
  - **Bancarrotas**: Tasa de quiebra en simulaciones de capital finito.
- **Visualización de Resultados**:
  - **Gráficos Interactivos**: Generación de gráficos de alta calidad para comparar todas las corridas.
  - **Múltiples Métricas**: Frecuencia relativa acumulada y flujo de caja por número de tiradas.

## Requisitos Previos

Se requiere una instalación de Python con las siguientes librerías instaladas en un entorno virtual `.venv`:
- `matplotlib`
- `numpy`

## Instalación

1.  **Crear y activar el entorno virtual:**
    ```bash
    python -m venv .venv
    .\.venv\Scripts\activate  # En Windows
    source .venv/bin/activate  # En Linux/Mac
    ```

2.  **Instalar dependencias:**
    ```bash
    pip install -r requirements.txt
    ```

## Uso

La herramienta se ejecuta desde la línea de comandos usando el script `index.py`.

### Sintaxis Básica

```bash
python index.py -c <corridas> -n <tiradas> -s <estrategia> -a <capital> [-e <numero_elegido>]
```

### Parámetros Disponibles

| Parámetro | Descripción | Requerido | Opciones/Rango |
|-----------|-------------|-----------|----------------|
| `-c`      | Número de corridas (simulaciones independientes). | Sí | > 0 |
| `-n`      | Número de tiradas por corrida. | Sí | > 0 |
| `-e`      | Número específico a apostar (apuesta a pleno). | No | 0-36 |
| `-s`      | Estrategia a usar. | Sí | `m` (Martingala), `d` (D'Alembert), `f` (Fibonacci) |
| `-a`      | Tipo de capital. | Sí | `i` (Infinito), `f` (Finito) |

### Ejemplos de Uso

**1. Martingala con capital infinito y apuesta a pleno (número 21):**
```bash
python index.py -c 10 -n 200 -e 21 -a i -s m
```

**2. Fibonacci con capital finito y apuesta sencilla (pares):**
```bash
python index.py -c 5 -n 150 -a f -s f
```

**3. D'Alembert con capital infinito y apuesta a pleno (número 0):**
```bash
python index.py -c 20 -n 300 -e 0 -a i -s d
```

## Salida del Programa

Al ejecutar el script, se mostrará:
1.  **Reporte Estadístico** en consola con los resultados consolidados de todas las corridas.
2.  **Gráficos Interactivos**:
    -   Frecuencia relativa acumulada (frsa).
    -   Flujo de caja (fc) para cada corrida.

Ambos gráficos se guardarán automáticamente como `resultado_simulacion.png` en el directorio actual.

## Estructura del Proyecto

- `index.py`: Script principal de ejecución y parseo de argumentos.
- `simulator.py`: Lógica de la ruleta y las estrategias de apuestas.
- `plots.py`: Generación de gráficos estadísticos.
- `requirements.txt`: Dependencias del proyecto.
- `.venv`: Entorno virtual (opcional).