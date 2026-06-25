# scripts/world_model/collision.py
import logging

logger = logging.getLogger(__name__)

def check_and_resolve_collisions(entity, obstacles):
    """
    Проверяет коллизии сущности (круг) со списком препятствий (AABB - прямоугольники).
    Возвращает True, если столкновение произошло, и корректирует позицию.
    """
    collided = False
    
    for obstacle in obstacles:
        if not obstacle.active or obstacle == entity:
            continue
            
        # 1. Определение AABB (Axis-Aligned Bounding Box) для препятствия
        # Form "1x4" означает x=1, y=4. Центр препятствия в (obs.x, obs.y)
        ox, oy = obstacle.x, obstacle.y
        fw, fh = 1.0, 1.0 # Базовый размер, будем менять динамически
        
        # Парсим Form (например "1x4")
        if "x" in obstacle.form:
            try:
                dims = obstacle.form.split('x')
                fw, fh = float(dims[0]), float(dims[1])
            except: pass

        # Координаты углов прямоугольника
        min_x = ox - (fw / 2)
        max_x = ox + (fw / 2)
        min_y = oy - (fh / 2)
        max_y = oy + (fh / 2)

        # 2. Находим ближайшую точку прямоугольника к центру круга (агента)
        closest_x = max(min_x, min(entity.x, max_x))
        closest_y = max(min_y, min(entity.y, max_y))

        # 3. Вычисляем вектор до этой точки
        dist_x = entity.x - closest_x
        dist_y = entity.y - closest_y
        distance_sq = (dist_x * dist_x) + (dist_y * dist_y)

        # 4. Проверка коллизии (радиус сущности)
        radius = getattr(entity, 'radius', 0.5)
        if distance_sq < (radius * radius):
            collided = True
            
            # Если расстояние 0 (центр внутри), выталкиваем вверх
            distance = 0.0 if distance_sq == 0 else distance_sq ** 0.5
            
            overlap = radius - distance
            
            # Направление выталкивания
            if distance == 0:
                nx, ny = 1.0, 0.0 # Fallback
            else:
                nx = dist_x / distance
                ny = dist_y / distance
            
            # Применяем выталкивание
            entity.x += nx * overlap
            entity.y += ny * overlap
            
            # logger.debug(f"Collision resolved: {entity.name} vs {obstacle.name}")
            
    return collided

def apply_border_constraints(entity, arena_size):
    """Жесткие границы арены: если вышел за край — возвращаем."""
    radius = getattr(entity, 'radius', 0.5)
    
    if entity.x - radius < 0:
        entity.x = radius
    elif entity.x + radius > arena_size:
        entity.x = arena_size - radius
        
    if entity.y - radius < 0:
        entity.y = radius
    elif entity.y + radius > arena_size:
        entity.y = arena_size - radius