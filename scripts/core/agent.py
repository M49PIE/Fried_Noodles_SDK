# scripts/core/agent.py
import logging
import json
import math
import random
from pathlib import Path
import matplotlib.pyplot as plt
from scripts.meat_balls.needs import NeedsSystem
from scripts.plate.environment import Environment
from scripts.garlic.sensation import SensationSystem
from scripts.onion.perception import PerceptionSystem
from scripts.ebi.behavior import BehaviorSystem
from scripts.noodles.field_memory import FieldMemory
from scripts.debug.plate.environment_debug import EnvironmentDebug
from scripts.debug.meat_balls.needs_debug import NeedsDebug

logger = logging.getLogger(__name__)

class FriedNoodlesAgent:
    def __init__(self, config_path: str, enable_debug: bool = False):
        self.config = self._load_config(config_path)
        self.tick_count = 0
        self.enable_debug = enable_debug
        
        self.position = (10.0, 10.0)
        self.speed = 0.4
        self.interaction_radius = 1.5
        
        # Для случайного блуждания
        self.wander_direction = (random.uniform(-1, 1), random.uniform(-1, 1))
        self.wander_timer = 0

        self.needs_system = NeedsSystem(self.config)
        self.environment = Environment()
        self.sensation = SensationSystem(perception_radius=5.0)
        self.perception = PerceptionSystem(self.config)
        self.behavior_system = BehaviorSystem()
        self.memory = FieldMemory()
        
        if self.enable_debug:
            self.viz_plate = EnvironmentDebug()
            self.viz_needs = NeedsDebug()
            plt.ion()
            logger.info("🔧 Debug visualizations enabled")
        
        self.state = {
            "energy": self.config.get("homeostasis", {}).get("energy", {}).get("initial", 1.0),
            "tension": 0.0,
            "quasi_need": None
        }
        logger.info(f"🤖 Agent initialized at {self.position}")

    def _load_config(self, path: str) -> dict:
        config_file = Path(path)
        if not config_file.exists():
            return {
                "agent_id": "agent_001", 
                "homeostasis": {
                    "energy": {
                        "initial": 1.0, 
                        "decay_rate": 0.01, 
                        "tension_threshold": 0.3, 
                        "restore_amount": 0.3
                    }
                }, 
                "innate_priors": {"Food": 0.0, "Rock": 0.0}
            }
        with open(config_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _try_interact(self, perceived_objects: list) -> bool:
        interactable = [obj for obj in perceived_objects if obj["distance"] <= self.interaction_radius]
        if not interactable:
            return False
            
        target = max(interactable, key=lambda x: x["salience"])
        
        if target["type"] == "Food":
            if self.state["energy"] > 0.95:
                return False
                
            restore = self.config.get("homeostasis", {}).get("energy", {}).get("restore_amount", 0.3)
            self.state["energy"] = min(1.0, self.state["energy"] + restore)
            
            # ✅ ОБУЧЕНИЕ: еда = хорошо
            self.memory.perceive_object(target["type"], target["x"], target["y"], valence=0.8, salience=target["salience"])
            
            for env_obj in self.environment.objects:
                if env_obj["type"] == target["type"] and env_obj["x"] == target["x"] and env_obj["y"] == target["y"]:
                    env_obj["consumed"] = True
                    break
            
            logger.info(f"🍽️ Ate Food! Energy +{restore:.2f}")
            return True
            
        elif target["type"] == "Rock":
            # ✅ ОБУЧЕНИЕ: камень = бесполезно (валентность становится отрицательной)
            self.memory.perceive_object(target["type"], target["x"], target["y"], valence=-0.2, salience=target["salience"])
            logger.info("🪨 Investigated Rock: no nutritional value (valence=-0.2)")
            return False
            
        return False

    def _update_wander_direction(self):
        """Меняет направление случайного блуждания"""
        self.wander_direction = (random.uniform(-1, 1), random.uniform(-1, 1))
        self.wander_timer = random.randint(5, 15)

    def tick(self) -> dict:
        self.tick_count += 1
        
        decay = self.config.get("homeostasis", {}).get("energy", {}).get("decay_rate", 0.01)
        self.state["energy"] = max(0.0, self.state["energy"] - decay)
        
        self.memory.update_agent_position(self.position[0], self.position[1])
        
        nearby_objects = self.environment.get_nearby_objects(self.position[0], self.position[1], 15.0)
        stimuli = self.sensation.filter_stimuli(nearby_objects)
        perceived_objects = self.perception.interpret_stimuli(stimuli, self.state)
        
        for obj in perceived_objects:
            self.memory.perceive_object(obj["type"], obj["x"], obj["y"], obj["valence"], obj["salience"])
        
        self.state["tension"] = self.needs_system.calculate_tension(self.state["energy"])
        self.state["quasi_need"] = self.needs_system.get_quasi_need(self.state["tension"])
        
        # 1. Попытка взаимодействия
        if self._try_interact(perceived_objects):
            action = "Consume: Success"
            if self.state["quasi_need"] and self.state["energy"] > 0.5:
                self.state["quasi_need"] = None
        else:
            # 2. Выбор действия
            action = self.behavior_system.select_action(self.state["quasi_need"], perceived_objects)
            
            # 3. Обработка действий
            if action.startswith("Approach:") or action.startswith("Investigate:"):
                target_type = action.split(": ")[1]
                targets = [obj for obj in nearby_objects if obj['type'] == target_type]
                
                if not targets:
                    remembered = self.memory.get_nearest_object_by_type(target_type)
                    if remembered:
                        targets = [remembered]
                
                if targets:
                    target = min(targets, key=lambda k: k['distance'])
                    dx = target['x'] - self.position[0]
                    dy = target['y'] - self.position[1]
                    dist = math.sqrt(dx**2 + dy**2)
                    
                    if dist <= self.interaction_radius:
                        action = "Idle"
                    elif dist > 0.5:
                        move_x = (dx / dist) * self.speed
                        move_y = (dy / dist) * self.speed
                        self.position = (self.position[0] + move_x, self.position[1] + move_y)
            
            elif action == "FieldAction: Wander":
                # ✅ ПОЛЕВОЕ ПОВЕДЕНИЕ: случайное блуждание
                self.wander_timer -= 1
                if self.wander_timer <= 0:
                    self._update_wander_direction()
                
                # Нормализуем вектор
                dx, dy = self.wander_direction
                norm = math.sqrt(dx**2 + dy**2)
                if norm > 0:
                    dx, dy = dx / norm, dy / norm
                
                move_x = dx * self.speed * 0.5  # Медленнее при блуждании
                move_y = dy * self.speed * 0.5
                
                # Ограничиваем ареной
                new_x = max(0, min(20, self.position[0] + move_x))
                new_y = max(0, min(20, self.position[1] + move_y))
                self.position = (new_x, new_y)

        # 4. Визуализация
        if self.enable_debug:
            self.viz_plate.update(nearby_objects, self.position)
            self.viz_plate.fig.canvas.draw()
            self.viz_plate.fig.canvas.flush_events()
            self.viz_needs.update(self.tick_count, self.state["energy"], self.state["tension"], self.state["quasi_need"])
            self.viz_needs.fig.canvas.draw()
            self.viz_needs.fig.canvas.flush_events()
            plt.pause(0.01)
            
        # 5. Лог
        memory_count = len(self.memory.object_memories)
        perception_log = ", ".join([f"{p['type']}({p['valence']}, sal={p['salience']})" for p in perceived_objects]) if perceived_objects else "None"
        logger.info(f"[Tick {self.tick_count:03d}] Pos=({self.position[0]:.2f}, {self.position[1]:.2f}) | E={self.state['energy']:.2f} T={self.state['tension']:.2f} | Mem={memory_count} | Action: {action}")
        
        return self.state.copy()

    def run_demo(self, ticks: int = 100):
        logger.info("🍽️ Setting up environment...")
        
        # Спавним 2 еды и 1 камень для интереса
        for _ in range(2):
            fx, fy = random.uniform(5, 18), random.uniform(5, 18)
            self.environment.add_object("Food", x=fx, y=fy, base_valence=0.0)
            logger.info(f"Spawned Food at ({fx:.1f}, {fy:.1f})")
            
        rx, ry = random.uniform(2, 8), random.uniform(8, 12)
        self.environment.add_object("Rock", x=rx, y=ry, base_valence=0.0)
        logger.info(f"Spawned Rock at ({rx:.1f}, {ry:.1f})")
        
        for _ in range(ticks):
            self.tick()
        
        if self.enable_debug:
            plt.ioff()
            plt.show()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    agent = FriedNoodlesAgent("configs/agent_profile.json", enable_debug=True)
    agent.run_demo()