# To Verifier

v1 of `rtl/pipe_delay.v` ready, spec in `spec/spec.md` (pipeline delay line). Ready for simulation.

- Module: `pipe_delay` (params `WIDTH=8`, `DEPTH=4`)
- Top-level: `pipe_delay`
- Ports: `clk`, `rst` (sync active-high), `en`, `d_in[7:0]`, `d_out[7:0]` (wire tap of pipe[3])
- Latency: d_out reflects d_in from exactly DEPTH=4 *enabled* clock cycles ago.
- All stages freeze together when en=0 — disabled cycles do not consume pipeline positions.
- Implemented with generate loop; stage[0] takes d_in, each subsequent stage takes the previous.
- d_out is an assign wire (combinational), not a separate register.
- Yosys `check -assert`: 0 problems.
- Iteration: 1

Verification tips:
- Single pulse: d_in=0xAB for 1 cycle then 0x00; d_out shows 0xAB at cycle 4 (DEPTH en-cycles later).
- Sequence trace: d_in=1,2,3,4,5,0,0,0,0 → d_out=0,0,0,0,1,2,3,4,5 (DEPTH-cycle delay).
- En gating: insert en=0 cycles; d_out pauses and resumes (delay is in enabled cycles).
- DEPTH=1: verify d_out is d_in from 1 cycle ago.
- Randomized: Python deque(maxlen=4), push d_in on en=1, verify d_out matches popleft.
