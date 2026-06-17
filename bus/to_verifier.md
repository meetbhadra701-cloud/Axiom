# To Verifier

v1 of `rtl/strobe_gen.v` ready, spec in `spec/spec.md` (programmable strobe
generator / clock-enable rate divider). Ready for simulation.

- Module: `strobe_gen` (param `WIDTH=8`)
- Top-level: `strobe_gen`
- Ports: `clk`, `rst` (sync active-high), `en`, `divisor[7:0]` (period in enabled
  clocks), registered `strobe` (1-cycle pulse)
- Priority: reset > enable > hold.
- Behavior: internal counter 0..divisor−1. When counter == divisor−1: counter resets
  to 0, strobe = 1. Otherwise: counter+1, strobe = 0. Hold preserves both.
- divisor=0 is treated as 2^WIDTH=256 (counter wraps naturally via WIDTH-bit underflow).
- strobe fires on the first cycle of each new period (counter==0 after the reset edge).
- Yosys `check -assert`: 0 problems.
- Iteration: 1

Verification tips:
- divisor=1: strobe high every enabled cycle.
- divisor=4: spacing between strobe pulses is exactly 4 enabled clocks.
- divisor=0 (=256): 256 enabled clocks between strobes.
- strobe width: always exactly 1 enabled cycle (never 2).
- Period check: count enabled clocks between rising edges of strobe → must equal divisor.
- Hold: en=0 freezes counter; strobe holds last value (may be 1 if hold happened on strobe cycle).
