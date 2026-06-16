# Spec — sine_lut (Sine Lookup Table)

**Status:** authoritative. Ground truth for Architect and Verifier.
Previous specs archived in `spec/`.

## Purpose

Quarter-wave ROM-based sine lookup table. Converts a phase value from an NCO
(or any source) into a signed sine amplitude. Completing the NCO into a full DDS
requires mapping `phase_out[PHASE_WIDTH-1:0]` → `sin_out[DATA_WIDTH-1:0]`.

The quarter-wave trick: only 2^(ADDR_WIDTH-2) entries are stored; the full cycle
is reconstructed from quadrant symmetry.

## Parameters

| Parameter  | Default | Description |
|---|---|---|
| ADDR_WIDTH | 8  | Phase bits consumed. LUT depth = 2^(ADDR_WIDTH-2) = 64 entries for default. |
| DATA_WIDTH | 8  | Output amplitude bits. Signed range: -(2^(DATA_WIDTH-1)) to +(2^(DATA_WIDTH-1)-1). |

## Ports

| Port      | Direction | Width       | Description |
|---|---|---|---|
| clk       | input     | 1           | Clock. |
| phase_in  | input     | ADDR_WIDTH  | Phase address (unsigned). Top 2 bits select quadrant. |
| sin_out   | output    | DATA_WIDTH  | Signed sine amplitude. Registered (one-cycle latency). |

No reset port — ROM contents are static; output is valid one cycle after phase_in.

## Behaviour

Let N = 2^(ADDR_WIDTH-2) = 64 for defaults (quarter-wave depth).
Let `quad = phase_in[ADDR_WIDTH-1:ADDR_WIDTH-2]` (top 2 bits).
Let `idx  = phase_in[ADDR_WIDTH-3:0]` (lower ADDR_WIDTH-2 bits).

**Quadrant decode (combinational):**

| quad | ROM index   | Output sign |
|------|-------------|-------------|
| 2'b00 (Q0) | `idx`   | positive |
| 2'b01 (Q1) | `~idx`  | positive |
| 2'b10 (Q2) | `idx`   | negative |
| 2'b11 (Q3) | `~idx`  | negative |

**ROM contents:**
`lut[i] = round( (2^(DATA_WIDTH-1) - 1) * sin( (i + 0.5) * pi / (2*N) ) )`
For ADDR_WIDTH=8, DATA_WIDTH=8: N=64, amplitudes in 0..127 (unsigned in the LUT).

**Negation for Q2/Q3:** apply two's-complement negation to the unsigned LUT value.
At DATA_WIDTH=8, peak stored value is 127; -127 is representable; -128 is never produced.

**Output register:** `sin_out` is registered at `posedge clk`. One-clock pipeline latency.

## Synthesis notes

- ROM initialised with `initial` block assigning a `reg [DATA_WIDTH-1:0] lut [0:DEPTH-1]`.
  This is the **one permitted use of `initial`** in this project — all synthesis targets
  (Xilinx, Intel, Lattice, Yosys) support `initial` for constant ROM content.
- Quadrant decode is pure combinational (`wire` or `always @(*)`).
- The registered stage is a single `always @(posedge clk)` with one `<=` assignment.
- No reset input — this is intentional and per spec.
- Expected Yosys `check -assert`: 0 problems.

## Verification tip (for Verifier)

Key checks for ADDR_WIDTH=8, DATA_WIDTH=8 (N=64, period=256 phases):
1. After 1 clock: `phase_in=0` → `sin_out` ≈ +3 (first bin centre is sin(π/512)×127≈0.78, rounds to 1; exact value depends on rounding).
2. `phase_in=64`  (Q1 start, 90°) → sin_out should be close to the peak ≈ +127.
3. `phase_in=128` (Q2 start, 180°) → sin_out close to 0 (negative side).
4. `phase_in=192` (Q3 start, 270°) → sin_out close to -127.
5. Full 256-cycle sweep: output is non-decreasing through Q0, non-increasing through Q1,
   non-increasing (negative) through Q2, non-decreasing through Q3.
6. Sum of all 256 outputs ≈ 0 (no DC bias).
