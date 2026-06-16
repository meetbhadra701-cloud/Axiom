# Spec — `lfsr`: Galois Linear Feedback Shift Register

**Status:** authoritative. Ground truth for Architect and Verifier.
Previous specs archived in `spec/`.

## 1. Overview

A synchronous Galois-form LFSR (Linear Feedback Shift Register). Generates a
maximal-length pseudorandom binary sequence (PRBS) with period `2^WIDTH - 1` (all
non-zero states). Used for noise generation, test-pattern generation, data scrambling,
and CRC computation.

**Galois form** (also called internal XOR): feedback is applied to individual internal
tap positions in parallel, rather than chaining through the whole register. This
produces shorter combinational paths and better synthesis results than Fibonacci form.

Single clock domain, synchronous reset.

## 2. Parameters

| Name    | Default     | Meaning                                                         |
|---------|-------------|-----------------------------------------------------------------|
| `WIDTH` | `16`        | Register width and output width. Must be ≥ 2.                  |
| `POLY`  | `16'hB400`  | Galois feedback polynomial mask. Bit `i` of `POLY` being 1 means tap at position `i` is active. See §4. |

Default polynomial `16'hB400` = 16'b1011_0100_0000_0000 corresponds to the maximal-
length 16-bit polynomial x^16 + x^15 + x^13 + x^4 + 1 (taps at positions 15, 13, 3 in
0-indexed Galois notation). Produces a period of 65535.

## 3. Ports

| Name   | Dir | Width   | Description                                               |
|--------|-----|---------|-----------------------------------------------------------|
| `clk`  | in  | 1       | Clock. All state changes on rising edge.                  |
| `rst`  | in  | 1       | Synchronous, active-high reset. Loads `state` with the seed `SEED` parameter. |
| `en`   | in  | 1       | Shift enable (active-high).                               |
| `out`  | out | `WIDTH` | Registered LFSR state output.                             |

`out` is registered (driven from flip-flops).

## 4. Galois LFSR operation

In Galois form, the shift and XOR happen in one step:

- The **new LSB** (`next[0]`) is the **old MSB** (`state[WIDTH-1]`), which is the output bit.
- For bit positions `i` where `1 ≤ i ≤ WIDTH-1`:
  - If `POLY[i] == 1` (tap is active): `next[i] = state[i-1] ^ state[WIDTH-1]`
  - If `POLY[i] == 0` (no tap):       `next[i] = state[i-1]`

This can be written compactly as:
```
feedback = state[WIDTH-1]
next     = (state >> 1) ^ (feedback ? POLY : 0)
```

## 5. Seed / reset value

A separate parameter `SEED` specifies the post-reset state.

| Name   | Default | Meaning                                                           |
|--------|---------|-------------------------------------------------------------------|
| `SEED` | `1`     | Non-zero initial state loaded on `rst`. Must not be 0 (the LFSR locks up at all-zero). |

The all-zero state is the only fixed point that never exits; the spec prohibits `SEED=0`.

## 6. Behavior (per rising edge of `clk`)

Priority: **reset > enable > hold.**

1. If `rst == 1`    → `state <= SEED`.
2. else if `en == 1`→ apply one Galois step: `state <= (state >> 1) ^ (state[WIDTH-1] ? POLY : {WIDTH{1'b0}})`.
3. else             → `state` holds.

`out` always reflects the registered `state`.

## 7. Reset semantics

Synchronous, active-high. `rst` must not appear in a sensitivity list.

## 8. Synthesis constraints (CLAUDE.md §3)

- Single `always @(posedge clk)` block, non-blocking `<=`.
- Galois next-state logic is combinational — express inline or as a `wire`, not in an `always @(*)`.
- No `initial`, no `#` delays, no inferred latches.
- Must pass Yosys `check -assert` with 0 problems.
