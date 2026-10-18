scoreboard objectives add calc_load dummy
function calc_runtime:scan
tellraw @a [{"text":"Occupied CALC chunks loaded: "},{"score":{"name":"#loaded","objective":"calc_load"}},{"text":" / 1424."}]
execute if score #loaded calc_load matches 1424 run tellraw @a "All occupied CALC chunks loaded. Keep the loader active and allow signals to settle."
