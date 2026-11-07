from map_traverser import goTo, getPos

clear()

map_size = get_world_size()


def harvestForIterations(count=10):
    for _ in range(count):
        pass


def harvestUntilItemCountAbove(threshold=100000):
    prepareMap()
    while num_items(Items.Gold) <= threshold:
        traverse()
        prepareMap()
        pass


def harvestAlways():
    prepareMap()
    while True:
        traverse()
        prepareMap()
        pass


def spawnMazeSize(sideLength):
    plant(Entities.Bush)
    substance = sideLength * 2 ** (num_unlocked(Unlocks.Mazes) - 1)
    use_item(Items.Weird_Substance, substance)


def traverse():
    dir = North
    while not atTreasure():
        dir = left_of[dir]
        while not move(dir):
            dir = right_of[dir]
    harvest()


def atTreasure():
    global treasurePosition
    return treasurePosition == getPos()


def prepareMap():
    global treasurePosition
    goTo(0, 0)
    spawnMazeSize(get_world_size())
    treasurePosition = measure()


right_of = {
    North: East,
    East: South,
    South: West,
    West: North,
}
left_of = {
    North: West,
    East: North,
    South: East,
    West: South,
}

if __name__ == "__main__":
    harvestUntilItemCountAbove(616448)