# To Architect

## Verification result - gray_codec - iteration 1

- Result: PASS.
- Simulation: Cocotb testbench passed with `SIM=icarus`.
- Coverage: synchronous reset, reset priority, enable-hold, directed encode examples,
  exhaustive encode/decode round-trip for all 256 values, Gray-code single-bit adjacency
  for consecutive binary values, exhaustive decode mode inputs, mode switching, and
  500 randomized reset/enable/mode/data cycles.
- Synthesis: Yosys `check -assert` passed with 0 reported problems.
- Note: `/tmp/axiom-cocotb-venv` had been cleaned between sessions, so it was recreated
  with Python 3.13 and cocotb 2.0.1 before running simulation.
