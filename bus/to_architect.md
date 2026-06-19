# To Architect

## Verification result - uart_tx - iteration 1

- Result: PASS.
- Simulation: Cocotb testbench passed with `SIM=icarus`.
- Coverage: synchronous reset, directed 0x55/0xAA/0x00/0xFF frames, start/data/stop
  sampling at baud midpoints, exact busy duration, ignored `en` while busy, random
  20-byte TX stream deserialisation, and back-to-back start on the stop-bit completion
  edge.
- Synthesis: Yosys `check -assert` passed with 0 reported problems.
- Note: Initial sim caught that `en` on the stop-bit completion edge was ignored. Verifier
  applied a small RTL fix so STOP can immediately load the next byte and drive the next
  start bit.
- Note: Final netlist contains 113 cells for the default-width UART.
- Note: Simulation used the existing Python 3.13 cocotb 2.0.1 venv at
  `/tmp/axiom-cocotb-venv`.
