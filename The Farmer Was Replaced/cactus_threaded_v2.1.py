from map_traverser import goTo
from utils import *

map_size = get_world_size()
half_size = map_size / 2
oppositeOf = {North: South, South: North, West: East, East: West}


def idle():
    while True:
        do_a_flip()


def planter(moveTo):
    if get_ground_type() == Grounds.Grassland:
        till()
    plant(Entities.Cactus)
    move(moveTo)


def plantSector(side):
    if side == North:
        forward = North
        backward = South
        next = East
    elif side == South:
        forward = South
        backward = North
        next = East
    for _ in range(half_size - 1):
        planter(forward)
    planter(next)
    for _ in range(half_size):
        planter(backward)
    move(forward)


def horizontalSort(direction):
    posX = get_pos_x()
    for _ in range(half_size):
        for i in range(32):
            if i % 2 == 0:
                if measure(West) > measure():
                    swap(West)
                else:
                    waitForTicks(200)
            else:
                if measure() > measure(East):
                    if posX == map_size - 1:
                        waitForTicks(200)
                    else:
                        swap(East)
                else:
                    waitForTicks(202)
        move(direction)


def verticalSort(direction):
    posY = get_pos_y()
    for _ in range(half_size):
        for i in range(32):
            if i % 2 == 0:
                if measure(North) < measure():
                    swap(North)
                else:
                    waitForTicks(200)
            else:
                if measure() < measure(South):
                    if posY == 0:
                        waitForTicks(200)
                    else:
                        swap(South)
                else:
                    waitForTicks(202)
        move(direction)


def sortLine(direction):
    # do line sorting logic with
    if direction == North or direction == South:
        horizontalSort(direction)
    else:
        verticalSort(direction)


def goSide(pos, timer, direction, sectorSide, initial):
    for _ in range(pos):
        move(direction)
    child()
    waitUntilTime(timer)
    if initial:
        plantSector(sectorSide)
    sortLine(sectorSide)
    # idle()


def spawnSideDrones(timer, sectorSide, initial):
    if sectorSide == North or sectorSide == South:
        forward = West
        backward = East
    else:
        forward = South
        backward = North
    spawn_drone(goSide, 2, timer, forward, sectorSide, initial)
    for i in range(7):
        spawn_drone(goSide, (i + 2) * 2, timer, forward, sectorSide, initial)
        spawn_drone(goSide, (i + 1) * 2, timer, backward, sectorSide, initial)


def spawnSubMaster(sectorSise, timer, initial=True):
    subMaster()
    move(sectorSise)
    spawnSideDrones(timer, sectorSise, initial)
    waitUntilTime(timer)
    if initial:
        plantSector(sectorSise)
    sortLine(sectorSise)
    # idle()


clear()
master()


def exec_horizontal():
    goTo(map_size / 2, map_size / 2)
    timer = get_time() + 1.2
    spawn_drone(spawnSubMaster, South, timer)
    spawnSideDrones(timer, North, True)
    waitUntilTime(timer)
    plantSector(North)
    sortLine(North)


def exec_vertical():
    goTo(map_size / 2, map_size / 2)
    timer = get_time() + 1.2
    spawn_drone(spawnSubMaster, West, timer, False)
    spawnSideDrones(timer, East, False)
    waitUntilTime(timer)
    sortLine(East)
    harvest()


while True:
    exec_horizontal()
    exec_vertical()
