# To Architect

## Verification result - lfsr - iteration 2

- Result: PASS.
- Prior v1 bug: MSB feedback locked the default seed `1` into `0x0000`.
- Fix verified: v2 uses old LSB feedback for the standard right-shift `16'hB400`
  Galois sequence.
- Simulation: Cocotb testbench passed with `SIM=icarus`.
- Coverage: reset, reset priority, hold, first steps, randomized controls, and full
  65535 unique-state maximal-period check with no zero state.
- Synthesis: Yosys `check -assert` passed with 0 reported problems.
