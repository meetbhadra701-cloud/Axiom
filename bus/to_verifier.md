# To Verifier

v1 of `rtl/iir_biquad.v` ready, spec in `spec/spec.md` (2nd-order IIR biquad, Direct Form I). Ready for simulation.

- Module: `iir_biquad`
- Top-level: `iir_biquad`
- Ports: `clk`, `rst` (sync active-high), `en`, `x_in[15:0]` signed, `b0/b1/b2/a1/a2[15:0]` signed, `y_out[15:0]` signed, `y_valid`
- Default params: DATA_W=16, COEF_W=16, FRAC_W=14.
- Equation: `y[n] = b0*x[n] + b1*x[n-1] + b2*x[n-2] - a1*y[n-1] - a2*y[n-2]` (coefficients scaled by 2^FRAC_W).
- Latency: 1 enabled cycle (combinational MAC + single register).
- y_valid=1 when en=1; y_valid=0 when en=0.
- Yosys `check -assert`: 0 problems.
- Iteration: 1

Coefficient format (Q1.14 with FRAC_W=14):
- 1.0 → 16384; -1.0 → -16384; -2.0 → -32768; max ≈ +1.99994 → 32767.

Key test vectors:
1. Reset → y_out=0, y_valid=0.
2. Hold (en=0) → y_out unchanged, y_valid=0.
3. Identity (b0=16384, b1=b2=a1=a2=0): x_in=100 → y_out=100 after 1 en-cycle.
4. Half-gain (b0=8192, others=0): x_in=1000 → y_out=500; x_in=1001 → y_out=500 (truncation).
5. DC blocker (b0=16384, b1=-32768, b2=16384, a1=-31130, a2=14746): 50-sample impulse
   response matches Python reference.

Python reference for the filter:
```python
def biquad_ref(b0, b1, b2, a1, a2, xs, frac_w=14):
    x1 = x2 = y1 = y2 = 0
    ys = []
    for x in xs:
        # Python int arithmetic — no overflow concern
        acc = b0*x + b1*x1 + b2*x2 - a1*y1 - a2*y2
        # Arithmetic right shift (truncation toward -inf, matching Verilog >>>)
        y = acc >> frac_w
        # Truncate to DATA_W signed range
        y = y & 0xFFFF
        if y >= 0x8000:
            y -= 0x10000
        ys.append(y)
        x2, x1, y2, y1 = x1, x, y1, y
    return ys
```

Note: Verilog bit-slice `acc[FRAC_W+DATA_W-1:FRAC_W]` truncates (floors) toward
negative infinity for negative numbers — same as Python `>>`. No rounding.

Cocotb note: all coefficient and data ports are declared `signed` in Verilog. Drive them
as signed Python ints; cocotb handles two's-complement automatically for negative values.
