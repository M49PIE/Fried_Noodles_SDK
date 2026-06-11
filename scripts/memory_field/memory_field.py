# scripts/memory_field/memory_field.py
import logging
import json
import math
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum

logger = logging.getLogger(__name__)

class LearningSource(Enum):
    USER_OSTENSIVE = "user_ostensive"
    DICTIONARY = "dictionary"
    NARRATIVE = "narrative"
    SELF_NAMED = "self_named"
    DIRECT_EXPERIENCE = "direct_experience"

@dataclass
class SemanticTriple:
    subject: str
    verb: str
    object: str
    tags: List[str] = field(default_factory=list)
    source: LearningSource = LearningSource.DIRECT_EXPERIENCE
    confidence: float = 0.5
    verified: bool = False
    coordinates: Optional[Tuple[float, float]] = None
    is_relative: bool = False
    context: str = ""
    id: str = ""

    def to_dict(self) -> dict:
        d = asdict(self)
        d["source"] = self.source.value if isinstance(self.source, LearningSource) else self.source
        return d

    @classmethod
    def from_dict(cls, data: dict) -> "SemanticTriple":
        data["source"] = LearningSource(data.get("source", "direct_experience"))
        return cls(**data)

@dataclass
class ObjectEntry:
    name: str
    tags: List[str] = field(default_factory=list)
    focusable_parts: Dict[str, Dict] = field(default_factory=dict)
    coordinates: Optional[Tuple[float, float]] = None
    last_seen_tick: int = 0
    valence: float = 0.0
    salience: float = 0.0
    is_relative: bool = False
    emoji: str = ""  # ✅ Новое поле для эмодзи

    def to_dict(self) -> dict:
        return asdict(self)

