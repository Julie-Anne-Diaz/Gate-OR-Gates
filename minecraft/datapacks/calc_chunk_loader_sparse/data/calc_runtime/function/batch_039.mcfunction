execute unless score #running calc_load matches 1 run return 0
execute in minecraft:overworld run forceload add 1104 192
execute in minecraft:overworld run forceload add 1104 224
execute in minecraft:overworld run forceload add 1104 240
execute in minecraft:overworld run forceload add 1120 -16
execute in minecraft:overworld run forceload add 1120 0
execute in minecraft:overworld run forceload add 1120 16
execute in minecraft:overworld run forceload add 1120 96
execute in minecraft:overworld run forceload add 1120 144
execute in minecraft:overworld run forceload add 1120 160
execute in minecraft:overworld run forceload add 1120 176
execute in minecraft:overworld run forceload add 1120 224
execute in minecraft:overworld run forceload add 1120 240
execute in minecraft:overworld run forceload add 1136 -16
execute in minecraft:overworld run forceload add 1136 0
execute in minecraft:overworld run forceload add 1136 16
execute in minecraft:overworld run forceload add 1136 96
execute in minecraft:overworld run forceload add 1136 144
execute in minecraft:overworld run forceload add 1136 160
execute in minecraft:overworld run forceload add 1136 176
execute in minecraft:overworld run forceload add 1136 192
execute in minecraft:overworld run forceload add 1136 208
execute in minecraft:overworld run forceload add 1136 224
execute in minecraft:overworld run forceload add 1136 240
execute in minecraft:overworld run forceload add 1152 -16
execute in minecraft:overworld run forceload add 1152 0
execute in minecraft:overworld run forceload add 1152 16
execute in minecraft:overworld run forceload add 1152 80
execute in minecraft:overworld run forceload add 1152 96
execute in minecraft:overworld run forceload add 1152 112
execute in minecraft:overworld run forceload add 1152 128
execute in minecraft:overworld run forceload add 1152 144
execute in minecraft:overworld run forceload add 1152 160
tellraw @a "CALC occupied chunk requests: 1280/1424."
schedule function calc_runtime:batch_040 10t replace
