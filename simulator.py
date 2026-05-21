from typing import List, Dict, Any, Optional
from roulette import Roulette, get_strategy

class SimulationRun:
    """Representa el resultado detallado de una única corrida (simulación de n tiradas)."""
    
    def __init__(self, run_id: int):
        self.run_id: int = run_id
        self.capital_history: List[float] = [] # Historial de capital por tirada (tamaño n+1, incluye capital inicial en pos 0)
        self.frsa_history: List[float] = []    # Historial de frecuencia relativa acumulada de éxitos (tamaño n)
        self.success_history: List[int] = []   # Historial de aciertos (1 para éxito, 0 para fallo, tamaño n)
        self.rulette_numbers: List[int] = []   # Números resultantes de cada giro (tamaño n)
        self.bet_history: List[float] = []     # Historial de apuestas realizadas (tamaño n)
        self.is_bankrupt: bool = False         # Indica si el jugador quebró en esta corrida
        self.bankruptcy_spin: Optional[int] = None # Tirada en la que ocurrió la quiebra (1-indexed)


class RouletteSimulator:
    """Orquestador principal que ejecuta las corridas del simulador de ruleta."""
    
    def __init__(self, initial_capital: float = 1000.0):
        self.initial_capital = initial_capital

    def run_single_simulation(
        self, 
        spins: int, 
        strategy_code: str, 
        capital_type: str, 
        chosen_number: Optional[int] = None,
        run_id: int = 1
    ) -> SimulationRun:
        """Ejecuta una corrida individual de n tiradas de ruleta.
        
        Args:
            spins: Cantidad de tiradas (n).
            strategy_code: Código de la estrategia ('m', 'd', 'f').
            capital_type: Tipo de capital ('i' para infinito, 'f' para finito).
            chosen_number: Número elegido para apostar (None para apuestas sencillas).
            run_id: Identificador de la corrida.
            
        Returns:
            SimulationRun: Los datos e historial de la simulación.
        """
        roulette = Roulette()
        # Inicializar la estrategia con apuesta base de 1.0 unidad
        strategy = get_strategy(strategy_code, base_bet=1.0)
        
        run = SimulationRun(run_id)
        run.capital_history.append(self.initial_capital)
        
        current_capital = self.initial_capital
        won_last_round = True  # La primera apuesta usará el valor base de la estrategia
        success_count = 0
        is_finite = (capital_type.lower() == 'f')
        
        for spin_idx in range(1, spins + 1):
            if is_finite and current_capital <= 0:
                # El jugador ya quebró. No puede apostar.
                run.is_bankrupt = True
                if run.bankruptcy_spin is None:
                    run.bankruptcy_spin = spin_idx - 1
                
                # Sigue girando la ruleta para la estadística de frecuencia relativa
                num = roulette.spin()
                run.rulette_numbers.append(num)
                
                favorable = roulette.is_favorable(num, chosen_number)
                if favorable:
                    success_count += 1
                    run.success_history.append(1)
                else:
                    run.success_history.append(0)
                
                run.frsa_history.append(success_count / spin_idx)
                run.capital_history.append(0.0)
                run.bet_history.append(0.0)
                continue
                
            # Determinar la apuesta sugerida por la estrategia
            # Para la primera tirada, llamamos a get_next_bet con True para que use la apuesta base.
            # En tiradas subsiguientes se pasa el resultado de la tirada anterior.
            if spin_idx == 1:
                bet_amount = strategy.current_bet
            else:
                bet_amount = strategy.get_next_bet(won_last_round)
            
            # Si el capital es finito, restringir la apuesta al capital disponible
            actual_bet = bet_amount
            if is_finite and bet_amount > current_capital:
                actual_bet = current_capital
            
            # Girar la ruleta
            num = roulette.spin()
            run.rulette_numbers.append(num)
            run.bet_history.append(actual_bet)
            
            # Evaluar apuesta
            favorable = roulette.is_favorable(num, chosen_number)
            
            # Registrar éxito en ruleta (frecuencia relativa de la apuesta)
            if favorable:
                success_count += 1
                run.success_history.append(1)
                
                # Pago: Pleno 35:1, Sencilla 1:1
                multiplier = 35.0 if chosen_number is not None else 1.0
                win_amount = actual_bet * multiplier
                current_capital += win_amount
                won_last_round = True
            else:
                run.success_history.append(0)
                current_capital -= actual_bet
                won_last_round = False
            
            # Registrar el capital tras la tirada
            # Para capital finito, nos aseguramos de que no baje de 0 por redondeos
            if is_finite and current_capital < 1e-9:
                current_capital = 0.0
                
            run.capital_history.append(current_capital)
            run.frsa_history.append(success_count / spin_idx)
            
        # Al terminar la corrida, si el capital final es 0 pero no se marcó la quiebra antes
        if is_finite and current_capital <= 0:
            run.is_bankrupt = True
            if run.bankruptcy_spin is None:
                run.bankruptcy_spin = spins
                
        return run

    def run_multi_simulation(
        self,
        runs_count: int,
        spins: int,
        strategy_code: str,
        capital_type: str,
        chosen_number: Optional[int] = None
    ) -> Dict[str, Any]:
        """Ejecuta múltiples corridas independientes del simulador.
        
        Args:
            runs_count: Número de corridas a realizar (c).
            spins: Cantidad de tiradas por corrida (n).
            strategy_code: Estrategia elegida ('m', 'd', 'f').
            capital_type: Capital infinito o finito ('i', 'f').
            chosen_number: Número elegido (si aplica).
            
        Returns:
            Dict: Un diccionario con los datos detallados de cada corrida y estadísticas agregadas.
        """
        runs_data: List[SimulationRun] = []
        bankruptcies = 0
        ended_positive = 0
        ended_negative = 0
        ended_equal = 0
        
        final_capitals = []
        min_capitals = []
        max_capitals = []
        
        for i in range(1, runs_count + 1):
            run = self.run_single_simulation(
                spins=spins,
                strategy_code=strategy_code,
                capital_type=capital_type,
                chosen_number=chosen_number,
                run_id=i
            )
            runs_data.append(run)
            
            final_cap = run.capital_history[-1]
            final_capitals.append(final_cap)
            min_capitals.append(min(run.capital_history))
            max_capitals.append(max(run.capital_history))
            
            if run.is_bankrupt:
                bankruptcies += 1
                
            if final_cap > self.initial_capital:
                ended_positive += 1
            elif final_cap < self.initial_capital:
                ended_negative += 1
            else:
                ended_equal += 1
                
        # Calcular estadísticas resumidas
        stats = {
            "initial_capital": self.initial_capital,
            "total_runs": runs_count,
            "spins_per_run": spins,
            "strategy": strategy_code,
            "capital_type": capital_type,
            "chosen_number": chosen_number,
            "bankruptcies": bankruptcies,
            "bankruptcy_rate": bankruptcies / runs_count if runs_count > 0 else 0,
            "ended_positive": ended_positive,
            "ended_negative": ended_negative,
            "ended_equal": ended_equal,
            "max_final_capital": max(final_capitals),
            "min_final_capital": min(final_capitals),
            "avg_final_capital": sum(final_capitals) / len(final_capitals),
            "max_historical_capital": max(max_capitals),
            "min_historical_capital": min(min_capitals),
        }
        
        return {
            "runs": runs_data,
            "stats": stats
        }
