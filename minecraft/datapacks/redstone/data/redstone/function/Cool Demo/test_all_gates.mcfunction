# Latest supplied layouts: AND, OR, NOT, NAND, NOR, XOR, XNOR.
# Origins every 10 blocks along +Z; supports placed first.

# AND: origin Z +0
setblock ~0 ~-1 ~0 minecraft:redstone_lamp replace
setblock ~1 ~-1 ~0 minecraft:orange_wool replace
setblock ~0 ~-1 ~2 minecraft:redstone_lamp replace
setblock ~1 ~-1 ~2 minecraft:orange_wool replace
setblock ~2 ~0 ~2 minecraft:orange_wool replace
setblock ~2 ~0 ~1 minecraft:orange_wool replace
setblock ~2 ~0 ~0 minecraft:orange_wool replace
setblock ~3 ~-1 ~2 minecraft:orange_wool replace
setblock ~3 ~-1 ~1 minecraft:orange_wool replace
setblock ~3 ~-1 ~0 minecraft:orange_wool replace
setblock ~4 ~-1 ~1 minecraft:redstone_lamp replace
setblock ~0 ~0 ~0 minecraft:lever[face=floor,facing=west,powered=false] replace
setblock ~1 ~0 ~0 minecraft:redstone_wire replace
setblock ~0 ~0 ~2 minecraft:lever[face=floor,facing=west,powered=false] replace
setblock ~1 ~0 ~2 minecraft:redstone_wire replace
setblock ~2 ~1 ~0 minecraft:redstone_torch replace
setblock ~2 ~1 ~2 minecraft:redstone_torch replace
setblock ~2 ~1 ~1 minecraft:redstone_wire replace
setblock ~3 ~0 ~1 minecraft:redstone_wall_torch[facing=east] replace
setblock ~4 ~0 ~1 minecraft:redstone_wire replace

# OR: origin Z +10
setblock ~0 ~-1 ~10 minecraft:redstone_lamp replace
setblock ~0 ~-1 ~12 minecraft:redstone_lamp replace
setblock ~1 ~-1 ~10 minecraft:lime_wool replace
setblock ~1 ~-1 ~12 minecraft:lime_wool replace
setblock ~2 ~-1 ~12 minecraft:lime_wool replace
setblock ~2 ~-1 ~10 minecraft:lime_wool replace
setblock ~3 ~0 ~12 minecraft:lime_wool replace
setblock ~3 ~0 ~10 minecraft:lime_wool replace
setblock ~3 ~-1 ~11 minecraft:lime_wool replace
setblock ~4 ~-1 ~11 minecraft:redstone_lamp replace
setblock ~0 ~0 ~10 minecraft:lever[face=floor,facing=west,powered=false] replace
setblock ~0 ~0 ~12 minecraft:lever[face=floor,facing=west,powered=false] replace
setblock ~1 ~0 ~10 minecraft:redstone_wire replace
setblock ~1 ~0 ~12 minecraft:redstone_wire replace
setblock ~2 ~0 ~10 minecraft:repeater[facing=west,delay=1] replace
setblock ~2 ~0 ~12 minecraft:repeater[facing=west,delay=1] replace
setblock ~3 ~0 ~11 minecraft:redstone_wire replace
setblock ~4 ~0 ~11 minecraft:redstone_wire replace

# NOT: origin Z +20
setblock ~0 ~-1 ~20 minecraft:redstone_lamp replace
setblock ~1 ~-1 ~20 minecraft:yellow_wool replace
setblock ~2 ~0 ~20 minecraft:yellow_wool replace
setblock ~4 ~-1 ~20 minecraft:redstone_lamp replace
setblock ~0 ~0 ~20 minecraft:lever[face=floor,facing=west,powered=false] replace
setblock ~1 ~0 ~20 minecraft:redstone_wire replace
setblock ~3 ~0 ~20 minecraft:redstone_wall_torch[facing=east] replace
setblock ~4 ~0 ~20 minecraft:redstone_wire replace

