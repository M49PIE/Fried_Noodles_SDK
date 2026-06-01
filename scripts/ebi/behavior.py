# scripts/ebi/behavior.py
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

class BehaviorSystem:
    """Блок 7: Ebi. Выбор действия с учетом избегания негативного опыта."""
    
    def __init__(self):
        logger.info("🍤 BehaviorSystem initialized")
        
    def select_action(self, quasi_need: Optional[str], perceived_objects: List[Dict]) -> str:
        # 1. Нет потребности -> отдыхаем
        if not quasi_need:
            return "Idle"
            
        target_type = quasi_need.replace("Seek", "")
        
        # ✅ ФИЛЬТР: Игнорируем объекты с негативным опытом (валентность < 0)
        safe_objects = [obj for obj in perceived_objects if obj.get("valence", 0.0) > 0.0]
        
        # 2. Ищем целевые объекты (например, Food) среди БЕЗОПАСНЫХ
        relevant_objects = [obj for obj in safe_objects if obj["type"] == target_type]
        
        if relevant_objects:
            target = max(relevant_objects, key=lambda x: x["salience"])
            return f"Approach: {target['type']}"
        
        # 3. Целевого нет -> ищем ЛЮБОЙ безопасный объект для исследования
        if safe_objects:
            target = max(safe_objects, key=lambda x: x["salience"])
            return f"Investigate: {target['type']}"
        
        # 4. Поле пустое или только опасное -> блуждаем
        return "FieldAction: Wander"