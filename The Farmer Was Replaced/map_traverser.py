map_size = get_world_size()
movementMapSimple = []
movementMapZigZag = []


def empty():
    pass


def createMovementMaps():
    # simple movement
    for _ in range(map_size):
        for _ in range(map_size - 1):
            movementMapSimple.append(North)
        movementMapSimple.append(East)

    # zig-zag movement
    for i in range(2):
        for col in range(map_size):
            if col % 2 == 0:
                for _ in range(map_size - 1):
                    movementMapZigZag.append(North)
            else:
                for _ in range(map_size - 1):
                    movementMapZigZag.append(South)
            if col < map_size - 1:
                if i == 0:
                    movementMapZigZag.append(East)
                else:
                    movementMapZigZag.append(West)


def simpleTraverse(action=None):
    for step in movementMapSimple:
        action()
        move(step)


def zigZagTraverse(action):
    for step in movementMapZigZag:
        action()
        move(step)


def goTo(tx_or_vector, ty=None):
    if ty == None:
        tx = tx_or_vector[0]
        ty = tx_or_vector[1]
    else:
        tx = tx_or_vector
    s = get_world_size()
    dx = (tx - get_pos_x()) % s
    dy = (ty - get_pos_y()) % s

    if dx > s // 2:
        dx -= s
    if dy > s // 2:
        dy -= s

    for _ in range(max(dx, 0)):
        move(East)
    for _ in range(max(-dx, 0)):
        move(West)
    for _ in range(max(dy, 0)):
        move(North)
    for _ in range(max(-dy, 0)):
        move(South)


def getPos():
    return (get_pos_x(), get_pos_y())


createMovementMaps()
