# scripts/locutionary_output/locutionary_output.py
import logging
from typing import List, Optional, Tuple
from scripts.memory_field.memory_field import MemoryField, SemanticTriple, LearningSource

logger = logging.getLogger(__name__)

class LocutionaryOutput:
    """Блок 8: Cherry. Генерация семантических троек и управление именованием."""

    def __init__(self, memory: MemoryField):
        self.memory = memory
        logger.info("🍒 LocutionaryOutput initialized (Semantic Triple Generator)")

    def generate_triple(self, subject: str, verb: str, object_name: str,
                        tags: List[str], coordinates: Optional[Tuple[float, float]] = None,
                        source: LearningSource = LearningSource.DIRECT_EXPERIENCE) -> SemanticTriple:
        self.memory.register_object(object_name, tags, coordinates)

        triple = SemanticTriple(
            subject=subject, verb=verb, object=object_name, tags=tags,
            source=source,
            confidence=0.7 if source != LearningSource.SELF_NAMED else 0.5,
            verified=(source == LearningSource.DIRECT_EXPERIENCE),
            coordinates=coordinates,
            is_relative=(source == LearningSource.DICTIONARY)
        )
        self.memory.add_triple(triple)
        
        # ✅ Изменено с logger.debug на logger.info, чтобы видеть в консоли
        logger.info(f"🗣️ Triple: [{subject}] {verb} {object_name} | tags: {tags} | src: {source.value}")
        
        return triple

    def generate_self_named(self, subject: str, verb: str, tags: List[str],
                            coordinates: Optional[Tuple[float, float]] = None) -> SemanticTriple:
        temp_name = self.memory._generate_name_from_tags(tags)
        return self.generate_triple(subject, verb, temp_name, tags, coordinates, LearningSource.SELF_NAMED)

    def get_relevant_triples(self, limit: int = 5) -> List[SemanticTriple]:
        scored = [(t, t.confidence + (0.2 if t.verified else 0)) for t in self.memory.triples]
        scored.sort(key=lambda x: x[1], reverse=True)
        return [t for t, _ in scored[:limit]]

    def verbalize(self, triple: SemanticTriple) -> str:
        coord = f" @ {triple.coordinates}" if triple.coordinates else ""
        verified = " [✓]" if triple.verified else ""
        return f"[{triple.subject}] {triple.verb} {triple.object}{coord} | {triple.tags}{verified}"