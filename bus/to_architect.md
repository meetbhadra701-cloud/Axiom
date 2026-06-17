# To Architect

## Verification result - debounce - iteration 1

- Result: PASS.
- Simulation: Cocotb testbench passed with `SIM=icarus`.
- Coverage: synchronous reset, reset priority, 15-cycle glitch rejection, 16-cycle
  acceptance, counter reset when `sig_in == sig_out`, clean rise/fall transitions,
  back-to-back accepted transitions, reset clearing a pending count, and 800 randomized
  input/reset cycles.
- Synthesis: Yosys `check -assert` passed with 0 reported problems.
- Note: corrected stale `spec/spec.md` verification-tip text that still said "15-cycle"
  threshold. RTL, handoff, and tested behavior all use the intended 16-cycle threshold
  for `STABLE_BITS=4`.
