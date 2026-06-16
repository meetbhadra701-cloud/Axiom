# To Architect

## Verification result - mixer - iteration 1

- Result: PASS.
- Simulation: Cocotb testbench passed with `SIM=icarus`.
- Coverage: synchronous reset, reset priority, enable-hold, zero/positive/negative
  directed products, signed extremes (`127*127`, `-128*127`, `127*-128`,
  `-128*-128`), and 500 randomized signed reference-model cycles.
- Synthesis: Yosys `check -assert` passed with 0 reported problems.
