# Spec — `fir`: Parameterizable Direct-Form FIR Filter

**Status:** authoritative. Ground truth for the Architect and Verifier.
Previous module specs archived at `spec/counter.md` and `spec/mac_spec.md`.
Ambiguities → `bus/status.md` "Questions for Manager", not guesses.

## 1. Overview

A synchronous, direct-form, fixed-coefficient FIR (Finite Impulse Response) filter.
On each enabled clock edge, it shifts a new input sample into an `N_TAPS`-deep delay
line, multiplies each tap by a fixed signed coefficient, and sums all products into a
registered output `y`.

Single clock domain, single synchronous reset. Coefficients are compile-time parameters,
not runtime-loadable (no coefficient RAM).

## 2. Parameters

| Name         | Default | Meaning                                                      |
|--------------|---------|--------------------------------------------------------------|
| `N_TAPS`     | `4`     | Number of filter taps. Must be ≥ 1.                          |
| `DATA_WIDTH` | `8`     | Bit width of signed input sample `x` and each delay element. |
| `COEF_WIDTH` | `8`     | Bit width of each signed coefficient.                        |
| `OUT_WIDTH`  | `32`    | Bit width of registered signed output `y`.                   |

Coefficients are passed as a flat packed parameter `COEFFS`, declared as a
`(N_TAPS * COEF_WIDTH)`-bit vector. Tap 0 (most recent sample) uses bits
`[COEF_WIDTH-1:0]`, tap 1 uses `[2*COEF_WIDTH-1:COEF_WIDTH]`, etc.

For the default 4-tap 8-bit case: `COEFFS = 32'h01_02_04_02` gives coefficients
`[2, 4, 2, 1]` in that order (tap 3 … tap 0), which is a simple low-pass kernel.

## 3. Ports

| Name  | Dir | Width        | Description                                              |
|-------|-----|--------------|----------------------------------------------------------|
| `clk` | in  | 1            | Clock. All state changes on rising edge.                 |
| `rst` | in  | 1            | Synchronous, active-high reset. Clears delay line and `y`.|
| `en`  | in  | 1            | Sample enable (active-high). Shift and compute when high. |
| `x`   | in  | `DATA_WIDTH` | Signed input sample.                                     |
| `y`   | out | `OUT_WIDTH`  | Registered signed filtered output.                       |

`y` is a registered output (driven from a flip-flop), not combinational.

## 4. Behavior (per rising edge of `clk`)

**Priority: reset > enable > hold.**

1. If `rst == 1`:
   - All delay-line registers `d[0..N_TAPS-1]` ← 0.
   - Output register `y` ← 0.
2. else if `en == 1`:
   - Shift the delay line: `d[N_TAPS-1] ← d[N_TAPS-2]`, …, `d[1] ← d[0]`, `d[0] ← x`.
   - Compute `y ← sum over i of (d[i] * coef[i])`, each product sign-extended to
     `OUT_WIDTH` before summation. Result registered.
3. else: all registers hold.

The `d[i] * coef[i]` products and the final sum are computed combinationally from the
registered delay line; only `y` and the delay-line registers are sequential.

## 5. Arithmetic semantics

- `x`, `d[i]` are signed (`DATA_WIDTH` bits, two's complement).
- `coef[i]` is signed (`COEF_WIDTH` bits, two's complement, extracted from `COEFFS`).
- Each product is `DATA_WIDTH + COEF_WIDTH` bits wide (signed).
- Products are sign-extended to `OUT_WIDTH` before the sum.
- The sum and `y` are `OUT_WIDTH`-bit signed, wrapping (no saturation).

## 6. Reset semantics

- Synchronous, active-high only. Do not put `rst` in a sensitivity list.
- Reset clears all delay-line taps and `y` to zero.

## 7. Synthesis constraints (CLAUDE.md §3)

- Delay-line and `y` updates in a **single** `always @(posedge clk)` block.
- Combinational sum in a separate `always @(*)` block with a default assignment
  (no inferred latches), or as `wire` assignments.
- Non-blocking `<=` for sequential; blocking `=` for combinational.
- No `initial`, no `#` delays. Explicit widths throughout.
- Must pass Yosys `check -assert` with 0 problems.
