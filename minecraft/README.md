# Minecraft build functions

[`snapshots/redstone.zip`](snapshots/redstone.zip) contains seventeen generated functions from the host's
uploaded `function(2).zip`. The source folder alone lacked pack metadata;
`pack.mcmeta` supplies the Minecraft Java 26.3 datapack wrapper.

These are an **earlier generated snapshot**, including a 51,988-line compact ALU
function. They were not regenerated from the latest source code and do not
include the host's actual world. Verify each circuit's behavior in Minecraft.
Keep the current host world/working pack when copying an exact demo.

The local setup script extracts this snapshot into a normal `redstone` folder
beside the hardware controls pack, so generated functions can be edited/replaced.
For manual installation, extract the ZIP into `world/datapacks/redstone`; its
`pack.mcmeta` must be directly inside that folder.
Run `/reload` as an operator. Then, while standing on the floor in a clear area:

```mcfunction
/function redstone:test_all_gates
/function redstone:and
/function redstone:and_chain
/function redstone:full_adder
/function redstone:mux_2
/function redstone:mux_4
/function redstone:alu_compact
```

Use a fresh empty area for each build; commands replace blocks and generally
extend east (+X) and south (+Z). Relative functions need a player executor.
Large builds can take time and require loaded chunks; propagation delay and
server simulation cost are separate from rendering FPS.

[Full command inventory](CONTENTS.txt) ·
[Generate a new circuit](../docs/HDL_PIPELINE.md) ·
[Copy an existing world](../docs/WORLD_BACKUPS.md)
