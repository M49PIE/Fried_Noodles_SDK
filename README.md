# 🍜 Fried Noodles SDK

**AI-driven Game Agent Framework** — psychological architecture for autonomous NPCs based on Kurt Lewin's *Field Theory*.

---

## 🎯 Overview

Fried Noodles SDK is a **psychologically-grounded cognitive architecture** for creating autonomous game agents that learn, adapt, and make decisions based on internal needs and past experience. Unlike traditional finite-state-machine NPCs, agents in this framework:

- 🧠 **Learn from outcomes** — positive experiences reinforce behavior, negative ones teach avoidance (operant conditioning)
- 🌍 **Navigate hodological space** — decision-making uses psychological distance, not just Euclidean geometry
- ⚖️ **Maintain homeostasis** — energy decay creates tension, tension drives motivated behavior
- 👁️ **Perceive through needs** — hunger amplifies attention to food, satiety allows exploration
- 🗣️ **Verbally express internal state** — context-driven speech generation from structured dictionaries

**Ideal for:** AI game designers prototyping behavior, social psychology researchers, narrative designers building adaptive characters.

---

## 📦 9 Modules Breakdown

### 🔵 Block 1: World Model (Plate)
**Path:** `scripts/world_model/world_model.py`

Core environment simulation. Manages entities (agents, objects, barriers), collision detection, spawning, and spatial queries.

| Method | Purpose |
|---|---|
| `add_entity()` | Spawn objects into the world |
| `get_nearby_objects(x, y, radius)` | Returns entities within perception range |
| `get_entities_in_radius()` | Filtered spatial query by type/tags |
| `tick(dt)` | Advances physics, spawner, entity behaviors |

**Key design:** Objects carry a `consumed` flag to prevent re-interaction. Arena size is configurable (default 20×20).

---

### 🔵 Block 2: Tension System (Meat Balls)
**Path:** `scripts/tension_system/tension_system.py`

Maintains physiological homeostasis. Energy decays each tick → tension rises → quasi-needs emerge.

| Method | Purpose |
|---|---|
| `calculate_tension(energy)` | `tension = 1.0 - energy` |
| `get_quasi_need(tension)` | Returns `"SeekFood"` if tension > threshold (default 0.3) |

**Psychological basis:** Lewin's *tension system* — disrupted homeostasis creates psychological pressure to act.

---

### 🔵 Block 3: Sensation Input (Garlic)
**Path:** `scripts/sensation_input/sensation_input.py`

Filters raw environmental data by perception radius. Acts as the agent's sensory organs.

| Method | Purpose |
|---|---|
| `filter_stimuli(objects)` | Returns only objects within `perception_radius` |
| `_calculate_intensity(distance)` | Linear decay from 1.0 (near) to 0.0 (at radius edge) |

---

### 🔵 Block 4: Perception Filter (Onion)
**Path:** `scripts/perception_filter/perception_filter.py`

Interprets stimuli through the lens of current needs. Implements **need-driven attention modulation**.

| Method | Purpose |
|---|---|
| `interpret_stimuli(stimuli, state, memory_valences)` | Returns perceived objects with valence and salience |

**Key features:**
- **Memory retrieval** — objects previously encountered use remembered valence
- **Attention boost** — `1.0 + tension × 0.8` (hungry agent notices food more)
- **Dynamic threshold** — salience threshold lowers when tension is high
- **Sorts by salience** — most relevant objects first

---

### 🔵 Block 5: Memory & Field (Noodles + Field)
**Paths:** `scripts/memory_field/memory_field.py`, `scripts/memory_field/field.py`

Two-layer memory system:

| Layer | Class | Purpose |
|---|---|---|
| **Long-term** | `MemoryField` | Hodological space — stores object types, valences, semantic triples, coordinates |
| **Working** | `PsychologicalField` | Dynamic cognitive map — reflects only currently perceived objects each tick |

**MemoryField key capabilities:**
- `register_object(name, tags, coordinates)` — learn new object types
- `update_object_valence(name, valence, salience)` — reinforce learned values
- `get_nearest_object_by_type(type)` — retrieve from hodological space
- `add_triple(triple)` — semantic memory (subject-verb-object relationships)
- Persistence via `save_to_disk()` — saves as `semantic_base.json` and `known_objects.json`
- Loads innate knowledge from `innate_dictionary/` (objects, verbs, adjectives with emojis)

**PsychologicalField:** Clears and rebuilds every tick from perception output. Used by the decision engine for mental simulation of paths.

---

### 🔵 Block 6: Decision Engine (Cheese → Thinking)
**Path:** `scripts/decision_engine/thinking.py`

**Hybrid Utility AI + Behavior Tree** architecture with mental simulation.

