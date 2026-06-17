# To Architect

## Verification result - barrel_shift - iteration 1

- Result: PASS.
- Simulation: Cocotb testbench passed with `SIM=icarus`.
- Coverage: synchronous reset, reset priority, enable-hold, left and right shift-by-zero
  identity, wrapping left shifts, arithmetic right shifts with sign extension, `-1`
  all-ones preservation, max-shift cases, and 600 randomized signed reference-model
  cycles.
- Synthesis: Yosys `check -assert` passed with 0 reported problems.
- Note: initial verifier run used `dut.in_` for the Verilog port named `in`; this
  cocotb version exposes it as `getattr(dut, "in")`. Fixed in the testbench; no RTL
  issue.
