# Spec - sat_adder (Saturating Signed Adder)

**Status:** authoritative. Ground truth for Architect and Verifier.

## Purpose

Synchronous signed saturating adder. Adds two signed two's-complement inputs and
clips overflow to the representable signed range instead of wrapping. This is useful
after DSP gain/mix stages where overflow should become a bounded output value.

## Parameters

| Parameter | Default | Description |
|---|---:|---|
| `WIDTH` | 16 | Signed input and output width. |

For `WIDTH=16`, the output range is `-32768..32767`.

## Ports

| Port | Direction | Width | Description |
|---|---|---:|---|
| `clk` | input | 1 | Clock. |
| `rst` | input | 1 | Synchronous, active-high reset. |
| `en` | input | 1 | Sample enable. |
| `a` | input | `WIDTH` | Signed addend. |
| `b` | input | `WIDTH` | Signed addend. |
| `sum` | output | `WIDTH` | Registered signed saturated result. |

## Behavior

All state changes occur on `posedge clk`.

Priority: **reset > enable > hold**.

1. If `rst == 1`, `sum <= 0`.
2. Else if `en == 1`, compute the mathematical signed sum `a + b`.
   - If the result is greater than signed max, `sum <= 2^(WIDTH-1)-1`.
   - If the result is less than signed min, `sum <= -2^(WIDTH-1)`.
   - Otherwise `sum <= a + b`.
3. Else `sum` holds its previous value.

## Overflow Rule

Use signed overflow detection:

- Positive overflow occurs when `a` and `b` are both non-negative but the wrapped
  `WIDTH`-bit result is negative.
- Negative overflow occurs when `a` and `b` are both negative but the wrapped
  `WIDTH`-bit result is non-negative.

## Synthesis Constraints

- Use a single `always @(posedge clk)` block for state.
- Use non-blocking assignments for `sum`.
- Use explicit signed declarations for signed arithmetic.
- No `initial`, no `#` delays, no inferred latches.
- Yosys `check -assert` must report 0 problems.

## Verification Requirements

For default `WIDTH=16`:

- Reset drives `sum` to `0`.
- Reset has priority over `en`.
- `en=0` holds `sum`.
- Normal positive, normal negative, and mixed-sign additions are exact.
- Positive overflow saturates to `32767`.
- Negative overflow saturates to `-32768`.
- Boundary cases around `32767`, `-32768`, `0`, `1`, and `-1` are checked.
- Random signed input pairs match a Python saturating-reference model.
