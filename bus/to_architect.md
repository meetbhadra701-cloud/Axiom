# To Architect

## Verification result - one_hot - iteration 1

- Result: PASS.
- Simulation: Cocotb testbench passed with `SIM=icarus` for default `N=8, LOG2W=3`
  and an override run with `N=16, LOG2W=4`.
- Coverage: synchronous reset, reset priority over enable, hold behavior, directed
  indices, exhaustive all-index decode for each tested width, one-hot exclusivity,
  reset clearing an active output, and 500 randomized reset/enable/index cycles
  against a Python reference model.
- Synthesis: Yosys `check -assert` passed with 0 reported problems.
- Note: Final default-width netlist contains 8 enabled/reset flops plus combinational
  decode logic.
- Note: Simulation used the existing Python 3.13 cocotb 2.0.1 venv at
  `/tmp/axiom-cocotb-venv`.
