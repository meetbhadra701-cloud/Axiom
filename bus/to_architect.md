# To Architect

## Verification result - edge_det - iteration 1

- Result: PASS.
- Simulation: Cocotb testbench passed with `SIM=icarus`.
- Coverage: synchronous reset, reset priority, sustained low/high behavior, registered
  rise/fall/any-edge pulses, 1-cycle input pulse behavior, reset clearing an in-flight
  transition, `any_edge == rise | fall`, and 600 randomized signal/reset cycles.
- Synthesis: Yosys `check -assert` passed with 0 reported problems.
- Note: the test models the registered pipeline directly. For a 0->1 input transition,
  `rise` is observed after the pipe has sampled the new and old values (`pipe[0]=1`,
  `pipe[1]=0`).
