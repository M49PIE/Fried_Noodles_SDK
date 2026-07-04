# scripts/decision_engine/thinking.py
import logging
import math
from typing import Tuple, Dict, List
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class MentalPath:
    """Результат ментальной симуляции"""
    success: bool
    reason: str = ""

class ThinkingSystem:
    """
    Блок 6: Cheese -> Thinking.
    Быстрая проверка пути в уме.
    """
    def __init__(self, step_size: float = 0.4, max_steps: int = 50):
        self.step_size = step_size
        self.max_steps = max_steps
        logger.info(f"🧀 ThinkingSystem initialized (step={step_size})")

    def simulate_full_path(self, start_pos: Tuple[float, float], target: Dict,
                          field_objects: List[Dict], arena_size: float = 20.0) -> MentalPath:
        """
        Быстрая ментальная проверка: можно ли дойти до цели?
        """
        target_pos = (target["x"], target["y"])
        current_pos = list(start_pos)
        interaction_radius = 1.5
        
        for step in range(self.max_steps):
            dx = target_pos[0] - current_pos[0]
            dy = target_pos[1] - current_pos[1]
            dist = math.sqrt(dx**2 + dy**2)
            
            # Цель достигнута в уме
            if dist <= interaction_radius:
                return MentalPath(success=True, reason="Goal reached mentally")
            
            # Двигаем "мысль"
            if dist > 0:
                dx, dy = dx/dist, dy/dist
                next_x = current_pos[0] + dx * self.step_size
                next_y = current_pos[1] + dy * self.step_size
            else:
                break
            
            # Ограничение ареной
            next_x = max(0, min(arena_size, next_x))
            next_y = max(0, min(arena_size, next_y))
            
            # Проверка препятствий в уме
            for obj in field_objects:
                if obj.get("type") in ("Wall", "Rock", "Barrier"):
                    obj_dist = math.sqrt((next_x - obj["x"])**2 + (next_y - obj["y"])**2)
                    if obj_dist < 1.0:
                        return MentalPath(success=False, reason=f"Blocked by {obj.get('type')}")
            
            current_pos = [next_x, next_y]
        
        return MentalPath(success=False, reason="Max steps exceeded")