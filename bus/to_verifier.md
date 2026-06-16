# To Verifier

v1 of `rtl/sine_lut.v` ready, spec in `spec/spec.md` (quarter-wave ROM sine LUT,
`ADDR_WIDTH=8`, `DATA_WIDTH=8`). Ready for simulation.

- Module: `sine_lut`
- Top-level: `sine_lut`
- Parameters: `ADDR_WIDTH=8`, `DATA_WIDTH=8`
- Ports: `clk`, `phase_in[7:0]` unsigned phase, registered signed `sin_out[7:0]`
- No reset port; output is valid one clock after `phase_in` is sampled.
- Quadrant decode: top two bits select quadrant; lower six bits index the 64-entry ROM.
- Q0: forward index, positive. Q1: mirrored index, positive.
- Q2: forward index, negative. Q3: mirrored index, negative.
- ROM formula: `round(127 * sin((i + 0.5) * pi / 128))` for `i=0..63`.
- Default anchor values: phase `0 -> +2`, `64 -> +127`, `128 -> -2`, `192 -> -127`.
- Yosys `check -assert`: 0 problems.
- Iteration: 1
