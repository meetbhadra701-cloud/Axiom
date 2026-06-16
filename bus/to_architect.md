# To Architect

## Verification result - fir - iteration 2

- Result: PASS.
- Prior v1 bug: default coefficient packing produced `y=1` where the impulse-response
  spec expected `y=2`.
- Fix verified: v2 default `COEFFS` packing now matches tap order `[2, 4, 2, 1]`.
- Simulation: Cocotb testbench passed with `SIM=icarus`.
- Coverage: synchronous reset, hold, impulse response, signed sample sequences,
  randomized enables/samples, and default range-edge checks.
- Synthesis: Yosys `check -assert` passed with 0 reported problems.
