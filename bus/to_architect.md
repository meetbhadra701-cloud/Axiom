# To Architect

## Verification result - crc8 - iteration 1

- Result: PASS.
- Simulation: Cocotb testbench passed with `SIM=icarus`.
- Coverage: synchronous reset, reset priority, hold behavior, zero byte, single leading
  1-bit state (`0x8C`), full byte `0x01` (`0x5E`), byte `0xFF` (`0x35`), standard
  `"123456789"` check (`0xA1`), 50 randomized byte strings, and 400 randomized
  reset/enable/bit cycles against a manual CRC-8/MAXIM reference model.
- Synthesis: Yosys `check -assert` passed with 0 reported problems.
- Note: Verifier corrected the spec/handoff note for byte `0x01`: `0x8C` is the state
  after one enabled `1` bit, while the full byte `0x01` CRC is `0x5E`.
- Note: Final netlist contains 8 enabled/reset flops, 3 XNORs, and 1 NOT.
- Note: Simulation used the existing Python 3.13 cocotb 2.0.1 venv at
  `/tmp/axiom-cocotb-venv`.
