# To Verifier

v1 of `rtl/moving_avg.v` ready, spec in `spec/spec.md` (sliding-window moving average). Ready for simulation.

- Module: `moving_avg` — **this is module 25, the final module in the v1.0 library.**
- Top-level: `moving_avg`
- Ports: `clk`, `rst` (sync active-high), `en`, `x_in[DATA_W-1:0]` unsigned, `avg_out[DATA_W-1:0]` unsigned, `avg_valid`
- Default params: DATA_W=8, LOG2N=3 (N=8 window).
- Running sum maintained in ACC_W=11-bit accumulator (no overflow for DATA_W=8, N=8).
- avg_out = acc >> LOG2N (bit-slice [10:3], i.e., the upper 8 bits).
- Shift register: sr[0]=newest, sr[N-1]=oldest. Stage-zero-split pattern (generate g=1..N-1).
- avg_valid strobes high on each en=1 cycle.
- Fill-in: first N samples after reset are padded with zeros (avg diluted until window full).
- Yosys `check -assert`: 0 problems.
- Iteration: 1

Key test vectors (DATA_W=8, LOG2N=3, N=8):
1. Reset → avg_out=0, avg_valid=0.
2. en=0 → avg_out unchanged, avg_valid=0.
3. 8 × x_in=8: avg_out=8 after the 8th en-cycle.
4. Push x_in=16 after full window of 8s: avg_out=9 (acc=72, 72>>3=9).
5. All 255s: avg_out=255 (acc=2040, no overflow in 11 bits).
6. Constant-to-step: window of 0s, then 8 × 255 pushed in one at a time.
   avg_out steps: 31, 63, 95, 127, 159, 191, 223, 255 (each += 31 = 255>>3).

Python reference:
```python
from collections import deque
import math

def moving_avg_ref(samples, log2n, data_w=8):
    n = 1 << log2n
    window = deque([0]*n, maxlen=n)
    acc = 0
    avgs = []
    for s in samples:
        acc = acc + s - window[0]   # window[0] is oldest (left side of deque)
        window.append(s)            # appending pushes oldest out of window[0]
        avgs.append(acc >> log2n)
    return avgs
```

Parametrize: also test LOG2N=2 (N=4), DATA_W=8 — verify 4-sample window.

Cocotb note: all port names safe (no Python keywords). Drive x_in as non-negative int.
