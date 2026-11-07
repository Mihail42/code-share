import utils
threshold = 110000000
left_of = {North : West, East : North, South : East, West : South}
right_of = {North : East, East : South, South : West, West : North}
opposite_of = {North : South, East : West, South : North, West : East}

def setup_maze():
    clear()
    plant(Entities.Bush)
    substance = get_world_size() * 2 ** (num_unlocked(Unlocks.Mazes) - 1)
    use_item(Items.Weird_Substance, substance)

def get_possible_dirs(exclude = None):
    dirs = []
    if can_move(North):
        dirs.append(North)
    if can_move(East):
        dirs.append(East)
    if can_move(South):
        dirs.append(South)
    if can_move(West):
        dirs.append(West)
    if exclude != None:
        for dir_to_remove in exclude:
            if dir_to_remove in dirs:
                dirs.remove(dir_to_remove)
    return dirs

def position():
    return (get_pos_x(), get_pos_y())
    
def get_next_pos(dir):
    dx = 0
    dy = 0
    if dir == North:
        dy = 1
    elif dir == East:
        dx = 1
    elif dir == South:
        dy = -1
    else:
        dx = -1
    return (get_pos_x() + dx, get_pos_y() + dy)
    
def dir_from_to(a, b):
    ax = a[0]
    ay = a[1]
    bx = b[0]
    by = b[1]
    if ax == bx and ay < by: 
        return North
    if ax == bx and by < ay: 
        return South
    if ay == by and ax < bx: 
        return East
    if ay == by and bx < ax: 
        return West
    return None

def check_intersection(old_pos, curr_pos, next_dir):        
    # get possible directions at the current position
    dirs = get_possible_dirs()
    # return if not at intersection 
    if len(dirs) <= 2:
        return []
    # exclude direction resulting in going back
    if old_pos != None:
        back_dir = dir_from_to(curr_pos, old_pos)
        if back_dir in dirs:
            dirs.remove(back_dir)        
    # remove it 
    if next_dir != None:
        dirs.remove(next_dir)
    # Remaining are spawn directions
    return dirs

def try_collect_chest():
    if get_entity_type() == Entities.Treasure:
        harvest()
        return True
    return False

def choose_dir(initial_dir, visited):
    all_possible = get_possible_dirs()
    for possible_dir in all_possible:
        if get_next_pos(possible_dir) in visited:
            continue
        return possible_dir

def traverse(initial_dir, visited):
    def drone_func():
        if try_collect_chest():
            if num_items(Items.Gold) <= threshold:
                setup_maze()
                begin_maze()
            else:
                clear()
        if initial_dir == None:
            return
        old_pos = position()
        if old_pos in visited:
            return
        visited.add(old_pos)
        move(initial_dir)
        curr_pos = position()
        next_dir = choose_dir(initial_dir, visited)
        dirs_at_intersection = check_intersection(old_pos, curr_pos, next_dir)
        if len(dirs_at_intersection) >= 1:
            for new_dir in dirs_at_intersection:
                spawn_drone(traverse(new_dir, visited))
        traverse(next_dir, visited)()
    return drone_func
    
def begin_maze():
    start_dir = North 
    if can_move(East):
        if not can_move(North):
            start_dir = East
        else:
            spawn_drone(traverse(East, set()))
    traverse(start_dir, set())()
    
set_world_size(32)
#set_execution_speed(1)
setup_maze() 
begin_maze()