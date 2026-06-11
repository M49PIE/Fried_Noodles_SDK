# scripts/debug/world_model/world_model_debug.py
import matplotlib.pyplot as plt
import matplotlib
import logging
import numpy as np

from scripts.world_model.icon_loader import IconLoader

# ✅ Настройка темной темы
matplotlib.rcParams['axes.facecolor'] = '#1e1e1e'
matplotlib.rcParams['figure.facecolor'] = '#1e1e1e'
matplotlib.rcParams['text.color'] = '#ffffff'
matplotlib.rcParams['axes.labelcolor'] = '#ffffff'
matplotlib.rcParams['xtick.color'] = '#ffffff'
matplotlib.rcParams['ytick.color'] = '#ffffff'
matplotlib.rcParams['grid.color'] = '#404040'
matplotlib.rcParams['font.size'] = 10

logger = logging.getLogger(__name__)

class EnvironmentDebug:
    def __init__(self, innate_objects: dict = None, icon_dir: str = None):
        self.fig, self.ax = plt.subplots(figsize=(8, 8))
        self.ax.set_xlim(0, 20)
        self.ax.set_ylim(0, 20)
        self.ax.set_title("🍽️ World Model (Plate) Visualization", color='white', fontsize=12, fontweight='bold')
        self.ax.grid(True, linestyle='--', alpha=0.5, color='#404040')
        
        # Инициализируем загрузчик иконок
        self.icon_loader = IconLoader(icon_dir=icon_dir)
        
        logger.info("🔍 EnvironmentDebug initialized (PNG Icon Rendering - Dark Theme)")

    def update(self, objects: list, agent_pos: tuple):
        self.ax.clear()
        self.ax.set_xlim(0, 20)
        self.ax.set_ylim(0, 20)
        self.ax.grid(True, linestyle='--', alpha=0.5, color='#404040')
        self.ax.set_title("🍽️ World Model (Plate) Visualization", color='white', fontsize=12, fontweight='bold')
        self.ax.set_xlabel("X", color='white')
        self.ax.set_ylabel("Y", color='white')
        
        # Темный фон
        self.ax.set_facecolor('#1e1e1e')
        self.fig.patch.set_facecolor('#1e1e1e')

        # 1. Отрисовка Агента (отдельно, так как он не в списке объектов)
        agent_icon = self.icon_loader.get_icon("Agent")
        if agent_icon:
            self._draw_image(self.ax, agent_pos[0], agent_pos[1], agent_icon, scale=0.6)
        else:
            # Fallback: если иконки нет, рисуем текст
            self.ax.text(agent_pos[0], agent_pos[1], "👽", ha='center', va='center', fontsize=20, color='white')

        # 2. Отрисовка объектов мира
        for obj in objects:
            if obj.get("consumed"):
                continue

            obj_type = obj.get("type")
            icon = self.icon_loader.get_icon(obj_type)
            
            if icon:
                # Рисуем картинку
                self._draw_image(self.ax, obj["x"], obj["y"], icon, scale=0.5)
            else:
                # Fallback для неизвестных объектов
                self.ax.text(obj["x"], obj["y"], "?", ha='center', va='center', fontsize=20, color='gray')

    def _draw_image(self, ax, x, y, image, scale=0.5):
        """Вспомогательный метод для отрисовки PIL изображения на графике"""
        # extent задает границы: [x-left, x-right, y-bottom, y-top]
        extent = [x - scale, x + scale, y - scale, y + scale]
        ax.imshow(image, aspect='auto', extent=extent)

    def close(self):
        plt.close(self.fig)