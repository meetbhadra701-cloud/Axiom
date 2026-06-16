# To Verifier

v1 of `rtl/mixer.v` ready, spec in `spec/spec.md` (signed DSP mixer).

- Module: `mixer`
- Top-level: `mixer`
- Parameters: `SAMPLE_WIDTH=8`, `LO_WIDTH=8`, `OUT_WIDTH=16`
- Ports: `clk`, `rst` (sync active-high), `en`, signed `sample[7:0]`, signed `lo[7:0]`,
  registered signed `mixed[15:0]`
- Priority: reset > enable > hold
- Behavior: when enabled, `mixed <= sample * lo` using signed two's-complement arithmetic.
- Default widths preserve the full signed product.
- Iteration: 1
