from map_traverser import simpleTraverse, zigZagTraverse, goTo

# uses fertilizer to instantly grow pumpkins

clear()

map_size = get_world_size()


def harvestForIterations(count=10):
    simpleTraverse(prepareMap)
    for _ in range(count):
        harvestPumpkin()


def harvestUntilItemCountAbove(threshold=100000):
    simpleTraverse(prepareMap)
    while num_items(Items.Hay) <= threshold:
        harvestPumpkin()


def harvestAlways():
    simpleTraverse(prepareMap)
    while True:
        harvestPumpkin()


def harvestPumpkin():
    # traverse grid to replace dead pumpkins
    for _ in range(map_size):
        for _ in range(map_size):
            if not can_harvest():
                plantAndGrow()
            move(North)
        move(East)
    harvest()

    # plant new pumpkins
    for i in range(map_size):
        for j in range(map_size):
            if not can_harvest():
                plant(Entities.Pumpkin)
            move(North)
        move(East)
    pass


def plantAndGrow():
    plant(Entities.Pumpkin)
    while not can_harvest():
        use_item(Items.Fertilizer, 2)
        plant(Entities.Pumpkin)


def prepareMap():
    if get_ground_type() == Grounds.Grassland:
        till()
    plant(Entities.Pumpkin)
