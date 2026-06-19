# To Verifier

v1 of `rtl/uart_tx.v` ready, spec in `spec/spec.md` (8-N-1 UART transmitter). Ready for simulation.

- Module: `uart_tx`
- Top-level: `uart_tx`
- Ports: `clk`, `rst` (sync active-high), `en`, `data[7:0]`, `tx` (reg), `busy` (reg)
- Default params: CLKS_PER_BIT=868, CLKDIV_W=10. Use CLKS_PER_BIT=4, CLKDIV_W=2 for sim.
- Format: 8-N-1. Start=0, 8 data bits LSB-first, Stop=1.
- Busy: high from en-load until 10*CLKS_PER_BIT cycles later (IDLE re-entered).
- en ignored when busy=1 (no overrun).
- Yosys `check -assert`: 0 problems. ~86 cells.
- Iteration: 1

Timing (CLKS_PER_BIT = N):
```
Cycle 0:     en=1 fired  → tx=0, busy=1, state=START
Cycles 0..N-1:  START state, tx=0 (baud_cnt 0..N-1)
Cycle N:        → DATA, bit_idx=0, tx=data[0] (baud_cnt reset to 0)
Cycles N..2N-1: DATA bit 0 (baud_cnt 0..N-1)
...
Cycles 9N..10N-1: STOP state, tx=1
Cycle 10N:        → IDLE, busy=0
```

Key test vectors (CLKS_PER_BIT=4):
1. Reset → tx=1, busy=0.
2. Transmit 0x55 (01010101b): TX sequence = 0, 1,0,1,0,1,0,1,0, 1 (start, 8 data, stop).
3. Transmit 0xAA (10101010b): TX = 0, 0,1,0,1,0,1,0,1, 1.
4. Transmit 0x00: TX = 0, 0,0,0,0,0,0,0,0, 1.
5. Transmit 0xFF: TX = 0, 1,1,1,1,1,1,1,1, 1.
6. busy spans exactly 10*CLKS_PER_BIT=40 cycles.
7. en during busy: data not overwritten, no corruption.
8. Back-to-back: en=1 on cycle 40 → second transmission begins immediately.
9. Randomized: 20 random bytes, deserialise tx stream, compare.

Python tx-stream deserialiser (see spec for full version):
```python
def uart_rx_sample(tx_trace, clks_per_bit):
    i = 0; rx_bytes = []
    while i < len(tx_trace):
        if tx_trace[i] == 0:          # start bit detected
            i += clks_per_bit // 2   # advance to mid-start
            bits = []
            for _ in range(8):
                i += clks_per_bit
                bits.append(tx_trace[i] if i < len(tx_trace) else 1)
            rx_bytes.append(sum(b << k for k, b in enumerate(bits)))
            i += clks_per_bit         # skip stop bit
        else:
            i += 1
    return rx_bytes
```

Cocotb note: use `COCOTB_PARAM_CLKS_PER_BIT=4` and `COCOTB_PARAM_CLKDIV_W=2`
(or equivalent plusargs) to reduce sim time. All port names are safe (no Python keywords).
