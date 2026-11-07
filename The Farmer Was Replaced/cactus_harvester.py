from map_traverser import goTo

# clear()

map_size = get_world_size()


def harvestForIterations(count=10):
    for _ in range(count):
        pass
    pass


def harvestUntilItemCountAbove(threshold=100000):
    while num_items(Items.Hay) <= threshold:
        pass
    pass


def harvestAlways():
    prepareMap()
    while True:
        for _ in range(get_world_size()):
            sortLine("horizontal")
            goTo(0, get_pos_y() + 1)
        for _ in range(get_world_size()):
            sortLine("vertical")
            goTo(get_pos_x() + 1, 0)
        harvest()
        prepareMap()


def sortLine(direction):
    if direction == "horizontal":
        downIdx = 1
        upIdx = map_size - 2
        dir = 1
        swapped = True
        while downIdx < upIdx:
            swapped = False
            if dir == 1:
                while get_pos_x() < upIdx:
                    move(East)
                    swapped = sortTripleInDirection(direction) or swapped
                upIdx -= 1
            else:
                while get_pos_x() > downIdx:
                    move(West)
                    swapped = sortTripleInDirection(direction) or swapped
                downIdx += 1
            if not swapped:
                return
            dir *= -1
    else:
        downIdx = 1
        upIdx = map_size - 2
        dir = 1
        swapped = True
        while downIdx < upIdx:
            swapped = False
            if dir == 1:
                while get_pos_y() < upIdx:
                    move(North)
                    swapped = sortTripleInDirection(direction) or swapped
                upIdx -= 1
            else:
                while get_pos_y() > downIdx:
                    move(South)
                    swapped = sortTripleInDirection(direction) or swapped
                downIdx += 1
            if not swapped:
                return
            dir *= -1


def measureTriple(direction):
    if direction == "horizontal":
        return (measure(West), measure(), measure(East))
    else:
        return (measure(South), measure(), measure(North))


def sortTripleInDirection(direction):
    if direction == "horizontal":
        prev, curr, next = measureTriple("horizontal")
        madeSwap = False
        while not (prev <= curr and curr <= next):
            if prev < curr:
                swap(East)
                madeSwap = True
            elif prev > curr:
                swap(West)
                madeSwap = True
            elif prev > next:
                swap(East)
                madeSwap = True
            prev, curr, next = measureTriple("horizontal")
        return madeSwap
    else:
        prev, curr, next = measureTriple("vertical")
        madeSwap = False
        while not (prev <= curr and curr <= next):
            if prev < curr:
                swap(North)
                madeSwap = True
            elif prev > curr:
                swap(South)
                madeSwap = True
            elif prev > next:
                swap(North)
                madeSwap = True
            prev, curr, next = measureTriple("vertical")
        return madeSwap


def prepareMap():
    for i in range(map_size):
        for j in range(map_size):
            if get_ground_type() != Grounds.Soil:
                till()
            plant(Entities.Cactus)
            if j != 0:
                current = measure()
                last = measure(South)
                if last > current:
                    swap(South)
            if i != 0:
                current = measure()
                last = measure(West)
                if last > current:
                    swap(West)
            move(North)
        move(East)
