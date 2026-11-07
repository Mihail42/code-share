def createCycle():
    cycle = []
    size = get_world_size()
    half_size = size / 2
    for _ in range(size - 1):
        cycle.append(North)

    for _ in range(half_size - 1):
        cycle.append(East)
        for _ in range(half_size - 1):
            cycle.append(South)
        cycle.append(East)
        for _ in range(half_size - 1):
            cycle.append(North)
    cycle.append(East)
    for _ in range(size - 1):
        cycle.append(South)

    for _ in range(half_size - 1):
        cycle.append(West)
        for _ in range(half_size - 1):
            cycle.append(North)
        cycle.append(West)
        for _ in range(half_size - 1):
            cycle.append(South)
    cycle.append(West)
    return cycle


def useCycle():
    cycle = createCycle()
    while True:
        for m in cycle:
            move(m)
        if not can_move(North):
            clear()
            change_hat(Hats.Dinosaur_Hat)


set_world_size(32)
clear()
change_hat(Hats.Dinosaur_Hat)
useCycle()
