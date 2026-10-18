execute unless data storage bridge:pulses key0 run scoreboard players set #key0busy bridge_pulse 0
execute unless data storage bridge:pulses key0 run return 0
execute store success score #loaded bridge_pulse run function bridge:pulse/loaded with storage bridge:pulses key0
execute if score #loaded bridge_pulse matches 0 run schedule function bridge:pulse/finish/key0 1s replace
execute if score #loaded bridge_pulse matches 0 run return 0
function bridge:pulse/off with storage bridge:pulses key0
data remove storage bridge:pulses key0
scoreboard players set #key0busy bridge_pulse 2
schedule function bridge:pulse/next/key0 1t replace
