# Window width-------------------------------------------------------
from utils import goTo, getPos, waitUntilTime, addVec, master

set_world_size(32)
size = get_world_size()

# handles intial column setup and harvesting logic


def prepare_column(initial=False):
    def planter_initial():
        till()
        plant(Entities.Bamboo)
        use_item(Items.Water, 2)

    def planter_replant():
        plant(Entities.Bamboo)
        if get_water() < 0.5:
            use_item(Items.Water, 2)

    planter = None
    if initial:
        planter = planter_initial
    else:
        hover(0)
        move(West)
        planter = planter_replant

    planter()
    for _ in range(size - 1):
        move(North)
        planter()
    move(East)
    move(North)


def trim_colum_complete():
    def trim_bamboo():
        hover(measure(West))
        move(West)
        move(East)

    def trim_column():
        for _ in range(size):
            trim_bamboo()
            move(North)

    for _ in range(2):
        trim_column()


def drone_function():
    prepare_column(True)
    while True:
        trim_colum_complete()
        prepare_column()


def for_all():
    for _ in range(size/2-1):
        spawn_drone(drone_function)
        move(East)
        move(East)
    master()
    drone_function()


def main():
    clear()
    for_all()
    # drone_function()


if __name__ == "__main__":
    main()
