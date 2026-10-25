# analog-canvas-extensions

The package `analog-canvas-extensions` 0.2, [`analog-canvas-extensions.rnl`](analog-canvas-extensions.rnl): the symbols of Analog Canvas that the standard series 0.3 does not draw. They are its appearance variants of standard symbols and its chopper; since 0.2 the package also defines four facts of Analog Canvas's drawings that the netlist does not keep (below). It is not part of the standard series: a file that uses it names it in its header record, `@USE-PACKAGE(name="analog-canvas-extensions", version="0.2")` (16.2), as Analog Canvas does in the files it exports. It is a public package rather than a built-in package; the file must be included in the Library/pool or supplied on a search path.

Each symbol is named `$CANVAS_` and the Analog Canvas component it draws, and comments in the file give that component and the order of its pins. The controlled sources of two terminals are here in both drawings: the standard series 0.3 draws `$VCVS`, `$VCCS`, `$CCVS` and `$CCCS` as diamonds, and `$CANVAS_*_DIAMOND` draw the same, while `$CANVAS_*_CIRCLE` draw the circle that the series drew before, Analog Canvas's own, so that a netlist written with it round-trips; the pins, the boxes and the labels of the circles are those of the series' symbols of that time. Pins bind by terminal number, so each symbol fits either dialect. Coordinates are y-up, one unit a grid step, ten Analog Canvas units.

| Symbols | Count |
| --- | --- |
| Op amps and comparators: `$CANVAS_OPAMP_LETTERED`, `$CANVAS_OPAMP_WIDE`, `$CANVAS_OPAMP_WIDE_LETTERED`, `$CANVAS_COMPARATOR_UNMARKED`, and seven fully differential op amps, `$CANVAS_OPAMP_DIFFERENTIAL_…` (crossed, lettered, wide, and their combinations) | 11 |
| `$CANVAS_VOLTAGE_AMPLIFIER_LETTERED` | 1 |
| `$CANVAS_INDUCTOR_LARGE`, `$CANVAS_PULSE_VOLTAGE_SOURCE`, and the diamond sources `$CANVAS_CURRENT_SOURCE_DIAMOND`, `$CANVAS_VCVS_DIAMOND`, `$CANVAS_VCCS_DIAMOND`, `$CANVAS_CCVS_DIAMOND`, `$CANVAS_CCCS_DIAMOND` | 7 |
| The controlled sources in Analog Canvas's circle: `$CANVAS_VCVS_CIRCLE`, `$CANVAS_VCCS_CIRCLE`, `$CANVAS_CCVS_CIRCLE`, `$CANVAS_CCCS_CIRCLE` | 4 |
| `$CANVAS_SIMPLE_SWITCH`, `$CANVAS_SIMPLE_SPDT_SWITCH` (a drawing of `$SPDT_SWITCH`), `$CANVAS_PORT_FILLED` (a drawing of `$IO_PORT`) | 3 |
| `$CANVAS_CHOPPER` | 1 |
| The gates with four inputs as Analog Canvas draws them: `$CANVAS_AND_4INPUT`, `$CANVAS_NAND_4INPUT`, `$CANVAS_OR_4INPUT`, `$CANVAS_NOR_4INPUT`, `$CANVAS_XOR_4INPUT`, `$CANVAS_XNOR_4INPUT` | 6 |

The file is written by `build-std.mjs` in rnl-dev, with the standard series 0.3, from Analog Canvas's definitions and its symbol list; a symbol that Analog Canvas adds to the list is written the same way and taken here, such as the diamond VCVS and CCVS (Analog Canvas #1740). It is written in the language 0.3, as the series is. As in the standard series 0.3, any box side with pins lies on the outermost pin of that side while sides without pins keep their drawing margin (existing solver records written against the old padded boxes will be flagged as not matching the current input). The six gates keep Analog Canvas's spacing of their inputs, `y` = 1.2, 0.4, −0.4 and −1.2, while the standard gates with four inputs of `rnl-std-logic` have theirs on integer points. Checked on its own, the package gives a hint for each of those 24 pins (9.2.4) and nothing else.

## Meaning only, since 0.2

Four general definitions (9.4) with an empty body and no symbol. Analog Canvas attaches them so that a file it writes comes back to it unchanged. A usage of them draws nothing and constrains nothing: a tool that does not know them reads the file as if the usage were not there, and may list it as a semantic usage. Another tool that edits the file leaves them as they are, or drops them with the objects they are attached to.

| Definition | Role | Parameters | Meaning |
| --- | --- | --- | --- |
| `$CANVAS_NAME` | `part`, an instance | `name` | The name Analog Canvas gives the part where the netlist must spell it otherwise, such as `M1` for the SPICE card `XM1`: `$CANVAS_NAME @ATTACH(name="M1") #XM1` |
| `$CANVAS_LABEL` | `label`, a label | `bind`: `"name"`, `"value"`, `"parameter"`, `"net"` or `"port"`; `parameter`, the parameter's name for `"parameter"`; `show_value`, false to show the parameter's name only | The label's text is that fact of the drawing, set as Analog Canvas sets names, and follows it there; the text written in the TEXT is what every viewer shows: `$CANVAS_LABEL @ATTACH(bind="name") #XM1::name` |
| `$CANVAS_TYPESETTING` | `level`, the level (a lone `#`) | `subscript_case` (`"preserve"`, `"uppercase"`, `"lowercase"`), `subscript_italic`, `underscore_subscript`, `subscript_after_first`, `first_letter_italic`, `face` (`"serif"`) | How Analog Canvas sets the names in labels in that level; a parameter left out is Analog Canvas's default. Like the rest of a level's RNL it reaches the levels the level contains (6.1), where their own usage, written later, gives theirs: `$CANVAS_TYPESETTING @ATTACH(subscript_italic=false) #` |
| `$CANVAS_PARAMETER_TEXT` | `part`, an instance | `name`, `text` | The text the author wrote for a parameter where the netlist writes it otherwise, such as `100fF`, which Spectre takes as `100f`: `$CANVAS_PARAMETER_TEXT @ATTACH(name="c", text="100fF") #CCM` |

The parameters have no defaults: Analog Canvas writes only what differs from its own defaults.

Like the rest of `libraries/`, it is under CC0-1.0 ([`REUSE.toml`](../../REUSE.toml)).

This package is not built into the core. In a viewer, include its file in Library (the web viewer also offers File › Include Public Package…). In the CLI, pass `--path libraries/analog-canvas-extensions`. In an npm frontend, add the separately shipped package file to the build request’s `files` and `pool`.
