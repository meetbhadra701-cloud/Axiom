# To Verifier

v1 of `rtl/nco.v` ready, spec in `spec/spec.md` (NCO phase accumulator, unsigned,
wrapping, synchronous reset, enable). Ready for simulation.

- Module: `nco` (param `PHASE_WIDTH=24`)
- Top-level: `nco`
- Ports: `clk`, `rst` (sync active-high), `en`, unsigned `phase_inc[PHASE_WIDTH-1:0]`,
  registered unsigned `phase_out[PHASE_WIDTH-1:0]`
- Behavior: `phase_out += phase_inc` per enabled clock edge, wraps at 2^PHASE_WIDTH.
  `phase_inc=0` → holds. `phase_inc=2^(PHASE_WIDTH-1)` → Nyquist toggle.
- Yosys `check -assert`: 0 problems
- Iteration: 1
