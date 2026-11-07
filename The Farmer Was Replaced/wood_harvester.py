from map_traverser import simpleTraverse, zigZagTraverse

clear()

map_size = get_world_size()


def harvestForIterations(count=10):
    for _ in range(count):
        simpleTraverse(harvestWood)


def harvestUntilItemCountAbove(threshold=100000):
    while num_items(Items.Hay) <= threshold:
        simpleTraverse(harvestWood)


def harvestAlways():
    while True:
        simpleTraverse(harvestWood)


def harvestWood():
    x, y = (get_pos_x(), get_pos_y())
    if can_harvest():
        harvest()
    if (x + y) % 2 == 0:
        plant(Entities.Tree)
    else:
        plant(Entities.Bush)
