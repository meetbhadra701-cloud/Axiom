# To Architect

## Verification result - mac - iteration 1

- Result: PASS.
- Simulation: Cocotb testbench passed with `SIM=icarus`.
- Coverage: synchronous reset, reset priority, clear priority, enable-hold,
  signed positive/negative products, 300 randomized golden-model cycles, and
  two's-complement accumulator wrap stress.
- Synthesis: Yosys `check -assert` passed with 0 reported problems.
- Note: `SIM=verilator` remains blocked by the host C++ toolchain issue
  (`#include <memory>` not found before tests run), so no RTL bug is filed.
