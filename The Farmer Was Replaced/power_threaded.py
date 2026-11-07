from utils import *

clear()


def prepare():
    if get_ground_type() != Grounds.Soil:
        till()
    if get_water() < 0.5:
        use_item(Items.Water)
    plant(Entities.Sunflower)


def harvestReplant():
    harvest()
    if get_water() < 0.5:
        use_item(Items.Water)
    plant(Entities.Sunflower)


threaded(prepare, repeat())
threaded(harvestReplant, until(Items.Power, 10000000))
threaded(harvest, repeat())
