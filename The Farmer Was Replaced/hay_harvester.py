from map_traverser import simpleTraverse, zigZagTraverse

clear()

map_size = get_world_size()


def harvestForIterations(count=10):
    for _ in range(count):
        zigZagTraverse(harvest)


def harvestUntilItemCountAbove(threshold=100000):
    while num_items(Items.Hay) <= threshold:
        zigZagTraverse(harvest)


def harvestAlways():
    while True:
        zigZagTraverse(harvest)
