# Working together

Use feature branches and pull requests so HDL, routing, hardware and documentation
changes can be reviewed independently. Keep each change scoped to its subsystem.

## Before pushing

- Commit HDL, Python, Quartus source projects/pin assignments, Arduino sketches,
  reusable datapacks and documentation.
- Keep runtime worlds, server.properties, passwords, Java/server downloads,
  Python environments, Quartus build databases and logs out of Git.
- Record the Minecraft version when changing datapack syntax or block states.
- Do not replace newer templates/router code with a file from an older function
  archive. Generated snapshots and source changes have different provenance.

## Validate your change

Hardware protocol and setup, from the repository root:

```text
python -m unittest discover -s hardware_bridge/tests -v
```

Pipeline regressions, with Yosys and root requirements installed:

```text
python -m unittest discover -s tests -v
```

Inspect redstone in-game as well as testing logical/geometry output. For a new
or changed gate, check all input combinations and its output behavior. For a
sequential circuit, check reset, capture, hold and clock timing. Passing routing
checks alone does not prove Minecraft physics.

In a pull request, describe the changed behavior, relevant commands/tests, and
any remaining in-game validation. If generated files changed, record their HDL
sources and generator settings. Stop the server before sharing a world backup;
share world ZIPs through team storage instead of committing them.
