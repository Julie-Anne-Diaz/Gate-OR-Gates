execute unless data storage bridge:pulses key1 run scoreboard players set #key1busy bridge_pulse 0
execute unless data storage bridge:pulses key1 run return 0
execute store success score #loaded bridge_pulse run function bridge:pulse/loaded with storage bridge:pulses key1
execute if score #loaded bridge_pulse matches 0 run schedule function bridge:pulse/finish/key1 1s replace
execute if score #loaded bridge_pulse matches 0 run return 0
function bridge:pulse/off with storage bridge:pulses key1
data remove storage bridge:pulses key1
scoreboard players set #key1busy bridge_pulse 2
schedule function bridge:pulse/next/key1 1t replace
