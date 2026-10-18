execute unless score #running calc_load matches 1 run return 0
function calc_runtime:scan
tellraw @a [{"text":"Occupied CALC chunks loaded: "},{"score":{"name":"#loaded","objective":"calc_load"}},{"text":" / 1424."}]
execute if score #loaded calc_load matches 1424 run return run tellraw @a "All 1424 occupied CALC chunks loaded. They stay force-loaded until /function calc_runtime:stop."
scoreboard players add #polls calc_load 1
execute if score #polls calc_load matches 60.. run return run tellraw @a "Some chunks are still unavailable. Tickets remain active. Use calc_runtime:check or calc_runtime:stop."
schedule function calc_runtime:poll 100t replace
