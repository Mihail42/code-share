from utils import *
clear()

def planter():
    harvest()
    if get_water() < 0.5:
        use_item(Items.Water, 2)
    plant(Entities.Carrot)
        
threaded(till, repeat(get_world_size()))
threaded(planter, always)
# threaded(harvest, until(Items.Hay, 247 * 10**6))
# threaded(harvest, repeat(10))
