# scripts/onion/perception.py
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

class PerceptionSystem:
    """Блок 4: Onion. Интерпретация стимулов и расчёт динамической валентности."""
    
    def __init__(self, config: dict):
        # Используем innates_priors вместо defaults
        self.innate_priors = config.get("innate_priors", {})
        # Снижаем порог шума, чтобы видеть нейтральные объекты (валентность 0.0)
        self.noise_threshold = 0.05 
        logger.info("🧅 PerceptionSystem initialized (Tabula Rasa mode)")
        
    def interpret_stimuli(self, stimuli: List[Dict], agent_state: Dict) -> List[Dict]:
        """
        Преобразует сырые стимулы в воспринятые объекты.
        Если объект неизвестен (нет в innate_priors), валентность = 0.0.
        """
        perceived = []
        hunger_level = 1.0 - agent_state.get("energy", 1.0)
        
        for stim in stimuli:
            obj_type = stim["type"]
            
            # БЕРЕМ ВАЛЕНТНОСТЬ: Если в приорах 0 или нет объекта -> 0.0
            base_valence = self.innate_priors.get(obj_type, 0.0)
            
            # Динамическая коррекция (пока только для инстинктов, но структура готова)
            dynamic_valence = self._calculate_dynamic_valence(obj_type, base_valence, hunger_level)
            
            # Фильтрация только абсолютного шума (очень близко к 0, но не сам 0, если объект важен)
            # Логика: если объект физически есть, мы его видим, даже если он нам безразличен
            if abs(dynamic_valence) < self.noise_threshold and obj_type not in self.innate_priors:
                continue
                
            perceived.append({
                "type": obj_type,
                "distance": stim["distance"],
                "intensity": stim["intensity"],
                "valence": dynamic_valence
            })
            
        if perceived:
            log_items = [f"{p['type']}({p['valence']})" for p in perceived]
            logger.debug(f"Perceived: {', '.join(log_items)}")
        else:
            logger.debug("Perception: Field is empty or noise only")
            
        return perceived
    
    def _calculate_dynamic_valence(self, obj_type: str, base_valence: float, hunger: float) -> float:
        """Корректирует валентность."""
        valence = base_valence
        
        # Если валентность была положительной (инстинкт), голод её усиливает
        # Если валентность была 0 (незнание), голод пока не меняет её (агент не знает, что это еда)
        if base_valence > 0: 
            valence += hunger * 0.5
            
        return round(max(-1.0, min(1.0, valence)), 2)