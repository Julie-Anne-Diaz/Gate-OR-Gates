scoreboard objectives add bridge_tmp dummy
scoreboard objectives add bridge_pulse dummy
data modify storage bridge:meta pulse_version set value 2
schedule clear bridge:pulse/next/key0
schedule clear bridge:pulse/finish/key0
scoreboard players set #key0queue bridge_pulse 0
scoreboard players set #key0busy bridge_pulse 0
execute if data storage bridge:pulses key0 run function bridge:pulse/finish/key0
schedule clear bridge:pulse/next/key1
schedule clear bridge:pulse/finish/key1
scoreboard players set #key1queue bridge_pulse 0
scoreboard players set #key1busy bridge_pulse 0
execute if data storage bridge:pulses key1 run function bridge:pulse/finish/key1
