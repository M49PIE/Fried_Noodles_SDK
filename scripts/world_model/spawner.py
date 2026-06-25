# scripts/world_model/spawner.py
import logging
import random
import math
from typing import List, Dict, Any, Optional

from scripts.world_model.entities import Apple, Rock, Wall

logger = logging.getLogger(__name__)

ARENA_SIZE = 20.0
CELL_SIZE = 2.0  # Размер клетки для лабиринта


class WorldSpawner:
    """Управляет спавном сущностей"""
    
    def __init__(self, world):
        self.world = world
        self._initialized = False
        self.apple_spawn_timer = 0.0
        self.apple_spawn_interval = 8.0  # Яблоко каждые 8 секунд
        self.max_apples = 10  # Максимум яблок на карте
        
        logger.info("🌍 WorldSpawner initialized")
    
    def initialize_world(self) -> None:
        """Инициализация мира"""
        logger.info("🏗️ [START] Initializing simplified world...")
        
        try:
            if self._initialized:
                return
            
            # 1. Создаем лабиринт из 6 барьеров
            logger.info("🏗️ Step 1: Spawning maze walls (6 barriers)")
            self._spawn_maze_walls()
            
            # 2. Спавним 8 камней
            logger.info("🏗️ Step 2: Spawning 8 rocks")
            for i in range(8):
                rock_pos = self._random_position(min_dist_from_walls=2.0)
                rock = Rock(position=rock_pos)
                self.world.add_entity(rock)
                logger.info(f"✅ Rock {i+1} spawned at {rock_pos}")
            
            # 3. Начальные яблоки (3 шт)
            logger.info("🏗️ Step 3: Spawning 3 initial apples")
            for i in range(3):
                apple_pos = self._random_position(min_dist_from_walls=2.0)
                apple = Apple(position=apple_pos)
                self.world.add_entity(apple)
                logger.info(f"✅ Apple {i+1} spawned at {apple_pos}")
            
            self._initialized = True
            logger.info(f"✅ [DONE] World init complete | Entities: {len(self.world.entities)}")
            
        except Exception as e:
            logger.error(f"❌ ERROR during init: {e}", exc_info=True)
            raise
    
    def _spawn_maze_walls(self) -> None:
        """
        Создает простой лабиринт из 6 барьеров.
        Коридоры шириной минимум 3 клетки (6 единиц).
        """
        # Паттерн 1: Горизонтальные стены с проходами
        wall_positions = [
            (5.0, 5.0), (7.0, 5.0), (9.0, 5.0),   # Верхняя секция
            (11.0, 10.0), (13.0, 10.0), (15.0, 10.0)  # Нижняя секция
        ]
        
        for i, pos in enumerate(wall_positions):
            wall = Wall(position=pos)
            self.world.add_entity(wall)
            logger.info(f"✅ Wall {i+1} spawned at {pos}")
    
    def tick(self, dt: float) -> None:
        """Периодический спавн"""
        if not self._initialized:
            return
        
        # Спавн яблок
        self.apple_spawn_timer += dt
        if self.apple_spawn_timer >= self.apple_spawn_interval:
            self.apple_spawn_timer = 0.0
            
            # Считаем активные яблоки
            active_apples = sum(1 for e in self.world.entities 
                               if e.active and e.name == "Apple")
            
            if active_apples < self.max_apples:
                apple_pos = self._random_position(min_dist_from_walls=2.0)
                apple = Apple(position=apple_pos)
                self.world.add_entity(apple)
                logger.info(f"🍎 Apple spawned at {apple_pos}")
    
    def _random_position(self, min_dist_from_walls: float = 0.0) -> tuple:
        """Генерирует случайную позицию"""
        for _ in range(50):
            x = random.uniform(1.0, ARENA_SIZE - 1.0)
            y = random.uniform(1.0, ARENA_SIZE - 1.0)
            
            # Проверяем расстояние от стен
            if min_dist_from_walls > 0:
                too_close = False
                for entity in self.world.entities:
                    if entity.active and entity.name == "Wall":
                        dist = math.sqrt((x - entity.x)**2 + (y - entity.y)**2)
                        if dist < min_dist_from_walls:
                            too_close = True
                            break
                
                if not too_close:
                    return (x, y)
            else:
                return (x, y)
        
        return (random.uniform(1.0, ARENA_SIZE - 1.0), 
                random.uniform(1.0, ARENA_SIZE - 1.0))