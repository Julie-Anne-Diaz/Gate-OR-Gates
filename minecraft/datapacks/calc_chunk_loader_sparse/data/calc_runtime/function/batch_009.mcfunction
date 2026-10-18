execute unless score #running calc_load matches 1 run return 0
execute in minecraft:overworld run forceload add 128 80
execute in minecraft:overworld run forceload add 128 96
execute in minecraft:overworld run forceload add 128 112
execute in minecraft:overworld run forceload add 128 128
execute in minecraft:overworld run forceload add 128 144
execute in minecraft:overworld run forceload add 128 160
execute in minecraft:overworld run forceload add 128 176
execute in minecraft:overworld run forceload add 128 192
execute in minecraft:overworld run forceload add 128 208
execute in minecraft:overworld run forceload add 128 240
execute in minecraft:overworld run forceload add 128 256
execute in minecraft:overworld run forceload add 128 288
execute in minecraft:overworld run forceload add 128 304
execute in minecraft:overworld run forceload add 128 320
execute in minecraft:overworld run forceload add 128 336
execute in minecraft:overworld run forceload add 128 352
execute in minecraft:overworld run forceload add 128 368
execute in minecraft:overworld run forceload add 128 384
execute in minecraft:overworld run forceload add 128 400
execute in minecraft:overworld run forceload add 128 416
execute in minecraft:overworld run forceload add 128 432
execute in minecraft:overworld run forceload add 128 448
execute in minecraft:overworld run forceload add 128 464
execute in minecraft:overworld run forceload add 128 480
execute in minecraft:overworld run forceload add 128 496
execute in minecraft:overworld run forceload add 128 512
execute in minecraft:overworld run forceload add 128 528
execute in minecraft:overworld run forceload add 128 544
execute in minecraft:overworld run forceload add 128 560
execute in minecraft:overworld run forceload add 128 576
execute in minecraft:overworld run forceload add 128 592
execute in minecraft:overworld run forceload add 128 608
tellraw @a "CALC occupied chunk requests: 320/1424."
schedule function calc_runtime:batch_010 10t replace
