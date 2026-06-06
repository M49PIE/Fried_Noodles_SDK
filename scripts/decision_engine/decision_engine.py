# scripts/cheese/thinking.py
import logging
from typing import List, Dict, Optional, Callable
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class ActionType(Enum):
    """Типы доступных действий"""
    APPROACH = "approach"
    INVESTIGATE = "investigate"
    CONSUME = "consume"
    FLEE = "flee"
    WANDER = "wander"
    IDLE = "idle"
    SPEAK = "speak"

@dataclass
class ActionCandidate:
    """Кандидат на выполнение с utility score"""
    action_type: ActionType
    target: Optional[Dict]
    utility: float
    reason: str
    valence: float = 0.0  # ✅ NEW: валентность цели

class BehaviorNode:
    """Базовый узел Behavior Tree"""
    def __init__(self, name: str):
        self.name = name
        self.children: List['BehaviorNode'] = []
    
    def evaluate(self, context: Dict) -> str:
        raise NotImplementedError

class SelectorNode(BehaviorNode):
    """Выбирает первый успешный дочерний узел"""
    def evaluate(self, context: Dict) -> str:
        for child in self.children:
            status = child.evaluate(context)
            if status == "success":
                return "success"
        return "failure"

class SequenceNode(BehaviorNode):
    """Выполняет все дочерние узлы по порядку"""
    def evaluate(self, context: Dict) -> str:
        for child in self.children:
            status = child.evaluate(context)
            if status != "success":
                return status
        return "success"

class ConditionNode(BehaviorNode):
    """Проверяет условие"""
    def __init__(self, name: str, condition: Callable[[Dict], bool]):
        super().__init__(name)
        self.condition = condition
    
    def evaluate(self, context: Dict) -> str:
        if self.condition(context):
            return "success"
        return "failure"

class ActionNode(BehaviorNode):
    """Листовой узел - генерирует ActionCandidate с utility score"""
    def __init__(self, name: str, action_type: ActionType, utility_func: Callable[[Dict], float]):
        super().__init__(name)
        self.action_type = action_type
        self.utility_func = utility_func
    
    def evaluate(self, context: Dict) -> str:
        utility = self.utility_func(context)
        target = context.get("target")
        valence = target.get("valence", 0.0) if target else 0.0
        
        # ✅ NEW: Не добавляем действия с негативной валентностью
        if valence < -0.1:
            return "failure"
        
        if utility > 0.0:
            context["candidates"].append(ActionCandidate(
                action_type=self.action_type,
                target=target,
                utility=utility,
                reason=f"{self.name} (utility={utility:.2f})",
                valence=valence
            ))
            return "success"
        return "failure"

class ThinkingSystem:
    """
    Блок 6: Cheese. Hybrid Utility + Behavior Tree.
    Оценивает все возможные действия и выбирает оптимальное.
    ✅ ИСПРАВЛЕНО: Фильтрация по валентности
    """
    
    def __init__(self):
        self.tree = self._build_default_tree()
        logger.info("🧀 ThinkingSystem initialized (Hybrid Utility + Behavior Tree)")
    
    def _build_default_tree(self) -> BehaviorNode:
        """Строит Behavior Tree по умолчанию"""
        
        root = SelectorNode("Root")
        
        # 1. Ветвь: Выжить (высокий приоритет)
        survival = SequenceNode("Survival")
        survival.children.append(ConditionNode("IsHungry", lambda ctx: ctx.get("tension", 0) > 0.5))
        survival.children.append(ActionNode(
            "ApproachFood", 
            ActionType.APPROACH,
            lambda ctx: ctx.get("tension", 0) * ctx.get("food_valence", 0.5)
        ))
        root.children.append(survival)
        
        # 2. Ветвь: Исследовать (средний приоритет) — ТОЛЬКО если валентность >= 0
        explore = SequenceNode("Explore")
        explore.children.append(ConditionNode("SeesUnknown", lambda ctx: ctx.get("unknown_objects", False)))
        explore.children.append(ConditionNode("ValenceOK", lambda ctx: ctx.get("target", {}).get("valence", 0.0) >= -0.1))
        explore.children.append(ActionNode(
            "Investigate",
            ActionType.INVESTIGATE,
            lambda ctx: 0.3 * ctx.get("curiosity", 0.5)
        ))
        root.children.append(explore)
        
        # 3. Ветвь: Блуждать (низкий приоритет)
        wander = ActionNode("Wander", ActionType.WANDER, lambda ctx: 0.1)
        root.children.append(wander)
        
        return root
    
    def select_action(self, context: Dict, memory_valences: Dict = None) -> ActionCandidate:
        """
        Оценивает все действия через Behavior Tree + Utility Scoring.
        ✅ NEW: memory_valences — словарь {type_x_y: valence} для фильтрации
        Возвращает ActionCandidate с наивысшим utility score.
        """
        context["candidates"] = []
        
        # ✅ NEW: Если есть память о валентности — добавляем в контекст
        if memory_valences and context.get("target"):
            target = context["target"]
            mem_key = f"{target['type']}_{target['x']}_{target['y']}"
            if mem_key in memory_valences:
                target["valence"] = memory_valences[mem_key]
        
        # Запускаем Behavior Tree - он заполнит candidates
        self.tree.evaluate(context)
        
        # ✅ NEW: Фильтруем кандидаты по валентности (дополнительная защита)
        valid_candidates = [c for c in context["candidates"] if c.valence >= -0.1]
        
        # Выбираем действие с максимальным utility
        if valid_candidates:
            best = max(valid_candidates, key=lambda c: c.utility)
            logger.debug(f"Thinking: {best.reason} | valence={best.valence:.2f}")
            return best
        
        # Fallback: Idle
        return ActionCandidate(
            action_type=ActionType.IDLE,
            target=None,
            utility=0.0,
            reason="No valid actions available",
            valence=0.0
        )
    
    def add_custom_action(self, parent_node: BehaviorNode, action_type: ActionType, 
                          utility_func: Callable[[Dict], float], name: str = "Custom"):
        """Позволяет динамически добавлять действия (например, из LLM)"""
        node = ActionNode(name, action_type, utility_func)
        parent_node.children.append(node)
        logger.info(f"Added custom action: {name}")