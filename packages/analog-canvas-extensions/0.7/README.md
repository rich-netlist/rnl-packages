# analog-canvas-extensions

The package `analog-canvas-extensions` 0.7, [`analog-canvas-extensions.rnl`](analog-canvas-extensions.rnl): Analog Canvas's own package for the language 0.4. It holds what the standard series 0.4 does not draw or keep. A file that uses it names it in its header record, `@USE-PACKAGE(name="analog-canvas-extensions", version="0.7")` (16.2), as Analog Canvas does in the files it exports. It is written in the language 0.4, so only a file of 0.4 can use it (decision 0017). The earlier versions, 0.1 to 0.6, are packages of 0.3.

What it holds:
- **Appearance variants of standard symbols**, each named `$CANVAS_` and the Analog Canvas component it draws: the lettered and wide op-amps, the unmarked comparator, the fully differential op-amps other than the twisted one, the lettered voltage amplifier, the large inductor, the simple switches, the filled port, the current-source diamond and the controlled sources in Analog Canvas's circle.
- **Analog Canvas's four-input gates**, with its spacing of the inputs.
- **Its four-terminal MOSFETs**, with the body pin at (1, 0).
- **The definitions of meaning only** that bring a file it wrote back to it unchanged.

Since 0.7, the parts the standard series 0.4 now draws are no longer here: the crystal, the polarized capacitor, the other parts 0.5 and 0.6 added, the controlled-source diamonds, the pulse source, the chopper and the twisted differential op-amp. Every pin binds the terminal of its name, as the standard symbols of 0.4 do (9.2.4). Coordinates are y-up; one unit is one grid step, ten Analog Canvas units.
