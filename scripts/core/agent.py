# scripts/core/agent.py
import logging
import json
import math
import random
from pathlib import Path
import matplotlib.pyplot as plt
from typing import Optional

# Core systems
from scripts.tension_system.tension_system import NeedsSystem
from scripts.world_model.world_model import WorldModel
from scripts.sensation_input.sensation_input import SensationSystem
from scripts.perception_filter.perception_filter import PerceptionSystem
from scripts.action_executor.action_executor import BehaviorSystem
from scripts.memory_field.memory_field import MemoryField, LearningSource
from scripts.memory_field.field import PsychologicalField
from scripts.decision_engine.thinking import ThinkingSystem, MentalPath
from scripts.valence_update.valence_update import LearningSystem
from scripts.locutionary_output.locutionary_output import LocutionaryOutput

# Debug tools
from scripts.debug.world_model.world_model_debug import EnvironmentDebug
from scripts.debug.debug_interface import UnifiedDebug  # 🔥 НОВЫЙ ИМПОРТ

logger = logging.getLogger(__name__)


class FriedNoodlesAgent:
    def __init__(self, config_path: str, enable_debug: bool = False):
        self.config = self._load_config(config_path)
        self.tick_count = 0
        self.enable_debug = enable_debug
        
        self.position = (10.0, 10.0)
        self.speed = 0.4
        self.radius = 0.5
        self.interaction_radius = 1.5
        
        self.wander_direction = (random.uniform(-1, 1), random.uniform(-1, 1))
        self.wander_timer = 0
        
        self.arena_bounds = (0, 20)

        # 1. Инициализация базовых систем
        self.needs_system = NeedsSystem(self.config)
        self.environment = WorldModel()
        self.sensation = SensationSystem(perception_radius=30.0)
        self.perception = PerceptionSystem(self.config)
        self.action_executor = BehaviorSystem()
        
        # 2. Инициализация памяти, поля и мышления
        self.memory = MemoryField(data_dir="scripts/memory_field")
        self.field = PsychologicalField()
        self.thinking = ThinkingSystem(step_size=0.4)
        self.cherry = LocutionaryOutput(self.memory)
        self.learning = LearningSystem(learning_rate=0.3)
        
        # 3. Инициализация визуализации
        if self.enable_debug:
            self.viz_plate = EnvironmentDebug(
                innate_objects=self.memory.innate_objects, 
                icon_dir="scripts/world_model/icons"
            )
            self.viz = UnifiedDebug()  # 🔥 ОБЪЕДИНЁННЫЙ ДЕБАГ
            plt.ion()
            logger.info("🔧 Debug visualizations enabled")
        
        # 4. Данные агента
        agent_data = self.memory.innate_objects.get("Agent", {})
        self.agent_emoji = agent_data.get("emoji", "")
        self.agent_tags = agent_data.get("tags", ["alive", "intelligent"])
        
        self.state = {
            "energy": self.config.get("homeostasis", {}).get("energy", {}).get("initial", 1.0),
            "tension": 0.0,
            "quasi_need": None
        }
        logger.info(f"{self.agent_emoji} Agent initialized at {self.position}")

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
                "innate_priors": {"Apple": 0.0, "Rock": 0.0}
            }
        with open(config_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _try_interact(self, nearby_objects: list) -> tuple[bool, str]:
        interactable = [obj for obj in nearby_objects if obj["distance"] <= self.interaction_radius]
        if not interactable:
            return False, "neutral"
        
        food_targets = [obj for obj in interactable if obj["type"] in ("Food", "Apple", "Bread")]
        target = min(food_targets, key=lambda x: x["distance"]) if food_targets else min(interactable, key=lambda x: x["distance"])
        
        old_valence = target.get("valence", 0.0)
        
        if target["type"] in ("Food", "Apple", "Bread"):
            if self.state["energy"] > 0.95: return False, "neutral"
                
            restore = self.config.get("homeostasis", {}).get("energy", {}).get("restore_amount", 0.3)
            self.state["energy"] = min(1.0, self.state["energy"] + restore)
            
            new_valence = self.learning.update_valence(old_valence, "success", target["type"])
            self.memory.register_object(target["type"], tags=target.get("tags", []), coordinates=(target["x"], target["y"]))
            self.memory.update_object_valence(target["type"], new_valence, 1.0)
            
            entity_to_remove = None
            for entity in self.environment.entities:
                if (hasattr(entity, 'name') and entity.name == target["type"] and 
                    abs(entity.x - target["x"]) < 0.5 and abs(entity.y - target["y"]) < 0.5):
                    entity_to_remove = entity
                    break
            if entity_to_remove: self.environment.remove_entity(entity_to_remove)
            
            self.learning.log_event(tick=self.tick_count, action="Consume", target_type=target["type"], outcome="success", valence_before=old_valence, valence_after=new_valence)
            logger.info(f"🍽️ Ate {target['type']}! Energy +{restore:.2f} | Valence: {old_valence:.2f} → {new_valence:.2f}")
            
            # 🗣️ ТРИГГЕР РЕЧИ: ПОЕЛ
            self.cherry.speak("eat", target["type"], target.get("tags", []), self.state["energy"], self.state["tension"], self.tick_count)
            return True, "success"
            
        elif target["type"] == "Rock":
            new_valence = self.learning.update_valence(old_valence, "failure", "Rock")
            self.memory.register_object("Rock", tags=["rock", "hard"], coordinates=(target["x"], target["y"]))
            self.memory.update_object_valence("Rock", new_valence, 1.0)
            
            self.learning.log_event(tick=self.tick_count, action="Investigate", target_type="Rock", outcome="failure", valence_before=old_valence, valence_after=new_valence)
            logger.info(f"🪨 Investigated Rock: no value | Valence: {old_valence:.2f} → {new_valence:.2f}")
            
            # 🗣️ ТРИГГЕР РЕЧИ: НЕУДАЧА (только если это первый раз)
            if old_valence == 0.0:
                self.cherry.speak("fail", "Rock", target.get("tags", []), self.state["energy"], self.state["tension"], self.tick_count)
            return False, "failure"
            
        return False, "neutral"

    def _update_wander_direction(self):
        self.wander_direction = (random.uniform(-1, 1), random.uniform(-1, 1))
        self.wander_timer = random.randint(5, 15)

    def _find_best_target(self, nearby_objects: list) -> Optional[dict]:
        if self.state["energy"] >= 0.6: return None
        food = [o for o in nearby_objects if o['type'] == 'Apple']
        return min(food, key=lambda x: x['distance']) if food else None

    def tick(self) -> dict:
        self.tick_count += 1
        self.environment.tick()
        
        # Энергия и напряжение
        decay = self.config.get("homeostasis", {}).get("energy", {}).get("decay_rate", 0.01)
        self.state["energy"] = max(0.0, self.state["energy"] - decay)
        self.state["tension"] = self.needs_system.calculate_tension(self.state["energy"])
        self.state["quasi_need"] = self.needs_system.get_quasi_need(self.state["tension"])
        
        if self.state["energy"] <= 0:
            if self.tick_count % 20 == 0: logger.warning(f"[Tick {self.tick_count:03d}] Agent collapsed! Energy=0.00")
            return self.state.copy()
        
        self.memory.update_agent_position(self.position[0], self.position[1])
        
        # Восприятие
        nearby_objects = self.environment.get_nearby_objects(self.position[0], self.position[1], 30.0)
        stimuli = self.sensation.filter_stimuli(nearby_objects)
        
        memory_valences = {}
        for obj in nearby_objects:
            mem_key = f"{obj['type']}_{obj['x']}_{obj['y']}"
            if obj["type"] in self.memory.objects: memory_valences[mem_key] = self.memory.objects[obj["type"]].valence
        
        perceived_objects = self.perception.interpret_stimuli(stimuli, self.state, memory_valences)
        
        # 🗣️ ТРИГГЕР РЕЧИ: ПЕРВЫЙ КОНТАКТ
        for obj in perceived_objects:
            if obj["type"] not in self.memory.objects:
                self.memory.register_object(obj["type"], tags=obj.get("tags", []), coordinates=(obj["x"], obj["y"]))
                self.cherry.speak("first_see", obj["type"], obj.get("tags", []), self.state["energy"], self.state["tension"], self.tick_count)

        # 🗣️ ТРИГГЕР РЕЧИ: ГОЛОД (раз в 50 тиков если голоден)
        if self.state["tension"] > 0.4 and (self.tick_count - self.cherry.last_hunger_tick > 50):
            self.cherry.speak("hunger", "", [], self.state["energy"], self.state["tension"], self.tick_count)
            self.cherry.last_hunger_tick = self.tick_count

        # 🔥 ОБНОВЛЕНИЕ ПОЛЯ КАЖДЫЙ ТИК
        self.field.update(perceived_objects)

        # 🧠 МЫШЛЕНИЕ + ДВИЖЕНИЕ
        action = "Wander"
        target = self._find_best_target(nearby_objects)
        
        if target and self.state["tension"] >= 0.1:
            mental_result = self.thinking.simulate_full_path(
                start_pos=self.position,
                target=target,
                field_objects=self.field.get_all()
            )
            
            if mental_result.success:
                dx = target['x'] - self.position[0]
                dy = target['y'] - self.position[1]
                dist = math.sqrt(dx**2 + dy**2)
                
                if dist <= self.interaction_radius:
                    acted, _ = self._try_interact(nearby_objects)
                    action = "Consume: Success" if acted else "Approach"
                elif dist > 0.1:
                    move_x = (dx / dist) * self.speed
                    move_y = (dy / dist) * self.speed
                    self.position = (self.position[0] + move_x, self.position[1] + move_y)
                    action = "Approach"
                else:
                    action = "Idle"
            else:
                action = "Wander (Blocked)"
        
        # Блуждание
        if action == "Wander" or action == "Wander (Blocked)":
            self.wander_timer -= 1
            if self.wander_timer <= 0:
                self._update_wander_direction()
            
            dx, dy = self.wander_direction
            norm = math.sqrt(dx**2 + dy**2)
            if norm > 0: dx, dy = dx / norm, dy / norm
            
            move_x = dx * self.speed * 0.5
            move_y = dy * self.speed * 0.5
            
            new_x = max(0, min(20, self.position[0] + move_x))
            new_y = max(0, min(20, self.position[1] + move_y))
            self.position = (new_x, new_y)

        # VISUALS
        if self.enable_debug:
            all_entities_for_viz = []
            for entity in self.environment.entities:
                if entity.active:
                    all_entities_for_viz.append({'type': entity.name, 'x': entity.x, 'y': entity.y, 'distance': math.sqrt((entity.x - self.position[0])**2 + (entity.y - self.position[1])**2), 'tags': entity.tags, 'valence': getattr(entity, 'value', 0.0), 'salience': 1.0})
            self.viz_plate.update(all_entities_for_viz, self.position)
            self.viz_plate.fig.canvas.draw()
            self.viz_plate.fig.canvas.flush_events()
            
            # 🔥 ОБНОВЛЕНИЕ ОБЪЕДИНЁННОГО ИНТЕРФЕЙСА
            self.viz.update(
                tick=self.tick_count,
                energy=self.state["energy"],
                tension=self.state["tension"],
                quasi_need=self.state["quasi_need"],
                field_objects=self.field.get_all(),
                agent_pos=self.position
            )
        
        memory_count = len(self.memory.objects)
        logger.info(f"{self.agent_emoji} [Tick {self.tick_count:03d}] Pos=({self.position[0]:.2f}, {self.position[1]:.2f}) | E={self.state['energy']:.2f} T={self.state['tension']:.2f} | Field={len(self.field.get_all())} | Action: {action}")
        
        if self.tick_count % 50 == 0: self.memory.save_to_disk()
        return self.state.copy()

    def run_demo(self, ticks: int = 400):
        logger.info("️ Setting up environment...")
        for _ in range(ticks): self.tick()
        summary = self.learning.get_learning_summary()
        logger.info(f"🧠 Learning Summary: {summary}")
        self.memory.save_to_disk()
        self.field.clear()
        if self.enable_debug:
            self.viz.close()  # 🔥 Закрытие объединённого интерфейса
            plt.ioff()
            plt.show()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    agent = FriedNoodlesAgent("configs/agent_profile.json", enable_debug=True)
    agent.run_demo()