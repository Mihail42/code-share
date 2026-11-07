import plant

width = get_world_size()
height = width

def reset_full():
    reset()
    harvestAll()

def reset():
    moveTo(0,0)
        
def harvestAll():
    for i in range(width):
        for j in range(height):
            harvest()
            move(North)
        move(East)
        
def harvest_hay():
    for i in range(width):
        for j in range(height):
            if can_harvest():
                harvest()
            plant.hay()
            move(North)
        move(East)

def harvest_carrot():
    for i in range(width):
        for j in range(height):
            if can_harvest():
                harvest()
            plant.carrot()
            move(North)
        move(East)

def harvest_wood():
    index = 0
    for i in range(width):
        for j in range(height):
            if can_harvest():
                harvest()
            if index % 2 == 0:
                plant.tree()
            else: 
                plant.bush()
            index += 1
            move(North)
        index += 1
        move(East)

def harvest_sunflower():
    for i in range(width):
        for j in range(height):
            if can_harvest():
                harvest()
            plant.sunflower()
            move(North)
        move(East)
    move(East)

def harvest_pumpkin():
    # plant pumpkins
    for i in range(width):
        for j in range(height):
            index = i * height + j
            if can_harvest():
                harvest()
            plant.pumpkin()
            move(North)
        move(East)
    # replant dead pumpkins
    pumpkins_ready = 0
    while pumpkins_ready != width * height:
        pumpkins_ready = 0
        for i in range(width):
            for j in range(height):
                index = i * height + j
                plant.pumpkin()
                if can_harvest():
                    pumpkins_ready += 1
                else:
                    pumpkins_ready -= 1
                move(North)
            move(East)
    harvest()

def harvest_cactus():
    #plant cactus
    for i in range(width):
        for j in range(height):
            if can_harvest():
                harvest()
            plant.cactus()
            move(North)
        move(East)
    #sort cactus
    #sort row
    for row in range(height):
        swapped = True
        while swapped:
            swapped = False
            for col in range(width - 1):
                current = measure()
                next = measure(East)
                if (current < next):
                    swap(East)
                    swapped = True
                move(East)
            move(East)
        move(North)
    #sort col
    for col in range(height):
        swapped = True
        while swapped:
            swapped = False
            for row in range(width - 1):
                current = measure()
                next = measure(North)
                if (current < next):
                    swap(North)
                    swapped = True
                move(North)
            move(North)
        move(East)
    harvest()

def wait_for_harvest():
    while not can_harvest():
        pass
    harvest()
    
def do_harvest():
    if can_harvest():
        harvest()
        
def moveTo(x, y):
    size = get_world_size()
    x = max(0, min(x, size - 1))
    y = max(0, min(y, size - 1))

    dir = (size / 2) - ((x - get_pos_x() + size) % size)
    if dir <= 0:
        while get_pos_x() != x:
            move(West)
    else:
        while get_pos_x() != x:
            move(East)
    dir = (size / 2) - ((y - get_pos_y() + size) % size)    
    if dir <= 0:
        while get_pos_y() != y:
            move(South)
    else:
        while get_pos_y() != y:
            move(North)

    

    
    
    
    
    
    
    
    
    
    
    
    
    
    
    