# scripts/world_model/icon_loader.py
import logging
from pathlib import Path
from PIL import Image

logger = logging.getLogger(__name__)

class IconLoader:
    def __init__(self, icon_dir: str = None):
        if icon_dir is None:
            # По умолчанию ищем папку icons рядом с этим файлом
            self.icon_dir = Path(__file__).parent / "icons"
        else:
            self.icon_dir = Path(icon_dir)
            
        self.cache = {}
        self._load_icons()
        logger.info(f"🖼️ IconLoader initialized from {self.icon_dir}")

    def _load_icons(self):
        if not self.icon_dir.exists():
            logger.warning(f"Icon directory not found: {self.icon_dir}")
            return

        # Ищем все PNG файлы
        for file_path in self.icon_dir.glob("*.png"):
            name = file_path.stem  # Имя файла без расширения (напр. "Food")
            try:
                # Загружаем иконку
                img = Image.open(file_path)
                self.cache[name] = img
                logger.debug(f"✅ Loaded icon: {name}")
            except Exception as e:
                logger.error(f"❌ Failed to load icon {name}: {e}")
    
    def get_icon(self, name: str):
        return self.cache.get(name)

    def has_icon(self, name: str):
        return name in self.cache