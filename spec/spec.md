# Spec — debounce (Signal Debouncer)

**Status:** authoritative. Ground truth for Architect and Verifier.
Previous specs archived in `spec/`.

## Purpose

Synchronous signal debouncer. Outputs a clean version of a noisy 1-bit input by
requiring the input to be stable for `2^STABLE_BITS` consecutive clock cycles before
the output updates. Designed to be chained with `edge_det` (debounce first, then
detect the clean transition).

## Parameters

| Parameter     | Default | Description |
|---|---:|---|
| `STABLE_BITS` | 4 | Stability counter width. Output updates after 2^STABLE_BITS = 16 stable cycles. |

## Ports

| Port      | Direction | Width | Description |
|---|---|---:|---|
| `clk`     | input  | 1 | Clock. |
| `rst`     | input  | 1 | Synchronous, active-high reset. Clears counter; `sig_out` resets to 0. |
| `sig_in`  | input  | 1 | Noisy input signal. |
| `sig_out` | output | 1 | Registered debounced output. |

No `en` port — debouncing runs continuously; `rst` is the only control.

## Behaviour

All state changes on `posedge clk`. Priority: **reset > normal**.

Internal state: `counter` (STABLE_BITS bits), the number of consecutive cycles that
`sig_in` has **differed** from `sig_out`.

1. If `rst == 1`: `counter <= 0`, `sig_out <= 0`.
2. Else:
   - If `sig_in == sig_out`: `counter <= 0` (input matches output — stable, reset counter).
   - Else if `counter == {STABLE_BITS{1'b1}}` (counter saturated — stable for 2^STABLE_BITS cycles):
     - `sig_out <= sig_in` (accept the new value)
     - `counter <= 0`
   - Else: `counter <= counter + 1'b1` (still waiting for stability).

**Output update rule:** `sig_out` changes only when `sig_in` has differed from
`sig_out` for exactly `2^STABLE_BITS` consecutive cycles. A single-cycle glitch on
`sig_in` resets the counter but does not change `sig_out`.

**Counter semantics:** the counter counts how many consecutive cycles `sig_in ≠ sig_out`.
It resets to 0 whenever the two match or whenever `sig_out` updates.

## Synthesis constraints

- Single `always @(posedge clk)` block, two non-blocking assignments.
- Counter is `reg [STABLE_BITS-1:0]`.
- Full-ones comparison `counter == {STABLE_BITS{1'b1}}` synthesises to a single AND gate.
- No `initial`, no `#` delays, no inferred latches.
- Yosys `check -assert` must report 0 problems.

## Verification tips (for Verifier)

For STABLE_BITS=4 (stable threshold = 16 consecutive differing cycles):

1. **Reset:** counter=0, sig_out=0 after rst=1.
2. **Clean transition:** drive sig_in=1 continuously; sig_out→1 on cycle 16
   (counter increments from 0 to 15 over 15 cycles, fires on the 16th).
3. **Short glitch:** drive sig_in=1 for only 15 cycles then back to 0; sig_out stays 0.
4. **Counter reset on match:** drive sig_in=1 for 10 cycles, then sig_in=0 for 1 cycle;
   counter resets; another 16 cycles of sig_in=1 needed before sig_out updates.
5. **Fall transition:** sig_in=0 for 16+ cycles after sig_out is 1; sig_out→0.
6. **Glitch immunity:** interleave sig_in pulses shorter than 16 cycles; sig_out never changes.
7. **Back-to-back transitions:** after sig_out updates to 1, immediately drive sig_in=0
   for 16 cycles; sig_out→0 correctly.
8. **Randomized:** random sig_in patterns with known stable runs; verify sig_out only
   changes after a verified 16-cycle stable stretch.
