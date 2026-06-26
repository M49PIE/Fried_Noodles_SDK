# scripts/debug/memory_field/field_debug.py
import matplotlib.pyplot as plt
import logging

logger = logging.getLogger(__name__)

class FieldDebug:
    def __init__(self):
        self.fig, self.ax = plt.subplots(figsize=(6, 6))
        self.ax.set_title("🧠 Psychological Field (Cognitive Map)")
        self.ax.set_xlim(0, 20)
        self.ax.set_ylim(0, 20)
        self.ax.set_aspect('equal')
        self.ax.set_facecolor('#121212')
        self.ax.grid(True, linestyle='--', alpha=0.3)
        plt.ion()
        logger.info("👁️ FieldDebug initialized")

    def update(self, field_objects: list, agent_pos: tuple) -> None:
        self.ax.clear()
        self.ax.set_title("🧠 Psychological Field (Cognitive Map)")
        self.ax.set_xlim(0, 20)
        self.ax.set_ylim(0, 20)
        self.ax.set_aspect('equal')
        self.ax.set_facecolor('#121212')
        self.ax.grid(True, linestyle='--', alpha=0.3)
        self.ax.set_xlabel("X")
        self.ax.set_ylabel("Y")

        # Агент
        self.ax.plot(agent_pos[0], agent_pos[1], 'bo', markersize=12, label='Agent')

        if field_objects:
            xs = [o['x'] for o in field_objects]
            ys = [o['y'] for o in field_objects]
            
            # Цвет по типу объекта: Apple=зелёный, Rock=серый
            colors = ['#4CAF50' if o['type'] == 'Apple' else '#9E9E9E' for o in field_objects]
            
            self.ax.scatter(xs, ys, c=colors, s=60, alpha=0.85, edgecolors='white', linewidth=0.5)

        self.ax.legend(loc='upper right')
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()
        plt.pause(0.01)