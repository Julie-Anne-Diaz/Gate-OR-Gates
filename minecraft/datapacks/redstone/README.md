# Add the team builder functions here

Put the generated **`.mcfunction`** files inside `data/redstone/function/`.
For example, `data/redstone/function/alu.mcfunction` runs as `/function redstone:alu`.
Keep `pack.mcmeta` here at the pack root. Include any helper functions or tags
needed by the builds, and keep their namespace/path conventions.

The placeholder file only keeps the empty directory visible in Git. Setup uses
the bundled snapshot until at least one `.mcfunction` is supplied here. Once
functions exist, setup copies this complete pack instead. Existing installed
runtime packs are preserved and must be updated manually.

See [builder setup](../../../docs/REDSTONE_BUILDER.md) for installation and updates.
