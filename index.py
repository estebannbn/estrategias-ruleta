import argparse
import sys
import os

# Autodetectar e inyectar dinámicamente el entorno virtual .venv local en el path de Python.
# Esto permite que el comando 'python' global cargue matplotlib y numpy de forma transparente.
venv_site_packages = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".venv", "Lib", "site-packages")
if os.path.exists(venv_site_packages):
    sys.path.insert(0, venv_site_packages)

from typing import Optional
from simulator import RouletteSimulator
from plots import generate_simulation_plots

def validate_args(args: argparse.Namespace) -> None:
    """Realiza validaciones detalladas de los argumentos de entrada.
    
    Args:
        args: El objeto Namespace de argparse.
    """
    if args.c <= 0:
        print("Error: El número de corridas (-c) debe ser mayor que 0.", file=sys.stderr)
        sys.exit(1)
        
    if args.n <= 0:
        print("Error: El número de tiradas (-n) must be greater than 0.", file=sys.stderr)
        sys.exit(1)
        
    if args.e is not None:
        if args.e < 0 or args.e > 36:
            print("Error: El número elegido (-e) debe estar en el rango de 0 a 36 para una ruleta europea.", file=sys.stderr)
            sys.exit(1)
            
    if args.s.lower() not in ['m', 'd', 'f']:
        print(f"Error: Estrategia (-s) no válida: '{args.s}'. Las opciones válidas son 'm' (Martingala), 'd' (D'Alembert), 'f' (Fibonacci).", file=sys.stderr)
        sys.exit(1)
        
    if args.a.lower() not in ['i', 'f']:
        print(f"Error: Tipo de capital (-a) no válido: '{args.a}'. Las opciones válidas son 'i' (infinito), 'f' (finito).", file=sys.stderr)
        sys.exit(1)
        
    if args.capital <= 0:
        print("Error: El capital inicial debe ser un número positivo.", file=sys.stderr)
        sys.exit(1)


def print_elegant_report(stats: dict) -> None:
    """Imprime un reporte estadistico elegante y profesional en la consola con colores.
    
    Args:
        stats: Diccionario con los datos estadisticos consolidados.
    """
    # Colores ANSI
    C_GREEN = "\033[92m"
    C_RED = "\033[91m"
    C_CYAN = "\033[96m"
    C_YELLOW = "\033[93m"
    C_BOLD = "\033[1m"
    C_RESET = "\033[0m"
    
    strategy_map = {'m': 'Martingala', 'd': "D'Alembert", 'f': 'Fibonacci'}
    strat = strategy_map.get(stats["strategy"].lower(), stats["strategy"])
    cap_type = "Finito" if stats["capital_type"].lower() == 'f' else "Infinito"
    bet_type = f"Pleno (No. {stats['chosen_number']})" if stats["chosen_number"] is not None else "Apuesta Sencilla (Par)"
    
    width = 65
    print("\n" + "=" * width)
    print(f"{C_BOLD}{C_CYAN}    REPORTE DE SIMULACION DE RULETA EUROPEA{C_RESET}".center(width + 12))
    print("=" * width)
    
    # Parametros
    print(f" {C_BOLD}Parametros de Simulacion:{C_RESET}")
    print(f"  - Estrategia:        {strat}")
    print(f"  - Tipo de Apuesta:   {bet_type}")
    print(f"  - Gestion de Capital:{cap_type}")
    print(f"  - Capital Inicial:   {stats['initial_capital']:.2f}")
    print(f"  - No. de Corridas (c):{stats['total_runs']}")
    print(f"  - Tiradas/Corrida (n):{stats['spins_per_run']}")
    print("-" * width)
    
    # Resultados del capital
    avg_final = stats['avg_final_capital']
    profit_loss = avg_final - stats['initial_capital']
    pl_color = C_GREEN if profit_loss >= 0 else C_RED
    pl_sign = "+" if profit_loss >= 0 else ""
    
    print(f" {C_BOLD}Rendimiento de Capital:{C_RESET}")
    print(f"  - Capital Final Promedio:   {avg_final:.2f}")
    print(f"  - Ganancia/Perdida Promedio:{pl_color}{pl_sign}{profit_loss:.2f} ({pl_sign}{(profit_loss/stats['initial_capital'])*100:.2f}%){C_RESET}")
    print(f"  - Capital Final Maximo:     {C_GREEN}{stats['max_final_capital']:.2f}{C_RESET}")
    print(f"  - Capital Final Minimo:     {C_RED}{stats['min_final_capital']:.2f}{C_RESET}")
    print(f"  - Capital Pico Historico:   {C_CYAN}{stats['max_historical_capital']:.2f}{C_RESET}")
    print(f"  - Capital Minimo Historico: {C_YELLOW}{stats['min_historical_capital']:.2f}{C_RESET}")
    print("-" * width)
    
    # Ratios de Exito
    total = stats['total_runs']
    pos_pct = (stats['ended_positive'] / total) * 100
    neg_pct = (stats['ended_negative'] / total) * 100
    eq_pct = (stats['ended_equal'] / total) * 100
    
    print(f" {C_BOLD}Distribucion de Resultados (Fin de Simulacion):{C_RESET}")
    print(f"  - Corridas con Ganancia (cc > fci): {C_GREEN}{stats['ended_positive']}{C_RESET} ({pos_pct:.1f}%)")
    print(f"  - Corridas con Perdida (cc < fci):  {C_RED}{stats['ended_negative']}{C_RESET} ({neg_pct:.1f}%)")
    print(f"  - Corridas sin Cambio (cc = fci):   {C_YELLOW}{stats['ended_equal']}{C_RESET} ({eq_pct:.1f}%)")
    
    # Quiebras en capital finito
    if stats["capital_type"].lower() == 'f':
        br_pct = stats['bankruptcy_rate'] * 100
        print(f"  - {C_BOLD}Quiebras totales (cc = 0):{C_RESET}        {C_RED}{stats['bankruptcies']}{C_RESET} ({br_pct:.1f}%)")
        
    print("=" * width + "\n")


