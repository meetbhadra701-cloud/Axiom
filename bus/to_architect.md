# To Architect

## Verification result - pwm - iteration 1

- Result: PASS.
- Simulation: Cocotb testbench passed with `SIM=icarus`.
- Coverage: synchronous reset, reset priority, enable-hold, pre-increment comparison,
  duty `0`, duty `255`, duty `128`, arbitrary full-period high-count checks, counter
  period wrap, and 400 randomized reset/enable/duty cycles.
- Synthesis: Yosys `check -assert` passed with 0 reported problems.
