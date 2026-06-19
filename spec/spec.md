# Spec — moving_avg (Sliding-Window Moving Average)

**Status:** authoritative. Ground truth for Architect and Verifier.

## Purpose

Power-of-2 sliding-window moving average. Maintains a shift register of the last N
samples and a running sum, producing avg = sum / N each enabled cycle. Division by N
is an exact right-shift (N must be a power of two). Registers avg_out with a valid strobe.

## Parameters

| Parameter | Default | Description |
|---|---:|---|
| `DATA_W` | 8  | Bit width of input/output samples (unsigned). |
| `LOG2N`  | 3  | log₂ of the window length. Window N = 2^LOG2N = 8. |

`localparam N = 1 << LOG2N;`
`localparam ACC_W = DATA_W + LOG2N;` — accumulator is just wide enough to hold N×max_sample.

## Ports

| Port       | Dir   | Width  | Description |
|---|---|---:|---|
| `clk`      | input | 1      | Clock. |
| `rst`      | input | 1      | Synchronous, active-high reset. Clears all state to 0. |
| `en`       | input | 1      | Sample enable. Loads x_in and updates avg_out on each posedge when high. |
| `x_in`     | input | DATA_W | Input sample (unsigned). |
| `avg_out`  | output | DATA_W | Registered average output (truncated, unsigned). |
| `avg_valid` | output | 1     | Strobes high for 1 cycle when avg_out is fresh (mirrors en). |

## Behaviour

All state changes on `posedge clk`. Priority: **reset > enable > hold**.

**On each en=1 cycle:**

1. Read `evicted = sr[N-1]` (oldest sample, wire — combinational).
2. Compute `acc_next = acc + x_in − evicted` (ACC_W-bit unsigned arithmetic).
3. Register: `acc <= acc_next`, `avg_out <= acc_next[ACC_W-1:LOG2N]`, `avg_valid <= 1`.
4. Shift register: `sr[0] <= x_in`; `sr[g] <= sr[g-1]` for g = 1..N-1 (stage 0 explicit,
   stages 1..N-1 via generate loop — follows stage-zero-split convention).

**On en=0:** `avg_valid <= 0`; all other state holds.

**On rst:** all `sr` registers, `acc`, `avg_out`, `avg_valid` cleared to 0.

**Fill-in behaviour:** for the first N samples after reset, the window is padded with zeros.
Average is the sum of loaded samples divided by N (not by the number of samples loaded),
so results are diluted until the window is full. This is expected behaviour; no
separate valid-after-N-samples signal is provided.

## Synthesis notes

- `evicted` is a `wire [DATA_W-1:0]` reading `sr[N-1]` combinationally.
- `acc_next` is a `wire [ACC_W-1:0]` with the add/subtract.
- Stage 0 of shift register is an explicit `always @(posedge clk)` block (not in the
  generate loop) to keep `sr[g-1]` valid at g=1 without a `sr[-1]` reference.
- Generate loop covers g=1..N-1.
- Three separate always blocks: shift-reg stage 0, shift-reg stages 1..N-1 (generate),
  accumulator+output. All use the same `rst > en > hold` priority.
- No `initial`, no `#` delays, no inferred latches.
- Yosys `check -assert` must report 0 problems.

## Known test vectors (DATA_W=8, LOG2N=3, N=8)

- **After reset:** avg_out=0.
- **8 × x_in=8 (fill window):** acc=64, avg_out=8.
- **Push x_in=16 after full window of 8s:** acc = 64+16-8 = 72, avg_out=9.
- **All zeros:** avg_out stays 0.
- **All 255s (max input):** acc = 8×255 = 2040 < 2^11 ✓; avg_out = 2040>>3 = 255.

## Verification tips (for Verifier)

1. **Reset:** avg_out=0, avg_valid=0.
2. **Hold:** en=0 → avg_out, avg_valid, acc, sr all unchanged.
3. **avg_valid strobe:** high exactly on en=1 cycles, low otherwise.
4. **Constant input:** load N copies of value V → avg_out = V.
5. **Sliding transition:** window full of 0 → start loading 255 one at a time. Verify
   avg_out steps up by 255/N = 31 (truncated) per en cycle.
6. **Overflow check:** max input 255 × N=8 = 2040, fits in ACC_W=11 bits.
7. **Window length:** LOG2N=2 (N=4) parametrize; verify avg over 4-sample window.
8. **Randomized:** 200 samples; compare to a Python reference:
   ```python
   from collections import deque
   def moving_avg_ref(samples, n, data_w=8):
       window = deque([0]*n, maxlen=n)
       acc = 0
       avgs = []
       for s in samples:
           acc = acc + s - window[0]  # window[0] is oldest
           window.append(s)
           avgs.append(acc >> int(math.log2(n)))
       return avgs
   ```
