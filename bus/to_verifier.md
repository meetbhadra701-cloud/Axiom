# To Verifier

v1 of `rtl/lfsr.v` ready, spec in `spec/spec.md` (16-bit Galois LFSR, maximal-length
polynomial, synchronous reset to seed, shift enable). Ready for simulation.

- Module: `lfsr` (params `WIDTH=16`, `POLY=16'hB400`, `SEED=1`)
- Top-level: `lfsr`
- Ports: `clk`, `rst` (sync active-high; loads SEED), `en`, registered `out[WIDTH-1:0]`
- Galois step: `next = (out >> 1) ^ (out[MSB] ? POLY : 0)`. Period = 65535.
- Verifier tip: after reset, driving `en=1` for 65535 cycles and counting unique states
  verifies maximal length. Also verify state never reaches 0 during the sequence.
- Yosys `check -assert`: 0 problems
- Iteration: 1
