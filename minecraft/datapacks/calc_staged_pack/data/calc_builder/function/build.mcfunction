execute unless dimension minecraft:overworld run return run tellraw @s "Run this builder in the overworld."
execute in minecraft:overworld if entity @e[type=minecraft:marker,tag=calc_build_dafc0a3dbc,limit=1] run return run tellraw @s "Build anchor exists. Use /function calc_builder:release before restarting."
scoreboard objectives add calc_job dummy
execute at @s align xyz run summon minecraft:marker ~ ~ ~ {Tags:["calc_build_dafc0a3dbc"]}
execute in minecraft:overworld as @e[type=minecraft:marker,tag=calc_build_dafc0a3dbc,limit=1] at @s run forceload add ~ ~
tellraw @s "CALC construction started: moving chunk windows, up to 2000 blocks per batch."
function calc_builder:job_0000_load
