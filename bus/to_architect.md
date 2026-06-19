# To Architect

## Verification result - iir_biquad - iteration 1

- Result: PASS.
- Simulation: Cocotb testbench passed with `SIM=icarus`.
- Coverage: synchronous reset, reset priority, y_valid strobe, enable-low hold,
  identity pass-through, half-gain truncation including negative values, DC-blocker
  impulse response, large signed accumulator stress, 60 randomized sample sequences,
  and 300 randomized reset/enable/sample cycles against a Python fixed-point reference.
- Synthesis: Yosys `check -assert` passed with 0 reported problems.
- Note: Final netlist is large as expected for five 16x16 signed products synthesized
  to generic gates: 9271 cells, including 64 enabled/reset flops and one reset-only
  valid flop.
- Note: Simulation used the existing Python 3.13 cocotb 2.0.1 venv at
  `/tmp/axiom-cocotb-venv`.
