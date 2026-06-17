# To Architect

## Verification result - shift_reg - iteration 1

- Result: PASS.
- Simulation: Cocotb testbench passed with `SIM=icarus`.
- Coverage: synchronous reset, reset priority over load/shift, load behavior,
  load priority over enabled shift, hold behavior, PISO MSB-first serial output for
  `8'hAB`, SIPO assembly of `8'hB4`, combinational `serial_out`/`parallel_out` taps,
  mid-shift reset, and 500 randomized reset/load/enable/input cycles against a Python
  reference model.
- Synthesis: Yosys `check -assert` passed with 0 reported problems.
- Note: Simulation used the existing Python 3.13 cocotb 2.0.1 venv at
  `/tmp/axiom-cocotb-venv`.
