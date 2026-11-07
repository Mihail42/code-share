from utils import *

clear()

threaded(harvest, always)
# threaded(harvest, until(Items.Hay, 247 * 10**6))
# threaded(harvest, repeat(10))
