# To Verifier

v1 of `rtl/sine_lut.v` ready, spec in `spec/spec.md` (quarter-wave ROM sine LUT,
ADDR_WIDTH=8, DATA_WIDTH=8). Ready for simulation.

- Module: `sine_lut` (params `ADDR_WIDTH=8`, `DATA_WIDTH=8`)
- Top-level: `sine_lut`
- Ports: `clk`, `phase_in[7:0]` (unsigned phase), `sin_out[7:0]` (signed amplitude, registered)
- No reset port — output is valid one clock after phase_in.
- Quadrant decode: top 2 bits of phase_in select quadrant; lower 6 bits index the 64-entry ROM.
  Q0(00): forward index, positive. Q1(01): mirrored index, positive.
  Q2(10): forward index, negative. Q3(11): mirrored index, negative.
- ROM: 64 unsigned values computed as round(127 * sin((i+0.5)*π/128)) for i=0..63.
  Range: lut[0]=2 .. lut[63]=127.
- Negation for Q2/Q3: two's-complement `-$signed({1'b0, raw})`. Max output: ±127; -128 never produced.
- One-cycle pipeline latency: sin_out updates the clock after phase_in changes.
- Yosys `check -assert`: 0 problems (ABC combinational warning is expected, not a latch).
- Iteration: 1

Verification tips:
- phase_in=0   → sin_out≈+2  (after 1 clock; bin 0 is sin(π/512)×127≈2)
- phase_in=64  → sin_out≈+127 (Q1 start: mir_idx=~0=63, lut[63]=127, positive)
- phase_in=128 → sin_out≈-2  (Q2 start: forward idx=0, lut[0]=2, negated → -2)
- phase_in=192 → sin_out≈-127 (Q3 start: mir_idx=63, lut[63]=127, negated → -127)
- Full 256-cycle sweep verifies monotonicity in each quadrant.
- Sum of all 256 sin_out values should be close to 0 (no DC bias).
