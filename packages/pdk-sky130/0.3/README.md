# pdk-sky130

The RNL 0.4 symbol package `pdk-sky130` 0.3, [`pdk-sky130.rnl`](pdk-sky130.rnl), for the **SkyWater Open Source PDK** (`sky130_fd_pr`, v0.2.0 / `open_pdks` `sky130A` & `sky130B`). Its package file is that of 0.2 with only the version changed; 0.3 differs from 0.2 in its examples alone, which check with no diagnostic at all (see section 3). Versions 0.1 (RNL 0.3) and 0.2 stay as published.

In foundry PDKs, transistors, precision resistors, capacitors, varactors, diodes, and inductors are instantiated as subcircuit calls (such as `XM1 d g s b sky130_fd_pr__nfet_01v8 w=4 l=0.15` in SPICE or `M1 (d g s b) sky130_fd_pr__nfet_01v8 w=4u l=0.15u` in Spectre). Without a PDK package, RNL cannot tell the device kind or terminal names of these instances and draws them as generic boxes. `pdk-sky130` declares the terminal names and the kind of every `sky130_fd_pr` device with `@DEVICE`, maps the devices to the symbols of the standard series 0.4, and defines custom symbols where SKY130 devices carry extra substrate, bulk, or shield pins.

- **Target PDK**: [SkyWater SKY130 `sky130_fd_pr`](https://github.com/google/skywater-pdk-libs-sky130_fd_pr) (v0.2.0, upstream license `Apache-2.0`).
- **No foundry model data**: This package contains only RNL `@DEVICE` declarations, `@DEFINE-SYMBOL` drawings, and `@SELECT-INSTANCE` rules. No SPICE/Spectre model parameters, equations, or PDK subcircuit netlists are copied into this repository.
- **Package license**: `CC0-1.0`, like the other packages in this repository.

## Changes from 0.1

These came with 0.2 and hold for 0.3.

| 0.1 (RNL 0.3) | 0.2 and 0.3 (RNL 0.4) |
| --- | --- |
| Built on `rnl-std-basic` and `rnl-std-semiconductors` 0.3 | Built on `rnl-std-basic` and `rnl-std-semiconductors` 0.4 |
| `@DEVICE` gives terminal names only | The transistor families also give their kind: `type="nmos"`, `"pmos"`, `"npn"` or `"pnp"`, so the standard's semantics (the differential pairs and current mirrors, the bulk fills) treat SKY130 subcircuit calls as the native devices |
| `$RESISTOR` and `$CAPACITOR` bound `r0 r1` and `c0 c1` by position | The 2-terminal resistor and MIM capacitor rules write `@SET-SYMBOL(terminals=["p", "n"])`: the standard 0.4 symbols bind terminal names, and these bind the device's two terminals in node order |
| Rules act on the level they are read in | Every rule writes `recursive=true` and reaches instances at every level |
| `$DIODE` lying, anode at the left | The standard 0.4 `$DIODE` stands upright, anode `a` at the top |
| Examples in RNL 0.3 | Examples in RNL 0.4 (see below) |

The eight custom symbols keep the drawings, pins and boxes of 0.1, and bind by position.

---

## 1. Quick Start

Reference `pdk-sky130` in the `@RNL(type="header")` record of a SPICE or Spectre netlist, after the standard series:

```spice
* @RNL(type="header") {
*   @VERSION("0.4");
*   @USE-PACKAGE(name="rnl-std-all", version="0.4");
*   @USE-PACKAGE(name="pdk-sky130", version="0.3")
* }
```

Check or render the netlist by passing the package's directory to `rnl`:

```sh
rnl check --package-dir packages/pdk-sky130/0.3 packages/pdk-sky130/0.3/examples/ota5t.sp
rnl render --package-dir packages/pdk-sky130/0.3 packages/pdk-sky130/0.3/examples/ota5t.sp -o out
```

### Without PDK Models vs. With PDK Models

`pdk-sky130` works identically whether or not the netlist includes the SKY130 model library files:

1. **Without PDK model files included**: the `@DEVICE(name="*", model="sky130_fd_pr__...", terminals=[...])` declarations in the package's header record supply the terminal names (`d`, `g`, `s`, `b`, `c`, `e`, `r0`, `r1`, `c0`, `c1`, etc.) of every SKY130 device.
2. **With PDK `.subckt` / `subckt` definitions included**: RNL reads the port names from each `.subckt` / `subckt` header. The `@DEVICE` declarations match the `sky130_fd_pr` port orders, so every terminal reference (`#XM1:d`, `#XR1:r0`, `#XQ1:e`, `#XC1:c0`) resolves to the same pin in both modes, and the drawings are the same.

> **Note on `.include` / `.lib`**: RNL's SPICE and Spectre hosts read every active `.include` / `.lib` / `include` directive and report an error if the file does not exist. When the PDK is not installed, keep the directive commented out or point it to a stub file of `.subckt ... .ends` headers, as the examples do.

### SPICE and Spectre

Every `@DEVICE` declaration uses `name="*"` and every rule selects by `model="..."`, so the package works in both dialects:

- **SPICE**: subcircuit calls (`XM1 d g s b sky130_fd_pr__nfet_01v8 w=4 l=0.15`, `XR1 r0 r1 b sky130_fd_pr__res_high_po_0p35 l=10`) and primitive elements naming a SKY130 model (`D1`, `Q1`, `M1`).
- **Spectre**: instances without an `X` prefix (`M1 (d g s b) sky130_fd_pr__nfet_01v8 w=4u l=0.15u`, `CL (c0 c1) sky130_fd_pr__cap_mim_m3_1 w=10u l=10u`).

### `W/L` and Device Parameters in Labels

A label that references a host parameter such as `${w}` or `${l}` needs that parameter written on the instance line; RNL does not evaluate the defaults of a `.subckt`. Therefore:

- By default, `pdk-sky130` shows `${name}` (`key="name"`) and `${model}` (`key="model"` on transistors and BJTs, `key="value"` on resistors, capacitors and inductors), so any instance checks cleanly.
- To show `W/L` or passive dimensions, override `key="model"` or `key="value"` in your netlist:

```rnl
# @SELECT-INSTANCE(model="sky130_fd_pr__*fet*", recursive=true) => @TEXT("W/L=${w}/${l}", key="model");
# @SELECT-INSTANCE(model="sky130_fd_pr__res_high_po_*", recursive=true) => @TEXT("L=${l}", key="value");
# @SELECT-INSTANCE(model="sky130_fd_pr__cap_mim_*", recursive=true) => @TEXT("${w}\times{}${l} \mu{}m^{2}", key="value");
# @SELECT-INSTANCE(model="sky130_fd_pr__pnp_*", recursive=true) => @TEXT("m=${mult}", key="model");
```

The keys are those of the symbols' texts, so an override keeps each label where the symbol puts it.

---

## 2. Supported SKY130 Devices (`sky130_fd_pr`)

| Category | Models / Patterns | Terminals (Order) | Type | Symbol |
| --- | --- | --- | --- | --- |
| **NMOS (4-terminal)** | `sky130_fd_pr__nfet_01v8`, `sky130_fd_pr__nfet_01v8_lvt`, `sky130_fd_pr__nfet_g5v0d10v5`, `sky130_fd_pr__esd_nfet_01v8`, `sky130_fd_pr__esd_nfet_g5v0d10v5`, `sky130_fd_pr__special_nfet_latch*`, `sky130_fd_pr__special_nfet_pass*`, `sky130_fd_pr__rf_nfet_01v8*`, `sky130_fd_pr__rf_nfet_g5v0d10v5*` | `d g s b` | `nmos` | `$NMOS_4TERM` |
| **Native / Zero-Vt NMOS (4-terminal)** | `sky130_fd_pr__nfet_03v3_nvt`, `sky130_fd_pr__nfet_05v0_nvt`, `sky130_fd_pr__esd_nfet_05v0_nvt`, `sky130_fd_pr__esd_nfet_g5v0d10v5_nvt`, `sky130_fd_pr__nfet_20v0_nvt`, `sky130_fd_pr__nfet_20v0_zvt` | `d g s b` | `nmos` | `$DEPLETION_NMOS_4TERM` |
| **Drain-Extended / 20 V NMOS (4-terminal)** | `sky130_fd_pr__nfet_g5v0d16v0`, `sky130_fd_pr__nfet_20v0`, `sky130_fd_pr__nfet_extenddrain`, `sky130_fd_pr__esd_rf_nfet_20v0*`, `sky130_fd_pr__rf_nfet_20v0_aup`, `sky130_fd_pr__rf_nfet_20v0_nvt_aup`, `sky130_fd_pr__rf_nfet_20v0_*withptap` | `d g s b` | `nmos` | `$NDMOS_4TERM` |
| **Isolated 20 V NMOS (5-terminal)** | `sky130_fd_pr__nfet_20v0_iso`, `sky130_fd_pr__nfet_20v0_nvt_iso`, `sky130_fd_pr__nfet_20v0_reverse_iso`, `sky130_fd_pr__rf_nfet_20v0_*iso` | `d g s b sub` | `nmos` | `$SKY130_NMOS_5TERM` |
| **PMOS (4-terminal)** | `sky130_fd_pr__pfet_01v8`, `sky130_fd_pr__pfet_01v8_lvt`, `sky130_fd_pr__pfet_01v8_mvt`, `sky130_fd_pr__pfet_01v8_hvt`, `sky130_fd_pr__pfet_g5v0d10v5`, `sky130_fd_pr__esd_pfet_g5v0d10v5`, `sky130_fd_pr__special_pfet_pass*`, `sky130_fd_pr__rf_pfet_01v8*` | `d g s b` | `pmos` | `$PMOS_4TERM` |
| **Drain-Extended / 20 V PMOS (4-terminal)** | `sky130_fd_pr__pfet_g5v0d16v0`, `sky130_fd_pr__pfet_20v0`, `sky130_fd_pr__pfet_extenddrain`, `sky130_fd_pr__rf_pfet_20v0*` | `d g s b` | `pmos` | `$PDMOS_4TERM` |
| **NPN BJT (4-terminal)** | `sky130_fd_pr__npn_05v5_W1p00L1p00`, `sky130_fd_pr__npn_05v5_W1p00L2p00`, `sky130_fd_pr__npn_11v0_W1p00L1p00`, `sky130_fd_pr__npn_*`, `sky130_fd_pr__rf_npn_*` | `c b e s` | `npn` | `$SKY130_NPN_4TERM` |
| **PNP BJT (4-terminal)** | `sky130_fd_pr__pnp_05v5_W0p68L0p68`, `sky130_fd_pr__pnp_05v5_W3p40L3p40`, `sky130_fd_pr__pnp_*`, `sky130_fd_pr__rf_pnp_*` | `c b e s` | `pnp` | `$SKY130_PNP_4TERM` |
| **Precision Poly & Well Resistors (3-terminal)** | `sky130_fd_pr__res_high_po`, `sky130_fd_pr__res_high_po_0p35`..`5p73`, `sky130_fd_pr__res_xhigh_po_0p35`..`5p73`, `sky130_fd_pr__res_iso_pw`, `sky130_fd_pr__res_generic_pw` | `r0 r1 b` | | `$SKY130_RESISTOR_3TERM` |
| **Variable-Width Extra-High Poly Resistor (3-terminal)** | `sky130_fd_pr__res_xhigh_po` | `r0 r1 sub` | | `$SKY130_RESISTOR_3TERM` |
| **Base Extra-High Poly Resistor (3-terminal)** | `sky130_fd_pr__res_xhigh_po__base` | `r1 r2 b` | | `$SKY130_RESISTOR_3TERM` |
| **Diffusion Resistors (3-terminal)** | `sky130_fd_pr__res_generic_nd`, `sky130_fd_pr__res_generic_nd__hv`, `sky130_fd_pr__res_generic_pd`, `sky130_fd_pr__res_generic_pd__hv` | `t1 t2 b` | | `$SKY130_RESISTOR_3TERM` |
| **Poly & Metal Interconnect Resistors (2-terminal)** | `sky130_fd_pr__res_generic_po`, `sky130_fd_pr__res_generic_nw`, `sky130_fd_pr__res_generic_l1`, `sky130_fd_pr__res_generic_m1`..`m5`, `sky130_fd_pr__res_generic_r1`, `sky130_fd_pr__model__parasitic__res_po` | `r0 r1` | | `$RESISTOR` (`p n`) |
| **MIM Capacitors (2-terminal)** | `sky130_fd_pr__cap_mim_m3_1`, `sky130_fd_pr__cap_mim_m3_2`, `sky130_fd_pr__cap_mim_m3*`, `sky130_fd_pr__cap_mim_m4*` | `c0 c1` | | `$CAPACITOR` (`p n`) |
| **MOS Varactors (3-terminal)** | `sky130_fd_pr__cap_var_lvt`, `sky130_fd_pr__cap_var_hvt`, `sky130_fd_pr__cap_var*` | `c0 c1 b` | | `$SKY130_VARACTOR_3TERM` |
| **VPP Capacitors (3-terminal)** | `sky130_fd_pr__cap_vpp_*` (unshielded / 3-terminal variants) | `c0 c1 b` | | `$SKY130_CAPACITOR_3TERM` |
| **Shielded VPP Capacitors (4-terminal)** | `sky130_fd_pr__cap_vpp_*_shield*m5*`, `sky130_fd_pr__cap_vpp_*_shield*m4*`, `sky130_fd_pr__cap_vpp_*_shield*m3*` | `c0 c1 b m5` | | `$SKY130_CAPACITOR_4TERM` |
| **Diodes (2-terminal)** | `sky130_fd_pr__diode_pw2nd_05v5*`, `sky130_fd_pr__diode_pw2nd_11v0`, `sky130_fd_pr__diode_pd2nw_05v5*`, `sky130_fd_pr__diode_pd2nw_11v0`, `sky130_fd_pr__diode_*`, `sky130_fd_pr__esd_rf_diode_*`, `sky130_fd_pr__model__parasitic__*diode_*` | `a k` | | `$DIODE` |
| **RF Spiral Inductors (4-terminal)** | `sky130_fd_pr__ind_03_90`, `sky130_fd_pr__ind_05_125`, `sky130_fd_pr__ind_05_220`, `sky130_fd_pr__ind_*` | `a b ct sub` | | `$SKY130_INDUCTOR_4TERM` |

The standard symbols bind terminal names: `$NMOS_4TERM` and the other MOSFETs bind `d g s b`, `$DIODE` binds `a k`, and `$RESISTOR` and `$CAPACITOR` bind `p n`, which the rules map to the device's two terminals in node order.

### Custom Symbols Defined by `pdk-sky130`

All pins sit on integer grid points, and on any side with pins the symbol's `box` edge lies on the outermost pin of that side. The pins bind the device's terminals by position:

| Symbol | Pins (`terminal: (x, y) direction`) | Used For |
| --- | --- | --- |
| `$SKY130_RESISTOR_3TERM` | `1: (0, 2) up`, `2: (0, -2) down`, `3: (-2, 0) left` | 3-terminal poly, well, and diffusion resistors (`r0 r1 b`, `r0 r1 sub`, `r1 r2 b`, `t1 t2 b`) |
| `$SKY130_CAPACITOR_3TERM` | `1: (0, 2) up`, `2: (0, -2) down`, `3: (-2, 0) left` | 3-terminal VPP capacitors (`c0 c1 b`) |
| `$SKY130_CAPACITOR_4TERM` | `1: (0, 2) up`, `2: (0, -2) down`, `3: (-2, 0) left`, `4: (2, 0) right` | 4-terminal shielded VPP capacitors (`c0 c1 b m5`) |
| `$SKY130_VARACTOR_3TERM` | `1: (0, 2) up`, `2: (0, -2) down`, `3: (-2, 0) left` | 3-terminal MOS varactors (`c0 c1 b`) |
| `$SKY130_NPN_4TERM` | `1: (0, 2) up`, `2: (-3, 0) left`, `3: (0, -2) down`, `4: (1, 0) right` | 4-terminal vertical NPN subcircuits (`c b e s`) |
| `$SKY130_PNP_4TERM` | `1: (0, -2) down`, `2: (-3, 0) left`, `3: (0, 2) up`, `4: (1, 0) right` | 4-terminal vertical PNP subcircuits (`c b e s`) |
| `$SKY130_NMOS_5TERM` | `1: (0, 2) up`, `2: (-3, 0) left`, `3: (0, -2) down`, `4: (1, 0) right`, `5: (1, -1) right` | 5-terminal isolated 20 V drain-extended NMOS (`d g s b sub`) |
| `$SKY130_INDUCTOR_4TERM` | `1: (0, 2) up`, `2: (0, -2) down`, `3: (-1, 0) left`, `4: (-1, -1) left` | 4-terminal center-tapped RF spiral inductors (`a b ct sub`) |

---

## 3. Examples and Verification Script

The [`examples/`](examples/) directory holds four SKY130 schematics written in RNL 0.4. Each checks with no diagnostic at all, not even a hint, without and with the stub PDK models:

| File | Dialect | Circuit & SKY130 Devices Demonstrated |
| --- | --- | --- |
| [`examples/ota5t.sp`](examples/ota5t.sp) | SPICE | Five-transistor OTA with `sky130_fd_pr__nfet_01v8`, `sky130_fd_pr__pfet_01v8`, and a `sky130_fd_pr__cap_mim_m3_1` load capacitor; the input pair is a `$DIFFERENTIAL_PAIR_N` and the load a `$CURRENT_MIRROR_P` |
| [`examples/ota5t.scs`](examples/ota5t.scs) | Spectre | The same OTA in Spectre syntax (`M1`–`M6`, `CL` without `X` prefixes) |
| [`examples/bandgap.sp`](examples/bandgap.sp) | SPICE | CMOS bandgap reference core with `sky130_fd_pr__pnp_05v5_W3p40L3p40` (`XQ1`, `XQ2`), 3-terminal `sky130_fd_pr__res_high_po_0p35` (`XR1`–`XR3`), and a `sky130_fd_pr__pfet_01v8_lvt` mirror (`XM1`, `XM2`) |
| [`examples/mim_switch.sp`](examples/mim_switch.sp) | SPICE | Switched-capacitor sampling network with `sky130_fd_pr__cap_mim_m3_1`/`m3_2` (`XC1`, `XC2`), an LVT CMOS switch (`sky130_fd_pr__nfet_01v8_lvt`, `sky130_fd_pr__pfet_01v8_lvt`) between the input and sampled nets, a 5 V native-Vt bottom-plate switch (`sky130_fd_pr__nfet_05v0_nvt`), and an input clamp diode (`sky130_fd_pr__diode_pw2nd_05v5`) |

The examples are top-level netlists, so their named nets carry `$NET_LABEL`s: `$IO_PORT` marks a port of its level. Each MOSFET's bulk pin carries a label of its net on the pin (`$NET_LABEL_STUB`), so a source and its bulk no longer draw two grounds or supplies side by side. The ground and supply stubs keep the standard's default gap, and the `W/L` texts hang below their anchor. `ota5t` and `bandgap` keep the arrangement of 0.1, the OTA a few units wider. In `mim_switch.sp` the CMOS switch sits between an input bus and a sampled-net bus, so the two nets do not run along one line.

To regenerate `pdk-sky130.rnl` or verify every version and its examples (both without PDK model files and with stubbed `.subckt` / `subckt` definitions):

```sh
python scripts/pdk/sky130.py
python scripts/pdk/sky130.py --check
```

---

## 4. How to Create an RNL Symbol Package for Another PDK

Foundry PDKs, open-source or commercial, follow the same pattern in SPICE and Spectre netlists: devices are instantiated as subcircuits or models with foundry-specific names and fixed port orders. An RNL 0.4 symbol package for any PDK takes four steps, and needs **no foundry model parameters or proprietary equations**.

### Step 1: Inventory Device Names and Port Orders from the PDK

Extract only the `.subckt` / `.model` (SPICE) or `subckt` / `model` (Spectre) header lines from the PDK model directory:

```sh
# SPICE / ngspice / HSPICE / Xyce model files
grep -rhE '^\s*\.(subckt|model)\b' /path/to/pdk/models/ | sort -u

# Spectre (.scs) model files
grep -rhE '^\s*(inline\s+)?subckt\b' /path/to/pdk/models/spectre/ | sort -u
```

Pay close attention to:
1. **Terminal count**: many PDK passives and BJTs have an extra substrate, bulk, or shield terminal compared to textbook primitives (3-terminal poly/diffusion resistors, 3-terminal MIM/VPP capacitors, 4-terminal vertical BJTs, 5-terminal isolated HV MOSFETs in deep N-well).
2. **Terminal names and order**: even within one PDK, resistor or capacitor families may name their ports differently (such as `r0 r1 b`, `r0 r1 sub` and `t1 t2 b` in SKY130).

### Step 2: Declare `@DEVICE` in `@RNL(type="header")`

In the package's header record, declare `@VERSION("0.4")`, `@PACKAGE(name="...", version="...")`, reference `rnl-std-basic` and `rnl-std-semiconductors`, and write one `@DEVICE` per model name or wildcard pattern. Give transistors their kind with `type=`, so the standard's semantics treat them as native devices:

```rnl
@RNL(type="header") {
  @VERSION("0.4");
  @PACKAGE(name="pdk-example", version="0.1");
  @USE-PACKAGE(name="rnl-std-basic", version="0.4");
  @USE-PACKAGE(name="rnl-std-semiconductors", version="0.4");

  @DEVICE(name="*", model="nmos_3v3*", terminals=["d", "g", "s", "b"], type="nmos");
  @DEVICE(name="*", model="pmos_3v3*", terminals=["d", "g", "s", "b"], type="pmos");
  @DEVICE(name="*", model="rpoly_h*", terminals=["p", "n", "sub"])
}
```

Always write `name="*"` rather than `name="X*"`: SPICE subcircuit calls start with `X` while `.model`-backed primitives start with `M`, `Q`, `D`, `R`, `C`, and Spectre instances have no element letter, so `name="*"` covers both dialects with one declaration.

### Step 3: Reuse Standard Symbols or Define Multi-Terminal Symbols

The symbols of the standard series 0.4 bind terminal names:

| Standard Symbol | Package | Pins |
| --- | --- | --- |
| `$NMOS_4TERM`, `$DEPLETION_NMOS_4TERM`, `$NDMOS_4TERM` | `rnl-std-semiconductors` | `d (0, 2) up`, `g (-3, 0) left`, `s (0, -2) down`, `b (0, 0) right` |
| `$PMOS_4TERM`, `$PDMOS_4TERM` | `rnl-std-semiconductors` | `d (0, -2) down`, `g (-3, 0) left`, `s (0, 2) up`, `b (0, 0) right` |
| `$DIODE` | `rnl-std-semiconductors` | `a (0, 2) up`, `k (0, -2) down` |
| `$RESISTOR`, `$CAPACITOR` | `rnl-std-basic` | `p (0, 2) up`, `n (0, -2) down` |

When the device's terminal names match, select the symbol as it is. When they differ, as with a resistor whose ports are `r0 r1`, name the symbol's terminals in node order: `@SET-SYMBOL(terminals=["p", "n"]) $RESISTOR`.

When a device has more terminals than any standard symbol (a 3-terminal resistor, a 4-terminal BJT, a 5-terminal isolated MOSFET), define a package symbol (`$PDKNAME_... = @DEFINE-SYMBOL(box=[...]) { ... }`) whose `@PIN(terminal=k, ...)` numbers are the 1-based positions of the ports in the PDK's `.subckt` header, with every pin on an integer grid point.

### Step 4: Map Models to Symbols with `@SELECT-INSTANCE`

In the package's body, assign symbols by `model`, with `recursive=true` so the rules reach instances at every level:

```rnl
@RNL {
  # @SELECT-INSTANCE(model="nmos_3v3*", recursive=true) => @SET-SYMBOL $NMOS_4TERM;
  # @SELECT-INSTANCE(model="pmos_3v3*", recursive=true) => @SET-SYMBOL $PMOS_4TERM;
  # @SELECT-INSTANCE(model="rpoly_h*", recursive=true) => @SET-SYMBOL $EXAMPLE_RESISTOR_3TERM
}
```

Order broad wildcard patterns before narrower overrides: at equal priority, the later rule wins.

A package for a commercial PDK holds only device names and port names, never model cards, corner tables or design rules, so a team can keep it in its own CAD library directory and load it with `--package-dir`.
