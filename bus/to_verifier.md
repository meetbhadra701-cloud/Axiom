# To Verifier

v1 of `rtl/one_hot.v` ready, spec in `spec/spec.md` (binary-to-one-hot decoder). Ready for simulation.

- Module: `one_hot`
- Top-level: `one_hot`
- Ports: `clk`, `rst` (sync active-high), `en`, `in[LOG2W-1:0]`, `out[N-1:0]` (output reg)
- Default params: N=8, LOG2W=3.
- Combinational decode: `wire [N-1:0] decoded = {{(N-1){1'b0}}, 1'b1} << in`.
- Priority: reset > enable > hold.
- Yosys `check -assert`: 0 problems. Synthesizes to 8 SDFFE + 6 ANDNOT + 5 AND + 1 NOR.
- Iteration: 1

Key test vectors (N=8, LOG2W=3):
1. Reset → out=0x00.
2. en=0 → out unchanged.
3. in=0 → out=0x01 (8'b00000001).
4. in=3 → out=0x08 (8'b00001000).
5. in=7 → out=0x80 (8'b10000000).
6. All indices 0..7: out == (1 << in).

Python reference:
```python
def one_hot_ref(n_bits, idx):
    return (1 << idx) & ((1 << n_bits) - 1)
```

Cocotb port names: `dut.clk`, `dut.rst`, `dut.en`, `dut.in_` (use `getattr(dut, 'in')` for
the `in` port — it's a Python keyword, so cocotb access via `getattr` is required, same
pattern as `barrel_shift`).

Also test N=16, LOG2W=4 by re-running with parameter overrides.
