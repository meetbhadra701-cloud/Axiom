# To Architect

## Verification result - fifo - iteration 1

- Result: PASS.
- Simulation: Cocotb testbench passed with `SIM=icarus`.
- Coverage: synchronous reset, reset priority, empty-read ignore, fill/full behavior,
  ignored full writes, simultaneous read/write, pointer wrap, drain ordering, and
  500 randomized queue-model cycles.
- Synthesis: Yosys `check -assert` passed with 0 reported problems.
- Note: transparent-read `dout` is not checked while FIFO is empty because reset leaves
  memory contents don't-care per spec.
