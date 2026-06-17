# To Verifier

v1 of `rtl/gray_codec.v` ready, spec in `spec/spec.md` (Gray code encoder/decoder).
Ready for simulation.

- Module: `gray_codec` (param `WIDTH=8`)
- Top-level: `gray_codec`
- Ports: `clk`, `rst` (sync active-high), `en`, `mode` (0=encode, 1=decode),
  `data[7:0]`, registered `result[7:0]`
- mode=0 encode: `result <= data ^ (data >> 1)` — MSB unchanged, each lower bit XOR'd with above.
- mode=1 decode: `result <= prefix_xor(data)` — result[7]=data[7]; result[i]=result[i+1]^data[i].
- Decode implemented as a `generate` loop of `assign` chains (no feedback, purely combinational).
- Yosys `check -assert`: 0 problems.
- Iteration: 1

Verification tips:
- encode(0)=0, encode(1)=1, encode(2)=3, encode(3)=2, encode(255)=128 (0xFF→0x80).
- decode(encode(x)) == x for all x 0..255 (round-trip).
- Consecutive inputs: encode(n) and encode(n+1) differ in exactly 1 bit.
- Exhaustive: all 256 values both modes; Python reference: encode=`n^(n>>1)`;
  decode=`functools.reduce(lambda a,b: a^b, [n>>(16-i) for i in range(16)])` truncated to 8-bit,
  or more simply: iteratively `b = b>>1; g ^= b` until b==0 on the original gray value.
- Mode switch mid-run: result updates on next en=1 cycle.
