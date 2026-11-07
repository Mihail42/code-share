# Window width-------------------------------------------------------
from utils import goTo, getPos, addVec, goToCenter

set_world_size(32)
clear()
goToCenter()


def check_coal(dir=None):
    if dir == None:
        return get_ground_type() == Grounds.Coal
    else:
        return get_ground_type(dir) == Grounds.Coal


def check_for_coal_sheet():
    return (
        check_coal(North) or
        check_coal(East) or
        check_coal(South) or
        check_coal(West)
    )

dir_offset = {North:(0,1), South:(0,-1), East:(1,0), West:(-1,0)}
added_coal_positions = set()
stack = list()

def append_coal_dir():
    global stack
    global added_coal_positions
    # Adjecent
    for dir in [West, South, East, North]:
        if check_coal(dir):
            result = addVec(getPos(), dir_offset[dir])
            if result in added_coal_positions:
                continue
            stack.append(result)
            added_coal_positions.add(result)

def mine_coal_sheet():
    global stack
    global added_coal_positions
    added_coal_positions.add(getPos())
    append_coal_dir()
    while stack:
        position = stack.pop()
        goTo(position)
        dig()
        append_coal_dir()


while True:
    # dig until coal is found
    # explore (flood fill) the coal sheet and mine it
    if check_for_coal_sheet():
        mine_coal_sheet()
        added_coal_positions = set()
        stack = list()
        goToCenter()
    else:
        dig()
