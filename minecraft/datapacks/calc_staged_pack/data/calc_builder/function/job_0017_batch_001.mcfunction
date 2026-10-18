execute in minecraft:overworld unless entity @e[type=minecraft:marker,tag=calc_build_dafc0a3dbc,limit=1] run return 0
execute in minecraft:overworld as @e[type=minecraft:marker,tag=calc_build_dafc0a3dbc,limit=1] at @s run function calc_builder:job_0017_batch_001_local
schedule function calc_builder:job_0017_check_001 4t replace