def main() -> None:
    """Funcion de entrada principal."""
    parser = argparse.ArgumentParser(
        description="Simulador de tiradas de ruleta europea para evaluar estrategias de apuestas progresivas.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    # Argumentos requeridos y según la estructura exacta solicitada
    parser.add_argument('-c', type=int, required=True, help="Numero de corridas (simulaciones independientes)")
    parser.add_argument('-n', type=int, required=True, help="Cantidad de tiradas para cada corrida")
    parser.add_argument('-e', type=int, default=None, help="Numero elegido (0-36, apuesta a pleno). Si no se provee, se realiza apuesta sencilla (pares).")
    parser.add_argument('-s', type=str, required=True, help="Estrategia elegida: m (Martingala), d (D'Alembert), f (Fibonacci)")
    parser.add_argument('-a', type=str, required=True, help="Tipo de capital: i (infinito), f (finito)")
    
    # Argumentos adicionales convenientes y profesionales
    parser.add_argument('--capital', type=float, default=1000.0, help="Capital inicial predefinido (por defecto: 1000.0)")
    parser.add_argument('--output', type=str, default="resultado_simulacion.png", help="Nombre del archivo de imagen de salida (por defecto: resultado_simulacion.png)")
    
    # Parsear
    args = parser.parse_args()
    
    # Validar
    validate_args(args)
    
    # Inicializar simulador
    simulator = RouletteSimulator(initial_capital=args.capital)
    
    print(f"\nIniciando simulacion: {args.c} corridas de {args.n} tiradas usando estrategia '{args.s}'...")
    
    # Ejecutar simulacion
    result = simulator.run_multi_simulation(
        runs_count=args.c,
        spins=args.n,
        strategy_code=args.s,
        capital_type=args.a,
        chosen_number=args.e
    )
    
    runs_data = result["runs"]
    stats = result["stats"]
    
    # Generar graficos
    output_path = os.path.abspath(args.output)
    print(f"Generando graficos de alta calidad y guardandolos en: {output_path}...")
    generate_simulation_plots(runs_data, stats, output_path)
    
    # Imprimir reporte elegante
    print_elegant_report(stats)
    print(f"Exito! La simulacion finalizo correctamente. Graficos guardados en '{args.output}'.\n")


if __name__ == "__main__":
    main()
