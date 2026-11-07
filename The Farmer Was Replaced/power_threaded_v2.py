from utils import *

clear()


def prepare():
    if get_ground_type() != Grounds.Soil:
        till()
    if get_water() < 0.5:
        use_item(Items.Water)
    plant(Entities.Sunflower)


def planter():
    plant(Entities.Sunflower)


def harvestHighest(n=15):
    def callable():
        if measure() == n:

            harvest()

    return callable


threaded(prepare, repeat())
while num_items(Items.Power) <= 10000000:
    for i in range(15, 6, -1):
        threaded(harvestHighest(i), repeat())
        while not num_drones() <= 1:
            pass
    threaded(planter, repeat())
