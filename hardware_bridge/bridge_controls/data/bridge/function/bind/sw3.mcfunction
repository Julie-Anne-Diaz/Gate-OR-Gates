scoreboard players set #found bridge_tmp 0
scoreboard players set #steps bridge_tmp 0
execute at @s anchored eyes positioned ^ ^ ^ anchored feet run function bridge:ray/sw3
execute if score #found bridge_tmp matches 0 run tellraw @s {"text":"No lever found within 6 blocks. Aim at its block, or use the stand command.","color":"red"}
