# Spec — pwm (Pulse Width Modulator)

**Status:** authoritative. Ground truth for Architect and Verifier.
Previous specs archived in `spec/`.

## Purpose

Synchronous PWM generator. An internal free-running phase counter is compared against
a programmable duty-cycle value to produce a single-bit output. Duty 0 → always low;
duty at full scale (2^WIDTH − 1) → one clock high per period (≈ 100% but one cycle low
per period when counter wraps, by the strict less-than comparison).

Practical use: DAC output stage downstream of the DSP mixer chain, or motor/LED control.

## Parameters

| Parameter | Default | Description |
|---|---:|---|
| `WIDTH` | 8 | Counter and duty-cycle resolution. Period = 2^WIDTH clocks. |

## Ports

| Port    | Direction | Width   | Description |
|---|---|---:|---|
| `clk`   | input  | 1       | Clock. |
| `rst`   | input  | 1       | Synchronous, active-high reset. Resets counter to 0 and output to 0. |
| `en`    | input  | 1       | Enable. Counter and output only advance when en=1. |
| `duty`  | input  | `WIDTH` | Unsigned duty-cycle threshold. Compared combinationally against the counter. |
| `pwm_out` | output | 1     | Registered PWM bit. |

## Behaviour

All state changes on `posedge clk`. Priority: **reset > enable > hold**.

1. If `rst == 1`: counter ← 0; `pwm_out` ← 0.
2. Else if `en == 1`:
   - counter ← counter + 1 (wraps naturally at 2^WIDTH).
   - `pwm_out` ← 1 if the **pre-increment** counter value is less than `duty`, else 0.
3. Else: counter and `pwm_out` hold their values.

**Pre-increment comparison:** the output registered in the same clock cycle as the
counter increment uses the counter value **before** the addition:
`pwm_out <= (counter < duty)` then `counter <= counter + 1`.
Both assignments are non-blocking and happen atomically at the posedge.

**Duty extremes (WIDTH=8):**
- `duty = 0`   → `pwm_out` is always 0 (counter is never < 0).
- `duty = 255` → `pwm_out` is 1 for 255 out of 256 cycles (high when counter is 0..254; low when counter = 255 since ~(255 < 255)).

## Synthesis constraints

- Single `always @(posedge clk)` block.
- Non-blocking `<=` for all assignments.
- No `initial`, no `#` delays, no inferred latches.
- Counter is an internal `reg [WIDTH-1:0]`.
- Yosys `check -assert` must report 0 problems.

## Verification tips (for Verifier)

For default WIDTH=8 (period = 256 clocks):

1. **Reset:** after rst=1 for one cycle, counter=0 and pwm_out=0.
2. **Hold:** en=0 holds both counter and pwm_out across multiple cycles.
3. **Duty=0:** pwm_out stays 0 for a full 256-cycle period.
4. **Duty=255:** pwm_out is 1 for 255 consecutive cycles, then 0 for 1 cycle.
5. **Duty=128 (50%):** exactly 128 highs and 128 lows per 256-cycle period.
6. **Period:** after 256 enabled clocks, counter returns to 0 (wraps).
7. **Arbitrary duty:** count high cycles over one full period and confirm count == duty.
