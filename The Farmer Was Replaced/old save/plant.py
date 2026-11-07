def hay():
    if get_ground_type() != Grounds.Grassland:
        till()
    harvest()
def bush():
    plant(Entities.Bush)
def tree():
    plant(Entities.Tree)
def carrot():
    if get_ground_type() != Grounds.Soil:
        till()
    plant(Entities.Carrot)
def sunflower():
    if get_ground_type() != Grounds.Soil:
        till()
    plant(Entities.Sunflower)
def pumpkin():
    if get_ground_type() != Grounds.Soil:
        till()
    plant(Entities.Pumpkin)
def cactus():
    if get_ground_type() != Grounds.Soil:
        till()
    plant(Entities.Cactus)