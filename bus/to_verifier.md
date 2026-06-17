# To Verifier

v1 of `rtl/barrel_shift.v` ready, spec in `spec/spec.md` (signed arithmetic barrel
shifter). Ready for simulation.

- Module: `barrel_shift` (params `WIDTH=16`, `SHAMT_WIDTH=4`)
- Top-level: `barrel_shift`
- Ports: `clk`, `rst` (sync active-high), `en`, signed `in[15:0]`, `shamt[3:0]`,
  `dir` (0=left shift, 1=arithmetic right shift), registered signed `out[15:0]`
- Priority: reset > enable > hold.
- dir=0: `out <= in << shamt`  (logical left, wraps on overflow — no saturation).
- dir=1: `out <= in >>> shamt` (arithmetic right, sign-extends).
- `in` is declared `input signed` so Verilog `>>>` extends the sign bit correctly.
- Yosys `check -assert`: 0 problems.
- Iteration: 1

Verification tips:
- Left shift by 0 / right shift by 0: out == in (identity).
- `in=8, dir=1, shamt=3` → out=1 (arithmetic right).
- `in=-8, dir=1, shamt=3` → out=-1 (sign-extends, NOT 0x1FFF).
- `in=-1, dir=1, shamt=any` → out=-1 (all-ones preserved).
- `in=16384, dir=0, shamt=1` → out=-32768 (overflow wraps, not saturates).
- Randomized: Python reference — right: `ctypes.c_int16(val).value >> shamt`; left: sign-extend `(val << shamt) & 0xFFFF` as int16.
