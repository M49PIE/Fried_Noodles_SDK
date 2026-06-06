# ️ Architecture Documentation

Technical overview of the Fried Noodles SDK architecture.

---

## System Overview

The agent follows a **cognitive pipeline** inspired by human perception-decision-action loops:

Perception → Interpretation → Decision → Action → Learning → Memory Update


Each block is **independent** and communicates through well-defined interfaces (Python dicts).

---

## Block Details

### 1. World_Model (Environment)
**File:** `scripts/world_model/world_model.py`

**Responsibility:** Stores the 2D world state — objects with coordinates, types, and consumption flags.

**Key Methods:**
- `add_object(type, x, y, base_valence)` — spawns an object
- `get_nearby_objects(agent_x, agent_y, max_distance)` — returns objects within range, filtering out consumed ones

**Design Notes:**
- Objects have a `consumed` flag to prevent re-eating
- Distance is calculated dynamically using Euclidean formula
- Arena bounds: 0-20 on both axes

---

### 2. Tension_System (Needs)
**File:** `scripts/tension_system/tension_system.py`

**Responsibility:** Maintains homeostasis, calculates tension, generates quasi-needs.

**Key Methods:**
- `calculate_tension(energy)` → `1.0 - energy`
- `get_quasi_need(tension)` → returns `"SeekFood"` if tension > threshold

**Design Notes:**
- Threshold is configurable (default: 0.10)
- Tension is a simple inverse of energy — can be extended to multi-dimensional needs later

---

### 3. Sensation_Input (Sensation)
**File:** `scripts/sensation_input/sensation_input.py`

**Responsibility:** Filters raw environment data by perception radius.

**Key Methods:**
- `filter_stimuli(objects)` → returns only objects within `perception_radius`

**Design Notes:**
- Intensity decays linearly with distance
- Acts as a "sensory filter" — agent literally cannot perceive what's too far

---

### 4. Perception_Filter (Perception)
**File:** `scripts/perception_filter/perception_filter.py`

**Responsibility:** Interprets stimuli, applies need-driven attention, calculates valence and salience.

**Key Methods:**
- `interpret_stimuli(stimuli, state, memory_valences)` → returns perceived objects with valence

**Design Notes:**
- **Critical feature:** Uses memory valences if object was previously experienced
- Attention boost scales with tension (hungry agent notices food more)
- Dynamic threshold filters out low-salience stimuli

---

### 5. Memory_Field (Field Memory)
**File:** `scripts/memory_field/memory_field.py`

**Responsibility:** Stores long-term memory of objects with their valences.

**Key Methods:**
- `perceive_object(type, x, y, valence, salience)` — creates or updates memory
- `get_nearest_object_by_type(type)` — finds closest remembered object
- `get_hodological_distance(x, y)` — psychological distance (currently Euclidean, extensible)

**Design Notes:**
- Memory keys: `{type}_{x}_{y}` (simple spatial indexing)
- Implements **hodological space** concept from Lewin's Field Theory
- Future: can be replaced with vector DB (ChromaDB) for ML integration

---

### 6. Decision_Engine (Thinking)
**File:** `scripts/decision_engine/decision_engine.py`

**Responsibility:** Hybrid Utility AI + Behavior Tree for decision-making.

**Key Methods:**
- `select_action(context, memory_valences)` → returns `ActionCandidate` with highest utility

**Architecture:**

Root (Selector)
├── Survival (Sequence)
│ ├── Condition: IsHungry (tension > 0.5)
│ └── Action: ApproachFood (utility = tension * food_valence)
├── Explore (Sequence)
│ ├── Condition: SeesUnknown
│ ├── Condition: ValenceOK (valence >= -0.1)
│ └── Action: Investigate (utility = 0.3 * curiosity)
└── Wander (Action)
└── utility = 0.1 (fallback)


**Design Notes:**
- Filters out objects with negative valence (learned avoidance)
- Prioritizes survival over exploration
- Extensible: can add custom actions dynamically

---

### 7. Action_Executor (Behavior)
**File:** `scripts/action_executor/action_executor.py`

**Responsibility:** Legacy behavior system (fallback). Currently minimal — main logic moved to Decision_Engine.

**Design Notes:**
- Kept for backward compatibility
- Future: will handle low-level action execution (animation triggers, sound effects)

---

### 8. Locutionary_Output (Speech) — *WIP*
**File:** `scripts/locutionary_output/` (empty)

**Planned Responsibility:** Generate speech/utterances based on agent's internal state.

**Planned Features:**
- Verbalize intentions ("I'm going to eat")
- Dialogue generation with other NPCs
- Emotional expression based on tension/valence

---

### 9. Valence_Update (Learning)
**File:** `scripts/valence_update/valence_update.py`

**Responsibility:** Updates valences based on interaction outcomes using operant conditioning.

**Key Methods:**
- `update_valence(current, outcome, type)` → returns new valence
- `log_event(...)` — records learning events for analysis
- `get_learning_summary()` — returns statistics

**Learning Rules:**
- **Success:** `valence += lr * (1.0 - valence)` → asymptotic growth to +1.0
- **Failure:** `valence -= lr * (1.0 + valence)` → asymptotic drop to -1.0
- **Neutral:** `valence *= 0.95` → soft decay to 0.0

**Design Notes:**
- Learning rate: 0.3 (configurable)
- Law of diminishing returns built into formula
- Events are logged with timestamps for future ML training

---

## Data Flow

┌─────────────┐
│ World_Model │ (Environment)
──────┬──────┘
│ raw objects
▼
┌─────────────┐
│Sensation_Inp│ (Garlic) — filters by radius
──────┬──────┘
│ stimuli
▼
┌─────────────┐
│Percept_Filter│ (Onion) — applies attention, memory
└──────┬──────┘
│ perceived objects
▼
┌─────────────┐ ┌─────────────┐
│ Memory_Field│◄────│Valence_Update│ (Sauce)
│ (Noodles) │ └─────────────┘
└──────┬────── ▲
│ │
│ hodological │ updates valences
│ space │
▼ │
┌─────────────┐ │
│Decision_Eng │ (Cheese) ──┘
│ (Thinking) │
└────┬────────┘
│ best action
▼
┌─────────────┐
│Action_Exec │ (Ebi) — executes movement
└─────────────┘


---

## Configuration Schema

See `configs/agent_profile.json` for full example.

```json
{
  "agent_id": "string",
  "homeostasis": {
    "energy": {
      "initial": "float (0-1)",
      "decay_rate": "float per tick",
      "tension_threshold": "float (0-1)",
      "restore_amount": "float per consumption"
    }
  },
  "innate_priors": {
    "ObjectType": "float (-1 to 1)"
  }
}

Extension Points
Adding New Object Types
Add to innate_priors in config
Add handling in _try_interact() in agent.py
Add color to DebugStyle.OBJECT_COLORS
Adding New Needs
Extend Tension_System with new dimension (e.g., thirst)
Add corresponding quasi-need
Add consumption logic in _try_interact()
Integrating ML
Replace Memory_Field with vector DB
Use Valence_Update.export_weights() for model training
Load trained model via Valence_Update.import_weights()
Performance
Tick rate: ~100 ticks/second (without visualization)
Memory: O(n) where n = number of objects in world
Scalability: Tested with 50+ objects, 400+ ticks

