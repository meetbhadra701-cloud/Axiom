# To Verifier

v1 of `rtl/edge_det.v` ready, spec in `spec/spec.md` (two-stage synchronous edge
detector). Ready for simulation.

- Module: `edge_det` (no parameters)
- Top-level: `edge_det`
- Ports: `clk`, `rst` (sync active-high), `sig_in`, registered `rise`, `fall`, `any_edge`
- No `en` port — detection runs continuously; rst is the only control.
- Internal: `pipe[1:0]`; pipe[0] = current sample, pipe[1] = one cycle older.
- rise = pipe[0] & ~pipe[1]; fall = ~pipe[0] & pipe[1]; any_edge = pipe[0] ^ pipe[1].
- All three outputs are registered — 2-cycle latency after input transition.
- Yosys `check -assert`: 0 problems.
- Iteration: 1

Verification tips:
- Rising edge: sig_in 0→1 on cycle N; rise=1 on cycle N+2 for exactly 1 cycle.
- Falling edge: sig_in 1→0 on cycle N; fall=1 on cycle N+2 for exactly 1 cycle.
- Sustained: no further pulses while sig_in held constant.
- 1-cycle glitch (0→1→0): rise fires cycle+2, fall fires cycle+3, any_edge fires both.
- any_edge == rise | fall at all times.
- Reset during in-flight: pipe and all outputs clear to 0.
