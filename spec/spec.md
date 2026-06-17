# Spec — delta_sigma (1st-Order Delta-Sigma Modulator)

**Status:** authoritative. Ground truth for Architect and Verifier.
Previous specs archived in `spec/`.

## Purpose

First-order delta-sigma (ΔΣ) modulator. Converts an unsigned multi-bit input sample
into a 1-bit pulse-density-modulated (PDM) bitstream whose time-average equals the
input value divided by 2^WIDTH. Useful as a 1-bit DAC output stage: filtering the
PDM output with an RC low-pass gives an analogue voltage proportional to the input.

Pairs with the `pwm` module: both produce 1-bit outputs, but delta-sigma has much
better noise-shaping (quantisation noise is pushed to high frequencies).

## Parameters

| Parameter | Default | Description |
|---|---:|---|
| `WIDTH`   | 8 | Unsigned input width. Accumulator is WIDTH+1 bits. |

## Ports

| Port     | Direction | Width   | Description |
|---|---|---:|---|
| `clk`    | input  | 1       | Clock. |
| `rst`    | input  | 1       | Synchronous, active-high reset. |
| `en`     | input  | 1       | Sample enable. Accumulator and output advance when high. |
| `in`     | input  | `WIDTH` | Unsigned input sample. |
| `ds_out` | output | 1       | Registered 1-bit PDM output. |

## Behaviour

All state changes on `posedge clk`. Priority: **reset > enable > hold**.

Internal state: `acc`, a WIDTH+1 bit register (the extra bit captures carry/overflow).

1. If `rst == 1`: `acc <= 0`, `ds_out <= 0`.
2. Else if `en == 1`:
   - `acc <= acc[WIDTH-1:0] + in` — add input to the lower WIDTH bits of acc; the
     result is WIDTH+1 bits wide (carry into bit WIDTH is the new `ds_out`).
   - `ds_out <= acc[WIDTH]`  — the carry bit from the previous addition becomes the output.
   
   Equivalently, using a WIDTH+1 accumulator where bit WIDTH is the carry:
   `{ds_out, acc[WIDTH-1:0]} <= {1'b0, acc[WIDTH-1:0]} + {1'b0, in}`
   This clears the carry bit before adding, so the accumulator runs in [0, 2^WIDTH−1]
   and overflows into ds_out when the running sum exceeds 2^WIDTH.
3. Else: `acc` and `ds_out` hold.

## Modulator equation

Let N = 2^WIDTH. Over many cycles with constant input value V (0 ≤ V < N):
- The fraction of cycles where `ds_out = 1` converges to V / N.
- For V = 0: `ds_out` is always 0.
- For V = N−1 (= 255 for WIDTH=8): `ds_out` is 1 on 255 out of every 256 cycles.
- For V = N/2 (= 128): `ds_out` is 1 on 128 out of 256 cycles (50% duty).

## Synthesis constraints

- Single `always @(posedge clk)` block; two non-blocking assignments (`acc` and `ds_out`).
- Accumulator declared as `reg [WIDTH:0] acc` (WIDTH+1 bits).
- The carry-clear before each add prevents acc from growing unboundedly.
- No `initial`, no `#` delays, no inferred latches.
- Yosys `check -assert` must report 0 problems.

## Verification tips (for Verifier)

For WIDTH=8 (N=256):

1. **Reset:** acc=0 and ds_out=0 after rst=1.
2. **Hold:** en=0 preserves acc and ds_out.
3. **in=0:** ds_out stays 0 indefinitely.
4. **in=255 (max):** ds_out is 1 on 255/256 cycles — one 0 per period.
5. **in=128 (50%):** count ds_out=1 over 256 cycles → exactly 128.
6. **in=64 (25%):** count over 256 cycles → exactly 64.
7. **Density sweep:** for each input V in 0..255, run 256 enabled cycles and assert
   `count_ones == V` (exact for all inputs with a 1st-order modulator over one full period).
8. **Randomised:** drive random inputs and verify running average converges to input/256.
