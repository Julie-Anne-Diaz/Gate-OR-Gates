execute unless score #running calc_load matches 1 run return 0
execute in minecraft:overworld run forceload add 288 160
execute in minecraft:overworld run forceload add 288 176
execute in minecraft:overworld run forceload add 288 192
execute in minecraft:overworld run forceload add 288 208
execute in minecraft:overworld run forceload add 288 224
execute in minecraft:overworld run forceload add 288 240
execute in minecraft:overworld run forceload add 288 256
execute in minecraft:overworld run forceload add 288 272
execute in minecraft:overworld run forceload add 288 288
execute in minecraft:overworld run forceload add 288 304
execute in minecraft:overworld run forceload add 288 320
execute in minecraft:overworld run forceload add 288 336
execute in minecraft:overworld run forceload add 288 352
execute in minecraft:overworld run forceload add 288 368
execute in minecraft:overworld run forceload add 288 384
execute in minecraft:overworld run forceload add 288 400
execute in minecraft:overworld run forceload add 288 416
execute in minecraft:overworld run forceload add 288 432
execute in minecraft:overworld run forceload add 288 448
execute in minecraft:overworld run forceload add 288 464
execute in minecraft:overworld run forceload add 288 640
execute in minecraft:overworld run forceload add 288 656
execute in minecraft:overworld run forceload add 288 864
execute in minecraft:overworld run forceload add 304 -16
execute in minecraft:overworld run forceload add 304 0
execute in minecraft:overworld run forceload add 304 16
execute in minecraft:overworld run forceload add 304 32
execute in minecraft:overworld run forceload add 304 48
execute in minecraft:overworld run forceload add 304 112
execute in minecraft:overworld run forceload add 304 128
execute in minecraft:overworld run forceload add 304 144
execute in minecraft:overworld run forceload add 304 160
tellraw @a "CALC occupied chunk requests: 640/1424."
schedule function calc_runtime:batch_020 10t replace
