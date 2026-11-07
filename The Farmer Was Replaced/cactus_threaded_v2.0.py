from map_traverser import goTo
from utils import threaded, repeat, waitUntilTime

clear()


def prepareMap():
    def callable():
        if get_ground_type() == Grounds.Grassland:
            till()
        plant(Entities.Cactus)

    threaded(callable, repeat())


def sortAction(direction, time_increment, startTime):
    if direction == East:
        prev = West
        next = East
        next_dir = North
    else:
        prev = South
        next = North
        next_dir = East

    increment = time_increment
    for _ in range(32):
        waitUntilTime(startTime)
        startTime += increment
        even = True
        while get_time() < startTime:
            if even:
                if measure(prev) > measure():
                    swap(prev)
            else:
                if measure() > measure(next):
                    swap(next)
            even = not even
        move(next_dir)


def spawnSorters(direction, time_increment):
    timer = get_time() + 1.3
    map_size = get_world_size()
    for i in range(map_size):
        if i % 2 == 1:
            handle = spawn_drone(sortAction, direction, time_increment, timer)
        move(direction)
    wait_for(handle)


def spawnSorterDrones():
    change_hat(Hats.Purple_Hat)
    spawnSorters(East, 1)
    spawnSorters(North, 1)


if __name__ != "__main__":
    while True:
        prepareMap()
        spawnSorterDrones()
        harvest()
else:
    for _ in range(1):
        prepareMap()
        spawnSorterDrones()
        harvest()
