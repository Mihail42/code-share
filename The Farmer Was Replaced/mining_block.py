# Window width-------------------------------------------------------
from utils import goTo, getPos, addVec, goToCenter
clear()
set_world_size(32)
size = get_world_size()

def drone_func():
    while True:
        dig()

def for_all_drones(func):
    for _ in range(size):
        if not spawn_drone(func):
            func()
        move(East)

for_all_drones(drone_func)
