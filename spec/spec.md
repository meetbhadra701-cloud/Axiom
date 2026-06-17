# Spec — rr_arb (Round-Robin Arbiter)

**Status:** authoritative. Ground truth for Architect and Verifier.
Previous specs archived in `spec/`.

## Purpose

Synchronous round-robin arbiter. Each cycle, one requesting port is granted access.
After a grant, the priority pointer rotates to the next port so every requestor
eventually gets served — no starvation. Outputs a one-hot `grant` vector and a binary
`grant_idx` indicating the winning port.

## Parameters

| Parameter | Default | Description |
|---|---:|---|
| `PORTS`  | 4 | Number of requestors. |
| `LOG2P`  | 2 | Index width. Must satisfy `2^LOG2P == PORTS`. |

## Ports

| Port        | Direction | Width    | Description |
|---|---|---:|---|
| `clk`       | input  | 1        | Clock. |
| `rst`       | input  | 1        | Synchronous, active-high reset. Clears grant, grant_idx, and priority pointer to 0. |
| `req`       | input  | `PORTS`  | Request bits. Any combination may be asserted simultaneously. |
| `grant`     | output | `PORTS`  | Registered one-hot grant vector. Bit i = 1 means port i is granted this cycle. |
| `grant_idx` | output | `LOG2P`  | Registered binary index of the granted port. Valid when any grant bit is set. |

No `en` port — the arbiter runs every clock cycle.

## Behaviour

All state changes on `posedge clk`.

Internal state: `ptr[LOG2P-1:0]` — the **start-of-scan** pointer, initialised to 0
after reset. Points to the next port to receive priority.

**Each cycle (combinational arbitration, then registered update):**

1. **Pass 1 — scan from `ptr` to `PORTS−1`:** find the lowest-indexed set bit in `req`
   at position ≥ `ptr`. If found, that port is the winner.
2. **Pass 2 — wrap — scan from `0` to `PORTS−1`:** only reached if Pass 1 found nothing.
   Find the lowest-indexed set bit in `req` (which must be at position < `ptr`, since
   Pass 1 already checked ≥ `ptr`). If found, that port wins.
3. **No requests:** `grant` ← 0; `grant_idx` and `ptr` unchanged.

**After a grant:**
- `grant`     ← one-hot: bit `winner` = 1, all others 0.
- `grant_idx` ← `winner`.
- `ptr`       ← (`winner` + 1) mod `PORTS` — priority rotates past the winner.

**Reset:** `grant` ← 0, `grant_idx` ← 0, `ptr` ← 0.

## Fairness guarantee

For PORTS=4 with all four lines continuously asserted, the grant sequence is
0, 1, 2, 3, 0, 1, 2, 3, … (starting from ptr=0 after reset).

## Synthesis notes

- Two `always` blocks: `always @(*)` for combinational winner selection (defaults before
  loops prevent latches); `always @(posedge clk)` for registered outputs and ptr update.
- One-hot encoding: `grant <= ({{PORTS-1{1'b0}}, 1'b1}) << next_enc`.
- Ptr wraps: `ptr <= (next_enc == PORTS-1) ? 0 : next_enc + 1`.
- No `initial`, no `#` delays, no inferred latches.
- Yosys `check -assert` must report 0 problems.

## Verification tips (for Verifier)

For PORTS=4, LOG2P=2:

1. **Reset:** grant=0, grant_idx=0, ptr=0 after rst=1.
2. **Single request:** req=4'b0001 continuously → grant always 4'b0001 (only one requester).
3. **All four asserted:** req=4'b1111 for 8 cycles → grant sequence 4'b0001, 4'b0010,
   4'b0100, 4'b1000, 4'b0001, … (repeating 0→1→2→3→0…).
4. **Wrap-around:** assert req=4'b1001 (ports 0 and 3). After granting port 3, ptr=0,
   so next grant is port 0. After granting port 0, ptr=1; no req at 1,2,3 so wrap
   back to port 3.
5. **No starvation:** with all ports asserted, each gets exactly 1 grant per 4 cycles.
6. **ptr continuity:** after granting port N, ptr advances to (N+1)%PORTS next cycle.
7. **Idle cycles:** when req=0, grant=0 and ptr holds.
8. **Randomized:** random req patterns; track which ports were requested and granted over
   many cycles; verify no port is skipped more than PORTS−1 cycles when continuously
   asserting its req.
