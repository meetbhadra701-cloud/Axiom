# To Verifier

v1 of `rtl/counter.v` ready, written to `spec/spec.md` (8-bit synchronous up-counter,
enable, synchronous active-high reset, modulo wrap). Synthesizes clean under Yosys
`check -assert` (zero latches/loops/multi-driven nets). Ready for simulation.

- Module: `counter`  (param `WIDTH`, default 8)
- Top-level: `counter`
- Ports: `clk`, `rst` (sync, active-high), `en`, `count[WIDTH-1:0]` (registered)
- Iteration: 1
