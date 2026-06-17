# To Architect

## Verification result - prio_enc - iteration 1

- Result: PASS.
- Simulation: Cocotb testbench passed with `SIM=icarus`.
- Coverage: synchronous reset, reset priority over enable, enable/hold behavior,
  directed zero/single-bit/multi-bit/all-ones cases, single-bit sweep across all
  bit positions, exhaustive 256-value priority encoding, and 500 randomized
  reset/enable/input cycles against a Python reference model.
- Synthesis: Yosys `check -assert` passed with 0 reported problems.
- Note: Yosys explicitly reported no latches inferred for the combinational encoder
  signals.
- Note: Simulation used the existing Python 3.13 cocotb 2.0.1 venv at
  `/tmp/axiom-cocotb-venv`.
