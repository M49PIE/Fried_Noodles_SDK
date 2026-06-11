# scripts/debug/tension_system/tension_system_debug.py
import matplotlib.pyplot as plt
import matplotlib
import logging

# ✅ Настраиваем темную тему
matplotlib.rcParams['axes.facecolor'] = '#1e1e1e'
matplotlib.rcParams['figure.facecolor'] = '#1e1e1e'
matplotlib.rcParams['text.color'] = '#ffffff'
matplotlib.rcParams['axes.labelcolor'] = '#ffffff'
matplotlib.rcParams['xtick.color'] = '#ffffff'
matplotlib.rcParams['ytick.color'] = '#ffffff'

logger = logging.getLogger(__name__)

class NeedsDebug:
    """Визуализация системы потребностей (Meat Balls)."""

    def __init__(self):
        self.fig, self.ax = plt.subplots(figsize=(6, 4))
        self.ax.set_xlim(0, 100)
        self.ax.set_ylim(0, 100)
        self.ax.axis('off')
        
        # Темный фон
        self.ax.set_facecolor('#1e1e1e')
        self.fig.patch.set_facecolor('#1e1e1e')
        
        logger.info("🔧 NeedsDebug initialized (Dark Theme)")

    def update(self, tick: int, energy: float, tension: float, quasi_need: str):
        self.ax.clear()
        self.ax.set_xlim(0, 100)
        self.ax.set_ylim(0, 100)
        self.ax.axis('off')
        
        # Темный фон
        self.ax.set_facecolor('#1e1e1e')
        self.fig.patch.set_facecolor('#1e1e1e')
        
        # Energy bar (зеленый)
        energy_width = energy * 80
        self.ax.add_patch(plt.Rectangle((10, 60), energy_width, 15, 
                                         facecolor='#4CAF50', alpha=0.8))
        self.ax.text(10, 67.5, "ENERGY", color='white', fontsize=10, fontweight='bold')
        
        # Tension bar (красный)
        tension_width = tension * 80
        self.ax.add_patch(plt.Rectangle((10, 35), tension_width, 15, 
                                         facecolor='#f44336', alpha=0.8))
        self.ax.text(10, 42.5, "TENSION", color='white', fontsize=10, fontweight='bold')
        
        # Quasi-need text
        need_text = quasi_need if quasi_need else "None"
        self.ax.text(50, 15, f"Need: {need_text}", color='white', 
                     fontsize=12, ha='center', fontweight='bold')
        
        # Tick counter
        self.ax.text(50, 85, f"Tick: {tick}", color='white', 
                     fontsize=14, ha='center', fontweight='bold')

    def close(self):
        plt.close(self.fig)