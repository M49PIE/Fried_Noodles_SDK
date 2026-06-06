# scripts/debug/plate/environment_debug.py
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from scripts.debug.shared.styles import DebugStyle

class EnvironmentDebug:
    """Визуализация блока Plate: Карта объектов и радиус восприятия."""

    def __init__(self, arena_size: int = 20):
        self.arena_size = arena_size
        
        # Создаём фигуру и оси
        self.fig, self.ax = plt.subplots(figsize=(8, 8))
        self.fig.set_facecolor(DebugStyle.BACKGROUND)
        self.ax.set_facecolor(DebugStyle.BACKGROUND)
        
        # Настройка внешнего вида
        self.ax.set_title("Plate Environment Visualization", color=DebugStyle.TEXT_COLOR)
        self.ax.set_xlabel("X Position", color=DebugStyle.TEXT_COLOR)
        self.ax.set_ylabel("Y Position", color=DebugStyle.TEXT_COLOR)
        self.ax.set_xlim(0, self.arena_size)
        self.ax.set_ylim(0, self.arena_size)
        self.ax.grid(True, color=DebugStyle.GRID_COLOR, alpha=0.3)
        
        # Элементы графика (будут обновляться)
        self.scatter_objects = None
        self.agent_circle = None
        self.radius_circle = None
        
        # Начальное положение агента (в центре)
        self.agent_pos = (self.arena_size / 2, self.arena_size / 2)
        self.perception_radius = 5.0

    def update(self, objects: list, agent_pos: tuple = (10.0, 10.0)):
        """
        Обновляет визуализацию новыми данными.
        objects: список словарей {'type': str, 'x': float, 'y': float, 'distance': float}
        agent_pos: кортеж (x, y) - текущая позиция агента
        """
        # 1. Отрисовка объектов
        if objects:
            x_coords = [obj['x'] for obj in objects]
            y_coords = [obj['y'] for obj in objects]
            obj_types = [obj['type'] for obj in objects]
            
            # Цвета для разных типов объектов
            colors = [DebugStyle.OBJECT_COLORS.get(t, DebugStyle.OBJECT_COLORS['Unknown']) for t in obj_types]
            
            # Удаляем старые точки и рисуем новые
            if self.scatter_objects:
                self.scatter_objects.remove()
            
            self.scatter_objects = self.ax.scatter(x_coords, y_coords, c=colors, s=100, marker='s', label='Objects')
        
        # 2. Отрисовка агента (точка в центре или в новой позиции)
        if self.agent_circle:
            self.agent_circle.remove()
        self.agent_circle = self.ax.scatter(
            [agent_pos[0]], [agent_pos[1]], 
            c=DebugStyle.AGENT_BODY, s=150, zorder=5, label='Agent'
        )
        
        # 3. Отрисовка радиуса восприятия (теперь вокруг новой позиции)
        if self.radius_circle:
            self.radius_circle.remove()
        self.radius_circle = patches.Circle(
            agent_pos, self.perception_radius, 
            fill=False, edgecolor=DebugStyle.AGENT_RADIUS, 
            linewidth=DebugStyle.LINE_WIDTH_RADIUS, linestyle='--'
        )
        self.ax.add_patch(self.radius_circle)
        
        # Обновляем легенду (чистим дубликаты)
        handles, labels = self.ax.get_legend_handles_labels()
        if labels:
            by_label = dict(zip(labels, handles))
            self.ax.legend(by_label.values(), by_label.keys(), loc='upper right', facecolor=DebugStyle.BACKGROUND, edgecolor='white', labelcolor='white')

    def show(self):
        """Запускает окно."""
        self.fig.tight_layout()
        plt.show()