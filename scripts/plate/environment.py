# scripts/plate/environment.py
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

class Environment:
    """Блок 1: Plate. Хранит состояние окружающей среды."""
    
    def __init__(self):
        self.objects: List[Dict] = []
        logger.info("️ Environment initialized")
        
    def add_object(self, obj_type: str, distance: float, base_valence: float = 0.0):
        """Добавляет объект в среду."""
        self.objects.append({
            "type": obj_type,
            "distance": distance,
            "base_valence": base_valence
        })
        logger.debug(f"Added object: {obj_type} at dist={distance}, valence={base_valence}")
        
    def get_nearby_objects(self, max_distance: float = 10.0) -> List[Dict]:
        """Возвращает объекты в радиусе восприятия агента."""
        return [obj for obj in self.objects if obj["distance"] <= max_distance]