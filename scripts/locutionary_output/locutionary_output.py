# scripts/locutionary_output/locutionary_output.py
import logging
import json
import random
from pathlib import Path
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

class LocutionaryOutput:
    """
    Блок 8: Cherry. Генерация речи на основе semantic_dictionary.json.
    Использует ТОЛЬКО слова из специализированных подкатегорий для каждого события.
    """
    def __init__(self, memory, dict_path: str = "scripts/world_model/semantic_dictionary.json"):
        self.memory = memory
        self.dictionary = self._load_dictionary(dict_path)
        self.last_hunger_tick = 0
        logger.info("🍒 LocutionaryOutput initialized (Context-driven Speech)")

    def _load_dictionary(self, path: str) -> Dict:
        p = Path(path)
        if p.exists():
            with open(p, 'r', encoding='utf-8') as f:
                return json.load(f)
        logger.warning(f"⚠️ Dictionary not found at {path}. Using fallback.")
        return {"verbs": {"eating": ["eat"]}, "tags": {"food_quality": ["tasty"]}}

    def _get_word(self, main_category: str, sub_category: str) -> str:
        """Безопасно достает случайное слово из конкретной подкатегории."""
        try:
            if main_category in self.dictionary and sub_category in self.dictionary[main_category]:
                words = self.dictionary[main_category][sub_category]
                if words:
                    return random.choice(words)
        except Exception as e:
            logger.debug(f"Error getting word from {main_category}.{sub_category}: {e}")
        return "thing"

    def speak(self, event_type: str, target_type: str = "", target_tags: List[str] = None, 
              energy: float = 1.0, tension: float = 0.0, tick: int = 0) -> Optional[str]:
        """
        Генерирует фразу в зависимости от события, используя ТОЛЬКО подходящие слова.
        """
        if target_tags is None:
            target_tags = []

        phrase = ""

        if event_type == "hunger":
            # Глаголы желания + прилагательные качества еды
            verb = self._get_word("verbs", "desiring")
            adj = self._get_word("tags", "food_quality")
            phrase = f"I {verb} {adj} food."

        elif event_type == "eat":
            # Глаголы поедания + прилагательные качества еды
            verb = self._get_word("verbs", "eating")
            adj = self._get_word("tags", "food_quality")
            phrase = f"I {verb} {adj} {target_type.lower()}."

        elif event_type == "first_see":
            # Глаголы восприятия + прилагательные внешнего вида
            verb = self._get_word("verbs", "seeing")
            adj = self._get_word("tags", "object_appearance")
            phrase = f"I {verb} {adj} {target_type.lower()}."

        elif event_type == "fail":
            # Глаголы исследования + прилагательные текстуры
            verb = self._get_word("verbs", "examining")
            adj = self._get_word("tags", "object_texture")
            phrase = f"I {verb} {adj} {target_type.lower()}."

        if phrase:
            logger.info(f"️ [Agent]: {phrase}")
            return phrase
        return None