import matplotlib.pyplot as plt
import numpy as np
from typing import List, Dict, Any

def generate_simulation_plots(runs_data: List[Any], stats: Dict[str, Any], filepath: str = "resultado_simulacion.png") -> None:
    """Genera gráficos de alta calidad comparando las corridas de la simulación de la ruleta.
    
    Implementa un diseño moderno y oscuro (premium) para los dos gráficos solicitados:
    1. frsa (Frecuencia relativa de obtener la apuesta favorable según n) con la probabilidad teórica.
    2. fc (Flujo de caja) a lo largo de n tiradas con fci (Flujo de caja inicial) como referencia.
    
    Args:
        runs_data: Lista de instancias SimulationRun.
        stats: Diccionario con estadísticas consolidadas.
        filepath: Ruta del archivo donde se guardará la imagen final.
    """
    c = stats["total_runs"]
    n = stats["spins_per_run"]
    chosen_number = stats["chosen_number"]
    initial_capital = stats["initial_capital"]
    capital_type = stats["capital_type"]
    strategy_name = {
        'm': 'Martingala',
        'd': "D'Alembert",
        'f': 'Fibonacci',
        'l': 'Labouchere'
    }.get(stats["strategy"].lower(), stats["strategy"])
    
    # Calcular la probabilidad teórica de ganar
    if chosen_number is not None:
        p_teorica = 1.0 / 37.0
        tipo_apuesta = f"Pleno (N° {chosen_number})"
    else:
        p_teorica = 18.0 / 37.0
        tipo_apuesta = "Apuesta Sencilla (Par)"
        
    # Paleta de colores premium (diseño oscuro)
    bg_color = "#0B0C10"          # Fondo de la imagen general
    axes_bg = "#1F2833"           # Fondo de las áreas de gráficos
    text_color = "#FFFFFF"        # Color de texto principal
    muted_text = "#C5C6C7"        # Color de texto secundario
    grid_color = "#45A29E"        # Color sutil para la rejilla
    
    # Generar colores distintos y vibrantes para cada corrida
    cmap = plt.cm.rainbow
    run_colors = [cmap(val) for val in np.linspace(0.0, 0.85, c)] if c > 1 else ["#FF4C4C"]
    
    # Línea del capital inicial (fci): Azul brillante
    fci_color = "#1F78B4"         # Azul clásico elegante
    # Línea de probabilidad teórica: Verde menta / Neón
    p_color = "#66FCF1"           # Celeste/verde neón brillante
    
    # Configuración de estilos globales en matplotlib
    plt.rcParams['figure.facecolor'] = bg_color
    plt.rcParams['axes.facecolor'] = axes_bg
    plt.rcParams['text.color'] = text_color
    plt.rcParams['axes.labelcolor'] = muted_text
    plt.rcParams['xtick.color'] = muted_text
    plt.rcParams['ytick.color'] = muted_text
    plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'sans-serif']
    
    fig = plt.figure(figsize=(15, 10))
    gs = fig.add_gridspec(2, 2, height_ratios=[1, 0.65], hspace=0.28, wspace=0.25)
    ax1 = fig.add_subplot(gs[0, 0])
    ax2 = fig.add_subplot(gs[0, 1])
    ax3 = fig.add_subplot(gs[1, :])
    
    # --- GRÁFICO 1: FRECUENCIA RELATIVA ACUMULADA (frsa vs n) ---
    ax1.set_title("frsa (Frecuencia relativa de obtener la apuesta favorable según n)", 
                  fontsize=11, fontweight='bold', pad=12, color=text_color)
    
    # Graficar las líneas de frecuencia relativa acumulada para cada corrida
    # Si hay muchas corridas, usamos un alpha bajo para evitar saturación y ver la convergencia
    alpha_value = max(0.15, min(0.7, 3.0 / np.sqrt(c)))
    
    x_n = np.arange(1, n + 1)
    for idx, run in enumerate(runs_data):
        ax1.plot(x_n, run.frsa_history, color=run_colors[idx], alpha=alpha_value, linewidth=1.2)
        
    # Línea de probabilidad teórica
    ax1.axhline(y=p_teorica, color=p_color, linestyle='--', linewidth=2, 
                label=f"Probabilidad teórica (p ≈ {p_teorica:.4f})")
    
    ax1.set_xlabel("n (número de tiradas)", fontsize=10, fontweight='bold')
    ax1.set_ylabel("fr (frecuencia relativa)", fontsize=10, fontweight='bold')
    ax1.set_xlim(1, n)
    ax1.set_ylim(max(0.0, p_teorica - 0.25), min(1.0, p_teorica + 0.25))
    ax1.grid(True, color=grid_color, linestyle=':', alpha=0.3)
    ax1.legend(loc="upper right", framealpha=0.8, facecolor=bg_color, edgecolor=grid_color)
    
    # Quitar bordes innecesarios
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    ax1.spines['left'].set_color(grid_color)
    ax1.spines['bottom'].set_color(grid_color)
    
    # --- GRÁFICO 2: FLUJO DE CAJA (fc vs n) ---
    ax2.set_title("fc (flujo de caja)", 
                  fontsize=11, fontweight='bold', pad=12, color=text_color)
    
    # Graficar curvas de capital
    x_cap = np.arange(0, n + 1)
    for idx, run in enumerate(runs_data):
        ax2.plot(x_cap, run.capital_history, color=run_colors[idx], alpha=alpha_value, linewidth=1.2)
        
    # Línea de flujo de caja inicial (fci)
    ax2.axhline(y=initial_capital, color=fci_color, linestyle='-', linewidth=2.5, 
                label=f"fci (flujo de caja inicial: {initial_capital:,.0f})")
    
    ax2.set_xlabel("n (número de tiradas)", fontsize=10, fontweight='bold')
    ax2.set_ylabel("cc (cantidad de capital)", fontsize=10, fontweight='bold')
    ax2.set_xlim(0, n)
    
    # Configurar límites del eje Y de manera inteligente
    # Para capital infinito, el capital puede ser muy negativo.
    # Buscaremos los límites adecuados para que no se vea una línea gigante con outliers.
    all_capitals = []
    for run in runs_data:
        all_capitals.extend(run.capital_history)
    y_min = min(all_capitals)
    y_max = max(all_capitals)
    
    # Dar un margen superior e inferior
    margin_y = (y_max - y_min) * 0.05 if (y_max > y_min) else 100.0
    if capital_type.lower() == 'f':
        # En capital finito, el límite inferior es 0
        ax2.set_ylim(0, max(initial_capital * 1.5, y_max + margin_y))
    else:
        # En capital infinito, puede bajar de 0
        ax2.set_ylim(y_min - margin_y, y_max + margin_y)
        
    ax2.grid(True, color=grid_color, linestyle=':', alpha=0.3)
    ax2.legend(loc="upper right", framealpha=0.8, facecolor=bg_color, edgecolor=grid_color)
    
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)
    ax2.spines['left'].set_color(grid_color)
    ax2.spines['bottom'].set_color(grid_color)

    # --- GRÁFICO 3: APUESTA MÁXIMA ANTES DE LA QUIEBRA ---
    max_bets = []
    bar_colors = []
    for run in runs_data:
        if capital_type.lower() == 'f' and run.is_bankrupt and run.bankruptcy_spin is not None and run.bankruptcy_spin > 0:
            max_bet = max(run.bet_history[:run.bankruptcy_spin]) if run.bet_history[:run.bankruptcy_spin] else 0.0
        else:
            max_bet = max(run.bet_history) if run.bet_history else 0.0

        max_bets.append(max_bet)
        if capital_type.lower() == 'f':
            bar_colors.append('#FF6B6B' if run.is_bankrupt else '#4ECDC4')
        else:
            bar_colors.append('#66FCF1')

    run_labels = [f"R{i+1}" for i in range(len(runs_data))]
    ax3.bar(run_labels, max_bets, color=bar_colors, edgecolor=grid_color)
    ax3.set_title(
        "Apuesta máxima antes de la quiebra (capital finito)" if capital_type.lower() == 'f' else "Apuesta máxima por corrida (capital infinito)",
        fontsize=11, fontweight='bold', color=text_color, pad=12
    )
    ax3.set_xlabel("Corridas", fontsize=10, fontweight='bold')
    ax3.set_ylabel("Apuesta máxima", fontsize=10, fontweight='bold')
    ax3.grid(True, color=grid_color, linestyle=':', alpha=0.3)
    ax3.set_facecolor(axes_bg)
    ax3.spines['top'].set_visible(False)
    ax3.spines['right'].set_visible(False)
    ax3.spines['left'].set_color(grid_color)
    ax3.spines['bottom'].set_color(grid_color)

    if capital_type.lower() == 'f':
        bankruptcies = stats.get('bankruptcies', 0)
        ax3.text(
            0.99,
            0.85,
            f"Quiebras: {bankruptcies} / {len(runs_data)}",
            transform=ax3.transAxes,
            fontsize=10,
            color=text_color,
            ha='right',
            va='top',
            bbox=dict(facecolor=axes_bg, edgecolor=grid_color, boxstyle='round,pad=0.4', alpha=0.9)
        )

    # --- SUPER TÍTULO GENERAL Y METADATOS ---
    cap_type_desc = "Finito" if capital_type.lower() == 'f' else "Infinito"
    super_title = f"Simulación de Ruleta Europea | Estrategia: {strategy_name} | Capital: {cap_type_desc}\n"
    super_title += f"Configuración: {c} corridas de {n} tiradas | Apuesta: {tipo_apuesta}"
    
    fig.suptitle(super_title, fontsize=13, fontweight='bold', color=text_color, y=0.93)
    
    # Guardar la figura en disco
    plt.savefig(filepath, dpi=300, facecolor=bg_color)
    
    # Mostrar la ventana emergente interactiva
    print("Abriendo ventana emergente con los graficos interactivos...")
    try:
        plt.show()
    except Exception as e:
        print(f"Nota: No se pudo abrir la ventana emergente ({e}). La imagen se guardo con exito.")
    finally:
        plt.close()
