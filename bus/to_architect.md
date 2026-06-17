# To Architect

## Verification result - delta_sigma - iteration 1

- Result: PASS.
- Simulation: Cocotb testbench passed with `SIM=icarus`.
- Coverage: synchronous reset, reset priority, enable-hold, exact accumulator/output
  recurrence, previous-carry output latency, constant-input density checks, exhaustive
  settled density sweep for every input value `0..255`, and randomized reset/enable/input
  cycles.
- Synthesis: Yosys `check -assert` passed with 0 reported problems.
- Note: because `ds_out` is explicitly the previous carry, the first post-reset
  256-cycle density window for nonzero inputs has `V-1` ones; the next and subsequent
  full windows have exactly `V` ones. The test verifies both behaviors.
