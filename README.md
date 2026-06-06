# 🍜 Fried Noodles SDK

**AI-driven Game Agent Framework** based on Kurt Lewin's Field Theory and operant conditioning.

A Python implementation of an autonomous game agent that learns from experience, adapts to environment, and makes decisions based on psychological needs and valence-based memory.

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

---

## 🎯 Overview

Fried Noodles is not just another AI agent—it's a **psychologically-grounded framework** for creating game NPCs that:
- Learn from successes and failures (operant conditioning)
- Navigate using hodological space (psychological distance, not just physical)
- Avoid previously harmful objects based on experience
- Maintain homeostasis through need-driven behavior

**Perfect for:** Game designers prototyping AI behaviors, researchers studying computational psychology, developers building adaptive NPCs.

---

##  Core Concepts

### Psychological Foundations
- **Field Theory (Kurt Lewin):** Behavior = f(Person, Environment)
- **Valence:** Objects have positive/negative psychological value
- **Tension:** Drives quasi-needs when homeostasis is disrupted
- **Hodological Space:** Navigation based on psychological effort, not just Euclidean distance

### Learning System
The agent uses **operant conditioning**:
- ✅ **Success** (eating food) → valence increases → behavior reinforced
- ❌ **Failure** (investigating rocks) → valence decreases → behavior avoided

---

## 🏗️ Architecture

Fried_Noodles_SDK/
── scripts/
│ ├── core/
│ │ └── agent.py # Main agent loop
│ ├── world_model/ # Block 1: Environment
│ ├── tension_system/ # Block 2: Needs & Homeostasis
│ ├── sensation_input/ # Block 3: Stimulus Filtering
│ ├── perception_filter/ # Block 4: Interpretation & Attention
│ ├── memory_field/ # Block 5: Hodological Memory
│ ├── decision_engine/ # Block 6: Utility AI + Behavior Tree
│ ├── action_executor/ # Block 7: Physical Actions
│ ├── locutionary_output/ # Block 8: Speech Generation (WIP)
│ ├── valence_update/ # Block 9: Operant Conditioning
│ └── debug/
│ ├── world_model/
│ ├── tension_system/
│ └── shared/
├── configs/
│ └── agent_profile.json # Agent configuration
├── docs/
│ ├── architecture.md # Technical documentation
│ └── field_theory.md # Psychological foundations
├── README.md
└── requirements.txt

---

## 🚀 Quick Start

### Requirements
- Python 3.11+
- Matplotlib
- NumPy

### Install
```bash
git clone https://github.com/M49PIE/Fried_Noodles_SDK.git
cd Fried_Noodles_SDK
pip install matplotlib numpy

Run Demo
python -m scripts.core.agent

You'll see two windows:
Environment Visualization — agent (green), objects (yellow=food, gray=rocks), perception radius (blue circle)
Needs Monitor — energy (green bar) and tension (red bar) in real-time

📊 What You'll See
The agent will:
Wander when energy is high
Seek food when tension exceeds threshold (0.10)
Learn that food is good (valence → +0.3)
Investigate unknown objects (like rocks)
Avoid rocks after negative experience (valence → -0.3)
Survive by dynamically balancing needs and exploration
Demo Duration: 400 ticks (~2-3 minutes)

🎮 Configuration

Edit configs/agent_profile.json to customize:
{
  "agent_id": "agent_001",
  "homeostasis": {
    "energy": {
      "initial": 1.0,
      "decay_rate": 0.01,
      "tension_threshold": 0.10,
      "restore_amount": 0.3
    }
  },
  "innate_priors": {
    "Food": 0.0,
    "Rock": 0.0
  }
}

Key Parameters:
decay_rate: Energy loss per tick
tension_threshold: When to start seeking food (0.10 = 10% energy loss)
restore_amount: Energy gained from eating

📚 Documentation
architecture.md — Detailed block descriptions and API
field_theory.md — Theoretical foundations (Lewin, Skinner, Tolman)

👨‍💻 Author
Aleksey Soroka
Technical Narrative Designer | Master's of Social Psychology
📧 magpie1337@gmail.com

License
MIT License — feel free to use for learning, prototyping, or commercial projects.

