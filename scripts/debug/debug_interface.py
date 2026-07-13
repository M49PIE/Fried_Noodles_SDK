# scripts/debug/debug_interface.py
import matplotlib.pyplot as plt
import matplotlib
import logging

# ✅ Темная тема для всего интерфейса
matplotlib.rcParams['axes.facecolor'] = '#1e1e1e'
matplotlib.rcParams['figure.facecolor'] = '#1e1e1e'
matplotlib.rcParams['text.color'] = '#ffffff'
matplotlib.rcParams['axes.labelcolor'] = '#ffffff'
matplotlib.rcParams['xtick.color'] = '#ffffff'
matplotlib.rcParams['ytick.color'] = '#ffffff'

logger = logging.getLogger(__name__)

class UnifiedDebug:
    """
    Объединённый дебаг-интерфейс: Needs (сверху) + Psychological Field (снизу).
    """
    def __init__(self):
        # Вертикальное расположение: Needs (40%) + Field (60%)
        self.fig, (self.ax_needs, self.ax_field) = plt.subplots(
            2, 1, 
            figsize=(6, 10), 
            gridspec_kw={'height_ratios': [4, 6]},
            constrained_layout=True
        )
        
        # Настройка окна
        self.fig.suptitle("🔧 Fried Noodles Debug Interface", color='white', fontsize=14, fontweight='bold')
        self.fig.patch.set_facecolor('#1e1e1e')
        
        # === Настройка Needs (верхняя панель) ===
        self.ax_needs.set_xlim(0, 100)
        self.ax_needs.set_ylim(0, 100)
        self.ax_needs.axis('off')
        self.ax_needs.set_facecolor('#1e1e1e')
        
        # === Настройка Field (нижняя панель) ===
        self.ax_field.set_xlim(0, 20)
        self.ax_field.set_ylim(0, 20)
        self.ax_field.set_aspect('equal')
        self.ax_field.set_facecolor('#121212')
        self.ax_field.grid(True, linestyle='--', alpha=0.3)
        self.ax_field.set_xlabel("X", color='white')
        self.ax_field.set_ylabel("Y", color='white')
        self.ax_field.set_title("🧠 Psychological Field (Cognitive Map)", color='white', fontsize=10)
        
        plt.ion()
        logger.info("🔧 UnifiedDebug initialized (Dark Theme, Needs+Field)")

    def update(self, tick: int, energy: float, tension: float, quasi_need: str, 
               field_objects: list, agent_pos: tuple):
        """Обновление обоих панелей за один вызов."""
        
        # === Обновление Needs (верх) ===
        self.ax_needs.clear()
        self.ax_needs.set_xlim(0, 100)
        self.ax_needs.set_ylim(0, 100)
        self.ax_needs.axis('off')
        self.ax_needs.set_facecolor('#1e1e1e')
        
        # Energy bar (зеленый)
        energy_width = energy * 80
        self.ax_needs.add_patch(plt.Rectangle((10, 60), energy_width, 15, 
                                               facecolor='#4CAF50', alpha=0.8, edgecolor='white'))
        self.ax_needs.text(10, 67.5, "ENERGY", color='white', fontsize=10, fontweight='bold')
        
        # Tension bar (красный)
        tension_width = tension * 80
        self.ax_needs.add_patch(plt.Rectangle((10, 35), tension_width, 15, 
                                               facecolor='#f44336', alpha=0.8, edgecolor='white'))
        self.ax_needs.text(10, 42.5, "TENSION", color='white', fontsize=10, fontweight='bold')
        
        # Quasi-need text
        need_text = quasi_need if quasi_need else "None"
        self.ax_needs.text(50, 15, f"Need: {need_text}", color='white', 
                           fontsize=12, ha='center', fontweight='bold')
        
        # Tick counter
        self.ax_needs.text(50, 85, f"Tick: {tick}", color='white', 
                           fontsize=14, ha='center', fontweight='bold')
        
        # === Обновление Field (низ) ===
        self.ax_field.clear()
        self.ax_field.set_xlim(0, 20)
        self.ax_field.set_ylim(0, 20)
        self.ax_field.set_aspect('equal')
        self.ax_field.set_facecolor('#121212')
        self.ax_field.grid(True, linestyle='--', alpha=0.3)
        self.ax_field.set_xlabel("X", color='white')
        self.ax_field.set_ylabel("Y", color='white')
        self.ax_field.set_title("🧠 Psychological Field (Cognitive Map)", color='white', fontsize=10)
        
        # Агент
        self.ax_field.plot(agent_pos[0], agent_pos[1], 'bo', markersize=12, label='Agent')
        
        # Объекты в поле
        if field_objects:
            xs = [o['x'] for o in field_objects]
            ys = [o['y'] for o in field_objects]
            colors = ['#4CAF50' if o['type'] == 'Apple' else '#9E9E9E' for o in field_objects]
            self.ax_field.scatter(xs, ys, c=colors, s=60, alpha=0.85, 
                                  edgecolors='white', linewidth=0.5, label='Objects')
        
        self.ax_field.legend(loc='upper right', fontsize=8)
        
        # Отрисовка
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()
        plt.pause(0.01)

    def close(self):
        plt.close(self.fig)
        logger.info("🔧 UnifiedDebug closed")