# NAND: origin Z +30
setblock ~0 ~-1 ~30 minecraft:redstone_lamp replace
setblock ~1 ~-1 ~30 minecraft:purple_wool replace
setblock ~0 ~-1 ~32 minecraft:redstone_lamp replace
setblock ~1 ~-1 ~32 minecraft:purple_wool replace
setblock ~2 ~0 ~30 minecraft:purple_wool replace
setblock ~2 ~0 ~32 minecraft:purple_wool replace
setblock ~3 ~-1 ~31 minecraft:purple_wool replace
setblock ~4 ~-1 ~31 minecraft:redstone_lamp replace
setblock ~0 ~0 ~30 minecraft:lever[face=floor,facing=west,powered=false] replace
setblock ~1 ~0 ~30 minecraft:redstone_wire replace
setblock ~0 ~0 ~32 minecraft:lever[face=floor,facing=west,powered=false] replace
setblock ~1 ~0 ~32 minecraft:redstone_wire replace
setblock ~3 ~0 ~30 minecraft:redstone_wall_torch[facing=east] replace
setblock ~3 ~0 ~32 minecraft:redstone_wall_torch[facing=east] replace
setblock ~3 ~0 ~31 minecraft:redstone_wire replace
setblock ~4 ~0 ~31 minecraft:redstone_wire replace

# NOR: origin Z +40
setblock ~0 ~-1 ~40 minecraft:redstone_lamp replace
setblock ~0 ~-1 ~42 minecraft:redstone_lamp replace
setblock ~1 ~-1 ~40 minecraft:blue_wool replace
setblock ~1 ~-1 ~41 minecraft:blue_wool replace
setblock ~1 ~-1 ~42 minecraft:blue_wool replace
setblock ~2 ~-1 ~41 minecraft:blue_wool replace
setblock ~3 ~0 ~41 minecraft:blue_wool replace
setblock ~4 ~-1 ~41 minecraft:blue_wool replace
setblock ~5 ~-1 ~41 minecraft:redstone_lamp replace
setblock ~0 ~0 ~40 minecraft:lever[face=floor,facing=west,powered=false] replace
setblock ~0 ~0 ~42 minecraft:lever[face=floor,facing=west,powered=false] replace
setblock ~1 ~0 ~40 minecraft:redstone_wire replace
setblock ~1 ~0 ~41 minecraft:redstone_wire replace
setblock ~1 ~0 ~42 minecraft:redstone_wire replace
setblock ~2 ~0 ~41 minecraft:redstone_wire replace
setblock ~4 ~0 ~41 minecraft:redstone_wall_torch[facing=east] replace
setblock ~5 ~0 ~41 minecraft:redstone_wire replace

# XOR: origin Z +50
setblock ~0 ~-1 ~50 minecraft:redstone_lamp replace
setblock ~1 ~-1 ~50 minecraft:white_wool replace
setblock ~0 ~-1 ~52 minecraft:redstone_lamp replace
setblock ~1 ~-1 ~52 minecraft:white_wool replace
setblock ~2 ~0 ~52 minecraft:white_wool replace
setblock ~2 ~0 ~51 minecraft:white_wool replace
setblock ~2 ~0 ~50 minecraft:white_wool replace
setblock ~3 ~0 ~51 minecraft:white_wool replace
setblock ~4 ~-1 ~50 minecraft:white_wool replace
setblock ~4 ~-1 ~52 minecraft:white_wool replace
setblock ~5 ~-1 ~50 minecraft:white_wool replace
setblock ~5 ~-1 ~52 minecraft:white_wool replace
setblock ~6 ~0 ~50 minecraft:white_wool replace
setblock ~6 ~0 ~52 minecraft:white_wool replace
setblock ~8 ~-1 ~51 minecraft:redstone_lamp replace
setblock ~0 ~0 ~50 minecraft:lever[face=floor,facing=west,powered=false] replace
setblock ~1 ~0 ~50 minecraft:redstone_wire replace
setblock ~0 ~0 ~52 minecraft:lever[face=floor,facing=west,powered=false] replace
setblock ~1 ~0 ~52 minecraft:redstone_wire replace
setblock ~2 ~1 ~50 minecraft:redstone_torch replace
setblock ~2 ~1 ~52 minecraft:redstone_torch replace
setblock ~2 ~1 ~51 minecraft:redstone_wire replace
setblock ~3 ~1 ~51 minecraft:redstone_wire replace
setblock ~3 ~0 ~50 minecraft:redstone_wall_torch[facing=east] replace
setblock ~3 ~0 ~52 minecraft:redstone_wall_torch[facing=east] replace
setblock ~4 ~0 ~51 minecraft:redstone_wall_torch[facing=east] replace
setblock ~4 ~0 ~50 minecraft:redstone_wire replace
setblock ~4 ~0 ~52 minecraft:redstone_wire replace
setblock ~5 ~0 ~50 minecraft:redstone_wire replace
setblock ~5 ~0 ~52 minecraft:redstone_wire replace
setblock ~7 ~0 ~50 minecraft:redstone_wall_torch[facing=east] replace
setblock ~7 ~0 ~52 minecraft:redstone_wall_torch[facing=east] replace
setblock ~7 ~0 ~51 minecraft:redstone_wire replace
setblock ~8 ~0 ~51 minecraft:redstone_wire replace

