# scripts/world_model/world_model.py
import logging
from typing import List, Dict, Tuple, Optional, Any

from scripts.world_model.entities import Entity
from scripts.world_model.collision import check_and_resolve_collisions, apply_border_constraints
from scripts.world_model.spawner import WorldSpawner

logger = logging.getLogger(__name__)

ARENA_SIZE = 20.0


class WorldModel:
    """
    Блок 1: Plate. Управляет миром, физикой и сущностями.
    """
    def __init__(self, arena_size: float = ARENA_SIZE):
        self.arena_size = arena_size
        self.entities: List[Entity] = []
        self.spawner = WorldSpawner(self)
        logger.info(f"🍽️ WorldModel initialized | Arena: {arena_size}x{arena_size} | Physics Enabled")

    def add_entity(self, entity: Entity) -> None:
        if entity.active and entity not in self.entities:
            self.entities.append(entity)

    def remove_entity(self, entity: Entity) -> None:
        entity.active = False
        if entity in self.entities:
            self.entities.remove(entity)

    @property
    def objects(self) -> List[Entity]:
        return self.entities

    def tick(self, dt: float = 1.0) -> None:
        """Основной цикл мира"""
        
        if not self.spawner._initialized:
            self.spawner.initialize_world()
        
        self.spawner.tick(dt)
        
        for entity in list(self.entities):
            if entity.active:
                entity.tick(dt, {"arena_size": self.arena_size, "entities": self.entities})

        # Физика
        colliders = [e for e in self.entities if e.active and e.collides and e.type == "barrier"]
        movers = [e for e in self.entities if e.active and e.type in ["agent", "subject"]]
        
        for mover in movers:
            if colliders:
                check_and_resolve_collisions(mover, colliders)
            apply_border_constraints(mover, self.arena_size)

    def get_entities_in_radius(self, center: Tuple[float, float], radius: float,
                               entity_type: str = None, tags: List[str] = None) -> List[Entity]:
        cx, cy = center
        result = []
        rad_sq = radius * radius
        for e in self.entities:
            if not e.active: continue
            if entity_type and e.type != entity_type: continue
            if tags and not all(t in e.tags for t in tags): continue

            dx = e.x - cx
            dy = e.y - cy
            if (dx*dx + dy*dy) <= rad_sq:
                result.append(e)
        return result

    def get_nearby_objects(self, x: float, y: float, radius: float) -> List[Dict]:
        """Для Perception/Sensation."""
        nearby = self.get_entities_in_radius((x, y), radius, entity_type="object")
        result = []
        for e in nearby:
            dx = e.x - x
            dy = e.y - y
            dist = (dx*dx + dy*dy)**0.5
            result.append({
                "type": e.name,
                "x": e.x, "y": e.y,
                "distance": dist,
                "tags": e.tags,
                "valence": getattr(e, 'value', 0.0),
                "consumed": getattr(e, 'consumed', False)
            })
        return result