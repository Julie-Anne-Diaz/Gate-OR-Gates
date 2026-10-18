execute unless data storage bridge:bindings key1 run return 0
execute if score #key1queue bridge_pulse matches 32.. run return 0
scoreboard players add #key1queue bridge_pulse 1
execute if score #key1busy bridge_pulse matches 0 run function bridge:pulse/begin/key1
