# scripts/world_model/collision.py
import math

def check_and_resolve_collisions(mover, colliders):
    """
    Проверяет и разрешает коллизии между двигающимся объектом и барьерами.
    """
    for collider in colliders:
        if not collider.active: continue
        
        # Простая проверка дистанции (Circle-Circle collision approximation)
        dx = mover.x - collider.x
        dy = mover.y - collider.y
        dist = math.sqrt(dx*dx + dy*dy)
        min_dist = mover.radius + collider.radius
        
        if dist < min_dist and dist > 0:
            # Вектор отталкивания
            overlap = min_dist - dist
            nx = dx / dist
            ny = dy / dist
            
            # Отодвигаем mover
            mover.x += nx * overlap
            mover.y += ny * overlap

def apply_border_constraints(entity, arena_size):
    """
    Не дает объекту выйти за пределы арены (0 - arena_size).
    """
    entity.x = max(entity.radius, min(arena_size - entity.radius, entity.x))
    entity.y = max(entity.radius, min(arena_size - entity.radius, entity.y))