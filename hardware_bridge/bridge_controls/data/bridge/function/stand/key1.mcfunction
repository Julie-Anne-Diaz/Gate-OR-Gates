scoreboard players set #found bridge_tmp 0
execute at @s if block ~ ~ ~ minecraft:lever run function bridge:save/key1
execute if score #found bridge_tmp matches 0 at @s positioned ~ ~-1 ~ if block ~ ~ ~ minecraft:lever run function bridge:save/key1
execute if score #found bridge_tmp matches 0 run tellraw @s {"text":"Stand directly over the lever block first.","color":"red"}
