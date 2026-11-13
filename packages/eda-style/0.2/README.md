# eda-style

[`eda-style.rnl`](eda-style.rnl) is the independent visual package `eda-style` 0.2 for RNL 0.4. It styles standard, [`eda-symbol`](../../eda-symbol/0.2/README.md), and user-defined symbols without supplying their geometry. Neither EDA package imports the other; both are public extensions, outside the core's built-in packages. It references `rnl-std-basic` 0.4 for the definitions its rules select.

## Use

To keep the EDA drawings as well as their appearance, name the standard collection and both packages, in this order (use `*` instead of `//` in SPICE):

```spectre
// @RNL(type="header") {
//   @VERSION("0.4");
//   @USE-PACKAGE(name="rnl-std-all", version="0.4");
//   @USE-PACKAGE(name="eda-symbol", version="0.2");
//   @USE-PACKAGE(name="eda-style", version="0.2")
// }
```

Use only the `eda-style` line, after `rnl-std-all`, to apply the appearance to the standard drawings or to your own symbols. Its rules write `recursive=true`, so they reach every level below the one that uses the package (RNL 0.4, 10.4 and 16.2).

```sh
rnl check packages/eda-style/0.2/eda-style.rnl
rnl check packages/eda-style/0.2/eda-style-gallery.scs --path packages/eda-symbol/0.2 --path packages/eda-style/0.2
rnl render packages/eda-style/0.2/eda-style-gallery.scs --path packages/eda-symbol/0.2 --path packages/eda-style/0.2 -o out/eda-style
```

## Appearance

- Symbol outlines use green hairlines (`#00cc66`, `linewidth=0`); symbol text and labels use red (`#ff0000`).
- `$PIN_SQUARE` attaches a solid red 0.8 × 0.8 square to each pin of `$PIN_SQUARE_SET`: the pins of instances, including user-defined symbols, and of grounds and supplies, selected with `@SELECT-PIN`. Port models are left out and keep their solid red polygons. Squares are drawn on the top layer; geometry files do not repeat them. A file adds pins to `$PIN_SQUARE_SET` or removes them from it.
- Wires and scene annotations use dark hairlines (`#1d1d1f`), with wires on the bottom layer. Net and wire labels keep the base text style.
- Labels hint `Lucida Console, Monaco, DejaVu Sans Mono, Consolas, monospace`; the viewer chooses an available font.

## Changes from 0.1

- RNL 0.4; every rule writes `recursive=true`.
- Terminal squares are attached to pins (`@SELECT-PIN`), not terminals: in RNL 0.4 a terminal without a pin is still selected by `@SELECT-TERMINAL`. The set is `$PIN_SQUARE_SET` (was `$PIN_TERMINAL_SET`), and `$PIN_SQUARE` takes a pin.

## Examples

[`eda-style-gallery.scs`](eda-style-gallery.scs) imports both packages and places 128 visually distinct symbols in a root gallery, with six thematic subcircuits; it drops the automatic fill with `@USE-PACKAGE(name="rnl-std-fill") {}`, and sets the symbols of its placeholder instances with `terminals=` in node order. [`examples/custom-symbol.sp`](examples/custom-symbol.sp) shows the same visual rules on a user-defined symbol, a standard resistor, ground and supply usages, a no-connect mark and a wire.

## License

CC0-1.0.
