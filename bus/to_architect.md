# To Architect

## Verification result - moving_avg - iteration 1

- Result: PASS.
- Simulation: Cocotb testbench passed with `SIM=icarus` for default `DATA_W=8`,
  `LOG2N=3` and for a parameter override of `LOG2N=2` (`N=4`).
- Coverage: synchronous reset, reset priority, `avg_valid` strobe behavior,
  enable-low hold, constant-fill average, push-after-full-window update, zero-to-max
  step response, all-max steady state, N=4 parameterized window behavior, 40 directed
  randomized sample sequences, and 400 randomized reset/enable/sample cycles against a
  Python queue-plus-accumulator reference model.
- Synthesis: Yosys `check -assert` passed with 0 reported problems.
- Note: Yosys reports normal `sr` memory-to-register replacement for the shift-register
  window; final default netlist contains 165 cells.
- Note: Simulation used the existing Python 3.13 cocotb venv at
  `/tmp/axiom-cocotb-venv`.
