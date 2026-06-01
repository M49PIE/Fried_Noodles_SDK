# scripts/sauce/learning.py
import logging
from typing import Dict, Optional, List
from dataclasses import dataclass, asdict
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class LearningEvent:
    """Структура события обучения для логирования и экспорта."""
    tick: int
    action: str
    target_type: str
    outcome: str  # "success" | "failure" | "neutral"
    valence_before: float
    valence_after: float
    delta: float
    timestamp: str

class LearningSystem:
    """
    Блок 9: Sauce. Система обучения на основе опыта.
    Реализует оперантное обусловливание: действие → результат → обновление весов.
    """
    
    def __init__(self, learning_rate: float = 0.3):
        self.learning_rate = learning_rate  # Скорость обновления валентности
        self.history: List[LearningEvent] = []
        logger.info(f"🍲 LearningSystem initialized (lr={learning_rate})")
    
    def update_valence(
        self,
        current_valence: float,
        outcome: str,
        target_type: str
    ) -> float:
        """
        Обновляет валентность объекта на основе исхода взаимодействия.
        
        Алгоритм:
        - Success: valence += lr * (1.0 - valence)  # асимптотический рост к +1.0
        - Failure: valence -= lr * (1.0 + valence)   # асимптотическое падение к -1.0
        - Neutral: valence *= 0.95  # мягкое затухание к 0.0
        """
        old_valence = current_valence
        
        if outcome == "success":
            # Чем ближе к +1, тем медленнее рост (закон убывающей отдачи)
            delta = self.learning_rate * (1.0 - current_valence)
            new_valence = min(1.0, current_valence + delta)
            
        elif outcome == "failure":
            # Чем ближе к -1, тем медленнее падение
            delta = self.learning_rate * (1.0 + current_valence)
            new_valence = max(-1.0, current_valence - delta)
            
        else:  # neutral
            # Мягкое затухание к нейтралитету
            new_valence = current_valence * 0.95
            delta = new_valence - current_valence
        
        delta = round(new_valence - old_valence, 3)
        
        logger.debug(f"Learned: {target_type} {old_valence:.2f} → {new_valence:.2f} ({outcome}, Δ={delta:+.3f})")
        return round(new_valence, 3)
    
    def log_event(
        self,
        tick: int,
        action: str,
        target_type: str,
        outcome: str,
        valence_before: float,
        valence_after: float
    ):
        """Записывает событие обучения в историю."""
        event = LearningEvent(
            tick=tick,
            action=action,
            target_type=target_type,
            outcome=outcome,
            valence_before=valence_before,
            valence_after=valence_after,
            delta=round(valence_after - valence_before, 3),
            timestamp=datetime.now().isoformat()
        )
        self.history.append(event)
        logger.info(f"🧠 Learning Log: {asdict(event)}")
    
    def get_learning_summary(self) -> Dict:
        """Возвращает сводку по обучению (для отладки/экспорта)."""
        if not self.history:
            return {"total_events": 0}
        
        successes = [e for e in self.history if e.outcome == "success"]
        failures = [e for e in self.history if e.outcome == "failure"]
        
        return {
            "total_events": len(self.history),
            "successes": len(successes),
            "failures": len(failures),
            "avg_delta_success": round(sum(e.delta for e in successes) / len(successes), 3) if successes else 0,
            "avg_delta_failure": round(sum(e.delta for e in failures) / len(failures), 3) if failures else 0,
            "last_event": asdict(self.history[-1]) if self.history else None
        }
    
    # === ML Integration Hooks (заглушки для будущего) ===
    # Эти методы подготовлены для замены на PyTorch/TensorFlow без изменения интерфейса
    
    def export_weights(self) -> Dict[str, float]:
        """Экспорт текущих весов для ML-модели (stub)."""
        # В будущем: return torch.tensor([...]) или model.state_dict()
        return {"learning_rate": self.learning_rate}
    
    def import_weights(self, weights: Dict[str, float]):
        """Импорт весов из сохранённой ML-модели (stub)."""
        if "learning_rate" in weights:
            self.learning_rate = weights["learning_rate"]
            logger.info(f"Loaded learning_rate={self.learning_rate}")