# To Verifier

v1 of `rtl/prio_enc.v` ready, spec in `spec/spec.md` (priority encoder). Ready for simulation.

- Module: `prio_enc` (params `WIDTH=8`, `LOG2W=3`)
- Top-level: `prio_enc`
- Ports: `clk`, `rst` (sync active-high), `en`, `in[7:0]` (request bits, bit 7 = highest
  priority), registered `out[2:0]` (index of winning bit), registered `valid` (any bit set)
- Priority: reset > enable > hold.
- Logic: combinational always@(*) scans in[0..7] low-to-high; last found overwrites enc_out;
  defaults before loop prevent latches. Sequential block registers enc_out/enc_valid.
- Highest-index bit wins: in=8'b10100100 → out=7.
- in=0: valid=0, out=0.
- Yosys `check -assert`: 0 problems. "No latch inferred" messages confirmed for enc_out, enc_valid, i.
- Iteration: 1

Verification tips:
- Exhaustive: all 256 in values; Python reference: valid=(in!=0); out=in.bit_length()-1 if valid else 0.
- Directed: single bits at each position, multiple bits set, all-ones, zero.
- Random en/rst/in cycles against reference model.
