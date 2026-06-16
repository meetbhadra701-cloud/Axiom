# To Verifier

v1 of `rtl/pwm.v` ready, spec in `spec/spec.md` (synchronous PWM generator). Ready for simulation.

- Module: `pwm` (param `WIDTH=8`)
- Top-level: `pwm`
- Ports: `clk`, `rst` (sync active-high; resets counter and pwm_out to 0), `en`,
  unsigned `duty[WIDTH-1:0]`, registered `pwm_out`
- Behavior: internal `counter[WIDTH-1:0]` free-runs (wraps at 2^WIDTH) when en=1.
  `pwm_out <= (counter < duty)` — pre-increment comparison, both registered in the same cycle.
- Priority: reset > enable > hold.
- Duty extremes: duty=0 → pwm_out always 0; duty=255 → 255 highs / 1 low per 256-cycle period.
- Yosys `check -assert`: 0 problems. ABC combinational warning is expected (comparison logic), not a latch.
- Iteration: 1

Verification tips:
- duty=0: pwm_out stuck at 0 for a full period.
- duty=255: 255 consecutive highs then 1 low.
- duty=128: exactly 128 highs and 128 lows per 256-cycle period.
- After 256 enabled clocks, counter wraps back to 0.
- Count high cycles over one full period and assert count == duty for arbitrary duty values.
