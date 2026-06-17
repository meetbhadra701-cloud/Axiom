# To Architect

## Verification result - pipe_delay - iteration 1

- Result: PASS.
- Simulation: Cocotb testbench passed with `SIM=icarus` for default `DEPTH=4` and an
  override run with `DEPTH=1`.
- Coverage: synchronous reset, reset priority, enable-hold freeze, single-cycle pulse
  latency, continuous sequence latency, enable-gated paused latency, DEPTH=1 register
  behavior, and 600 randomized reset/enable/data cycles against a Python stage model.
- Synthesis: Yosys `check -assert` passed with 0 reported problems.
- Note: Verifier applied a small RTL portability cleanup before final PASS: split
  stage 0 out of the generate loop so Icarus no longer elaborates an unreachable
  `pipe[-1]` reference. Behavior is unchanged.
- Note: Yosys reports its normal pipe-array memory-to-register replacement warning;
  the final netlist contains 32 enabled/reset flops for WIDTH=8, DEPTH=4.
- Note: Simulation used the existing Python 3.13 cocotb 2.0.1 venv at
  `/tmp/axiom-cocotb-venv`.
