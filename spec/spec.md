# Spec — `counter`: 8-bit Synchronous Up-Counter

**Status:** authoritative. This file is ground truth (CLAUDE.md §2). If anything here is
ambiguous, the Architect must ask the human in `bus/status.md` rather than guess.

## 1. Overview

A parameterizable synchronous binary up-counter. On each rising edge of the clock it
either resets to zero, increments by one, or holds its current value, depending on the
control inputs. Single clock domain, single reset. Fully synchronous — no asynchronous
controls.

## 2. Parameters

| Name    | Default | Meaning                              |
|---------|---------|--------------------------------------|
| `WIDTH` | `8`     | Bit width of the counter / `count`.  |

The counter is `WIDTH` bits wide; the maximum value is `2**WIDTH - 1` (255 for the
default `WIDTH=8`).

## 3. Ports

| Name    | Dir | Width        | Description                                              |
|---------|-----|--------------|---------------------------------------------------------|
| `clk`   | in  | 1            | Clock. All state changes occur on its **rising edge**.  |
| `rst`   | in  | 1            | **Synchronous, active-high** reset. Sampled on `posedge clk`. |
| `en`    | in  | 1            | Count enable (active-high).                             |
| `count` | out | `WIDTH`      | Registered counter value.                               |

`count` is a registered output (driven from a flip-flop), not combinational.

## 4. Behavior (per rising edge of `clk`)

Priority order is **reset, then enable, then hold**:

1. If `rst == 1`  → `count <= 0`.
2. else if `en == 1` → `count <= count + 1`.
3. else            → `count` holds its current value.

## 5. Reset semantics

- Reset is **synchronous** and **active-high**: it only takes effect on a rising clock
  edge, and clears `count` to `0`.
- There is **no** asynchronous reset. Do **not** put `rst` in the sensitivity list.

## 6. Overflow / wrap-around

When `count == 2**WIDTH - 1` and the counter increments (`en==1`, `rst==0`), it wraps to
`0` (natural modulo-`2**WIDTH` wrap). For `WIDTH=8`: `255 -> 0`. No saturation, no flag.

## 7. Reset / power-on note

The counter's value is only defined after at least one synchronous reset. The Verifier
is expected to assert `rst` for one or more cycles at the start of any test before
relying on `count`.

## 8. Synthesis constraints (CLAUDE.md §3)

- Sequential logic in a single `always @(posedge clk)` block, non-blocking assignment.
- No `initial`, no `#` delays, no inferred latches.
- One driver for `count`. Explicit bit widths.
- Must pass Yosys `check -assert` with zero latches, loops, or multi-driven nets.
