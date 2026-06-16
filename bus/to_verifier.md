# To Verifier

v1 of `rtl/mac.v` ready, written to `spec/spec.md` (signed multiply-accumulate,
synchronous reset/clear, enable-controlled accumulation, signed wrap-around arithmetic).
Ready for simulation.

- Module: `mac` (params `A_WIDTH=8`, `B_WIDTH=8`, `ACC_WIDTH=32`)
- Top-level: `mac`
- Ports: `clk`, `rst`, `clear`, `en`, signed `a`, signed `b`, signed registered `acc`
- Iteration: 1
