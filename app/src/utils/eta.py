import time
from collections import deque
from typing import Optional


class ETATracker:
    """
    Класс для отслеживания прогресса и вычисления ETA (estimated time of arrival).
    
    Отслеживает изменения значения от 0 до 100 и на основе истории вычисляет:
    - Темп прироста значения
    - Оставшееся время до достижения 100
    """
    
    def __init__(self, history_size: int = 100):
        """
        Инициализация трекера ETA.
        
        Args:
            history_size: Размер истории для вычисления средней скорости
        """
        self.history_size = history_size
        self.history = deque(maxlen=history_size)  # Хранит пары (время, значение)
        self._last_eta: Optional[float] = None
        self._last_speed: Optional[float] = None
    
    def set_value(self, value: float) -> None:
        """
        Установить новое значение прогресса.
        
        Args:
            value: Значение прогресса от 0 до 100
        """
        value = max(0, min(100, value))
        current_time = time.time()
        self.history.append((current_time, value))
        self._last_eta = None
        self._last_speed = None

    def get_speed(self) -> Optional[float]:
        """
        Получить текущую скорость прироста значения (единиц в секунду).
        Returns:
            Скорость прироста значения или None, если недостаточно данных
        """
        if self._last_speed is not None:
            return self._last_speed
        if len(self.history) < 2:
            return None
        first_time, first_value = self.history[0]
        last_time, last_value = self.history[-1]
        time_diff = last_time - first_time
        if time_diff == 0:
            return None
        speed = (last_value - first_value) / time_diff
        self._last_speed = speed
        return speed
    
    def get_eta(self) -> Optional[float]:
        """
        Получить оставшееся время до достижения 100 (в секундах).
        
        Returns:
            Оставшееся время в секундах или None, если недостаточно данных
        """
        if self._last_eta is not None:
            return self._last_eta
            
        speed = self.get_speed()
        if speed is None or speed <= 0:
            return None
        
        current_value = self.history[-1][1]
        remaining = 100 - current_value
        
        if remaining <= 0:
            return 0.0
        
        eta = remaining / speed
        self._last_eta = eta
        return eta
    
    def get_eta_formatted(self) -> Optional[str]:
        """
        Получить оставшееся время в формате ЧЧ:ММ:СС.
        
        Returns:
            Отформатированное время или None, если недостаточно данных
        """
        eta = self.get_eta()
        if eta is None:
            return None
        
        # Округляем до целых секунд
        eta_seconds = int(eta)
        
        hours = eta_seconds // 3600
        minutes = (eta_seconds % 3600) // 60
        seconds = eta_seconds % 60
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes:02d}:{seconds:02d}"
    
    def get_progress_info(self) -> dict:
        """
        Получить полную информацию о прогрессе.
        Returns:
            Словарь с информацией о прогрессе, скорости и ETA
        """
        speed = self.get_speed()
        eta = self.get_eta()
        current_value = self.history[-1][1] if self.history else 0

        return {
            "progress": current_value,
            "speed": speed,
            "eta_seconds": eta,
            "eta_formatted": self.get_eta_formatted() if eta is not None else None
        }

    def reset(self) -> None:
        """Сбросить историю и все вычисления."""
        self.history.clear()
        self._last_eta = None
        self._last_speed = None