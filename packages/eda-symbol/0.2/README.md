# eda-symbol

[`eda-symbol.rnl`](eda-symbol.rnl) is the public package `eda-symbol` 0.2 for RNL 0.4: 133 schematic symbol definitions and instance/usage selection rules. Drawings contain geometry, pins and text anchors, with no fixed colors, line widths or terminal squares. The package can be used independently of [`eda-style`](../../eda-style/0.2/README.md), and is not built into the core.

| Definitions | Count |
| --- | ---: |
| Symbols with the names of the standard series 0.4 | 88 |
| Additional sources, switches, amplifiers, RF parts and filters | 45 |
| Total symbols | 133 |

## Use

A file of RNL 0.4 names the standard collection and both EDA packages in its header record (use `*` instead of `//` in SPICE):

```spectre
// @RNL(type="header") {
//   @VERSION("0.4");
//   @USE-PACKAGE(name="rnl-std-all", version="0.4");
//   @USE-PACKAGE(name="eda-symbol", version="0.2");
//   @USE-PACKAGE(name="eda-style", version="0.2")
// }
```

The package references `rnl-std-basic` and `rnl-std-signal-flow` 0.4 for the definitions its rules select, such as `$GROUND`, `$IO_PORT` and `$INTEGRATOR`. Its symbol definitions **replace the standard symbols of the same names**, including `$RESISTOR`, `$DIODE`, `$NMOS_4TERM` and `$D_FLIP_FLOP`, at the using level and below; hiding-definition hints are expected. Its rules write `recursive=true`, so they reach every level below the one that uses the package (RNL 0.4, 10.4 and 16.2).

```sh
rnl check packages/eda-symbol/0.2/eda-symbol.rnl
rnl render your-netlist.scs --path packages/eda-symbol/0.2 -o out/symbols
```

## Pins and terminals

Every pin keeps the coordinates and direction it has in 0.1, except in the diodes and the transformer, which stand upright as in the standard series 0.4 (see below). What changes is what a pin binds:

- The 88 symbols that share a name with the standard series 0.4 bind its terminal names, such as `p n` for passives and sources, `d g s b` for MOS, `c b e` for bipolar transistors, `a k` for diodes, `p n cp cn` for controlled sources and switches and `p1 n1 p2 n2` for transformers and transmission lines. A file that replaces `eda-symbol` with the standard symbols therefore keeps its terminal references.
- `$VSIN`, `$ISIN`, `$VPULSE`, `$IPULSE`, `$VPWL`, `$IPWL` (`p n`), `$SCHOTTKY` (`a k`) and `$NPN4` (`c b e s`) bind the terminal names of the Spectre primitive or model family they draw.
- The other eda-only symbols, for masters without standard terminal names, bind terminal numbers and match by position.
- Usage symbols bind the roles of their definitions by name. The pin of `$GROUND_SYMBOL`, `$SUPPLY_SYMBOL`, `$IO_PORT_SYMBOL`, `$IPIN` and `$OPIN` is named `pin` (`%g::pin`), and their net-name texts use `key="netname"` and `${p}`. The signal-flow symbols bind `in`, `in1`, `in2` and `out`. `$SPDT_SWITCH_SYMBOL` draws the figure `$SPDT_SWITCH`; its pins `com`, `a` and `b` bind nothing.

The instance rules write `@SET-SYMBOL(terminals=[…])` in node order (RNL 0.4, 11.3), so a symbol chosen by model, model type or SPICE letter binds by position as in 0.1, whether or not the host gives the instance terminal names. The SPICE letter rules are in a record with `language="spice"` (2.8): they apply to SPICE sections and never to the instance names of Spectre sections, so one file serves both dialects.

## Changes from 0.1

| 0.1 | 0.2 |
| --- | --- |
| `$VCVS`, `$CCVS` | `$CONTROLLED_VOLTAGE_SOURCE` (the `$VCVS` drawing), as in the standard series 0.4 |
| `$VCCS`, `$CCCS` | `$CONTROLLED_CURRENT_SOURCE` (the `$VCCS` drawing) |
| `$OPAMP_5TERM`, `$COMPARATOR_5TERM` | removed: `$OPAMP` and `$COMPARATOR` bind `inp inn out` by name on any number of nodes; the standard `$OPAMP_SUPPLY` and `$COMPARATOR_SUPPLY` draw supply pins |
| `$CURRENT_ARROW_SYMBOL` | removed: `$CURRENT_ARROW` usages are drawn with `$ARROW_SYMBOL` |
| `$DELAY_CELL_SYMBOL` | `$DELAY_CELL`, the two-terminal logic symbol `a y` |
| `$ADDER`, `$MULTIPLIER` (symbols) | `$ADDER_SYMBOL`, `$MULTIPLIER_SYMBOL`, drawn for the usages of the standard definitions `$ADDER` and `$MULTIPLIER` |
| `$SPDT_SWITCH_SYMBOL` on `sp2tswitch` instances | `$SP2TSWITCH`, a positional instance symbol; `$SPDT_SWITCH_SYMBOL` draws only the figure |
| `key="formula"` | `key="label"` |
| Net names of ports, supplies and named grounds, `key="name"` | `key="netname"` |
| The rule that drew named grounds through `$NAMED_GROUND_NET_SET` | removed: `rnl-std-fill` draws them itself |
| `$DIODE`, `$ZENER_DIODE`, `$SCHOTTKY` lying, anode at the left | upright, anode `a` at the top `(0, 3)` and cathode `k` at the bottom `(0, -3)`: the 0.1 drawing turned by R270, as in the standard series 0.4 |
| `$TRANSFORMER` lying, windings at the top and bottom | upright: the 0.1 drawing turned by R90, `p1` `(-2, 3)` over `n1` `(-2, -3)`, `p2` `(2, 3)` over `n2` `(2, -3)` |

Symbol sizes and lead lengths may differ from the standard drawings. In the six four-terminal MOS symbols, the bulk pin stays at `(0, 0)` facing right, rather than the standard's `(1, 0)`. Every pin-facing box edge lies on that side's outermost pin.

## License

CC0-1.0.
