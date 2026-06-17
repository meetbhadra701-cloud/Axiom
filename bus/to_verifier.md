# To Verifier

v1 of `rtl/debounce.v` ready, spec in `spec/spec.md` (synchronous signal debouncer).
Ready for simulation.

- Module: `debounce` (param `STABLE_BITS=4`, threshold = 16 consecutive differing cycles)
- Top-level: `debounce`
- Ports: `clk`, `rst` (sync active-high), `sig_in`, registered `sig_out`
- No `en` port — runs continuously.
- Internal: `counter[3:0]` counts cycles where sig_in ≠ sig_out.
  - sig_in == sig_out → counter = 0.
  - counter == 4'hF (15) → sig_out ← sig_in, counter ← 0.
  - else → counter++.
- Threshold: sig_out updates after **16** consecutive cycles of sig_in ≠ sig_out
  (counter starts at 0, takes 15 increments to reach 15, accept fires on cycle 16).
- Yosys `check -assert`: 0 problems.
- Iteration: 1

Verification tips (STABLE_BITS=4, threshold = 16 consecutive differing cycles):
- Clean rise: sig_in=1 continuously; sig_out→1 on cycle 16 (when counter reaches 15).
- Short glitch: sig_in=1 for only 15 cycles then back to 0 → sig_out stays 0.
- Counter reset: 15 cycles of sig_in=1 then 1 cycle sig_in=0 resets counter; 16 more needed.
- Fall: after sig_out=1, sig_in=0 for 16 cycles → sig_out→0.
- Reset mid-count: clears counter and sig_out to 0.
- Randomized: any stable run < 16 cycles never triggers; any run ≥ 16 cycles always triggers.
