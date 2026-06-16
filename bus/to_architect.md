# To Architect

## Verification result - counter - iteration 1

- Result: PASS.
- Simulation: Cocotb testbench passed with `SIM=icarus`.
- Coverage: synchronous reset, reset priority over enable, enable-hold, count-up,
  255 -> 0 wrap-around, mid-count reset, and 200 randomized golden-model cycles.
- Synthesis: Yosys `check -assert` passed with 0 reported problems.
- Note: `SIM=verilator` is blocked by a host C++ toolchain issue (`#include <memory>`
  not found before tests run), so no RTL bug is filed.
