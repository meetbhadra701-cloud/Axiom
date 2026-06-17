# To Verifier

v1 of `rtl/delta_sigma.v` ready, spec in `spec/spec.md` (1st-order delta-sigma
modulator). Ready for simulation.

- Module: `delta_sigma` (param `WIDTH=8`)
- Top-level: `delta_sigma`
- Ports: `clk`, `rst` (sync active-high), `en`, unsigned `in[7:0]`,
  registered `ds_out` (1-bit PDM output)
- Priority: reset > enable > hold.
- Internal: `acc[WIDTH:0]` (9 bits). Each enabled cycle:
    acc    <= {1'b0, acc[7:0]} + {1'b0, in}   // carry-cleared add
    ds_out <= acc[8]                            // carry from PREVIOUS cycle
- Time-average of ds_out = in / 256.
- in=0 → ds_out always 0; in=255 → 255 highs per 256-cycle period; in=128 → exactly 128/256.
- Yosys `check -assert`: 0 problems.
- Iteration: 1

Verification tips:
- For any constant input V (0..255), count ds_out=1 over exactly 256 enabled cycles → count == V.
- in=0: ds_out never goes high.
- in=255: exactly one 0 per 256-cycle period.
- in=128: exactly 128 ones per period.
- density sweep: iterate V=0..255, run 256 cycles each, assert count_ones == V.
