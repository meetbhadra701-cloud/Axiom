# Spec — prio_enc (Priority Encoder)

**Status:** authoritative. Ground truth for Architect and Verifier.
Previous specs archived in `spec/`.

## Purpose

Registered priority encoder. Scans a WIDTH-bit request vector and reports the index
of the **highest-priority (highest-index) set bit** plus a `valid` flag. If multiple
bits are set, the one at the highest index wins. If no bits are set, `valid = 0` and
`out` is 0.

Typical use: interrupt controller (`in` = pending interrupt flags, `out` = IRQ number
to service), bus arbiter pre-stage, or any module that needs to find the MSB.

## Parameters

| Parameter  | Default | Description |
|---|---:|---|
| `WIDTH`    | 8 | Number of input request bits. Must be a power of two ≥ 2. |
| `LOG2W`    | 3 | Output index width. Must satisfy `2^LOG2W == WIDTH`. For WIDTH=8 set LOG2W=3. |

Two separate parameters (rather than `$clog2`) keep the port declaration readable in
Verilog-2001 and avoid tool portability issues.

## Ports

| Port    | Direction | Width    | Description |
|---|---|---:|---|
| `clk`   | input  | 1        | Clock. |
| `rst`   | input  | 1        | Synchronous, active-high reset. |
| `en`    | input  | 1        | Sample enable. |
| `in`    | input  | `WIDTH`  | Request bits. Bit `WIDTH-1` has highest priority. |
| `out`   | output | `LOG2W`  | Registered index of the highest-priority set bit. |
| `valid` | output | 1        | Registered flag: 1 when any bit of `in` is set. |

## Behaviour

All state changes on `posedge clk`. Priority: **reset > enable > hold**.

1. If `rst == 1`: `out <= 0`, `valid <= 0`.
2. Else if `en == 1`: evaluate the combinational priority logic, then register:
   - `valid <= (in != 0)`
   - `out <= index of highest set bit in in` (or 0 if none set — guarded by `valid`).
3. Else: hold.

**Combinational priority logic (for loop):** scan from index 0 to WIDTH−1;
each found set bit overwrites `enc_out`. At the end of the loop, `enc_out` holds
the highest-index set bit. Default `enc_out = 0`, `enc_valid = 0` before the loop
prevents inferred latches.

## Synthesis notes

- Two `always` blocks: one `always @(*)` for combinational encoding (default assignments
  before the loop prevent latches), one `always @(posedge clk)` for the registered output.
- The combinational block drives `enc_out` and `enc_valid` wires; the sequential block
  registers them into `out` and `valid`.
- One driver per signal.
- No `initial`, no `#` delays.
- Yosys `check -assert` must report 0 problems.

## Verification tips (for Verifier)

For WIDTH=8, LOG2W=3:

1. **Reset:** out=0, valid=0 after rst=1.
2. **Hold:** en=0 preserves out and valid.
3. **Single bit:** `in=8'b00000001` → out=0, valid=1.
4. **Single bit:** `in=8'b10000000` → out=7, valid=1.
5. **Highest wins:** `in=8'b10100100` → out=7 (bit 7 set).
6. **Middle bit:** `in=8'b00001000` → out=3, valid=1.
7. **All ones:** `in=8'hFF` → out=7, valid=1.
8. **Zero:** `in=8'h00` → out=0, valid=0.
9. **Exhaustive:** for all 256 values of `in`, compare out to Python's `in.bit_length()-1`
   (which gives the MSB position); valid = (in != 0).
10. **Randomized:** random en/rst/in cycles against Python reference.
