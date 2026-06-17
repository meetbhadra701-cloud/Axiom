# To Verifier

v1 of `rtl/shift_reg.v` ready, spec in `spec/spec.md` (universal shift register).
Ready for simulation.

- Module: `shift_reg` (param `WIDTH=8`)
- Top-level: `shift_reg`
- Ports: `clk`, `rst` (sync active-high), `load`, `en`, `serial_in`, `parallel_in[7:0]`,
  `serial_out` (wire, sr[7]), `parallel_out[7:0]` (wire, = sr)
- Priority: reset > load > en (shift) > hold.
- Shift: left-shift `sr <= {sr[6:0], serial_in}` — serial_in enters at LSB, MSB exits.
- `serial_out` and `parallel_out` are combinational (direct wires from `sr`).
- Yosys `check -assert`: 0 problems.
- Iteration: 1

Verification tips:
- PISO transmit: load 8'hAB (10101011), then 8 shift cycles → serial_out sequence: 1,0,1,0,1,0,1,1.
- SIPO receive: shift in 8 bits into serial_in; verify parallel_out contains the
  assembled word (note: bits shifted in later end up in LSB positions).
- load=1 and en=1 simultaneously → load wins, no shift.
- serial_out is combinational: reflects sr[7] in the same cycle (no extra latency).
- Reset mid-shift clears sr immediately.