class MemoryField:
    """Блок 5: Noodles. Хранение семантических троек, объектов и координат."""

    def __init__(self, data_dir: str = "scripts/memory_field"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.triples: List[SemanticTriple] = []
        self.objects: Dict[str, ObjectEntry] = {}
        self.agent_position: Tuple[float, float] = (0.0, 0.0)
        
        # Innate Dictionary (статические знания)
        self.verbs: Dict = {}
        self.adjectives: Dict = {}
        self.innate_objects: Dict = {}  # ✅ Словарь из innate_dictionary/objects.json

        self._load_base_data()
        logger.info("🍜 MemoryField initialized (Hodological Space + Semantic Triples)")

    def _load_base_data(self):
        # ✅ Изменённые пути для innate_dictionary
        verbs_path = self.data_dir / "innate_dictionary" / "verbs.json"
        adjectives_path = self.data_dir / "innate_dictionary" / "adjectives.json"
        innate_objects_path = self.data_dir / "innate_dictionary" / "objects.json"
        base_triples_path = self.data_dir / "semantic_base.json"

        if verbs_path.exists():
            try:
                with open(verbs_path, "r", encoding="utf-8") as f:
                    self.verbs = json.load(f)
            except json.JSONDecodeError:
                logger.warning("verbs.json corrupted, using defaults.")
                self.verbs = {}
                
        if adjectives_path.exists():
            try:
                with open(adjectives_path, "r", encoding="utf-8") as f:
                    self.adjectives = json.load(f)
            except json.JSONDecodeError:
                logger.warning("adjectives.json corrupted, using defaults.")
                self.adjectives = {}
        
        # ✅ Загрузка innate_dictionary/objects.json
        if innate_objects_path.exists():
            try:
                with open(innate_objects_path, "r", encoding="utf-8") as f:
                    self.innate_objects = json.load(f)
                    logger.info(f" Loaded {len(self.innate_objects)} innate objects with emojis")
            except json.JSONDecodeError:
                logger.warning("innate_dictionary/objects.json corrupted, using defaults.")
                self.innate_objects = {}
                
        if base_triples_path.exists():
            try:
                with open(base_triples_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.triples = [SemanticTriple.from_dict(t) for t in data.get("triples", [])]
            except json.JSONDecodeError:
                logger.warning("semantic_base.json corrupted, resetting.")
                self.triples = []

    def update_agent_position(self, x: float, y: float):
        self.agent_position = (x, y)

    def add_triple(self, triple: SemanticTriple):
        # ✅ Фильтруем динамические теги для стабильного ID и чистой памяти
        stable_tags = tuple(sorted([t for t in triple.tags if not t.startswith("salience_")]))
        triple_id = f"{triple.subject}_{triple.verb}_{triple.object}_{hash(stable_tags) % 10000}"
        triple.id = triple_id
        triple.tags = list(stable_tags)

        # ✅ Обновляем существующую тройку вместо дублирования
        for i, existing in enumerate(self.triples):
            if existing.id == triple.id:
                if triple.confidence > existing.confidence or triple.coordinates != existing.coordinates:
                    self.triples[i] = triple
                return
        self.triples.append(triple)

    def get_triples(self, subject: str = None, verb: str = None, object_name: str = None) -> List[SemanticTriple]:
        result = self.triples
        if subject: result = [t for t in result if t.subject == subject]
        if verb: result = [t for t in result if t.verb == verb]
        if object_name: result = [t for t in result if t.object == object_name]
        return result

    def register_object(self, name: str, tags: List[str], coordinates: Optional[Tuple[float, float]] = None, is_relative: bool = False):
        # ✅ Фильтруем семантические теги от динамических
        semantic_tags = [t for t in tags if not t.startswith("salience_")]

        if name in self.objects:
            self.objects[name].tags = list(set(self.objects[name].tags + semantic_tags))
            if coordinates: self.objects[name].coordinates = coordinates
            return

        final_name = name
        if not name or name.startswith("obj_"):
            final_name = self._generate_name_from_tags(semantic_tags)
            logger.info(f"🏷️ Self-named: {final_name} from tags {semantic_tags}")

        # ✅ Проверяем, есть ли объект в innate_dictionary
        emoji = ""
        default_valence = 0.0
        if name in self.innate_objects:
            emoji = self.innate_objects[name].get("emoji", "")
            default_valence = self.innate_objects[name].get("default_valence", 0.0)
            # Добавляем теги из словаря, если их нет
            innate_tags = self.innate_objects[name].get("tags", [])
            semantic_tags = list(set(semantic_tags + innate_tags))

        self.objects[final_name] = ObjectEntry(
            name=final_name, 
            tags=semantic_tags, 
            coordinates=coordinates, 
            is_relative=is_relative,
            emoji=emoji,
            valence=default_valence
        )

    def _generate_name_from_tags(self, tags: List[str]) -> str:
        if not tags: return f"obj_{len(self.objects)}"
        return "-".join(list(dict.fromkeys(tags))[:2]).lower().replace(" ", "_")

    def get_nearest_object_by_type(self, target_type: str) -> Optional[ObjectEntry]:
        candidates = []
        for obj in self.objects.values():
            if target_type.lower() in [t.lower() for t in obj.tags] or target_type.lower() in obj.name.lower():
                if obj.coordinates:
                    dist = math.hypot(obj.coordinates[0] - self.agent_position[0], obj.coordinates[1] - self.agent_position[1])
                    candidates.append((dist, obj))
        if candidates:
            candidates.sort(key=lambda x: x[0])
            return candidates[0][1]
        return None

    def update_object_valence(self, name: str, valence: float, salience: float):
        if name in self.objects:
            self.objects[name].valence = valence
            self.objects[name].salience = salience

    def save_to_disk(self):
        with open(self.data_dir / "semantic_base.json", "w", encoding="utf-8") as f:
            json.dump({"triples": [t.to_dict() for t in self.triples]}, f, indent=2, ensure_ascii=False)
        # ✅ Изменённое имя файла
        with open(self.data_dir / "known_objects.json", "w", encoding="utf-8") as f:
            json.dump({k: v.to_dict() for k, v in self.objects.items()}, f, indent=2, ensure_ascii=False)
        
        logger.info(f"💾 MemoryField saved: {len(self.triples)} triples, {len(self.objects)} objects.")