# Spec — uart_tx (UART Transmitter)

**Status:** authoritative. Ground truth for Architect and Verifier.

## Purpose

8-N-1 UART serial transmitter. Serialises one byte per transmission: 1 start bit (0),
8 data bits (LSB first), 1 stop bit (1). Baud rate set by the `CLKS_PER_BIT` parameter.
Busy flag prevents overrun; back-to-back transmissions begin on the cycle IDLE is re-entered.

## Parameters

| Parameter    | Default | Description |
|---|---:|---|
| `CLKS_PER_BIT` | 868 | Clock cycles per UART bit period (868 → 115200 baud at 100 MHz). |
| `CLKDIV_W`     |  10 | Bit width of baud counter: must satisfy 2^CLKDIV_W > CLKS_PER_BIT. Explicit per library convention (no `$clog2`). |

For simulation use small values, e.g. CLKS_PER_BIT=4, CLKDIV_W=2.

## Ports

| Port   | Direction | Width | Description |
|---|---|---:|---|
| `clk`  | input  | 1 | Clock. |
| `rst`  | input  | 1 | Synchronous, active-high reset. Returns to idle, tx=1. |
| `en`   | input  | 1 | Load strobe. Ignored when `busy=1`. |
| `data` | input  | 8 | Byte to transmit. Latched on the cycle `en=1 & ~busy`. |
| `tx`   | output | 1 | UART serial output. Idles at 1 (mark). |
| `busy` | output | 1 | High during transmission; accept new `en` only when low. |

## Behaviour

All state changes on `posedge clk`. Synchronous active-high reset.

### State machine (2-bit, one-hot-compatible encoding)

```
IDLE  (2'd0): tx=1, busy=0. On en: latch data, tx←0, busy←1 → START.
START (2'd1): tx=0 (start bit). Count CLKS_PER_BIT cycles → DATA (bit_idx=0).
DATA  (2'd2): tx=data_reg[bit_idx]. Count CLKS_PER_BIT cycles per bit.
              bit_idx 0→7; after bit 7 → STOP (tx←1).
STOP  (2'd3): tx=1 (stop bit). Count CLKS_PER_BIT cycles → IDLE (busy←0).
```

### Baud counter

`baud_cnt` counts 0 to `CLKS_PER_BIT − 1` for each bit period. On the cycle
`baud_cnt == CLKDIV_MAX` (where `CLKDIV_MAX = CLKS_PER_BIT − 1`), advance state.

`CLKDIV_MAX` is a `localparam [CLKDIV_W-1:0]`.

### Bit order

LSB first. `data_reg[0]` is the first data bit driven after the start bit.

### Transmission timing (CLKS_PER_BIT = N)

```
Cycle 0         : en=1 → latch data, tx←0, busy←1, state←START
Cycles 1..N     : START state, tx=0  (N cycles)
Cycles N+1..2N  : DATA, bit 0        (N cycles)
Cycles 2N+1..3N : DATA, bit 1        (N cycles)
...
Cycles 8N+1..9N : DATA, bit 7        (N cycles)
Cycles 9N+1..10N: STOP, tx=1         (N cycles)
Cycle 10N+1     : IDLE, busy←0
```

Total = 10N cycles from en-pulse to busy going low.

### Back-to-back

`busy` goes low on the cycle IDLE is entered. If `en=1` on that same cycle, a new
transmission begins immediately (no idle gap).

## Synthesis notes

- Single `always @(posedge clk)` block implementing the state machine.
- No `initial`, no `#` delays, no inferred latches.
- All case paths either assign next state or hold (register hold, not latch).
- `default` case resets to IDLE.
- Yosys `check -assert` must report 0 problems.

## Verification tips (for Verifier)

Use CLKS_PER_BIT=4, CLKDIV_W=2 in simulation (40 cycles per byte). Override params in
cocotb's `plusargs` or `COCOTB_PARAM_*` environment.

1. **Reset:** tx=1, busy=0 after rst.
2. **Busy flag:** en ignored when busy=1 — no double-load.
3. **Transmit 0x55 (01010101b):** bits LSB-first = 1,0,1,0,1,0,1,0. Capture tx on each
   baud-period midpoint (cycle N//2 into each bit) and compare:
   `[0, 1,0,1,0,1,0,1,0, 1]` = start, data[0..7], stop.
4. **Transmit 0xAA (10101010b):** bits = 0,1,0,1,0,1,0,1.
5. **Transmit 0x00 and 0xFF:** corner cases.
6. **Busy duration:** assert busy=1 from cycle after en until after 10*CLKS_PER_BIT cycles.
7. **Back-to-back:** send 5 bytes with no idle gap between them.
8. **Randomized:** 20 random bytes; deserialise tx stream and compare to original.

Python deserialiser for the tx stream:
```python
def uart_rx_sample(tx_trace, clks_per_bit):
    """Sample tx_trace at baud midpoints. Returns list of received bytes."""
    i = 0
    rx_bytes = []
    while i < len(tx_trace):
        if tx_trace[i] == 0:  # falling edge = start bit
            i += clks_per_bit // 2  # mid start bit
            bits = []
            for _ in range(8):
                i += clks_per_bit
                if i < len(tx_trace):
                    bits.append(tx_trace[i])
            byte = sum(b << k for k, b in enumerate(bits))
            rx_bytes.append(byte)
            i += clks_per_bit  # skip stop bit
        else:
            i += 1
    return rx_bytes
```
