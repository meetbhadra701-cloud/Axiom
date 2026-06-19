# Spec — iir_biquad (2nd-Order IIR Biquad Filter)

**Status:** authoritative. Ground truth for Architect and Verifier.

## Purpose

Registered 2nd-order IIR biquad filter section, Direct Form I, signed fixed-point.
Implements the difference equation:

```
y[n] = b0·x[n] + b1·x[n-1] + b2·x[n-2] − a1·y[n-1] − a2·y[n-2]
```

One new output sample per enabled clock cycle (latency = 1 enabled cycle). Used to
build low-pass, high-pass, band-pass, and notch filters by cascading sections.

## Parameters

| Parameter | Default | Description |
|---|---:|---|
| `DATA_W` | 16 | Bit width of input/output samples (signed two's-complement). |
| `COEF_W` | 16 | Bit width of coefficients (signed two's-complement). |
| `FRAC_W` | 14 | Fractional bits in coefficients. Coefficients are in Q1.FRAC_W format. |

The accumulator width is derived internally as `ACC_W = DATA_W + COEF_W + 3` (3 guard
bits for summing 5 products without overflow). This is a `localparam` — not a port
parameter — so it cannot be misconfigured.

## Coefficient format

Coefficients are signed fixed-point with FRAC_W fractional bits (implicit binary point
at position FRAC_W from the right). With defaults DATA_W=16, COEF_W=16, FRAC_W=14:

- +1.0 → 16384 (= 2^14)
- -1.0 → -16384
- +2.0 → 32767 (saturates at 2^15 − 1; coefficients ≥ 2.0 require COEF_W > 16)
- Range: approximately −2.0 to +1.99994

This range covers all standard biquad coefficients produced by common design tools
(Butterworth, Chebyshev, notch, etc.).

## Ports

| Port    | Dir   | Width   | Description |
|---|---|---:|---|
| `clk`   | input | 1       | Clock. |
| `rst`   | input | 1       | Synchronous, active-high reset. Clears all state and `y_out` to 0. |
| `en`    | input | 1       | Sample enable. New output computed and registered each cycle en=1. |
| `x_in`  | input | DATA_W  | Input sample (signed). |
| `b0`    | input | COEF_W  | Feed-forward coefficient (signed). |
| `b1`    | input | COEF_W  | Feed-forward coefficient (signed). |
| `b2`    | input | COEF_W  | Feed-forward coefficient (signed). |
| `a1`    | input | COEF_W  | Feed-back coefficient (signed). Note: subtracted in the equation. |
| `a2`    | input | COEF_W  | Feed-back coefficient (signed). Note: subtracted in the equation. |
| `y_out` | output | DATA_W | Filtered output sample (signed, registered). |
| `y_valid` | output | 1  | Pulses high for 1 cycle to indicate y_out is fresh. Goes low when en=0. |

## Behaviour

All state changes on `posedge clk`. Priority: **reset > enable > hold**.

**On reset:** x1, x2, y1, y2, y_out all cleared to 0; y_valid cleared to 0.

**On en=1:**
1. Compute `acc = b0*x_in + b1*x1 + b2*x2 − a1*y1 − a2*y2` at full ACC_W precision.
2. Truncate: `acc_trunc = acc[FRAC_W+DATA_W-1 : FRAC_W]` — discards fractional bits.
3. Register: `y_out <= acc_trunc; y_valid <= 1`.
4. Update delays: `x2<=x1; x1<=x_in; y2<=y1; y1<=acc_trunc`.

**On en=0:** y_valid goes low; all delay registers and y_out hold their values.

Feedback uses the **truncated** result `acc_trunc` (same value as y_out), not the full
accumulator. This is standard for fixed-point IIR and introduces only quantization
noise, not extra pipeline registers.

## Synthesis notes

- `acc` and `acc_trunc` are combinational `wire`s.
- All inputs are declared `signed`; Verilog uses signed multiplication automatically.
- `localparam ACC_W = DATA_W + COEF_W + 3;`
- Single `always @(posedge clk)` block for all state.
- No `initial`, no `#` delays, no inferred latches.
- Yosys `check -assert` must report 0 problems.

## Known test vectors

**Identity filter** (b0=2^FRAC_W, b1=b2=a1=a2=0 → pass-through with gain 1):
- x_in = 100 → y_out = 100 after 1 enabled cycle.

**Half-gain** (b0=2^(FRAC_W−1), others=0):
- x_in = 1000 → y_out = 500.
- x_in = 1001 → y_out = 500 (truncation, not rounding).

**DC blocker** (approximation for 16 kHz audio):
- b0=16384, b1=-32768, b2=16384, a1=-31130, a2=14746
- Verify step response decays to zero.

## Verification tips (for Verifier)

1. **Reset:** all outputs 0 after rst.
2. **Hold:** en=0 → y_out, y_valid, delays all unchanged.
3. **y_valid strobe:** y_valid=1 exactly on cycles where en=1; 0 otherwise.
4. **Identity:** b0=16384, others=0 → y_out == x_in after 1 en-cycle.
5. **Half-gain:** b0=8192, others=0 → y_out == x_in >> 1 (truncated).
6. **Impulse response:** for a non-trivial filter (DC blocker), compute a 50-sample
   Python reference and compare cycle-by-cycle:
   ```python
   def biquad_ref(b, a, xs, frac_w=14):
       scale = 1 << frac_w
       x1 = x2 = y1 = y2 = 0
       ys = []
       for x in xs:
           acc = b[0]*x + b[1]*x1 + b[2]*x2 - a[0]*y1 - a[1]*y2
           # Truncate toward negative infinity (arithmetic right shift)
           y = acc >> frac_w  # Python >> is arithmetic
           ys.append(y)
           x2, x1, y2, y1 = x1, x, y1, y
       return ys
   ```
7. **Randomized:** random coefficients + random sample sequences, compare to reference.
