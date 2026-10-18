scoreboard players set #key1busy bridge_pulse 0
execute if score #key1queue bridge_pulse matches 1.. run function bridge:pulse/begin/key1
