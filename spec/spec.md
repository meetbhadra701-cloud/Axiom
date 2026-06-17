# Spec — barrel_shift (Arithmetic Barrel Shifter)

**Status:** authoritative. Ground truth for Architect and Verifier.
Previous specs archived in `spec/`.

## Purpose

Synchronous signed arithmetic barrel shifter. Left-shifts or arithmetic-right-shifts
a signed input by a variable amount in a single clock cycle. Useful for gain scaling
in the DSP chain (e.g. `mixer → barrel_shift` to normalise amplitude after mixing).

Arithmetic right-shift sign-extends — equivalent to division by 2^shamt rounding
toward negative infinity. Left-shift is logical — equivalent to multiplication by 2^shamt
(wraps on overflow by normal two's-complement truncation).

## Parameters

| Parameter    | Default | Description |
|---|---:|---|
| `WIDTH`      | 16 | Signed data width. |
| `SHAMT_WIDTH` | 4 | Shift-amount width. Max shift = 2^SHAMT_WIDTH − 1 = 15 for default. |

## Ports

| Port    | Direction | Width          | Description |
|---|---|---:|---|
| `clk`   | input  | 1              | Clock. |
| `rst`   | input  | 1              | Synchronous, active-high reset. |
| `en`    | input  | 1              | Sample enable. |
| `in`    | input  | `WIDTH`        | Signed input. |
| `shamt` | input  | `SHAMT_WIDTH`  | Unsigned shift amount. |
| `dir`   | input  | 1              | 0 = left shift; 1 = arithmetic right shift. |
| `out`   | output | `WIDTH`        | Registered signed result. |

## Behaviour

All state changes on `posedge clk`. Priority: **reset > enable > hold**.

1. If `rst == 1`: `out <= 0`.
2. Else if `en == 1`:
   - If `dir == 0`: `out <= in <<  shamt`  (logical left, two's-complement wraps).
   - If `dir == 1`: `out <= in >>> shamt`  (arithmetic right, sign-extends).
3. Else: `out` holds its previous value.

The `>>>` operator in Verilog performs arithmetic right shift only when the operand is
`signed`. Declare `in` as `input signed` or cast with `$signed(in)` before the shift.

## Synthesis constraints

- Single `always @(posedge clk)` block.
- Non-blocking `<=` for `out`.
- `in` must be treated as signed for `>>>` to be arithmetic; use `input signed` declaration.
- No `initial`, no `#` delays, no inferred latches.
- Yosys `check -assert` must report 0 problems.

## Verification tips (for Verifier)

For WIDTH=16, SHAMT_WIDTH=4:

1. **Reset:** out = 0 after rst=1.
2. **Hold:** en=0 holds out across cycles.
3. **Left shift by 0:** out == in (identity).
4. **Right shift by 0:** out == in (identity).
5. **Left shift positive:** `in=1, shamt=3` → out=8.
6. **Left shift overflow (wraps):** `in=16384, shamt=1` → out=-32768 (two's-complement wrap, not saturate).
7. **Arithmetic right shift positive:** `in=8, shamt=3` → out=1.
8. **Arithmetic right shift negative:** `in=-8, shamt=3` → out=-1 (sign-extended, not zero-padded).
9. **Arithmetic right shift -1:** any shamt → out=-1 (all-ones stays all-ones).
10. **Max shamt (15):** left of positive large value wraps; right of any negative value → -1 or 0.
11. **Randomized:** compare against Python `int16` reference with `>>` (arithmetic) and `<< & mask` (left, wrap).