```
Root (Selector)
├── Survival (Sequence)
│   ├── Condition: IsHungry (tension > 0.5)
│   └── Action: ApproachFood (utility = tension × food_valence)
├── Explore (Sequence)
│   ├── Condition: SeesUnknown
│   ├── Condition: ValenceOK (valence >= -0.1)
│   └── Action: Investigate (utility = 0.3 × curiosity)
└── Wander (Action) — fallback, utility = 0.1
```

| Method | Purpose |
|---|---|
| `simulate_full_path(start, target, field_objects)` | Mental pathfinding — checks if target is reachable without blocking |

**Mental simulation** runs up to 50 steps (configurable) through *PsychologicalField* obstacles. Returns `MentalPath(success, reason)`.

---

### 🔵 Block 7: Action Executor (Ebi)
**Path:** `scripts/action_executor/action_executor.py`

Legacy behavior selector. Filters perceived objects by valence ≥ -0.1 (avoids negative objects), selects action by salience.

| Method | Purpose |
|---|---|
| `select_action(quasi_need, perceived_objects)` | Returns action string: `"Approach: X"`, `"Investigate: X"`, or `"FieldAction: Wander"` |

**Note:** Primary action logic has moved to `agent.py` — this module kept for backward compatibility.

---

### 🔵 Block 8: Locutionary Output (Cherry)
**Path:** `scripts/locutionary_output/locutionary_output.py`

**Context-driven speech generation.** Produces utterances based on agent's internal state and events.

| Event | Trigger | Example |
|---|---|---|
| `hunger` | Tension > 0.4, max once per 50 ticks | *"I desire tasty food."* |
| `eat` | Successful food consumption | *"I devour tasty apple."* |
| `first_see` | First encounter with object type | *"I notice strange rock."* |
| `fail` | Negative experience (rock investigation) | *"I inspect hard rock."* |

Vocabulary is loaded from `semantic_dictionary.json` with subcategories: `verbs` (eating, seeing, desiring, examining) and `tags` (food_quality, object_appearance, object_texture).

---

### 🔵 Block 9: Valence Update (Sauce)
**Path:** `scripts/valence_update/valence_update.py`

**Operant conditioning engine.** Updates object valences based on interaction outcomes.

| Outcome | Update Rule | Behavior |
|---|---|---|
| ✅ **Success** | `valence += lr × (1.0 - valence)` | Asymptotic approach to +1.0 |
| ❌ **Failure** | `valence -= lr × (1.0 + valence)` | Asymptotic approach to -1.0 |
| ➖ **Neutral** | `valence × 0.95` | Soft decay to 0.0 |

| Method | Purpose |
|---|---|
| `update_valence(current, outcome, type)` | Apply learning rule, return new valence |
| `log_event(...)` | Record event with timestamp for analysis |
| `get_learning_summary()` | Statistics: success/failure counts, average deltas |
| `export_weights()` / `import_weights()` | ML integration hooks (PyTorch/TensorFlow stubs) |

**Learning rate:** 0.3 (configurable). Law of diminishing returns is built into the asymptotic formulas.

---

### 🔧 Debug Systems
**Path:** `scripts/debug/`

| Component | Purpose |
|---|---|
| `UnifiedDebug` | Combined debug UI showing tick, energy, tension, field objects, agent position |
| `EnvironmentDebug` | Matplotlib visualization — agent (green circle), food (yellow), rocks (gray), perception radius (blue) |
| `world_model/`, `tension_system/`, `shared/` | Per-module debug overlays |

---


## 🚀 Quick Start

### Requirements
- Python 3.11+
- `matplotlib` (visualization)
- `numpy`

### Installation & Run

```bash
# Clone
git clone https://github.com/M49PIE/Fried_Noodles_SDK.git
cd Fried_Noodles_SDK

# Install dependencies
pip install matplotlib numpy

# Run demo (400 ticks with visualization)
python -m scripts.core.agent
```

### What You'll Observe

The agent will:
1. 🚶 **Wander** when energy is high — exploring the environment
2. 🍎 **Seek food** when tension exceeds threshold — hunger-driven behavior
3. ✅ **Learn** that food is positive — valence increases toward +1.0
4. ❓ **Investigate** unknown objects (rocks, trees) — innate curiosity
5. ❌ **Avoid** rocks after negative experience — valence shifts toward -1.0
6. 🔄 **Balance** survival vs. exploration — dynamically prioritizing needs
7. 🗣️ **Speak** about internal states — context-appropriate utterances

## 👨‍💻 Author

**Aleksey Soroka**  
*Technical Narrative Designer | Master's of Social Psychology*  
📧 magpie1337@gmail.com

Built at the intersection of **game AI engineering** and **social psychology** — translating human cognitive models into computational architectures for autonomous game agents.

---

## 📄 License
MIT License — free for learning, prototyping, or commercial projects.