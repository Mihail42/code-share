# bi-directional buble sort (shaker - sort)
from map_traverser import goTo
from utils import *

map_size = get_world_size()
clear()


def sortTripleInDir(direction):
    if direction == North:
        prev = South
        next = North
    else:
        prev = West
        next = East
    swapped = False
    while not (measure(prev) <= measure() and measure() <= measure(next)):
        if measure() > measure(next):
            swap(next)
            swapped = True
        if measure(prev) > measure():
            swap(prev)
            swapped = True
    return swapped


def biBubleSortLine(direction):
    if direction == North:
        forward = North
        backward = South
        sortDir = North
        position = get_pos_y
    else:
        forward = East
        backward = West
        sortDir = East
        position = get_pos_x
    start = 1
    end = map_size - 2
    forwardPass = True
    while start < end:
        swappped = False
        if forwardPass:
            while position() < end:
                swappped = sortTripleInDir(sortDir) or swappped
                move(forward)
            end -= 1
        else:
            while start < position():
                swappped = sortTripleInDir(sortDir) or swappped
                move(backward)
            start += 1
        if not swappped:
            return
        forwardPass = not forwardPass


def sortLine(direction, init=False):
    def initialize():
        if direction == North:
            nextMove = North
            prev = South
        else:
            nextMove = East
            prev = West
        if get_ground_type() == Grounds.Grassland:
            till()
        plant(Entities.Cactus)
        move(nextMove)
        for _ in range(map_size - 2):
            if get_ground_type() == Grounds.Grassland:
                till()
            plant(Entities.Cactus)
            if measure(prev) > measure():
                swap(prev)
            move(nextMove)
        if get_ground_type() == Grounds.Grassland:
            till()
        plant(Entities.Cactus)
        if measure(prev) > measure():
            swap(prev)

    if init:
        initialize()
        move(North)
        move(North)
    biBubleSortLine(direction)


def spawnDrones():
    now = get_time()
    change_hat(Hats.Purple_Hat)
    for _ in range(31):
        spawn_drone(sortLine, North, True)
        move(East)
    sortLine(North, True)
    quick_print(get_time() - now)
    goTo(1, 0)
    while num_drones() > 1:
        pass
    for _ in range(31):
        spawn_drone(sortLine, East)
        move(North)
    sortLine(East)


for _ in range(1):
    spawnDrones()
    goTo(0, 0)
    while num_drones() > 1:
        pass
    harvest()
