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
from scripts.debug.plate.environment_debug import EnvironmentDebug

logger = logging.getLogger(__name__)

class FriedNoodlesAgent:
    def __init__(self, config_path: str, enable_debug: bool = False):
        self.config = self._load_config(config_path)
        self.tick_count = 0
        self.enable_debug = enable_debug
        
        # АГЕНТ ТЕПЕРЬ ИМЕЕТ ПОЗИЦИЮ (X, Y)
        # Центр арены 20x20
        self.position = (10.0, 10.0)
        self.speed = 0.4 # Скорость перемещения за тик

        # Инициализация систем
        self.needs_system = NeedsSystem(self.config)
        self.environment = Environment()
        self.sensation = SensationSystem(perception_radius=5.0) # Радиус восприятия теперь тоже в юнитах
        self.perception = PerceptionSystem(self.config)
        self.behavior_system = BehaviorSystem()
        
        # Инициализация дебаг-визуализации
        if self.enable_debug:
            self.debug_viz = EnvironmentDebug()
            plt.ion()
            logger.info(" Debug visualization enabled")
        
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
        
        # 2. Получаем объекты относительно текущей позиции агента
        nearby_objects = self.environment.get_nearby_objects(self.position[0], self.position[1], 15.0)
        
        # 3. Фильтруем стимулы
        stimuli = self.sensation.filter_stimuli(nearby_objects)
        
        # 4. Интерпретируем стимулы
        perceived_objects = self.perception.interpret_stimuli(stimuli, self.state)
        
        # 5. Расчет потребностей
        self.state["tension"] = self.needs_system.calculate_tension(self.state["energy"])
        self.state["quasi_need"] = self.needs_system.get_quasi_need(self.state["tension"])
        
        # 6. Выбор действия
        action = self.behavior_system.select_action(self.state["quasi_need"], perceived_objects)
        
        # 7. ДВИЖЕНИЕ АГЕНТА (Ebi)
        if action.startswith("Approach:"):
            target_type = action.split(": ")[1]
            # Ищем ближайший объект этого типа
            targets = [obj for obj in nearby_objects if obj['type'] == target_type]
            if targets:
                target = min(targets, key=lambda k: k['distance'])
                
                # Вектор движения
                dx = target['x'] - self.position[0]
                dy = target['y'] - self.position[1]
                dist = math.sqrt(dx**2 + dy**2)
                
                # Двигаемся, если не достигли цели
                if dist > 0.5:
                    move_x = (dx / dist) * self.speed
                    move_y = (dy / dist) * self.speed
                    self.position = (self.position[0] + move_x, self.position[1] + move_y)
                    logger.debug(f"Moving towards {target_type} at ({target['x']}, {target['y']})")

        # 8. Обновление визуализации
        if self.enable_debug and hasattr(self, 'debug_viz'):
            # Передаем реальные объекты с координатами
            self.debug_viz.update(nearby_objects, self.position)
            self.debug_viz.fig.canvas.draw()
            self.debug_viz.fig.canvas.flush_events()
            plt.pause(0.01)
            
        # 9. Лог в консоль
        perception_log = ", ".join([f"{p['type']}({p['valence']}, sal={p['salience']})" for p in perceived_objects]) if perceived_objects else "None"
        logger.info(f"[Tick {self.tick_count:03d}] Pos=({self.position[0]:.2f}, {self.position[1]:.2f}) | Energy={self.state['energy']:.2f} | Tension={self.state['tension']:.2f} | Action: {action}")
        
        return self.state.copy()

    def run_demo(self, ticks: int = 50):
        logger.info("🍽️ Setting up environment...")
        # Теперь объекты имеют X и Y
        self.environment.add_object("Food", x=13.0, y=10.0, base_valence=0.0) # Справа
        self.environment.add_object("Rock", x=7.0, y=10.0, base_valence=0.0)  # Слева
        self.environment.add_object("Tree", x=10.0, y=16.0, base_valence=0.0) # Сверху
        
        for _ in range(ticks):
            self.tick()
        
        if self.enable_debug:
            plt.ioff()
            plt.show()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    agent = FriedNoodlesAgent("configs/agent_profile.json", enable_debug=True)
    agent.run_demo()