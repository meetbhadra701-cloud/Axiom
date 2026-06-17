# Spec — shift_reg (Universal Shift Register)

**Status:** authoritative. Ground truth for Architect and Verifier.
Previous specs archived in `spec/`.

## Purpose

Synchronous left-shifting universal shift register. Supports both PISO (parallel-in
serial-out) and SIPO (serial-in parallel-out) use-cases in one module:

- **PISO** (transmit): assert `load` to preload `parallel_in`, then drive `en=1,
  load=0` for WIDTH cycles; `serial_out` delivers bits MSB-first.
- **SIPO** (receive): drive `en=1, load=0` for WIDTH cycles feeding bits into
  `serial_in` LSB-first; read the assembled word from `parallel_out`.

Core building block for SPI, I2S, and any MSB-first serial protocol.

## Parameters

| Parameter | Default | Description |
|---|---:|---|
| `WIDTH`   | 8 | Word width. |

## Ports

| Port           | Direction | Width   | Description |
|---|---|---:|---|
| `clk`          | input  | 1       | Clock. |
| `rst`          | input  | 1       | Synchronous, active-high reset. Clears register to 0. |
| `load`         | input  | 1       | Parallel load (overrides shift). |
| `en`           | input  | 1       | Shift enable (active only when `load=0`). |
| `serial_in`    | input  | 1       | Bit entering at LSB on each shift. |
| `parallel_in`  | input  | `WIDTH` | Parallel data loaded when `load=1`. |
| `serial_out`   | output | 1       | MSB of register (combinational tap — bit shifted out next). |
| `parallel_out` | output | `WIDTH` | Full register contents (combinational, reflects current state). |

## Behaviour

All state changes on `posedge clk`. Priority: **reset > load > shift(en) > hold**.

Internal state: `sr`, a WIDTH-bit shift register.

1. If `rst == 1`: `sr <= 0`.
2. Else if `load == 1`: `sr <= parallel_in` (regardless of `en`).
3. Else if `en == 1`: `sr <= {sr[WIDTH-2:0], serial_in}` — left-shift; `serial_in` enters at LSB [0], MSB [WIDTH-1] exits.
4. Else: hold.

**Combinational outputs (wires, not registered):**
- `serial_out = sr[WIDTH-1]`  — the bit that will exit on the next shift.
- `parallel_out = sr`         — the full current register value.

## Synthesis notes

- `sr` is the only state register; all outputs are combinational taps of it.
- Single `always @(posedge clk)` block.
- `serial_out` and `parallel_out` are `assign` statements, not driven from `always`.
- No `initial`, no `#` delays, no inferred latches.
- Yosys `check -assert` must report 0 problems.

## Verification tips (for Verifier)

For WIDTH=8:

1. **Reset:** sr=0, serial_out=0, parallel_out=0 after rst=1.
2. **Load:** assert load with parallel_in=8'hA5; next cycle parallel_out==8'hA5; serial_out==1 (MSB of A5).
3. **Load priority over en:** assert both load=1 and en=1 simultaneously; load wins, no shift occurs.
4. **Hold:** load=0, en=0 → register and outputs unchanged.
5. **PISO 8-bit transmit:** load 8'hAB (10101011), then 8 shift cycles; serial_out sequence MSB-first: 1,0,1,0,1,0,1,1.
6. **SIPO 8-bit receive:** shift in bits 1,0,1,1,0,1,0,0 (MSB-first sequence, entering at serial_in); after 8 cycles parallel_out == 8'hB4 (10110100 — the last shifted-in bits now occupy the LSBs).
7. **serial_out timing:** reflects sr[WIDTH-1] of the current cycle combinationally (not one cycle delayed).
8. **Reset mid-shift:** assert rst during a shift sequence; register clears immediately.
