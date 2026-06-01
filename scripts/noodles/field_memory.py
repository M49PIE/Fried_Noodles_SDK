# scripts/noodles/field_memory.py
import logging
import math
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class FieldMemory:
    """
    Блок 5: Noodles. Хранение психологического поля и памяти об объектах.
    Реализует концепцию Hodological Space (пространства путей).
    """
    
    def __init__(self):
        # Словарь памяти: ключ = тип объекта или ID, значение = данные
        self.object_memories: Dict[str, dict] = {}
        self.agent_position = (0.0, 0.0)
        logger.info("🍜 FieldMemory initialized (Hodological Space ready)")
    
    def update_agent_position(self, x: float, y: float):
        """Обновляет позицию агента для расчетов дистанции."""
        self.agent_position = (x, y)
    
    def perceive_object(self, obj_type: str, x: float, y: float, valence: float, salience: float):
        """
        Записывает или обновляет память об объекте.
        Если объект уже известен — обновляем позицию и валентность (learning).
        """
        obj_id = f"{obj_type}_{x}_{y}"  # Простой ID, в будущем заменим на UUID
        
        if obj_id in self.object_memories:
            # Обновляем существующую память
            memory = self.object_memories[obj_id]
            memory["valence"] = valence  # Обновляем валентность (опыт!)
            memory["last_seen"] = memory.get("last_seen", 0) + 1
            memory["salience"] = salience
            logger.debug(f"Updated memory: {obj_type} at ({x}, {y}) valence={valence:.2f}")
        else:
            # Создаем новую память
            self.object_memories[obj_id] = {
                "type": obj_type,
                "x": x,
                "y": y,
                "valence": valence,
                "salience": salience,
                "first_seen": 0,
                "last_seen": 0
            }
            logger.debug(f"New memory created: {obj_type} at ({x}, {y})")
    
    def get_hodological_distance(self, target_x: float, target_y: float) -> float:
        """
        Рассчитывает психологическую (ходологическую) дистанцию до цели.
        В MVP: просто евклидово расстояние.
        В будущем: учет препятствий, усталости, мотивации.
        """
        dx = target_x - self.agent_position[0]
        dy = target_y - self.agent_position[1]
        euclidean_dist = math.sqrt(dx**2 + dy**2)
        
        # Пока просто возвращаем физическую дистанцию
        # В будущем здесь будет формула: dist * (1 + barriers_coeff) / motivation
        return euclidean_dist
    
    def get_objects_by_valence(self, min_valence: float = -1.0, max_valence: float = 1.0) -> List[dict]:
        """Возвращает объекты в диапазоне валентности (для поиска целей)."""
        return [
            obj for obj in self.object_memories.values()
            if min_valence <= obj["valence"] <= max_valence
        ]
    
    def get_nearest_object_by_type(self, obj_type: str) -> Optional[dict]:
        """Находит ближайший объект указанного типа."""
        candidates = [obj for obj in self.object_memories.values() if obj["type"] == obj_type]
        if not candidates:
            return None
        
        # Сортируем по ходологической дистанции
        candidates.sort(key=lambda obj: self.get_hodological_distance(obj["x"], obj["y"]))
        return candidates[0]
    
    def clear_memory(self):
        """Очищает память (для тестов)."""
        self.object_memories.clear()
        logger.info("Memory cleared")