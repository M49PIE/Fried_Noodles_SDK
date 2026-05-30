# scripts/ebi/behavior.py
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

class BehaviorSystem:
    """Блок 7: Ebi. Выбор конкретного действия на основе квазипотребности и восприятия."""
    
    def __init__(self):
        logger.info("🍤 BehaviorSystem initialized")
        
    def select_action(self, quasi_need: Optional[str], perceived_objects: List[Dict]) -> str:
        """
        Выбирает действие.
        Логика MVP: Если есть потребность, но нет цели с высокой валентностью -> 
        включается Field Action (блуждание/поиск).
        """
        
        # 1. Если нет потребности -> отдыхаем
        if not quasi_need:
            return "Idle"
            
        # 2. Если потребность есть, но нет видимых целей -> Field Action (Поиск)
        # В будущем здесь будет векторное движение к объекту
        if not perceived_objects:
            return f"FieldAction: Wander (Seeking {quasi_need})"
            
        # 3. Если цели есть -> пробуем приблизиться к самой заметной (Salience)
        # Сортируем по заметности, так как валентность пока 0
        target = max(perceived_objects, key=lambda x: x["salience"])
        
        logger.debug(f"Target selected: {target['type']} (sal={target['salience']})")
        return f"Approach: {target['type']}"