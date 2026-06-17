# Spec — crc8 (CRC-8/MAXIM Generator)

**Status:** authoritative. Ground truth for Architect and Verifier.
Previous specs archived in `spec/`.

## Purpose

Bit-serial CRC-8/MAXIM (Dallas 1-Wire) accumulator. Processes one bit per enabled
clock cycle, accumulating the running checksum in an 8-bit LFSR. Used for data
integrity in DS18B20 temperature sensor reads and other 1-Wire protocol frames.

## CRC variant

| Property    | Value |
|---|---|
| Name        | CRC-8/MAXIM (also CRC-8/Dallas, iButton) |
| Polynomial  | x^8 + x^5 + x^4 + 1 (normal: 0x31; reflected: 0x8C) |
| Reflect in  | Yes — data bits processed LSB first |
| Reflect out | Yes |
| Init        | 0x00 |
| XorOut      | 0x00 |
| Check       | CRC of ASCII "123456789" = 0xA1 |

## Parameters

None. The polynomial and bit width are fixed for CRC-8/MAXIM.

## Ports

| Port     | Direction | Width | Description |
|---|---|---:|---|
| `clk`    | input  | 1 | Clock. |
| `rst`    | input  | 1 | Synchronous, active-high reset. Clears CRC to 0x00. |
| `en`     | input  | 1 | Shift enable. CRC advances by one bit when high. |
| `bit_in` | input  | 1 | Next data bit to accumulate (LSB of each byte first). |
| `crc`    | output | 8 | Registered running CRC. Valid after all data bits are processed. |

## Behaviour

All state changes on `posedge clk`. Priority: **reset > enable > hold**.

**LFSR step (one bit, reflected polynomial 0x8C):**
```
feedback = crc[0] ^ bit_in
crc[0] <= crc[1]
crc[1] <= crc[2]
crc[2] <= crc[3] ^ feedback    // poly bit 2 of 0x8C
crc[3] <= crc[4] ^ feedback    // poly bit 3 of 0x8C
crc[4] <= crc[5]
crc[5] <= crc[6]
crc[6] <= crc[7]
crc[7] <= feedback             // poly bit 7 of 0x8C (MSB/implicit)
```

`feedback` is the bit being shifted out (`crc[0]`) XOR the new data bit. The taps at
positions 2, 3, and 7 match the reflected polynomial 0x8C (= 10001100b; bits 7,3,2).

**Accumulating a byte:** drive 8 consecutive `en=1` cycles with `bit_in` = byte[0],
byte[1], …, byte[7] (LSB first).

**Known test vector:** CRC of single byte 0x01 (bits: 1,0,0,0,0,0,0,0 LSB-first) = 0x8C.
After processing the single leading 1-bit, crc = 0x8C; the remaining 7 zero bits
leave crc unchanged (feedback=0 on each).

## Synthesis notes

- `feedback` is a combinational `wire`.
- Single `always @(posedge clk)` block; 8 non-blocking assignments to `crc[7:0]`.
- Output `crc` is `output reg [7:0]`.
- No `initial`, no `#` delays, no inferred latches.
- Yosys `check -assert` must report 0 problems.

## Verification tips (for Verifier)

1. **Reset:** crc=0x00 after rst=1.
2. **Hold:** en=0 leaves crc unchanged.
3. **Zero byte (8 zeros):** starting from 0x00, crc stays 0x00.
4. **Byte 0x01** (bits 1,0,0,0,0,0,0,0): crc → 0x8C (first bit sets the polynomial;
   remaining 7 zero bits leave crc = 0x8C).
5. **Byte 0xFF** (8 ones): compute and compare against a Python reference.
6. **Check string "123456789":** process all 72 bits LSB-first; final crc = 0xA1.
   Python reference:
   ```python
   import crcmod
   fn = crcmod.predefined.mkCrcFun('crc-8-maxim')
   hex(fn(b'123456789'))  # → 0xa1
   ```
7. **Randomized:** random byte sequences against Python `crcmod` or manual bit-serial
   reference: `crc ^= bit; if crc & 1: crc = (crc >> 1) ^ 0x8C; else: crc >>= 1`.
