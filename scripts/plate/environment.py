# scripts/plate/environment.py
import logging
import math
from typing import List, Dict

logger = logging.getLogger(__name__)

class Environment:
    """Блок 1: Plate. Хранит состояние окружающей среды (X, Y координаты)."""
    
    def __init__(self):
        self.objects: List[Dict] = []
        logger.info("️ Environment initialized (Cartesian Coordinates)")
        
    def add_object(self, obj_type: str, x: float, y: float, base_valence: float = 0.0):
        """Добавляет объект в среду с координатами."""
        self.objects.append({
            "type": obj_type,
            "x": x,
            "y": y,
            "base_valence": base_valence
        })
        logger.debug(f"Added object: {obj_type} at ({x}, {y})")
        
    def get_nearby_objects(self, agent_x: float, agent_y: float, max_distance: float = 10.0) -> List[Dict]:
        """Возвращает объекты в радиусе, рассчитывая дистанцию динамически."""
        nearby = []
        for obj in self.objects:
            # Теорема Пифагора для дистанции
            dist = math.sqrt((obj["x"] - agent_x)**2 + (obj["y"] - agent_y)**2)
            
            if dist <= max_distance:
                # Возвращаем копию объекта с добавленной дистанцией (нужно для Onion/Ebi)
                obj_data = obj.copy()
                obj_data["distance"] = dist
                nearby.append(obj_data)
        
        return nearby