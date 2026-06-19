# Spec — one_hot (Binary-to-One-Hot Decoder)

**Status:** authoritative. Ground truth for Architect and Verifier.

## Purpose

Registered binary-to-one-hot decoder. Converts a LOG2W-bit binary index to an N-bit
one-hot output with exactly one bit set. Used for bus demuxing, state decode, and
priority output stages.

## Parameters

| Parameter | Default | Description |
|---|---:|---|
| `N`     | 8 | Output width (number of one-hot bits). Must be ≥ 2. |
| `LOG2W` | 3 | Bit width of the binary input. Must equal ceil(log2(N)). |

The two parameters are kept separate (no `$clog2`) for port-declaration portability,
matching the library convention established in `prio_enc` and `rr_arb`.

## Ports

| Port  | Direction | Width    | Description |
|---|---|---:|---|
| `clk` | input  | 1        | Clock. |
| `rst` | input  | 1        | Synchronous, active-high reset. Clears `out` to all-zeros. |
| `en`  | input  | 1        | Load enable. `out` updates on the next rising edge when high. |
| `in`  | input  | LOG2W    | Binary index. |
| `out` | output | N        | One-hot encoded output (registered). |

## Behaviour

All state changes on `posedge clk`. Priority: **reset > enable > hold**.

On each rising clock edge:
- If `rst`: `out ← 0` (all bits clear).
- Else if `en`: `out ← 1 << in` (bit `in` set, all others clear).
- Else: hold `out` unchanged.

The combinational decode is `wire [N-1:0] decoded = {{(N-1){1'b0}}, 1'b1} << in`.
This gives exactly N bits with a single 1 at position `in`.

**Examples (N=8):**

| `in` (binary) | `out` (one-hot, bit 7..0) |
|---|---|
| 3'b000 | 8'b00000001 |
| 3'b001 | 8'b00000010 |
| 3'b011 | 8'b00001000 |
| 3'b111 | 8'b10000000 |

## Synthesis notes

- `decoded` is a combinational `wire [N-1:0]`; no latch inferred.
- Single `always @(posedge clk)` block for the output register.
- No `initial`, no `#` delays.
- Yosys `check -assert` must report 0 problems.
- Expected cells: N DFFs (or SDFFEs), roughly 1 LUT per output bit from the shift.

## Verification tips (for Verifier)

1. **Reset:** out=0 after rst=1 regardless of in/en.
2. **Hold:** en=0 leaves out unchanged.
3. **All indices (N=8):** in=0..7, verify out = 1<<in after one en-cycle.
4. **Hot bit exclusive:** popcount(out)==1 for every valid in when en=1.
5. **Reset clears:** drive en=1 with in=5 (out=0x20), then rst=1, verify out=0x00.
6. **Large N:** test with N=16, LOG2W=4 — all 16 indices.
7. **Randomized:** random in values, compare out against (1 << in) in Python.
