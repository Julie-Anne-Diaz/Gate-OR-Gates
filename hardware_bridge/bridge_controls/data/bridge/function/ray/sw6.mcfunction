scoreboard players add #steps bridge_tmp 1
execute if block ~ ~ ~ minecraft:lever run function bridge:save/sw6
execute if score #found bridge_tmp matches 0 if score #steps bridge_tmp matches ..60 if block ~ ~ ~ minecraft:air positioned ^ ^ ^0.1 run function bridge:ray/sw6
