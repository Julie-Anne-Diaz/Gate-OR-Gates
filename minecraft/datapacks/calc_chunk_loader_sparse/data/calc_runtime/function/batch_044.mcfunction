execute unless score #running calc_load matches 1 run return 0
execute in minecraft:overworld run forceload add 1408 32
execute in minecraft:overworld run forceload add 1408 48
execute in minecraft:overworld run forceload add 1408 64
execute in minecraft:overworld run forceload add 1408 80
execute in minecraft:overworld run forceload add 1408 96
execute in minecraft:overworld run forceload add 1408 112
execute in minecraft:overworld run forceload add 1408 128
execute in minecraft:overworld run forceload add 1408 144
execute in minecraft:overworld run forceload add 1408 160
execute in minecraft:overworld run forceload add 1408 176
execute in minecraft:overworld run forceload add 1408 192
execute in minecraft:overworld run forceload add 1408 208
execute in minecraft:overworld run forceload add 1408 224
execute in minecraft:overworld run forceload add 1424 -16
execute in minecraft:overworld run forceload add 1424 0
execute in minecraft:overworld run forceload add 1424 16
schedule function calc_runtime:poll 10t replace
