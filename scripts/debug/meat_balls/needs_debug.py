# scripts/debug/meat_balls/needs_debug.py
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from scripts.debug.shared.styles import DebugStyle

class NeedsDebug:
    """
    Упрощенная визуализация: только две полоски (Energy и Tension).
    """
    def __init__(self):
        # Небольшое окно для двух баров
        self.fig, self.ax = plt.subplots(figsize=(5, 3))
        self.fig.set_facecolor(DebugStyle.BACKGROUND)
        self.ax.set_facecolor(DebugStyle.BACKGROUND)

        # Скрываем оси, тики и рамки для чистоты
        self.ax.axis('off')
        self.ax.set_xlim(0, 1)
        self.ax.set_ylim(0, 1)

        # --- ENERGY BAR (Верхняя полоска, Зеленая) ---
        self.ax.text(0.05, 0.65, "ENERGY", color='white', ha='left', va='center', fontweight='bold')
        self.energy_bar = patches.Rectangle((0.05, 0.55), 0, 0.15, facecolor=DebugStyle.AGENT_BODY)
        self.ax.add_patch(self.energy_bar)

        # --- TENSION BAR (Нижняя полоска, Красная) ---
        self.ax.text(0.05, 0.35, "TENSION", color='white', ha='left', va='center', fontweight='bold')
        self.tension_bar = patches.Rectangle((0.05, 0.25), 0, 0.15, facecolor='#e74c3c')
        self.ax.add_patch(self.tension_bar)

    def update(self, tick, energy, tension, quasi_need):
        """Обновляет ширину полосок (игнорирует tick и quasi_need)."""
        # Максимальная ширина 0.85 (чтобы был отступ справа)
        self.energy_bar.set_width(energy * 0.85)
        self.tension_bar.set_width(tension * 0.85)