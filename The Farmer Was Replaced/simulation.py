scripts = ["cactus_threaded_v4", "cactus_threaded_v3", "cactus_threaded"]
unlocks = Unlocks
items = {Items.Pumpkin: 1000000000, Items.Power: 1000000000}
globals = {}
seed = 0
speedup = 10
times = []
for script in scripts:
    times.append(simulate(script, unlocks, items, globals, seed, speedup))

for i in range(len(times)):
    quick_print(scripts[i], "\t- ", times[i])
