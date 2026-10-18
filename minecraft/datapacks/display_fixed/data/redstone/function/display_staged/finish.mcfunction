execute in minecraft:overworld unless entity @e[type=minecraft:marker,tag=hdl_build_ac9792f702,limit=1] run return 0
tellraw @a "Build complete: 11965 blocks verified. Chunks stay loaded for operation. Release them with /function redstone:display_staged/release."
