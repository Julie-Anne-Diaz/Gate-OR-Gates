scoreboard players set #key0busy bridge_pulse 0
execute if score #key0queue bridge_pulse matches 1.. run function bridge:pulse/begin/key0
