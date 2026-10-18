execute unless data storage bridge:bindings key0 run scoreboard players set #key0queue bridge_pulse 0
execute unless data storage bridge:bindings key0 run scoreboard players set #key0busy bridge_pulse 0
execute unless data storage bridge:bindings key0 run return 0
scoreboard players remove #key0queue bridge_pulse 1
scoreboard players set #key0busy bridge_pulse 1
data modify storage bridge:pulses key0 set from storage bridge:bindings key0
function bridge:pulse/on with storage bridge:pulses key0
schedule function bridge:pulse/finish/key0 4t replace
