# Spec — edge_det (Edge Detector)

**Status:** authoritative. Ground truth for Architect and Verifier.
Previous specs archived in `spec/`.

## Purpose

Two-stage synchronous edge detector. Samples `sig_in` into a two-flip-flop pipeline
and produces registered single-cycle pulses on rising edges, falling edges, or either.
Common uses: detecting button presses, ADC-ready strobes, protocol framing signals,
or any 1-bit transition that needs a single-cycle downstream trigger.

Note: this module does **not** synchronise asynchronous inputs across clock domains
(for that, use a dedicated 2-FF CDC synchroniser). `sig_in` is assumed to be
synchronous to `clk`.

## Parameters

None. The module is purely single-bit.

## Ports

| Port       | Direction | Width | Description |
|---|---|---:|---|
| `clk`      | input  | 1 | Clock. |
| `rst`      | input  | 1 | Synchronous, active-high reset. Clears pipeline and all outputs. |
| `sig_in`   | input  | 1 | Input signal to observe. |
| `rise`     | output | 1 | Registered 1-cycle pulse on 0→1 transition. |
| `fall`     | output | 1 | Registered 1-cycle pulse on 1→0 transition. |
| `any_edge` | output | 1 | Registered 1-cycle pulse on either transition (`rise | fall`). |

No `en` port — detection runs continuously; `rst` is the only control.

## Behaviour

All state changes on `posedge clk`.

Internal pipeline: `pipe[1:0]`, where `pipe[0]` is the most recent sample of
`sig_in` and `pipe[1]` is one cycle older. On each rising edge:

1. If `rst == 1`:
   - `pipe <= 2'b00`
   - `rise <= 0`, `fall <= 0`, `any_edge <= 0`
2. Else:
   - `pipe[0] <= sig_in`
   - `pipe[1] <= pipe[0]`
   - `rise     <= pipe[0] & ~pipe[1]`   — 0→1 detected in the previous pair
   - `fall     <= ~pipe[0] & pipe[1]`   — 1→0 detected in the previous pair
   - `any_edge <= pipe[0] ^ pipe[1]`    — either transition

**Latency:** `rise`/`fall`/`any_edge` are valid 2 clock cycles after the input transition.
- Cycle 0: transition occurs on `sig_in`.
- Cycle 1: `pipe[0]` captures the new value.
- Cycle 2: `pipe[1]` has the old value, `pipe[0]` has the new; outputs fire.

## Synthesis constraints

- Single `always @(posedge clk)` block; five non-blocking assignments.
- No combinational outputs — all three edge flags are registered.
- No `initial`, no `#` delays, no inferred latches.
- Yosys `check -assert` must report 0 problems.

## Verification tips (for Verifier)

1. **Reset:** pipe=00, rise=fall=any_edge=0 after rst=1.
2. **Rising edge:** drive sig_in=0 for 3 cycles, then sig_in=1; on the 2nd cycle
   after the transition, `rise=1` for exactly 1 cycle; `fall=0`, `any_edge=1`.
3. **Falling edge:** sig_in=1 then sig_in=0; `fall=1` for 1 cycle; `rise=0`, `any_edge=1`.
4. **Sustained high:** sig_in stays 1 for many cycles; all outputs stay 0 after the
   initial rise pulse.
5. **Sustained low:** all outputs stay 0.
6. **Glitch (1-cycle pulse):** sig_in goes 0→1→0 in successive cycles; rise fires on
   the cycle pipe[0]=1,pipe[1]=0; fall fires the next cycle; any_edge fires for both.
7. **Reset clears in-flight:** assert rst during a pending transition; outputs clear.
8. **any_edge == rise | fall** at all times.
