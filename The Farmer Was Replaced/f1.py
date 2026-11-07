clear()
def drone_func():
    while True:
        dig()
        move(North)
        
while spawn_drone(drone_func):
    move(East)
drone_func()