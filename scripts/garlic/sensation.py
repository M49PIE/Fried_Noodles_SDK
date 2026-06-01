# scripts/garlic/sensation.py
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

class SensationSystem:
    """Блок 3: Garlic. Фильтрация сырых сенсорных данных из окружения."""
    
    def __init__(self, perception_radius: float = 10.0):
        self.perception_radius = perception_radius
        logger.info(f"🧄 SensationSystem initialized (radius={perception_radius})")
        
    def filter_stimuli(self, environment_objects: List[Dict]) -> List[Dict]:
        """
        Фильтрует объекты окружения, оставляя только те,
        что попадают в радиус восприятия агента.
        """
        stimuli = []
        for obj in environment_objects:
            if obj["distance"] <= self.perception_radius:
                stimuli.append({
                    "type": obj["type"],
                    "distance": obj["distance"],
                    "x": obj["x"], # <-- ВОССТАНАВЛИВАЕМ X
                    "y": obj["y"], # <-- ВОССТАНАВЛИВАЕМ Y
                    "intensity": self._calculate_intensity(obj["distance"])
                })
        
        if stimuli:
            logger.debug(f"Sensing: {[s['type'] for s in stimuli]}")
        else:
            logger.debug("No stimuli detected")
            
        return stimuli
    
    def _calculate_intensity(self, distance: float) -> float:
        """Рассчитывает интенсивность стимула на основе дистанции."""
        intensity = 1.0 - (distance / self.perception_radius)
        return round(max(0.0, min(1.0, intensity)), 2)