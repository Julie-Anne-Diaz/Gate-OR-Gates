# Sharing with the team

The default is **one independent local workspace per teammate**. Clone/download
this repository, follow [setup](../docs/LOCAL_WORKSPACE.md), then join `localhost`.
No teammate needs to keep another person's PC running. Their own physical
hardware controls their own world.

For an exact copy of the host's current builds, use the
[world backup guide](../docs/WORLD_BACKUPS.md). A Git clone contains source and
sample functions, not a running world or private RCON configuration.

If the team later wants to watch one shared live demo, the host can optionally
use a [Playit Minecraft Java tunnel](https://playit.gg/support/how-to-setup-a-mc-server/)
to local game port 25565. Visitors then use the supplied public game address
rather than localhost. Only the host runs the agent and hardware. Keep RCON
25575 and its password private. This is optional, not needed for reproduction.
