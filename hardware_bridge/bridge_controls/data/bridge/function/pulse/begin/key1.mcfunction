execute unless data storage bridge:bindings key1 run scoreboard players set #key1queue bridge_pulse 0
execute unless data storage bridge:bindings key1 run scoreboard players set #key1busy bridge_pulse 0
execute unless data storage bridge:bindings key1 run return 0
scoreboard players remove #key1queue bridge_pulse 1
scoreboard players set #key1busy bridge_pulse 1
data modify storage bridge:pulses key1 set from storage bridge:bindings key1
function bridge:pulse/on with storage bridge:pulses key1
schedule function bridge:pulse/finish/key1 4t replace
