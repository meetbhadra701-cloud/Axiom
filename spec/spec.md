# Spec — pipe_delay (Pipeline Delay Line)

**Status:** authoritative. Ground truth for Architect and Verifier.
Previous specs archived in `spec/`.

## Purpose

Parameterized synchronous pipeline delay. Passes `d_in` through a chain of `DEPTH`
registered stages so `d_out` appears exactly `DEPTH` clock cycles later. Used to
align latencies when composing DSP blocks with different pipeline depths — for example,
matching a side-channel signal to the 2-cycle `edge_det` output, or providing a
reference tap N cycles behind a filter output.

`DEPTH=1` is a simple registered pipeline stage (D flip-flop array).

## Parameters

| Parameter | Default | Description |
|---|---:|---|
| `WIDTH`   | 8  | Data width. |
| `DEPTH`   | 4  | Number of pipeline stages. Each stage adds one clock cycle of latency. Range: 1..16. |

## Ports

| Port    | Direction | Width   | Description |
|---|---|---:|---|
| `clk`   | input  | 1       | Clock. |
| `rst`   | input  | 1       | Synchronous, active-high reset. Clears all pipeline registers to 0. |
| `en`    | input  | 1       | Pipeline enable. All stages advance when high; hold when low. |
| `d_in`  | input  | `WIDTH` | Data entering the pipeline. |
| `d_out` | output | `WIDTH` | Data exiting after `DEPTH` clock cycles. Registered. |

## Behaviour

All state changes on `posedge clk`. Priority: **reset > enable > hold**.

Internal: `pipe[0:DEPTH-1]`, an array of DEPTH registers each WIDTH bits wide.

1. If `rst == 1`: all `pipe[i] <= 0`.
2. Else if `en == 1`:
   - `pipe[0] <= d_in`
   - `pipe[i] <= pipe[i-1]` for i = 1..DEPTH-1
3. Else: all stages hold.

`d_out` is the last stage: `assign d_out = pipe[DEPTH-1]`.

**Latency:** `d_out` reflects the value of `d_in` from `DEPTH` enabled clock cycles ago.
Disabled cycles (en=0) do not consume pipeline positions — the delay is measured in
*enabled* clock cycles, not wall-clock cycles.

## Synthesis notes

- Implemented with a `generate` loop creating DEPTH `always @(posedge clk)` blocks,
  each holding one WIDTH-bit register.
- `d_out` is a combinational tap of `pipe[DEPTH-1]` (an `assign`), not a separate register.
- No `initial`, no `#` delays, no inferred latches.
- Yosys `check -assert` must report 0 problems.

## Verification tips (for Verifier)

For WIDTH=8, DEPTH=4:

1. **Reset:** all pipe stages and d_out = 0 after rst=1.
2. **Hold:** en=0 freezes all stages; d_out unchanged.
3. **Single pulse:** drive d_in=0xAB for 1 cycle then 0x00; d_out shows 0xAB exactly 4 enabled cycles later for exactly 1 cycle.
4. **Sequence:** drive d_in = 1, 2, 3, 4, 5, 0, 0, 0, 0, 0 continuously (en=1);
   d_out should be 0, 0, 0, 0, 1, 2, 3, 4, 5, 0 (shifted by DEPTH=4 cycles).
5. **Enable gating:** insert en=0 cycles mid-sequence; d_out should pause and then
   continue — the delay is in *enabled* cycles.
6. **DEPTH=1:** d_out reflects d_in from 1 cycle ago (simple register).
7. **Randomized:** random d_in with random en/rst; maintain a Python deque of depth 4;
   push d_in when en=1, verify d_out matches deque front.
