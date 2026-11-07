from map_traverser import goTo

set_world_size(8)
map_size = get_world_size()
clear()


def harvestForIterations(count=10):
    for _ in range(count):
        pass


def harvestUntilItemCountAbove(threshold=100000):
    while num_items(Items.Hay) <= threshold:
        pass


def harvestAlways():
    prepareMap()

    while True:
        for _ in range(map_size):
            sortLine("horizontal")
            goTo(0, get_pos_y() + 1)

        for _ in range(map_size):
            sortLine("vertical")
            goTo(get_pos_x() + 1, 0)

        harvest()
        prepareMap()


def sortLine(direction):
    if direction == "horizontal":
        forward = East
        backward = West
        position = get_pos_x
    else:
        forward = North
        backward = South
        position = get_pos_y

    low = 1
    high = map_size - 2
    forward_pass = True

    while low < high:
        swapped = False

        if forward_pass:
            while position() < high:
                move(forward)
                swapped = sortTripleInDirection(direction) or swapped

            high -= 1

        else:
            while position() > low:
                move(backward)
                swapped = sortTripleInDirection(direction) or swapped

            low += 1

        if not swapped:
            return

        forward_pass = not forward_pass


def sortTripleInDirection(direction):
    if direction == "horizontal":
        backward = West
        forward = East
    else:
        backward = South
        forward = North

    previous = measure(backward)
    current = measure()
    next = measure(forward)

    if previous > current:
        swap(backward)
        return True

    if current > next:
        swap(forward)
        return True

    return False


def sortWithPrevious(direction):
    current = measure()
    previous = measure(direction)

    if previous > current:
        swap(direction)


def prepareMap():
    for i in range(map_size):
        for j in range(map_size):
            if get_ground_type() != Grounds.Soil:
                till()

            plant(Entities.Cactus)

            if j != 0:
                sortWithPrevious(South)

            if i != 0:
                sortWithPrevious(West)

            move(North)

        move(East)


harvestAlways()
