# Spec — `fifo`: Parameterizable Synchronous FIFO

**Status:** authoritative. Ground truth for Architect and Verifier.
Previous specs archived in `spec/`.

## 1. Overview

A synchronous, single-clock FIFO (First-In First-Out) buffer. Data written to the FIFO
via `wr_en` is stored and read back in the same order via `rd_en`. Status flags `full`
and `empty` indicate when writes or reads should be withheld. Used between DSP pipeline
stages to decouple throughput.

Single clock domain. All controls synchronous and active-high.

## 2. Parameters

| Name    | Default | Meaning                                               |
|---------|---------|-------------------------------------------------------|
| `WIDTH` | `8`     | Bit width of each data word.                          |
| `DEPTH` | `16`    | Number of storage locations. Must be a power of 2 ≥ 2.|

The FIFO holds up to `DEPTH` words. Address wraps modulo `DEPTH` (pointer width =
`$clog2(DEPTH)` bits).

## 3. Ports

| Name    | Dir | Width   | Description                                              |
|---------|-----|---------|----------------------------------------------------------|
| `clk`   | in  | 1       | Clock. All state changes on rising edge.                 |
| `rst`   | in  | 1       | Synchronous, active-high reset. Clears pointers and flags.|
| `wr_en` | in  | 1       | Write enable. Writes `din` to FIFO when high and not `full`.|
| `rd_en` | in  | 1       | Read enable. Advances read pointer when high and not `empty`.|
| `din`   | in  | `WIDTH` | Data input word.                                         |
| `dout`  | out | `WIDTH` | Data output word (registered; reflects current read pointer).|
| `full`  | out | 1       | Asserted when FIFO holds `DEPTH` words. Registered.      |
| `full`  | out | 1       | Asserted when FIFO holds `DEPTH` words.                  |
| `empty` | out | 1       | Asserted when FIFO holds 0 words.                        |

## 4. Behavior (per rising edge of `clk`)

**Reset:**
- If `rst == 1`: write pointer `wr_ptr ← 0`, read pointer `rd_ptr ← 0`, `count ← 0`.
  `full ← 0`, `empty ← 1`. Memory contents are don't-care after reset (don't need
  explicit clear).

**Simultaneous read and write (count unchanged):**
- If `wr_en && !full && rd_en && !empty` in the same cycle: write `din` at `wr_ptr`,
  advance `wr_ptr`; read from `rd_ptr`, advance `rd_ptr`; `count` unchanged.

**Write only:**
- If `wr_en && !full && !(rd_en && !empty)`: write `din` at `wr_ptr`, `wr_ptr ← wr_ptr + 1`, `count ← count + 1`.

**Read only:**
- If `rd_en && !empty && !(wr_en && !full)`: `rd_ptr ← rd_ptr + 1`, `count ← count - 1`.

**Hold:** no valid wr_en or rd_en — all registers hold.

**Ignored operations:**
- `wr_en` when `full` → ignored (no write, no pointer change).
- `rd_en` when `empty` → ignored (no read, no pointer change).

## 5. Output `dout`

`dout` is the word at the current `rd_ptr` in the storage array, registered or read
directly from the array. The Architect may implement as:
- **registered read:** `dout` is a `reg` updated on the clock edge when `rd_en && !empty`, OR
- **transparent read:** `dout` is a `wire` driven by `mem[rd_ptr]` combinationally.

Either is acceptable; the Verifier's test must handle both. **Specify which you chose
in `bus/to_verifier.md`.**

## 6. `full` and `empty` flags

Both are registered (driven from flip-flops, not pure combinational).

- `empty` is high after reset and whenever `count == 0`.
- `full` is high whenever `count == DEPTH`.
- Updates take effect on the clock edge following the triggering read/write.

## 7. Reset semantics

Synchronous, active-high. `rst` must not appear in a sensitivity list.

## 8. Synthesis constraints (CLAUDE.md §3)

- Storage array as `reg [WIDTH-1:0] mem [0:DEPTH-1]`.
- All pointer/flag updates in a **single** `always @(posedge clk)` block.
- Non-blocking `<=` in sequential block. No `initial`, no `#` delays.
- No inferred latches; every combinational path has a default.
- Must pass Yosys `check -assert` with 0 problems.
- DEPTH must be a power of 2 so pointer wrap is automatic (no comparator needed).
