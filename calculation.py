from numba import njit

@njit(fastmath=True)
def is_player_near_block(px, py, bx, by, reach):
    dx = px - bx
    dy = py - by
    return (dx * dx + dy * dy) <= (reach * reach)

@njit(fastmath=True)
def smoothstep(t):
    return t * t * (3 - 2 * t)