# 🧠 Psychological Foundations

This document explains the theoretical basis of the Fried Noodles SDK. The framework integrates three major psychological theories into a unified computational model of agent behavior.

---

## 📚 Core Theories

### 1. Field Theory (Kurt Lewin, 1930s-1940s)

The central framework. Lewin proposed that **behavior is a function of the person and their environment**:

**B = f(P, E)**

Key concepts implemented in this SDK:

| Concept | Definition | Implementation |
|---------|-----------|----------------|
| **Life Space** | The total psychological environment as perceived by the agent | `Noodles` block (Field Memory) |
| **Valence** | The attractive/repulsive value of an object | Stored in memory as float [-1.0, +1.0] |
| **Tension** | Psychological state arising from unmet needs | `Meat Balls` block (Needs System) |
| **Hodological Space** | "Path space" — distance measured by effort, not meters | `FieldMemory.get_hodological_distance()` |
| **Locomotion** | Movement through the life space toward/away from goals | `Ebi` block (Behavior System) |
| **Barrier** | Anything that阻s locomotion | Objects with negative valence |

**Why it matters for games:** Unlike simple state machines, Field Theory explains *why* an agent chooses a path — not just *which* path. An agent might take a longer route if the shorter one passes through a "scary" region (negative valence).

---

### 2. Operant Conditioning (B.F. Skinner, 1938)

The learning mechanism. Behavior is shaped by its consequences:

- **Reinforcement** → behavior becomes more likely
- **Punishment** → behavior becomes less likely

**Implementation in `Sauce` (Learning System):**

```python
# Success: valence grows toward +1.0 (asymptotic)
if outcome == "success":
    new_valence = current + lr * (1.0 - current)

# Failure: valence drops toward -1.0 (asymptotic)
elif outcome == "failure":
    new_valence = current - lr * (1.0 + current)

Law of Diminishing Returns: Each success increases valence less than the previous one. This prevents infinite growth and models realistic learning curves.
Vicarious Learning (Bandura): Planned for future — agents can learn by observing others' outcomes, not just their own.
3. Cognitive Maps (Edward Tolman, 1948)
Tolman showed that rats don't just follow stimulus-response patterns — they build mental maps of their environment.
Implementation in Noodles (Field Memory):
Agent stores objects with coordinates and valences
Even when an object is out of sight, agent remembers its location
Agent can navigate to remembered locations (not just visible ones)
This is what enables the "RecallApproach" action — the agent walks toward a food location it saw earlier but can no longer see.

Key Data Flows
Perception Loop: Plate → Garlic → Onion → Noodles
Raw world data gets filtered, interpreted, and stored in memory
Decision Loop: Noodles → Cheese → Ebi
Memory feeds thinking, which selects behavior
Learning Loop: Ebi → Sauce → Noodles/Plate
Behavior outcomes update valences in memory
Action Loop: Ebi → Plate
Behavior physically changes the world (eating food, moving)

Document version: 1.0
Last updated: June 2026
Author: Aleksey Soroka
