execute in minecraft:overworld unless entity @e[type=minecraft:marker,tag=calc_build_dafc0a3dbc,limit=1] run return 0
scoreboard players set #missing calc_job 0
execute in minecraft:overworld as @e[type=minecraft:marker,tag=calc_build_dafc0a3dbc,limit=1] at @s run function calc_builder:job_0134_check_000_local
execute if score #missing calc_job matches 1.. run tellraw @a [{"text":"CALC stopped at job_0134_check_000; missing blocks: "},{"score":{"name":"#missing","objective":"calc_job"}},{"text":". Use /function calc_builder:release to cancel."}]
execute if score #missing calc_job matches 1.. run return 0
schedule function calc_builder:job_0134_batch_001 2t replace
