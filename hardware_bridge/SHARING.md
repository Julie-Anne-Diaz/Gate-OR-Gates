# Share the demo and project with the team

## Let teammates join the running demo

Use the existing vanilla Minecraft Java 26.3 server and its current world.
The host keeps the server, Python bridge, DE10-Lite, and Arduino running.

1. Start the server and confirm the host can join `localhost`.
2. Download the Windows Playit agent from [playit.gg](https://playit.gg/download),
   run it, and follow its browser link to create/sign in to your own account and
   link the agent. Keep Playit account details private.
3. Add a **Minecraft Java** tunnel. Set its local address to **127.0.0.1** and
   local port to **25565** (or your actual game port if you changed it). Keep
   the existing `server-ip=127.0.0.1` for this tunnel setup.
4. Keep the Playit agent running. Share its assigned public game address with
   teammates. Include its assigned port if the dashboard provides one.
5. Teammates use Minecraft **Java 26.3 → Multiplayer → Add Server** and enter
   that address. Only the host runs Playit; teammates need no client software.
6. The host can continue joining `localhost`. Everyone sees the same world and
   reactions to the host's physical switches and keys.

Tunnel the **game port 25565 only**. Do not expose RCON 25575 or share its password.
Keep `online-mode=true`. Router port forwarding is not required for Playit.
If the host's PC sleeps or the server/agent stops, the demo is unavailable.
The Python bridge is only needed for hardware control; the game server and
ordinary redstone continue to work when Python is stopped.

For a team-only session, first add your own and your teammates' Minecraft names
in the server console (no `/`), then enable the whitelist:

```text
whitelist add YourMinecraftName
whitelist add TeammateMinecraftName
whitelist on
```

If you leave the whitelist disabled, anyone who has the game address can try to
join. Ordinary players do not need `op` to join or watch. Give trusted builders
operator access individually only if they need `/function` or other admin
commands; operator privileges also allow broader server changes.

Playit's own [Minecraft guide](https://playit.gg/support/how-to-setup-a-mc-server/)
and [download page](https://playit.gg/download) describe public game tunneling.
Tunnel labels/UI can change; the destination remains your local game port.

## Share the existing built world

The repository contains source code and control datapacks. Your running world
is a separate artifact on the host PC; cloning the repository does not copy it.

1. Stop Python with Ctrl+C.
2. Type `stop` in the Minecraft server console and wait for it to exit so its
   world files are saved consistently.
3. In `Documents\MinecraftBridge`, right-click the entire `world` folder and
   choose **Compress to ZIP file** (or **Send to → Compressed (zipped) folder**).
   If `level-name` in server.properties is different, use that world folder.
4. Give the world ZIP to the team through your normal file-sharing channel.
   It includes builds, world data, datapacks and persistent lever bindings.
   It also contains player data; share it with the intended team.
5. Restart the server, Python and Playit for the live demo.

To use a copy on another server, stop that server first, back up its current
world, and extract the shared world as the configured `level-name` directory.
Use the same Minecraft version. Do not merge two worlds' region directories.
The receiving host sets their own local RCON password/COM port if using hardware.
Saved bindings refer to coordinates in the copied world, not a new empty world.
To open a copy in single-player, extract the world folder into `.minecraft/saves`;
it should directly contain `level.dat`. Building functions work with commands
allowed; external serial control still uses the dedicated-server RCON setup.

## Share code in GitHub

This `hardware_bridge/` folder contains the working bridge, its dedicated Python
dependencies, FPGA project/pin assignments, Arduino sketch, controls datapack,
launch scripts, tests and instructions. It is separate from the HDL placement
and routing pipeline at the repository root.

The host's actual generated gate datapack is another deliverable: copy the
complete working redstone pack from `world/datapacks` into a source folder such
as `datapacks/redstone/` if it isn't already tracked. Keep its `pack.mcmeta` and
`data/<namespace>/function` structure. Do not replace the newer gate catalog or
router code with an older copy from a function ZIP.

Do not commit server.properties (contains the RCON password), Playit credentials,
Python virtual environments, downloaded server JARs, runtime libraries/logs,
or large world saves. The hardware folder includes ignore rules for its runtime
files. If the runtime lives elsewhere in the repo, add matching ignore rules
there too. Keep demo world ZIPs in team file storage instead.

The host's live world and generated gate pack must be copied from their PC;
those current bytes are not included automatically by this hardware integration.
