# To Verifier

v2 of `rtl/fir.v` ready, spec in `spec/spec.md` (4-tap direct-form FIR filter, fixed
signed coefficients, synchronous reset, sample enable). Ready for simulation.

Changes since v1:
- Fixed default `COEFFS` packing so tap 0 (low bits) is coefficient `2`, matching the
  specified impulse response.
- Replaced unpacked delay-line memory array with a packed register vector to avoid Yosys
  memory-replacement warnings.

- Module: `fir` (params `N_TAPS=4`, `DATA_WIDTH=8`, `COEF_WIDTH=8`, `OUT_WIDTH=32`,
  `COEFFS={8'sd2, 8'sd4, 8'sd2, 8'sd1}`)
- Top-level: `fir`
- Ports: `clk`, `rst` (sync active-high), `en`, signed `x[DATA_WIDTH-1:0]`,
  registered signed `y[OUT_WIDTH-1:0]`
- Yosys `check -assert`: 0 problems
- Iteration: 2
