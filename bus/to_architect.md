# To Architect

## Verification result - strobe_gen - iteration 1

- Result: PASS.
- Simulation: Cocotb testbench passed with `SIM=icarus`.
- Coverage: synchronous reset, reset priority, enable-hold, `divisor=1`, `divisor=0`
  as 256 enabled clocks, representative divisors, exact pulse spacing, one-enabled-cycle
  pulse width, hold-high behavior when `en=0` after a pulse, and randomized
  reset/enable/divisor cycles.
- Synthesis: Yosys `check -assert` passed with 0 reported problems.
- Note: the first pulse after reset occurs on the `divisor`th enabled edge. For example,
  with `divisor=4`, observed pulse indices in a zero-based enabled-cycle window are
  3, 7, 11, ...
