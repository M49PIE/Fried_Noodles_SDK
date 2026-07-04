# scripts/world_model/entities.py
import uuid
import logging
from typing import List, Tuple, Dict, Any, Optional

logger = logging.getLogger(__name__)

# ============================================================
# БАЗОВЫЕ КЛАССЫ
# ============================================================

class Entity:
    """Базовый класс для всех сущностей"""
    def __init__(self, name: str, entity_type: str, position: Tuple[float, float],
                 tags: List[str] = None, collides: bool = False):
        self.id = str(uuid.uuid4())[:8]
        self.name = name
        self.type = entity_type
        self.x, self.y = position
        self.tags = tags or []
        self.collides = collides
        self.active = True
        self.radius = 0.5
        
    def tick(self, dt: float, world_context: Dict[str, Any]) -> None:
        pass

    def get_position(self) -> Tuple[float, float]:
        return (self.x, self.y)

    def has_tag(self, tag: str) -> bool:
        return tag in self.tags


class Collectible(Entity):
    """Подбираемый предмет"""
    def __init__(self, name: str, position: Tuple[float, float],
                 tags: List[str] = None, value: float = 0.0,
                 despawn_time: Optional[float] = 20.0):
        super().__init__(name, "object", position, tags, collides=False)
        self.value = value
        self.despawn_time = despawn_time
        self.age = 0.0

    def tick(self, dt: float, world_context: Dict[str, Any]) -> None:
        self.age += dt
        if self.despawn_time is not None and self.age >= self.despawn_time:
            self.active = False


class Barrier(Entity):
    """Непроходимый объект (стена)"""
    def __init__(self, name: str, position: Tuple[float, float],
                 tags: List[str] = None):
        super().__init__(name, "barrier", position, tags, collides=True)


# ============================================================
# ОБЪЕКТЫ
# ============================================================

class Apple(Collectible):
    """Яблоко - восстанавливает энергию, исчезает через 60 сек (было 20)"""
    def __init__(self, position: Tuple[float, float]):
        super().__init__(
            name="Apple", position=position,
            tags=["food", "organic", "renewable", "tasty", "natural", "healthy"],
            value=0.3, despawn_time=60.0  # ⬆️ УВЕЛИЧИЛ с 20 до 60 секунд
        )


class Rock(Collectible):
    """Камень - несъедобный, НЕ исчезает"""
    def __init__(self, position: Tuple[float, float]):
        super().__init__(
            name="Rock", position=position,
            tags=["hard", "obstacle", "ancient", "neutral", "landmark", "solid"],
            value=0.0, despawn_time=None
        )


class Wall(Barrier):
    """Стена - непроходимый барьер"""
    def __init__(self, position: Tuple[float, float]):
        super().__init__(
            name="Wall", position=position,
            tags=["barrier", "solid", "impassable"]
        )