def master():
    change_hat(Hats.Purple_Hat)


def subMaster():
    change_hat(Hats.Green_Hat)


def child():
    change_hat(Hats.Brown_Hat)


def waitForTicks(ticks):
    ticks -= 3
    for _ in range(ticks):
        pass


def wait(terminate):
    while not terminate():
        pass


def waitUntil(condition):
    while not condition:
        pass


def waitUntilTime(time):
    while get_time() < time:
        pass


def goTo(tx_or_vector, ty=None):
    if ty == None:
        tx = tx_or_vector[0]
        ty = tx_or_vector[1]
    else:
        tx = tx_or_vector
    s = get_world_size()
    dx = (tx - get_pos_x()) % s
    dy = (ty - get_pos_y()) % s

    if dx > s // 2:
        dx -= s
    if dy > s // 2:
        dy -= s

    for _ in range(max(dx, 0)):
        move(East)
    for _ in range(max(-dx, 0)):
        move(West)
    for _ in range(max(dy, 0)):
        move(North)
    for _ in range(max(-dy, 0)):
        move(South)

def goToCenter():
    size = get_world_size()
    goTo(size // 2, size // 2)

def getPos():
    return (get_pos_x(), get_pos_y())

def addVec(vector1, vector2):
    return (vector1[0] + vector2[0], vector1[1] + vector2[1])


def subVec(vector1, vector2):
    return (vector1[0] - vector2[0], vector1[1] - vector2[1])


def multVec(vector1, scalar):
    return (vector1[0] * scalar, vector1[1] * scalar)


def divVec(vector1, scalar):
    return (vector1[0] / scalar, vector1[1] / scalar)


def divIntVec(vector1, scalar):
    return (vector1[0] // scalar, vector1[1] // scalar)


def always():
    return False


def until(item, amount):
    def terminate():
        return num_items(item) >= amount

    return terminate


def repeat(amount=get_world_size()):
    count = -1

    def terminate():
        global count
        count += 1
        return count > amount

    return terminate


def columnAction(f, terminate):
    while not terminate():
        f()
        move(North)


def threaded(f, terminate):
    if terminate():
        return
    change_hat(Hats.Purple_Hat)
    for _ in range(get_world_size()):
        if not spawn_drone(columnAction, f, terminate):
            columnAction(f, terminate)
        move(East)
