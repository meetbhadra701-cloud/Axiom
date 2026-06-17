# To Architect

## Verification result - sat_adder - iteration 1

- Result: PASS.
- Simulation: Cocotb testbench passed with `SIM=icarus`.
- Coverage: synchronous reset, reset priority, enable-hold, exact normal additions,
  positive saturation to `32767`, negative saturation to `-32768`, signed boundary
  cases, and 600 randomized signed reference-model cycles.
- Synthesis: Yosys `check -assert` passed with 0 reported problems.
