# scripts/onion/perception.py
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

class PerceptionSystem:
    """Блок 4: Onion. Интерпретация стимулов, модуляция внимания потребностями."""
    
    def __init__(self, config: dict):
        self.innate_priors = config.get("innate_priors", {})
        self.base_noise_threshold = 0.05
        logger.info("🧅 PerceptionSystem initialized (Needs-driven Attention)")
        
    def interpret_stimuli(self, stimuli: List[Dict], agent_state: Dict) -> List[Dict]:
        """
        Преобразует стимулы в воспринятые объекты.
        Напряжение (Tension) модулирует порог фильтрации и интенсивность восприятия.
        """
        tension = agent_state.get("tension", 0.0)
        
        # 1. Модуляция внимания
        attention_boost = 1.0 + tension * 0.8
        dynamic_threshold = self.base_noise_threshold * max(0.2, (1.0 - tension * 0.7))
        
        perceived = []
        hunger_level = 1.0 - agent_state.get("energy", 1.0)
        
        for stim in stimuli:
            obj_type = stim["type"]
            base_valence = self.innate_priors.get(obj_type, 0.0)
            
            # 2. Применяем усиление внимания
            modulated_intensity = min(1.0, stim["intensity"] * attention_boost)
            
            # 3. Рассчитываем валентность
            dynamic_valence = self._calculate_dynamic_valence(obj_type, base_valence, hunger_level)
            
            # 4. Фильтрация с динамическим порогом
            if abs(dynamic_valence) < dynamic_threshold and obj_type not in self.innate_priors:
                continue
                
            perceived.append({
                "type": obj_type,
                "distance": stim["distance"],
                "x": stim["x"], # <-- ПЕРЕДАЕМ X ДАЛЬШЕ
                "y": stim["y"], # <-- ПЕРЕДАЕМ Y ДАЛЬШЕ
                "intensity": round(modulated_intensity, 2),
                "valence": dynamic_valence,
                "salience": round(modulated_intensity * (1.0 + tension), 2)
            })
            
        # Сортируем по заметности
        perceived.sort(key=lambda x: x["salience"], reverse=True)
        
        if perceived:
            log_items = [f"{p['type']}({p['valence']}, sal={p['salience']})" for p in perceived]
            logger.debug(f"Perceived: {', '.join(log_items)}")
        else:
            logger.debug("Perception: Field empty or below dynamic threshold")
            
        return perceived
    
    def _calculate_dynamic_valence(self, obj_type: str, base_valence: float, hunger: float) -> float:
        """Корректирует валентность с учётом гомеостаза."""
        valence = base_valence
        if base_valence > 0: 
            valence += hunger * 0.5
        return round(max(-1.0, min(1.0, valence)), 2)