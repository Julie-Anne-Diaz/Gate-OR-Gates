# Start with the host's existing builds

The clean local workspace creates a new world and includes the earlier generated-function
snapshot. It does not contain the host's current Minecraft world. To share an
exact copy of the current builds, datapacks and saved bindings:

## Host

1. Stop Python with Ctrl+C.
2. In the current server console type `stop`, then wait for it to finish saving.
3. ZIP the entire `world` folder from your existing MinecraftBridge folder.
   If `server.properties` uses a different `level-name`, ZIP that folder instead.
4. Give that world ZIP to your team through your normal file-sharing channel.
   Share the world, not server.properties or the entire used server folder.
5. Restart your own server/bridge if desired.

The world includes player data. Give it to the intended team. Do not copy a
world while its server or a single-player session is using it.

## Receiving teammate

1. Clone/download the repository and run `hardware_bridge/01_Setup.bat` once.
2. Keep both your old server and the new local workspace server stopped.
3. Extract the shared ZIP elsewhere. Identify the folder directly containing
   `level.dat` (often a folder named `world`).
4. Rename the local workspace's `hardware_bridge/runtime/world` to `world_backup` if you want to keep it.
5. Copy the received world folder to `hardware_bridge/runtime/world`. Ensure the result is
   `hardware_bridge/runtime/world/level.dat`, not `hardware_bridge/runtime/world/world/level.dat`.
6. Keep the received world's working redstone datapack. If it lacks the current
   controls pack, copy this repository's `hardware_bridge/bridge_controls` into
   `hardware_bridge/runtime/world/datapacks/bridge_controls`. Do not replace a newer gate pack
   with the older generated-function snapshot bundled in this local workspace.
7. Start `hardware_bridge/02_Start.bat` and join localhost using Minecraft Java 26.3.
8. Grant yourself operator access in your own server console: `op YourName`.
9. Inspect/rebind inputs for your intended circuit. Bindings were copied with
   the world, but your physical hardware is now controlling your independent copy.

Your RCON password, Arduino port, Java path and server RAM remain local settings.
Nothing needs to connect to the original host's PC. Do not merge region files
from two different worlds. Keep a backup before changing Minecraft versions.
