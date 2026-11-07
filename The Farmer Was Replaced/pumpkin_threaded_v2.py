from utils import *

clear()


def planter():
    size = get_world_size()
    for _ in range(size):
        plant(Entities.Pumpkin)
        use_item(Items.Fertilizer, 2)
        while not can_harvest():
            plant(Entities.Pumpkin)
            use_item(Items.Fertilizer)
        move(North)
    for _ in range(1500):
        pass
    for _ in range(size):
        cure()
        move(North)
    move(South)


def cure():
    if (get_pos_x() + get_pos_y() * 2) % 5 == 0:
        use_item(Items.Weird_Substance)


threaded(till, repeat())
while True:
    threaded(planter, repeat(1))
    while not num_drones() <= 1:
        pass
    harvest()
