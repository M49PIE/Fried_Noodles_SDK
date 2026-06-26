# scripts/world_model/spawner.py
import logging
import random
from typing import List

from scripts.world_model.entities import Apple, Rock

logger = logging.getLogger(__name__)

ARENA_SIZE = 20.0

class WorldSpawner:
    """Управляет спавном сущностей"""
    
    def __init__(self, world):
        self.world = world
        self._initialized = False
        self.apple_spawn_timer = 0.0
        self.apple_spawn_interval = 4.0  # ⬆️ Чаще
        self.max_apples = 15             # ⬆️ Больше
        logger.info("🌍 WorldSpawner initialized")
    
    def initialize_world(self) -> None:
        logger.info("🏗️ [START] Initializing simplified world...")
        try:
            if self._initialized: return
            
            # ✅ Только камни и яблоки. Барьеры удалены.
            logger.info("🏗️ Step 1: Spawning 8 rocks")
            for i in range(8):
                rock_pos = self._random_position()
                rock = Rock(position=rock_pos)
                self.world.add_entity(rock)
                logger.info(f"✅ Rock {i+1} spawned at {rock_pos}")
            
            logger.info("🏗️ Step 2: Spawning 3 initial apples")
            for i in range(3):
                apple_pos = self._random_position()
                apple = Apple(position=apple_pos)
                self.world.add_entity(apple)
                logger.info(f"✅ Apple {i+1} spawned at {apple_pos}")
            
            self._initialized = True
            logger.info(f"✅ [DONE] World init complete | Entities: {len(self.world.entities)}")
            
        except Exception as e:
            logger.error(f" ERROR during init: {e}", exc_info=True)
            raise
    
    def tick(self, dt: float) -> None:
        if not self._initialized: return
        
        self.apple_spawn_timer += dt
        if self.apple_spawn_timer >= self.apple_spawn_interval:
            self.apple_spawn_timer = 0.0
            active_apples = sum(1 for e in self.world.entities if e.active and e.name == "Apple")
            
            if active_apples < self.max_apples:
                apple_pos = self._random_position()
                apple = Apple(position=apple_pos)
                self.world.add_entity(apple)
                logger.info(f"🍎 Apple spawned at {apple_pos}")
    
    def _random_position(self) -> tuple:
        for _ in range(50):
            x = random.uniform(1.0, ARENA_SIZE - 1.0)
            y = random.uniform(1.0, ARENA_SIZE - 1.0)
            return (x, y)
        return (random.uniform(1.0, ARENA_SIZE - 1.0), random.uniform(1.0, ARENA_SIZE - 1.0))