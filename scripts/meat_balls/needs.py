# scripts/meat_balls/needs.py
import logging

logger = logging.getLogger(__name__)

class NeedsSystem:
    """Блок 2: Meat Balls. Расчёт гомеостаза, напряжения и квазипотребностей."""
    
    def __init__(self, config: dict):
        self.homeostasis_config = config.get("homeostasis", {})
        self.threshold = self.homeostasis_config.get("energy", {}).get("tension_threshold", 0.3)
        logger.info("🍖 NeedsSystem initialized")
        
    def calculate_tension(self, current_energy: float) -> float:
        """Рассчитывает напряжение на основе текущего уровня энергии."""
        return round(max(0.0, 1.0 - current_energy), 2)
        
    def get_quasi_need(self, tension: float) -> str | None:
        """Генерирует квазипотребность (намерение) на основе напряжения."""
        if tension > self.threshold:
            return "SeekFood"
        return None