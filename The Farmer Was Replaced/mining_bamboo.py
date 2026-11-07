# Window width-------------------------------------------------------
from utils import goTo, getPos, waitUntilTime, addVec


set_world_size(8)
size = get_world_size()

def prepare_map():
    for x in range(size):
        for y in range(size):
            move(North)
            till()
            plant(Entities.Bamboo)
        move(East)


def traverse_and_harvest():
    for x in range(size):
        for y in range(size):
            move(North)
        move(East)

def main():
    clear()
    prepare_map()
    while True:
        traverse_and_harvest()


if __name__ == "__main__":
    main()

