# Spec - mixer (Signed DSP Mixer)

**Status:** authoritative. Ground truth for Architect and Verifier.

## Purpose

A synchronous signed multiplier used as a real-valued DSP mixer. It multiplies an
input sample by a local-oscillator sample, producing a registered product. This block
can sit after `sine_lut` to mix a stream with a generated tone.

## Parameters

| Parameter | Default | Description |
|---|---:|---|
| `SAMPLE_WIDTH` | 8 | Signed input sample width. |
| `LO_WIDTH` | 8 | Signed local-oscillator sample width. |
| `OUT_WIDTH` | 16 | Signed registered output width. Must be large enough for the desired product precision. |

For the defaults, `OUT_WIDTH = SAMPLE_WIDTH + LO_WIDTH`, so the full signed product is
preserved without truncation.

## Ports

| Port | Direction | Width | Description |
|---|---|---:|---|
| `clk` | input | 1 | Clock. |
| `rst` | input | 1 | Synchronous, active-high reset. |
| `en` | input | 1 | Sample enable. |
| `sample` | input | `SAMPLE_WIDTH` | Signed input sample. |
| `lo` | input | `LO_WIDTH` | Signed oscillator/mixing sample. |
| `mixed` | output | `OUT_WIDTH` | Signed registered product. |

## Behavior

All state changes occur on `posedge clk`.

Priority: **reset > enable > hold**.

1. If `rst == 1`, `mixed <= 0`.
2. Else if `en == 1`, `mixed <= sample * lo`, interpreted as signed two's-complement
   multiplication.
3. Else `mixed` holds its previous value.

If `OUT_WIDTH` is narrower than the mathematical product, the assigned value wraps by
normal two's-complement truncation. With the default widths, no truncation occurs.

## Reset Semantics

Reset is synchronous and active-high. `rst` must not appear in the sensitivity list.

## Synthesis Constraints

- Use a single `always @(posedge clk)` block.
- Use non-blocking assignments for `mixed`.
- Use explicit signed declarations for signed arithmetic.
- No `initial`, no `#` delays, no inferred latches.
- Yosys `check -assert` must report 0 problems.

## Verification Requirements

For default parameters:

- Reset drives `mixed` to `0`.
- Reset has priority over `en`.
- `en=0` holds `mixed`.
- Positive, negative, and zero products are correct.
- Edge cases such as `127 * 127`, `-128 * 127`, and `-128 * -128` are correct.
- Random signed samples match a Python signed-reference model.
