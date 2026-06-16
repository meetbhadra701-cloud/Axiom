# To Verifier

v1 of `rtl/fifo.v` ready, spec in `spec/spec.md` (synchronous FIFO, power-of-2 depth,
transparent read output). Ready for simulation.

- Module: `fifo` (params `WIDTH=8`, `DEPTH=16`)
- Top-level: `fifo`
- Ports: `clk`, `rst` (sync active-high), `wr_en`, `rd_en`, `din[WIDTH-1:0]`,
  `dout[WIDTH-1:0]` (transparent/combinational), `full` (registered), `empty` (registered)
- Read style: **transparent** — `dout` is a combinational wire from `mem[rd_ptr]`.
  Valid data appears on `dout` in the same cycle `rd_ptr` points to it, with no
  extra read-latency cycle. `rd_en` advances the pointer on the next clock edge.
- Yosys `check -assert`: 0 problems (memory "no output FF" note is expected for
  transparent read — not a latch)
- Iteration: 1
