# Spec - sine_lut (Sine Lookup Table)

**Status:** authoritative. Ground truth for Architect and Verifier.

## Purpose

Quarter-wave ROM-based sine lookup table. Converts an unsigned phase value from an
NCO (or any source) into a signed sine amplitude. Completing the NCO into a full DDS
requires mapping `phase_out[PHASE_WIDTH-1:0]` to `sin_out[DATA_WIDTH-1:0]`.

The quarter-wave trick stores only `2^(ADDR_WIDTH-2)` entries and reconstructs the
full cycle from quadrant symmetry.

## Parameters

| Parameter | Default | Description |
|---|---:|---|
| `ADDR_WIDTH` | 8 | Phase bits consumed. LUT depth = `2^(ADDR_WIDTH-2)` = 64 entries by default. |
| `DATA_WIDTH` | 8 | Output amplitude bits. Signed range is `-(2^(DATA_WIDTH-1))` to `+(2^(DATA_WIDTH-1)-1)`. |

## Ports

| Port | Direction | Width | Description |
|---|---|---:|---|
| `clk` | input | 1 | Clock. |
| `phase_in` | input | `ADDR_WIDTH` | Unsigned phase address. Top two bits select the quadrant. |
| `sin_out` | output | `DATA_WIDTH` | Signed sine amplitude. Registered, one-cycle latency. |

There is no reset port. ROM contents are static, and output is valid one clock after
`phase_in` is sampled.

## Behavior

Let `N = 2^(ADDR_WIDTH-2)`; for defaults, `N = 64`.
Let `quad = phase_in[ADDR_WIDTH-1:ADDR_WIDTH-2]`.
Let `idx = phase_in[ADDR_WIDTH-3:0]`.

Quadrant decode:

| `quad` | ROM index | Output sign |
|---|---|---|
| `2'b00` (Q0) | `idx` | positive |
| `2'b01` (Q1) | `~idx` | positive |
| `2'b10` (Q2) | `idx` | negative |
| `2'b11` (Q3) | `~idx` | negative |

ROM contents:

```text
lut[i] = round((2^(DATA_WIDTH-1) - 1) * sin((i + 0.5) * pi / (2*N)))
```

For `ADDR_WIDTH=8`, `DATA_WIDTH=8`, the LUT has 64 unsigned amplitudes in the
range `2..127`.

For Q2/Q3, apply two's-complement negation to the unsigned LUT value. With 8-bit
output, the peak stored value is `127`, so `-127` is representable and `-128` is
never produced.

`sin_out` updates on `posedge clk`; the observed output corresponds to the phase
sampled on the previous clock edge.

## Synthesis Notes

- ROM initialization uses an `initial` block assigning constant values to a `reg`
  array. This is the one permitted `initial` exception for this project because
  FPGA synthesis tools and Yosys infer constant ROMs from this pattern.
- Quadrant decode is pure combinational logic.
- The registered stage is a single `always @(posedge clk)` block with non-blocking
  assignments.
- No reset input by design.
- Yosys `check -assert` must report 0 problems.

## Verification Requirements

For the default parameters:

- Verify one-cycle latency: each `sin_out` equals the expected value for the previous
  cycle's `phase_in`.
- Check anchor points: phase `0 -> +2`, `64 -> +127`, `128 -> -2`, `192 -> -127`.
- Sweep all 256 phase values against the ROM formula and quadrant decode.
- Verify Q0 and Q1 are positive mirrors, Q2 and Q3 are negative mirrors.
- Verify output range is `[-127, +127]`, with no `-128`.
- Verify the full-cycle sum is close to zero; exact default sum is `0`.
