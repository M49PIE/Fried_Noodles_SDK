# scripts/core/agent.py
import logging
import json
import math
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
        
        # Позиция агента
        self.position = (10.0, 10.0)
        self.speed = 0.4

        # Инициализация систем
        self.needs_system = NeedsSystem(self.config)
        self.environment = Environment()
        self.sensation = SensationSystem(perception_radius=5.0)
        self.perception = PerceptionSystem(self.config)
        self.behavior_system = BehaviorSystem()
        self.memory = FieldMemory()  # <-- НОВОЕ: Блок Noodles
        
        # Инициализация дебаг-визуализаций
        if self.enable_debug:
            self.viz_plate = EnvironmentDebug()
            self.viz_needs = NeedsDebug()
            plt.ion()
            logger.info("🔧 Debug visualizations enabled: Plate + Meat Balls")
        
        self.state = {
            "energy": self.config.get("homeostasis", {}).get("energy", {}).get("initial", 1.0),
            "tension": 0.0,
            "quasi_need": None
        }
        logger.info(f"🤖 Agent {self.config.get('agent_id', 'unknown')} initialized at {self.position}")

    def _load_config(self, path: str) -> dict:
        config_file = Path(path)
        if not config_file.exists():
            logger.warning(f"Config not found at {path}. Using defaults.")
            return {"agent_id": "agent_001", "homeostasis": {"energy": {"initial": 1.0, "decay_rate": 0.01, "tension_threshold": 0.3}}, "innate_priors": {"Food": 0.0, "Rock": 0.0}}
        with open(config_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def tick(self) -> dict:
        self.tick_count += 1
        
        # 1. Обновляем энергию
        decay = self.config.get("homeostasis", {}).get("energy", {}).get("decay_rate", 0.01)
        self.state["energy"] = max(0.0, self.state["energy"] - decay)
        
        # 2. Обновляем позицию в памяти
        self.memory.update_agent_position(self.position[0], self.position[1])
        
        # 3. Получаем объекты относительно позиции агента
        nearby_objects = self.environment.get_nearby_objects(self.position[0], self.position[1], 15.0)
        
        # 4. Фильтруем стимулы
        stimuli = self.sensation.filter_stimuli(nearby_objects)
        
        # 5. Интерпретируем стимулы
        perceived_objects = self.perception.interpret_stimuli(stimuli, self.state)
        
        # 6. ЗАПОМИНАНИЕ (Noodles)
        for obj in perceived_objects:
            # Сохраняем тип, координаты, валентность и заметность
            self.memory.perceive_object(obj["type"], obj["x"], obj["y"], obj["valence"], obj["salience"])
            
        # 7. Расчет потребностей
        self.state["tension"] = self.needs_system.calculate_tension(self.state["energy"])
        self.state["quasi_need"] = self.needs_system.get_quasi_need(self.state["tension"])
        
        # 8. Выбор действия
        action = self.behavior_system.select_action(self.state["quasi_need"], perceived_objects)
        
        # Если ничего не видно, но есть потребность -> пробуем вспомнить цель из памяти
        if action == "Idle" and self.state["quasi_need"]:
            target_type = self.state["quasi_need"].replace("Seek", "")
            remembered_obj = self.memory.get_nearest_object_by_type(target_type)
            if remembered_obj:
                action = f"RecallApproach: {target_type} (Memory)"
        
        # 9. ДВИЖЕНИЕ АГЕНТА (Ebi)
        if action.startswith("Approach:") or action.startswith("RecallApproach:"):
            target_type = action.split(": ")[1].split(" (")[0]
            
            # Ищем в текущем восприятии
            targets = [obj for obj in nearby_objects if obj['type'] == target_type]
            
            # Если нет в поле зрения -> берем из памяти
            if not targets:
                remembered_obj = self.memory.get_nearest_object_by_type(target_type)
                if remembered_obj:
                    targets = [remembered_obj]
            
            if targets:
                target = min(targets, key=lambda k: k['distance'])
                dx = target['x'] - self.position[0]
                dy = target['y'] - self.position[1]
                dist = math.sqrt(dx**2 + dy**2)
                
                # Двигаемся, если не достигли цели
                if dist > 0.5:
                    move_x = (dx / dist) * self.speed
                    move_y = (dy / dist) * self.speed
                    self.position = (self.position[0] + move_x, self.position[1] + move_y)

        # 10. Обновление ВИЗУАЛИЗАЦИЙ
        if self.enable_debug:
            self.viz_plate.update(nearby_objects, self.position)
            self.viz_plate.fig.canvas.draw()
            self.viz_plate.fig.canvas.flush_events()
            
            self.viz_needs.update(self.tick_count, self.state["energy"], self.state["tension"], self.state["quasi_need"])
            self.viz_needs.fig.canvas.draw()
            self.viz_needs.fig.canvas.flush_events()
            
            plt.pause(0.01)
            
        # 11. Лог в консоль
        memory_count = len(self.memory.object_memories)
        perception_log = ", ".join([f"{p['type']}({p['valence']}, sal={p['salience']})" for p in perceived_objects]) if perceived_objects else "None"
        logger.info(f"[Tick {self.tick_count:03d}] Pos=({self.position[0]:.2f}, {self.position[1]:.2f}) | Mem={memory_count} | Perceived: [{perception_log}] | Action: {action}")
        
        return self.state.copy()

    def run_demo(self, ticks: int = 60):
        logger.info("🍽️ Setting up environment...")
        self.environment.add_object("Food", x=13.0, y=10.0, base_valence=0.0)
        self.environment.add_object("Rock", x=7.0, y=10.0, base_valence=0.0)
        self.environment.add_object("Tree", x=10.0, y=16.0, base_valence=0.0)
        
        for _ in range(ticks):
            self.tick()
        
        if self.enable_debug:
            plt.ioff()
            plt.show()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    agent = FriedNoodlesAgent("configs/agent_profile.json", enable_debug=True)
    agent.run_demo()