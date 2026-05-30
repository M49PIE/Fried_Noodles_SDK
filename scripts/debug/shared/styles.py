# scripts/debug/shared/styles.py

class DebugStyle:
    """Настройки тёмной темы для отладочных графиков."""
    
    # Основные цвета фона и текста
    BACKGROUND = '#1e1e1e'
    TEXT_COLOR = '#ffffff'
    GRID_COLOR = '#2c2c2c'
    AXIS_COLOR = '#ffffff'
    
    # Семантические цвета агента
    AGENT_BODY = '#2ecc71'    # Энергия/Агент
    AGENT_RADIUS = '#3498db'  # Радиус восприятия
    AGENT_FIELD = '#f39c12'   # Психологическое поле (будущее)
    
    # Цвета объектов (по умолчанию)
    OBJECT_COLORS = {
        "Food": '#f1c40f',    # Жёлтый
        "Rock": '#95a5a6',    # Серый
        "Tree": '#27ae60',    # Зелёный
        "Unknown": '#bdc3c7'
    }
    
    # Шрифты и размеры
    FONT_SIZE_TITLE = 14
    FONT_SIZE_LABEL = 10
    FONT_SIZE_TICK = 8
    LINE_WIDTH_OBJECT = 5
    LINE_WIDTH_RADIUS = 2