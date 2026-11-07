from map_traverser import simpleTraverse, zigZagTraverse, goTo

# replants dead pumpkins

clear()

map_size = get_world_size()


def harvestForIterations(count=10):
    simpleTraverse(prepareMap)
    for _ in range(count):
        pass


def harvestUntilItemCountAbove(threshold=100000):
    simpleTraverse(prepareMap)
    while num_items(Items.Hay) <= threshold:
        pass


def harvestAlways():
    simpleTraverse(prepareMap)
    while True:
        harvestPumpkin()
        pass


def harvestPumpkin():
    # scan for dead pumpkins
    # keep track of their locations
    # move to the first -> second -> ect. dead pumpkin
    # check for "can_harvest()"
    #   if true -> remove current pumpkin from memory
    #   if false -> continue
    # replant -> go to next
    deadPos = []
    for i in range(map_size):
        for j in range(map_size):
            if not can_harvest():
                x, y = (get_pos_x(), get_pos_y())
                deadPos.append((x, y))
                plantAndWater()
            move(North)
        move(East)
    idx = 0
    while len(deadPos) > 0:
        x, y = deadPos[idx]
        goTo(x, y)
        if can_harvest():
            deadPos.pop(idx)
        else:
            plantAndWater()
            idx += 1
        if idx >= len(deadPos):
            idx = 0
    harvest()
    pass


def plantAndWater():
    plant(Entities.Pumpkin)
    if get_water() <= 0.75:
        use_item(Items.Water)


def prepareMap():
    if get_ground_type() == Grounds.Grassland:
        till()
    plant(Entities.Pumpkin)
