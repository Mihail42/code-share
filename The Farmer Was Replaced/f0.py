clear()

def drone_func():
    while True:
        place(Grounds.Block_Blue)
        move(North)
        
while spawn_drone(drone_func):
    move(East)
drone_func()