import random
from typing import List, Tuple, Optional

class Roulette:
    """Clase que representa una Ruleta Europea estándar con números del 0 al 36."""
    
    def spin(self) -> int:
        """Simula una tirada de la ruleta europea.
        
        Returns:
            int: Un número entero aleatorio entre 0 y 36.
        """
        return random.randint(0, 36)

    @staticmethod
    def is_favorable(number: int, chosen_number: Optional[int] = None) -> bool:
        """Determina si el número obtenido es favorable para el jugador.
        
        - Si se especifica chosen_number, se considera favorable si es idéntico a number (Apuesta a Pleno).
        - Si NO se especifica chosen_number, se asume una apuesta sencilla a PAR (excluyendo el 0).
          Los números pares del 2 al 36 son favorables (18 números). El 0 no es par ni impar para apuestas.
        
        Args:
            number: El número que salió en la ruleta.
            chosen_number: El número apostado (si es apuesta a pleno).
            
        Returns:
            bool: True si el jugador gana la apuesta, False en caso contrario.
        """
        if chosen_number is not None:
            return number == chosen_number
        else:
            # Apuesta sencilla a pares (excluyendo el 0)
            return number > 0 and number % 2 == 0


class BetStrategy:
    """Clase base y fábrica para las estrategias de progresión de apuestas."""
    
    def __init__(self, base_bet: float = 1.0):
        self.base_bet = base_bet
        self.current_bet = base_bet

    def reset(self) -> None:
        """Reinicia el estado de la estrategia al valor inicial."""
        self.current_bet = self.base_bet

    def get_next_bet(self, won_last_round: bool) -> float:
        """Calcula la siguiente apuesta basada en el resultado de la ronda anterior.
        
        Args:
            won_last_round: True si el jugador ganó la última ronda, False si perdió.
            
        Returns:
            float: El valor de la siguiente apuesta.
        """
        raise NotImplementedError("Debe ser implementado por las subclases.")


class MartingaleStrategy(BetStrategy):
    """Estrategia Martingala:
    Dobla la apuesta tras cada pérdida; vuelve a la apuesta base al ganar.
    """
    def get_next_bet(self, won_last_round: bool) -> float:
        if won_last_round:
            self.current_bet = self.base_bet
        else:
            self.current_bet = self.current_bet * 2.0
        return self.current_bet


class DAlembertStrategy(BetStrategy):
    """Estrategia D'Alembert:
    Aumenta la apuesta en 1 unidad tras perder; disminuye en 1 unidad tras ganar (sin bajar de la base).
    """
    def get_next_bet(self, won_last_round: bool) -> float:
        if won_last_round:
            self.current_bet = max(self.base_bet, self.current_bet - self.base_bet)
        else:
            self.current_bet = self.current_bet + self.base_bet
        return self.current_bet


class FibonacciStrategy(BetStrategy):
    """Estrategia Fibonacci:
    Avanza 1 paso en la secuencia tras perder; retrocede 2 pasos al ganar.
    La apuesta mínima es la base.
    """
    def __init__(self, base_bet: float = 1.0):
        super().__init__(base_bet)
        # Generar secuencia inicial de Fibonacci (se expandirá dinámicamente si es necesario)
        self.fib = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610, 987, 1597, 2584, 4181, 6765]
        self.fib_index = 0
        self._update_current_bet()

    def reset(self) -> None:
        super().reset()
        self.fib_index = 0
        self._update_current_bet()

    def _update_current_bet(self) -> None:
        self.current_bet = self.fib[self.fib_index] * self.base_bet

    def _ensure_fib_length(self, index: int) -> None:
        while len(self.fib) <= index:
            self.fib.append(self.fib[-1] + self.fib[-2])

    def get_next_bet(self, won_last_round: bool) -> float:
        if won_last_round:
            # Retrocede 2 pasos
            self.fib_index = max(0, self.fib_index - 2)
        else:
            # Avanza 1 paso
            self.fib_index += 1
            self._ensure_fib_length(self.fib_index)
            
        self._update_current_bet()
        return self.current_bet


def get_strategy(strategy_code: str, base_bet: float = 1.0) -> BetStrategy:
    """Fábrica de estrategias.
    
    Args:
        strategy_code: 'm' (martingala), 'd' (d'Alembert), 'f' (fibonacci)
        base_bet: Apuesta inicial base.
        
    Returns:
        BetStrategy: Instancia de la estrategia seleccionada.
    """
    code = strategy_code.lower()
    if code == 'm':
        return MartingaleStrategy(base_bet)
    elif code == 'd':
        return DAlembertStrategy(base_bet)
    elif code == 'f':
        return FibonacciStrategy(base_bet)
    else:
        raise ValueError(f"Estrategia desconocida: '{strategy_code}'. Debe ser 'm', 'd' o 'f'.")
