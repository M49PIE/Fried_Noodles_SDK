# scripts/memory_field/field.py
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

class PsychologicalField:
    """
    Блок 5: Field. Динамическая когнитивная карта.
    Отражает ТОЛЬКО текущее поле зрения агента.
    """
    def __init__(self):
        self._entities: Dict[str, dict] = {}
        logger.info("🧠 PsychologicalField initialized (Dynamic Perception Map)")

    def update(self, perceived_objects: List[dict]) -> None:
        """
        Полная синхронизация с текущим полем зрения.
        - Очищает старые записи
        - Добавляет только видимые объекты
        """
        self._entities.clear()

        for obj in perceived_objects:
            obj_id = f"{obj['x']:.2f}_{obj['y']:.2f}"
            
            self._entities[obj_id] = {
                "id": obj_id,
                "type": obj["type"],
                "x": obj["x"],
                "y": obj["y"],
                "valence": obj.get("valence", 0.0),
                "tags": obj.get("tags", [])
            }

    def get_all(self) -> List[dict]:
        return list(self._entities.values())

    def clear(self) -> None:
        self._entities.clear()
        logger.info("🧹 PsychologicalField cleared.")