from map_traverser import simpleTraverse, zigZagTraverse

clear()

map_size = get_world_size()


def harvestForIterations(count=10):
    simpleTraverse(prepareMap)
    for _ in range(count):
        simpleTraverse(harvestCarrot)


def harvestUntilItemCountAbove(threshold=100000):
    simpleTraverse(prepareMap)
    while num_items(Items.Hay) <= threshold:
        simpleTraverse(harvestCarrot)


def harvestAlways():
    simpleTraverse(prepareMap)
    while True:
        simpleTraverse(harvestCarrot)


def harvestCarrot():
    if can_harvest():
        harvest()
    plant(Entities.Carrot)


def prepareMap():
    if get_ground_type() == Grounds.Grassland:
        till()
    plant(Entities.Carrot)
