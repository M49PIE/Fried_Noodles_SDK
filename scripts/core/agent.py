# scripts/core/agent.py
import logging
import json
from pathlib import Path
from scripts.meat_balls.needs import NeedsSystem
from scripts.plate.environment import Environment
from scripts.garlic.sensation import SensationSystem

logger = logging.getLogger(__name__)

class FriedNoodlesAgent:
    def __init__(self, config_path: str):
        self.config = self._load_config(config_path)
        self.tick_count = 0
        
        # Инициализация систем
        self.needs_system = NeedsSystem(self.config)
        self.environment = Environment()
        self.sensation = SensationSystem(perception_radius=10.0)
        
        self.state = {
            "energy": self.config.get("homeostasis", {}).get("energy", {}).get("initial", 1.0),
            "tension": 0.0,
            "quasi_need": None
        }
        logger.info(f"🤖 Agent {self.config.get('agent_id', 'unknown')} initialized")

    def _load_config(self, path: str) -> dict:
        config_file = Path(path)
        if not config_file.exists():
            logger.warning(f"Config not found at {path}. Using defaults.")
            return {"agent_id": "agent_001", "homeostasis": {"energy": {"initial": 1.0, "decay_rate": 0.01, "tension_threshold": 0.3}}}
        with open(config_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def tick(self) -> dict:
        self.tick_count += 1
        
        # 1. Обновляем энергию
        decay = self.config.get("homeostasis", {}).get("energy", {}).get("decay_rate", 0.01)
        self.state["energy"] = max(0.0, self.state["energy"] - decay)
        
        # 2. Получаем данные из среды (Plate)
        nearby_objects = self.environment.get_nearby_objects(max_distance=15.0)
        
        # 3. Фильтруем стимулы (Garlic)
        stimuli = self.sensation.filter_stimuli(nearby_objects)
        
        # 4. Расчет потребностей (Meat Balls)
        self.state["tension"] = self.needs_system.calculate_tension(self.state["energy"])
        self.state["quasi_need"] = self.needs_system.get_quasi_need(self.state["tension"])
        
        # 5. Формируем лог
        action = self.state["quasi_need"] if self.state["quasi_need"] else "Idle"
        stimuli_log = ", ".join([f"{s['type']}({s['intensity']})" for s in stimuli]) if stimuli else "None"
        
        logger.info(f"[Tick {self.tick_count:03d}] Energy={self.state['energy']:.2f} | Tension={self.state['tension']:.2f} | Stimuli: [{stimuli_log}] | Action: {action}")
        
        return self.state.copy()

    def run_demo(self, ticks: int = 40):
        # Инициализация тестовой среды
        logger.info("🍽️ Setting up environment...")
        self.environment.add_object("Food", distance=5.0, base_valence=0.8)
        self.environment.add_object("Rock", distance=2.0, base_valence=0.0)
        self.environment.add_object("Tree", distance=12.0, base_valence=0.1)
        
        for _ in range(ticks):
            self.tick()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    agent = FriedNoodlesAgent("configs/agent_profile.json")
    agent.run_demo()