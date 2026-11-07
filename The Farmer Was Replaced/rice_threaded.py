# Window width-------------------------------------------------------
from utils import goTo, getPos, waitUntilTime, addVec, master

set_world_size(32)
size = get_world_size()


def dig_until_rice_level():
    while get_ground_type() != Grounds.Clay:
        dig()


def clear_and_plant_column():
    def plant_next():
        plant(Entities.Rice)
        use_item(Items.Water)
        move(North)

    for _ in range(size - 1):
        plant_next()
        dig_until_rice_level()
    plant_next()


def harvest_dig_layer(dig_layer=True):
    if dig_layer:
        for _ in range(size):
            harvest()
            dig()
            plant(Entities.Rice)
            move(North)
    else:
        for _ in range(size):
            harvest()
            move(North)

def drone_function():
    dig_until_rice_level()
    clear_and_plant_column()
    harvest_dig_layer()
    harvest_dig_layer(False)


def for_all():
    while spawn_drone(drone_function):
        move(East)
    master()
    drone_function()


def main():
    clear()
    jump(Unlocks.Rice)
    while True:
        # drone_function()
        for_all()
        clear()


if __name__ == "__main__":
    main()
