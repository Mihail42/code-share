# Window width-------------------------------------------------------
from utils import goTo, getPos, waitUntilTime, addVec

set_world_size(8)
size = get_world_size()

def water_plant():
    if get_water() < 0.5:
        use_item(Items.Water, 2)
    plant(Entities.Bamboo)

def till_plant():
    if get_ground_type() == Grounds.Grassland:
        till()
    water_plant()

def prepare_map():
    for x in range(size-1):
        if x % 2 == 0:
            till_plant()
            for y in range(size - 1):
                move(North)
                till_plant()
            move(East)
        else:
            move(East)
    goTo(get_pos_x(), 0)

opposite_of = {
    North:South,
    South:North,
    East:West,
    West:East
}

def trim(dir, initial = False):
    hover(measure(dir))
    move(dir)
    if initial:
        move(dir)
    else:
        move(opposite_of[dir])


def trim_column(dir):
    for i in range(size):
        if i == 0:
            trim(dir, True)
        else:
            trim(opposite_of[dir])
        move(North)

def trim_all():
    for i in range(2):
        for j in range(size/2):
            trim_column(East)

def harvest_all():
    hover(0)
    move(East)
    for _ in range(size/2 - 1):
        for _ in range(size):
            move(North)
            water_plant()
        move(East)
        move(East)
    for _ in range(size):
        move(North)
        water_plant()
    move(East)

def main():
    clear()
    prepare_map()
    while True:
        trim_all()
        harvest_all()


if __name__ == "__main__":
    main()