# XNOR: origin Z +60
setblock ~0 ~-1 ~60 minecraft:redstone_lamp replace
setblock ~1 ~-1 ~60 minecraft:black_wool replace
setblock ~0 ~-1 ~62 minecraft:redstone_lamp replace
setblock ~1 ~-1 ~62 minecraft:black_wool replace
setblock ~2 ~0 ~62 minecraft:black_wool replace
setblock ~2 ~0 ~61 minecraft:black_wool replace
setblock ~2 ~0 ~60 minecraft:black_wool replace
setblock ~3 ~0 ~61 minecraft:black_wool replace
setblock ~4 ~-1 ~60 minecraft:black_wool replace
setblock ~5 ~-1 ~60 minecraft:black_wool replace
setblock ~4 ~-1 ~62 minecraft:black_wool replace
setblock ~5 ~-1 ~62 minecraft:black_wool replace
setblock ~6 ~0 ~60 minecraft:black_wool replace
setblock ~6 ~0 ~62 minecraft:black_wool replace
setblock ~7 ~-1 ~61 minecraft:black_wool replace
setblock ~8 ~-1 ~61 minecraft:black_wool replace
setblock ~9 ~0 ~61 minecraft:black_wool replace
setblock ~11 ~-1 ~61 minecraft:redstone_lamp replace
setblock ~0 ~0 ~60 minecraft:lever[face=floor,facing=west,powered=false] replace
setblock ~1 ~0 ~60 minecraft:redstone_wire replace
setblock ~0 ~0 ~62 minecraft:lever[face=floor,facing=west,powered=false] replace
setblock ~1 ~0 ~62 minecraft:redstone_wire replace
setblock ~2 ~1 ~60 minecraft:redstone_torch replace
setblock ~2 ~1 ~62 minecraft:redstone_torch replace
setblock ~2 ~1 ~61 minecraft:redstone_wire replace
setblock ~3 ~0 ~60 minecraft:redstone_wall_torch[facing=east] replace
setblock ~3 ~0 ~62 minecraft:redstone_wall_torch[facing=east] replace
setblock ~4 ~0 ~61 minecraft:redstone_wall_torch[facing=east] replace
setblock ~3 ~1 ~61 minecraft:redstone_wire replace
setblock ~4 ~0 ~60 minecraft:redstone_wire replace
setblock ~5 ~0 ~60 minecraft:redstone_wire replace
setblock ~4 ~0 ~62 minecraft:redstone_wire replace
setblock ~5 ~0 ~62 minecraft:redstone_wire replace
setblock ~7 ~0 ~60 minecraft:redstone_wall_torch[facing=east] replace
setblock ~7 ~0 ~62 minecraft:redstone_wall_torch[facing=east] replace
setblock ~7 ~0 ~61 minecraft:redstone_wire replace
setblock ~8 ~0 ~61 minecraft:redstone_wire replace
setblock ~10 ~0 ~61 minecraft:redstone_wall_torch[facing=east] replace
setblock ~11 ~0 ~61 minecraft:redstone_wire replace
