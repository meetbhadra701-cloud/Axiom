# To Verifier

v1 of `rtl/sat_adder.v` ready, spec in `spec/spec.md` (synchronous signed saturating
adder). Ready for simulation.

- Module: `sat_adder`
- Top-level: `sat_adder`
- Parameter: `WIDTH=16`
- Ports: `clk`, `rst` (sync active-high), `en`, signed `a[15:0]`, signed `b[15:0]`,
  registered signed `sum[15:0]`
- Priority: reset > enable > hold
- Behavior: when enabled, output mathematical `a + b` clipped to `-32768..32767`.
- Positive overflow saturates to `32767`; negative overflow saturates to `-32768`.
- Iteration: 1
