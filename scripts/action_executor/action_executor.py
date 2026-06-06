# scripts/ebi/behavior.py
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

class BehaviorSystem:
    """Блок 7: Ebi. Выбор действия с учетом избегания негативного опыта."""
    
    def __init__(self):
        logger.info("🍤 BehaviorSystem initialized")
        
    def select_action(self, quasi_need: Optional[str], perceived_objects: List[Dict]) -> str:
        if not quasi_need:
            return "Idle"
            
        target_type = quasi_need.replace("Seek", "")
        
        # Принимаем объекты с valence >= -0.1 (нейтральные и позитивные)
        safe_objects = [obj for obj in perceived_objects if obj.get("valence", 0.0) >= -0.1]
        
        relevant_objects = [obj for obj in safe_objects if obj["type"] == target_type]
        
        if relevant_objects:
            target = max(relevant_objects, key=lambda x: x["salience"])
            return f"Approach: {target['type']}"
        
        if safe_objects:
            target = max(safe_objects, key=lambda x: x["salience"])
            return f"Investigate: {target['type']}"
        
        return "FieldAction: Wander"