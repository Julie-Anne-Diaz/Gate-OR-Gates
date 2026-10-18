scoreboard players set #found bridge_tmp 1
kill @e[type=minecraft:marker,tag=bridge_temp]
execute align xyz run summon minecraft:marker ~0.5 ~0.5 ~0.5 {Tags:["bridge_temp"]}
data modify storage bridge:bindings sw4 set value {x:0,y:0,z:0,dimension:"minecraft:overworld",face:"floor",facing:"west"}
execute store result storage bridge:bindings sw4.x int 1 run data get entity @e[type=minecraft:marker,tag=bridge_temp,limit=1] Pos[0] 1
execute store result storage bridge:bindings sw4.y int 1 run data get entity @e[type=minecraft:marker,tag=bridge_temp,limit=1] Pos[1] 1
execute store result storage bridge:bindings sw4.z int 1 run data get entity @e[type=minecraft:marker,tag=bridge_temp,limit=1] Pos[2] 1
execute if dimension minecraft:overworld run data modify storage bridge:bindings sw4.dimension set value "minecraft:overworld"
execute if dimension minecraft:the_nether run data modify storage bridge:bindings sw4.dimension set value "minecraft:the_nether"
execute if dimension minecraft:the_end run data modify storage bridge:bindings sw4.dimension set value "minecraft:the_end"
execute if block ~ ~ ~ minecraft:lever[face=floor] run data modify storage bridge:bindings sw4.face set value "floor"
execute if block ~ ~ ~ minecraft:lever[face=wall] run data modify storage bridge:bindings sw4.face set value "wall"
execute if block ~ ~ ~ minecraft:lever[face=ceiling] run data modify storage bridge:bindings sw4.face set value "ceiling"
execute if block ~ ~ ~ minecraft:lever[facing=north] run data modify storage bridge:bindings sw4.facing set value "north"
execute if block ~ ~ ~ minecraft:lever[facing=south] run data modify storage bridge:bindings sw4.facing set value "south"
execute if block ~ ~ ~ minecraft:lever[facing=east] run data modify storage bridge:bindings sw4.facing set value "east"
execute if block ~ ~ ~ minecraft:lever[facing=west] run data modify storage bridge:bindings sw4.facing set value "west"
kill @e[type=minecraft:marker,tag=bridge_temp]
tellraw @s {"text":"SW4 bound. Python will apply its state within about a second.","color":"green"}
