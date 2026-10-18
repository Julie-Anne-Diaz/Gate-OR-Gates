execute unless data storage bridge:bindings key0 run return 0
execute if score #key0queue bridge_pulse matches 32.. run return 0
scoreboard players add #key0queue bridge_pulse 1
execute if score #key0busy bridge_pulse matches 0 run function bridge:pulse/begin/key0
