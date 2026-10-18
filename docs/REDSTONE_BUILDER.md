# Set up the redstone builder datapack

There are two separate packs. **The builder places circuits**; **bridge_controls
assigns physical switches and buttons to the circuits' input levers**. Both packs
must be inside the same Minecraft world's `datapacks` folder.

## Where the builder belongs in the repository

When the team supplies its current complete builder pack, put it at:

```text
minecraft/datapacks/redstone/
```

Its `pack.mcmeta` must be directly inside that folder. For example:

| Repository path | Purpose |
|---|---|
| `minecraft/datapacks/redstone/pack.mcmeta` | Declares the complete builder datapack |
| `minecraft/datapacks/redstone/data/redstone/function/and.mcfunction` | Places an AND build |
| `minecraft/datapacks/redstone/data/redstone/function/alu_compact.mcfunction` | Places the ALU snapshot/example |
| `hardware_bridge/bridge_controls/pack.mcmeta` | Declares the separate controls pack |

Copy the team's actual complete folder, including any tags, helper functions,
storage initialization or other supporting files. Do not submit just its
`function` subfolder. Keep its existing namespace and filenames; `redstone`
is the namespace used by the supplied examples, not a requirement to rename
another working pack. Any external dependencies should be documented with it.
Minecraft Java 26.3 uses the singular directory name **`function`**.

**Current PR content:** `minecraft/snapshots/redstone.zip` contains the earlier
seventeen-function snapshot. The team's newest builder folder has not yet been
provided. Setup prefers `minecraft/datapacks/redstone` when it exists; otherwise
it extracts the bundled snapshot. It installs one builder pack, not both copies.

## Option A: automatic installation into a new local workspace

1. Obtain the repository, including the chosen builder source/snapshot and the
   controls pack. Complete the [local setup](LOCAL_WORKSPACE.md).
2. With the local server stopped, run `hardware_bridge/01_Setup.bat`.
3. On first setup, it installs both packs here:

   | Installed location | Pack |
   |---|---|
   | `hardware_bridge/runtime/world/datapacks/redstone/` | Circuit builder |
   | `hardware_bridge/runtime/world/datapacks/bridge_controls/` | Physical input controls |

4. Run `hardware_bridge/02_Start.bat` and join `localhost` with Minecraft Java 26.3.
5. In the server console, type `op YourMinecraftName` if you have not already
   enabled commands for yourself. Console commands have no leading slash.
6. In Minecraft chat, run:

   ```mcfunction
   /reload
   /datapack list enabled
   ```

   Both the builder and controls should appear. If one is shown as available
   rather than enabled, use the exact pack name printed by `/datapack list
   available`, for example `/datapack enable "file/redstone"`, then reload.

Setup deliberately preserves a builder already installed in a runtime world.
Adding a newer source folder to Git does not overwrite that runtime copy; use
the update instructions below.

## Option B: install into an existing world

1. Stop the server with `stop` and wait for world saving. Back up the world.
2. Find that world's `datapacks` folder. For the starter, it is
   `hardware_bridge/runtime/world/datapacks`. For the host's existing setup, it
   is `Documents/MinecraftBridge/world/datapacks`. If `level-name` was changed,
   use that world directory instead. For single-player, use the world's own
   `datapacks` folder inside `.minecraft/saves`.
3. Copy the complete builder folder there as `redstone` (or keep its actual
   existing pack folder name). If using the snapshot, extract its contents into
   `datapacks/redstone` so `pack.mcmeta` sits directly inside `redstone`.
4. Copy the complete `hardware_bridge/bridge_controls` folder alongside it.
   Do not put bridge_controls inside the redstone folder, or vice versa.
5. Ensure you have one copy of each pack: a folder and ZIP with the same content
   can both load and cause confusing overrides. Move old backups outside the
   world's `datapacks` folder.
6. Start the server, join, and run `/reload` and `/datapack list enabled`.

## Place a gate, mux, or ALU

1. Switch to creative mode if needed: `/gamemode creative`.
2. Stand on the floor in a large empty area. The supplied player-relative builds
   start at aligned player feet and generally extend east (+X) and south (+Z),
   regardless of where you look. Commands replace existing blocks.
3. Begin with a small build, in **Minecraft chat**:

   ```mcfunction
   /function redstone:and
   ```

4. Try other included functions in separate empty areas:

   ```mcfunction
   /function redstone:test_all_gates
   /function redstone:full_adder
   /function redstone:mux_2
   /function redstone:mux_4
   /function redstone:alu_compact
   ```

   The team's newer pack may use different names. Type `/function redstone:`
   and use autocomplete to see loaded functions. A nested function file such as
   `data/redstone/function/gates/and.mcfunction` is called as `redstone:gates/and`.
5. Wait for placement and redstone to settle. Large ALUs need substantial clear,
   loaded space. Use a fresh area when rebuilding: placement does not remove
   obsolete blocks from an older layout. Check the circuit's expected behavior.

Run the supplied builds from player chat because their commands use `@s` for
player-relative placement. Running them directly in the server console has no
player executor. If you need the console, explicitly select the intended player:

```text
execute as YourMinecraftName at @s run function redstone:and
```

## Connect the physical board

Start the Python bridge with the programmed UNO connected and Serial Monitor
closed. Look at a floor-mounted input lever, then assign a control:

```mcfunction
/function bridge:bind/sw0
```

Repeat with `sw1` through `sw9` as needed. For pulse inputs, point at separate
levers and run `bridge:bind/key0` and `bridge:bind/key1`. Do not assign two
hardware controls to the same lever. The builder places the circuit; binding
chooses which of its inputs the physical board drives. Bindings persist with
the world, but a moved/rebuilt circuit may require rebinding its new levers.

## Update the builder later

1. Stop the server and back up its world and existing builder pack.
2. Replace only the runtime builder folder with the current complete team pack.
   Keep `bridge_controls` as its own separate pack.
3. Start the server and `/reload`. Check both packs are enabled and check function
   autocomplete. Existing built blocks are not automatically updated by replacing
   the pack: run the new build function in a fresh area and rebind inputs.

For a single new export, copy its `.mcfunction` into the runtime builder's
`data/<namespace>/function` directory, reload and run it. Generating more circuits
is covered by the [HDL pipeline reference](HDL_PIPELINE.md).

## Troubleshooting

| Problem | Check |
|---|---|
| Pack absent from the list | `pack.mcmeta` must be directly inside the installed pack; check for an extra nested folder |
| Unknown `/function` | Correct namespace/file name, singular `function` directory, `/reload`, and errors in the server log |
| Pack listed but function missing | A syntax error may prevent that function from loading; inspect `runtime/logs/latest.log` |
| No permission | `op YourName` in the server console, then use slash commands in chat |
| Function runs but nothing builds | Use player chat, stand on the floor, and check function errors in the log |
| Old layout still appears | Remove duplicate packs and verify which runtime copy was updated; setup preserves existing packs |
| Built lever has no hardware response | Start the bridge, verify COM/firmware, and bind the actual input lever |

An ordinary single-player world can run the builder with commands allowed. The
physical input bridge in this project uses the separate local-server solution.
