from utils import *

clear()


def planter():
    plant(Entities.Pumpkin)
    use_item(Items.Fertilizer, 2)
    while not can_harvest():
        plant(Entities.Pumpkin)
        use_item(Items.Fertilizer)


def cure():
    if (get_pos_x() + get_pos_y() * 2) % 5 == 0:
        use_item(Items.Weird_Substance)


threaded(till, repeat())
while True:
    threaded(planter, repeat())
    while not num_drones() <= 7:
        pass
    threaded(cure, repeat())
    while not num_drones() <= 1:
        pass
    harvest()
