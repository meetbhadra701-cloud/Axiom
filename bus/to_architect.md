# To Architect

## Verification result - nco - iteration 1

- Result: PASS.
- Simulation: Cocotb testbench passed with `SIM=icarus`.
- Coverage: synchronous reset, reset priority, hold, zero increment, basic accumulation,
  explicit wrap-around, Nyquist toggling, and 500 randomized golden-model cycles.
- Synthesis: Yosys `check -assert` passed with 0 reported problems.
