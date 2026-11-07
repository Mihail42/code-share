# Window width-------------------------------------------------------
from utils import goTo, getPos, addVec, goToCenter

set_world_size(7)
size = get_world_size()
goTo(0,0)


def check_clay(dir=None):
    if dir == None:
        return get_ground_type() == Grounds.Clay
    else:
        return get_ground_type(dir) == Grounds.Clay

def reach_clay():
    while not check_clay():
        dig()

def expose_all_clay():
    for _ in range(size):
        for _ in range(size):
            reach_clay()
            use_item(Items.Water, 2)
            plant(Entities.Rice)
            move(North)
        move(East)

# def plant_all_rice():
#     for _ in range(size):
#         for _ in range(size):
#             use_item(Items.Water, 4)
#             plant(Entities.Rice)
#             move(North)
#         move(East)

def harvest_all_rice():
    for _ in range(size):
        for _ in range(size):
            harvest()
            move(North)
        move(East)

while True:
    # reach_clay()
    for _ in range(2):
        expose_all_clay()
        # plant_all_rice()
        harvest_all_rice()
    clear()
    # goTo(0,0)

