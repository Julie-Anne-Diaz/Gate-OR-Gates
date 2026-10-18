execute unless score #running calc_load matches 1 run return 0
execute in minecraft:overworld run forceload add 768 32
execute in minecraft:overworld run forceload add 768 48
execute in minecraft:overworld run forceload add 768 64
execute in minecraft:overworld run forceload add 768 80
execute in minecraft:overworld run forceload add 768 96
execute in minecraft:overworld run forceload add 768 112
execute in minecraft:overworld run forceload add 768 128
execute in minecraft:overworld run forceload add 768 144
execute in minecraft:overworld run forceload add 768 160
execute in minecraft:overworld run forceload add 768 176
execute in minecraft:overworld run forceload add 768 192
execute in minecraft:overworld run forceload add 768 208
execute in minecraft:overworld run forceload add 768 224
execute in minecraft:overworld run forceload add 768 240
execute in minecraft:overworld run forceload add 768 864
execute in minecraft:overworld run forceload add 784 -16
execute in minecraft:overworld run forceload add 784 0
execute in minecraft:overworld run forceload add 784 16
execute in minecraft:overworld run forceload add 784 96
execute in minecraft:overworld run forceload add 784 128
execute in minecraft:overworld run forceload add 784 144
execute in minecraft:overworld run forceload add 784 160
execute in minecraft:overworld run forceload add 784 192
execute in minecraft:overworld run forceload add 784 240
execute in minecraft:overworld run forceload add 784 864
execute in minecraft:overworld run forceload add 800 -16
execute in minecraft:overworld run forceload add 800 0
execute in minecraft:overworld run forceload add 800 16
execute in minecraft:overworld run forceload add 800 96
execute in minecraft:overworld run forceload add 800 128
execute in minecraft:overworld run forceload add 800 144
execute in minecraft:overworld run forceload add 800 160
tellraw @a "CALC occupied chunk requests: 960/1424."
schedule function calc_runtime:batch_030 10t replace
