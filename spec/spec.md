# Spec — strobe_gen (Programmable Strobe Generator)

**Status:** authoritative. Ground truth for Architect and Verifier.
Previous specs archived in `spec/`.

## Purpose

Programmable rate divider that produces a single-clock-wide enable pulse (`strobe`)
every `divisor` clock cycles. Used to connect DSP stages running at different sample
rates — for example, driving a FIR filter at 1/8 the system clock by routing
`strobe` to the FIR's `en` input.

## Parameters

| Parameter | Default | Description |
|---|---:|---|
| `WIDTH` | 8 | Counter width. Maximum divisor = 2^WIDTH. |

## Ports

| Port      | Direction | Width   | Description |
|---|---|---:|---|
| `clk`     | input  | 1       | Clock. |
| `rst`     | input  | 1       | Synchronous, active-high reset. Resets counter to 0 and strobe to 0. |
| `en`      | input  | 1       | Module enable. Counter only advances and strobe only fires when high. |
| `divisor` | input  | `WIDTH` | Number of enabled clock cycles between strobes. Range: 1..2^WIDTH. See note. |
| `strobe`  | output | 1       | Registered 1-cycle-wide pulse. High for exactly one `en` cycle per `divisor` cycles. |

**Divisor note:** `divisor = 0` is treated as `2^WIDTH` (maximum period, free-running).
This falls out naturally from the counter comparison and requires no special casing.

## Behaviour

All state changes on `posedge clk`. Priority: **reset > enable > hold**.

Internal state: `counter`, a WIDTH-bit register counting `0 .. divisor−1`.

1. If `rst == 1`: `counter <= 0`, `strobe <= 0`.
2. Else if `en == 1`:
   - If `counter == divisor − 1` (counter reached the end of the period):
     - `counter <= 0`
     - `strobe <= 1`
   - Else:
     - `counter <= counter + 1`
     - `strobe <= 0`
3. Else: `counter` and `strobe` hold (strobe is not forced low on hold — it retains
   its last registered value; if `en` went low on the same cycle strobe fired, the
   strobe output holds `1` until `en` goes high again and the counter advances).

**Strobe timing:** strobe fires on the cycle the counter resets, i.e. the first `en`
cycle of each new period. Counter goes to 0 and strobe = 1 on the same edge.

## Synthesis constraints

- Single `always @(posedge clk)` block, non-blocking `<=`.
- Counter comparison `counter == divisor - 1` is combinational; both are registered in the same cycle.
- No `initial`, no `#` delays, no inferred latches.
- Yosys `check -assert` must report 0 problems.

## Verification tips (for Verifier)

For WIDTH=8:

1. **Reset:** counter=0, strobe=0 after rst=1.
2. **Hold:** en=0 freezes counter and strobe.
3. **divisor=1:** strobe fires every enabled cycle (100% duty counter).
4. **divisor=4:** strobe fires on cycles 0, 4, 8, … (every 4th enabled clock).
5. **divisor=256 (=0 per note):** strobe fires every 256 enabled clocks.
6. **Period verification:** for divisor=N, count enabled cycles between successive
   rising edges of strobe; assert spacing is exactly N.
7. **strobe width:** strobe is high for exactly 1 enabled cycle per period.
8. **Divisor change mid-run:** changing divisor while running produces at most one
   truncated or extended period; subsequent periods are correct.
