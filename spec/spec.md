# Spec — `nco`: Numerically Controlled Oscillator (Phase Accumulator)

**Status:** authoritative. Ground truth for Architect and Verifier.
Previous specs archived in `spec/`.

## 1. Overview

A synchronous Numerically Controlled Oscillator (NCO), also called a Direct Digital
Synthesizer (DDS) phase accumulator. On each enabled clock edge it adds a frequency
word `phase_inc` to a registered phase accumulator `phase_out`. The output frequency
relative to `clk` is `f_out = phase_inc / 2^PHASE_WIDTH * f_clk`.

The high bits of `phase_out` form a sawtooth waveform; they can index a sine LUT
(not part of this module) to produce a sine wave. This module is the core frequency-
synthesis primitive used in software-defined radio, tone generation, and modulation.

Single clock domain, synchronous reset.

## 2. Parameters

| Name          | Default | Meaning                                              |
|---------------|---------|------------------------------------------------------|
| `PHASE_WIDTH` | `24`    | Bit width of the phase accumulator and `phase_out`.  |

A 24-bit accumulator gives ~0.06 Hz frequency resolution at 1 MHz clock, and supports
output frequencies from 0 Hz (phase_inc=0) up to f_clk/2 (phase_inc = 2^23).

## 3. Ports

| Name         | Dir | Width         | Description                                              |
|--------------|-----|---------------|----------------------------------------------------------|
| `clk`        | in  | 1             | Clock. All state changes on rising edge.                 |
| `rst`        | in  | 1             | Synchronous, active-high reset. Clears `phase_out` to 0.|
| `en`         | in  | 1             | Accumulator enable (active-high).                        |
| `phase_inc`  | in  | `PHASE_WIDTH` | Unsigned frequency word. Added to accumulator each cycle.|
| `phase_out`  | out | `PHASE_WIDTH` | Registered unsigned phase accumulator value.             |

`phase_out` is a registered output (flip-flop), not combinational.

## 4. Behavior (per rising edge of `clk`)

Priority order: **reset > enable > hold.**

1. If `rst == 1`    → `phase_out <= 0`.
2. else if `en == 1`→ `phase_out <= phase_out + phase_inc`. Natural wrap modulo
   `2^PHASE_WIDTH` (the adder overflows back to 0).
3. else             → `phase_out` holds.

## 5. Arithmetic semantics

- `phase_inc` and `phase_out` are **unsigned** integers.
- Accumulation wraps naturally (no saturation, no overflow flag).
- `phase_inc = 0` → accumulator holds at 0 (or any initial value after rst) → DC.
- `phase_inc = 2^(PHASE_WIDTH-1)` → accumulator toggles between 0 and the mid-point
  every cycle → output at Nyquist (f_clk/2).

## 6. Reset semantics

Synchronous, active-high. `rst` must not appear in a sensitivity list.
Clears `phase_out` to 0.

## 7. Synthesis constraints (CLAUDE.md §3)

- Single `always @(posedge clk)` block, non-blocking `<=` only.
- No `initial`, no `#` delays, no inferred latches.
- One driver for `phase_out`. Explicit bit widths.
- Must pass Yosys `check -assert` with 0 problems.
