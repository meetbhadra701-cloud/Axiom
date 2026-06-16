# Spec - `mac`: Signed Multiply-Accumulate

**Status:** authoritative for the current module. The previously verified counter spec is
archived at `spec/counter.md`.

## 1. Overview

`mac` is a parameterizable signed multiply-accumulate block for DSP-style pipelines. On
each rising edge of `clk`, it optionally clears or accumulates the signed product
`a * b` into the registered accumulator output `acc`.

Single clock domain. All controls are synchronous and active-high.

## 2. Parameters

| Name        | Default | Meaning                                      |
|-------------|---------|----------------------------------------------|
| `A_WIDTH`   | `8`     | Signed width of input `a`.                   |
| `B_WIDTH`   | `8`     | Signed width of input `b`.                   |
| `ACC_WIDTH` | `32`    | Signed width of registered accumulator `acc`. |

`ACC_WIDTH` must be greater than or equal to `A_WIDTH + B_WIDTH`.

## 3. Ports

| Name    | Dir | Width             | Description                                      |
|---------|-----|-------------------|--------------------------------------------------|
| `clk`   | in  | 1                 | Clock. All state changes occur on rising edge.   |
| `rst`   | in  | 1                 | Synchronous, active-high reset.                  |
| `clear` | in  | 1                 | Synchronous, active-high accumulator clear.       |
| `en`    | in  | 1                 | Accumulate enable.                               |
| `a`     | in  | `A_WIDTH` signed  | Signed multiplicand.                             |
| `b`     | in  | `B_WIDTH` signed  | Signed multiplier.                               |
| `acc`   | out | `ACC_WIDTH` signed | Registered signed accumulator value.             |

`acc` is registered, not combinational.

## 4. Behavior per rising edge

Priority order is **reset, clear, enable, hold**:

1. If `rst == 1`, then `acc <= 0`.
2. Else if `clear == 1`, then `acc <= 0`.
3. Else if `en == 1`, then `acc <= acc + signed(a) * signed(b)`.
4. Else `acc` holds its current value.

The product is sign-extended to `ACC_WIDTH` before addition.

## 5. Arithmetic semantics

All arithmetic is two's-complement signed arithmetic. Accumulator overflow wraps modulo
`2**ACC_WIDTH`; there is no saturation and no overflow flag.

For the default widths, `a` and `b` are signed 8-bit values in `[-128, 127]`, and `acc`
is signed 32-bit.

## 6. Reset and clear semantics

- `rst` is synchronous and active-high.
- `clear` is synchronous and active-high.
- `rst` has priority over `clear`.
- `clear` has priority over `en`.
- No asynchronous reset or asynchronous clear is present.

The accumulator value is only defined after at least one synchronous reset or clear.

## 7. Synthesis constraints

- Sequential state in one `always @(posedge clk)` block.
- Non-blocking assignments for `acc`.
- No `initial`, no delays, no inferred latches.
- One driver for `acc`.
- Must pass Yosys `check -assert` with zero latches, loops, or multi-driven nets.
