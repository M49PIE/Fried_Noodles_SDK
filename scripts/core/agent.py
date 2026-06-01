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
from scripts.sauce.learning import LearningSystem
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
        
        self.wander_direction = (random.uniform(-1, 1), random.uniform(-1, 1))
        self.wander_timer = 0
        
        # Для динамического спавна (еда чаще)
        self.next_food_spawn = random.randint(10, 20)
        self.next_rock_spawn = random.randint(50, 80)
        self.food_spawn_chance = 0.3
        self.rock_spawn_chance = 0.15
        self.arena_bounds = (0, 20)

        self.needs_system = NeedsSystem(self.config)
        self.environment = Environment()
        self.sensation = SensationSystem(perception_radius=5.0)
        self.perception = PerceptionSystem(self.config)
        self.behavior_system = BehaviorSystem()
        self.memory = FieldMemory()
        self.learning = LearningSystem(learning_rate=0.3)
        
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
                        "tension_threshold": 0.10,
                        "restore_amount": 0.3
                    }
                }, 
                "innate_priors": {"Food": 0.0, "Rock": 0.0}
            }
        with open(config_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _try_interact(self, perceived_objects: list) -> tuple[bool, str]:
        interactable = [obj for obj in perceived_objects if obj["distance"] <= self.interaction_radius]
        if not interactable:
            return False, "neutral"
            
        target = max(interactable, key=lambda x: x["salience"])
        
        if target.get("valence", 0.0) < 0:
            return False, "neutral"
        
        old_valence = target.get("valence", 0.0)
        
        if target["type"] == "Food":
            if self.state["energy"] > 0.95:
                return False, "neutral"
                
            restore = self.config.get("homeostasis", {}).get("energy", {}).get("restore_amount", 0.3)
            self.state["energy"] = min(1.0, self.state["energy"] + restore)
            
            new_valence = self.learning.update_valence(old_valence, "success", "Food")
            self.memory.perceive_object("Food", target["x"], target["y"], valence=new_valence, salience=target["salience"])
            
            for env_obj in self.environment.objects:
                if env_obj["type"] == "Food" and env_obj["x"] == target["x"] and env_obj["y"] == target["y"]:
                    env_obj["consumed"] = True
                    break
            
            self.learning.log_event(
                tick=self.tick_count,
                action="Consume",
                target_type="Food",
                outcome="success",
                valence_before=old_valence,
                valence_after=new_valence
            )
            
            logger.info(f"🍽️ Ate Food! Energy +{restore:.2f} | Valence: {old_valence:.2f} → {new_valence:.2f}")
            return True, "success"
            
        elif target["type"] == "Rock":
            new_valence = self.learning.update_valence(old_valence, "failure", "Rock")
            self.memory.perceive_object("Rock", target["x"], target["y"], valence=new_valence, salience=target["salience"])
            
            self.learning.log_event(
                tick=self.tick_count,
                action="Investigate",
                target_type="Rock",
                outcome="failure",
                valence_before=old_valence,
                valence_after=new_valence
            )
            
            logger.info(f"🪨 Investigated Rock: no value | Valence: {old_valence:.2f} → {new_valence:.2f}")
            return False, "failure"
            
        return False, "neutral"

    def _update_wander_direction(self):
        self.wander_direction = (random.uniform(-1, 1), random.uniform(-1, 1))
        self.wander_timer = random.randint(5, 15)

    def _try_spawn_objects(self):
        """Пытается заспавнить новые объекты в мире"""
        # СПАВН ЕДЫ: Частота увеличена (10-20 тиков)
        if self.tick_count >= self.next_food_spawn and random.random() < self.food_spawn_chance:
            for _ in range(10):
                fx = random.uniform(self.arena_bounds[0] + 1, self.arena_bounds[1] - 1)
                fy = random.uniform(self.arena_bounds[0] + 1, self.arena_bounds[1] - 1)
                dist_to_agent = math.sqrt((fx - self.position[0])**2 + (fy - self.position[1])**2)
                if dist_to_agent > 5.0:
                    self.environment.add_object("Food", x=fx, y=fy, base_valence=0.0)
                    logger.info(f"✨ Spawned Food at ({fx:.1f}, {fy:.1f})")
                    break
            self.next_food_spawn = self.tick_count + random.randint(10, 20)
        
        # Спавн камней (без изменений)
        if self.tick_count >= self.next_rock_spawn and random.random() < self.rock_spawn_chance:
            for _ in range(10):
                rx = random.uniform(self.arena_bounds[0] + 1, self.arena_bounds[1] - 1)
                ry = random.uniform(self.arena_bounds[0] + 1, self.arena_bounds[1] - 1)
                dist_to_agent = math.sqrt((rx - self.position[0])**2 + (ry - self.position[1])**2)
                if dist_to_agent > 5.0:
                    self.environment.add_object("Rock", x=rx, y=ry, base_valence=0.0)
                    logger.info(f"✨ Spawned Rock at ({rx:.1f}, {ry:.1f})")
                    break
            self.next_rock_spawn = self.tick_count + random.randint(50, 80)

    def tick(self) -> dict:
        self.tick_count += 1
        
        decay = self.config.get("homeostasis", {}).get("energy", {}).get("decay_rate", 0.01)
        self.state["energy"] = max(0.0, self.state["energy"] - decay)
        
        if self.state["energy"] <= 0:
            self.state["tension"] = 1.0
            self.state["quasi_need"] = "SeekFood"
            if self.tick_count % 20 == 0:
                logger.warning(f"[Tick {self.tick_count:03d}] Agent collapsed! Energy=0.00 | Position: ({self.position[0]:.2f}, {self.position[1]:.2f})")
            return self.state.copy()
        
        self.memory.update_agent_position(self.position[0], self.position[1])
        
        # Динамический спавн
        self._try_spawn_objects()
        
        nearby_objects = self.environment.get_nearby_objects(self.position[0], self.position[1], 15.0)
        stimuli = self.sensation.filter_stimuli(nearby_objects)
        
        memory_valences = {
            f"{obj['type']}_{obj['x']}_{obj['y']}": obj['valence']
            for obj in self.memory.object_memories.values()
        }
        
        perceived_objects = self.perception.interpret_stimuli(stimuli, self.state, memory_valences)
        
        for obj in perceived_objects:
            mem_key = f"{obj['type']}_{obj['x']}_{obj['y']}"
            if mem_key not in memory_valences:
                self.memory.perceive_object(obj["type"], obj["x"], obj["y"], obj["valence"], obj["salience"])
        
        self.state["tension"] = self.needs_system.calculate_tension(self.state["energy"])
        self.state["quasi_need"] = self.needs_system.get_quasi_need(self.state["tension"])
        
        interacted, outcome = self._try_interact(perceived_objects)
        
        if interacted:
            action = "Consume: Success"
            if self.state["quasi_need"] and self.state["energy"] > 0.5:
                self.state["quasi_need"] = None
        else:
            # 2. Выбор действия
            action = self.behavior_system.select_action(self.state["quasi_need"], perceived_objects)
            
            # ✅ ИСПРАВЛЕНИЕ: Если агент голоден, но ничего не видит -> принудительное блуждание
            if action == "Idle" and self.state["quasi_need"]:
                action = "FieldAction: Wander"
            
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
                self.wander_timer -= 1
                if self.wander_timer <= 0:
                    self._update_wander_direction()
                
                dx, dy = self.wander_direction
                norm = math.sqrt(dx**2 + dy**2)
                if norm > 0:
                    dx, dy = dx / norm, dy / norm
                
                move_x = dx * self.speed * 0.5
                move_y = dy * self.speed * 0.5
                
                new_x = max(0, min(20, self.position[0] + move_x))
                new_y = max(0, min(20, self.position[1] + move_y))
                self.position = (new_x, new_y)

        if self.enable_debug:
            self.viz_plate.update(nearby_objects, self.position)
            self.viz_plate.fig.canvas.draw()
            self.viz_plate.fig.canvas.flush_events()
            self.viz_needs.update(self.tick_count, self.state["energy"], self.state["tension"], self.state["quasi_need"])
            self.viz_needs.fig.canvas.draw()
            self.viz_needs.fig.canvas.flush_events()
            plt.pause(0.01)
            
        memory_count = len(self.memory.object_memories)
        perception_log = ", ".join([f"{p['type']}({p['valence']}, sal={p['salience']})" for p in perceived_objects]) if perceived_objects else "None"
        logger.info(f"[Tick {self.tick_count:03d}] Pos=({self.position[0]:.2f}, {self.position[1]:.2f}) | E={self.state['energy']:.2f} T={self.state['tension']:.2f} | Mem={memory_count} | Action: {action}")
        
        return self.state.copy()

    def run_demo(self, ticks: int = 400):
        logger.info("🍽️ Setting up environment...")
        
        # Начальный спавн
        for _ in range(2):
            fx, fy = random.uniform(5, 18), random.uniform(5, 18)
            self.environment.add_object("Food", x=fx, y=fy, base_valence=0.0)
            logger.info(f"Spawned Food at ({fx:.1f}, {fy:.1f})")
            
        rx, ry = random.uniform(2, 8), random.uniform(8, 12)
        self.environment.add_object("Rock", x=rx, y=ry, base_valence=0.0)
        logger.info(f"Spawned Rock at ({rx:.1f}, {ry:.1f})")
        
        for _ in range(ticks):
            self.tick()
        
        summary = self.learning.get_learning_summary()
        logger.info(f"🧠 Learning Summary: {summary}")
        
        if self.enable_debug:
            plt.ioff()
            plt.show()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    agent = FriedNoodlesAgent("configs/agent_profile.json", enable_debug=True)
    agent.run_demo()