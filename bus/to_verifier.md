# To Verifier

v1 of `rtl/crc8.v` ready, spec in `spec/spec.md` (CRC-8/MAXIM bit-serial generator). Ready for simulation.

- Module: `crc8`
- Top-level: `crc8`
- Ports: `clk`, `rst` (sync active-high), `en`, `bit_in` (1-bit), `crc[7:0]` (output reg)
- Variant: CRC-8/MAXIM (Dallas 1-Wire). Polynomial x^8+x^5+x^4+1; reflected poly 0x8C; init 0x00; XorOut 0x00.
- Bit order: LSB-first (bit_in = byte[0] on first cycle, byte[7] on last).
- One `always @(posedge clk)` block; `wire feedback = crc[0] ^ bit_in`; 8 non-blocking assignments per §3.
- Priority: reset > enable > hold.
- Yosys `check -assert`: 0 problems. Synthesizes to 8 SDFFE + 3 XNOR + 1 NOT.
- Iteration: 1

Key test vectors (all from init crc=0x00):
1. Reset → crc=0x00.
2. en=0 → crc unchanged.
3. 8 zero bits (byte 0x00) → crc stays 0x00.
4. Single leading 1-bit from reset → crc=0x8C; full byte 0x01
   (bits 1,0,0,0,0,0,0,0 LSB-first, 8 en-cycles) → crc=0x5E.
5. String "123456789" (72 bits LSB-first) → crc=0xA1.

Python reference for random byte sequences:
```python
def crc8_maxim_ref(data_bytes):
    crc = 0
    for byte in data_bytes:
        for _ in range(8):
            bit = byte & 1
            byte >>= 1
            feedback = (crc ^ bit) & 1
            crc >>= 1
            if feedback:
                crc ^= 0x8C
    return crc
```
Or: `crcmod.predefined.mkCrcFun('crc-8-maxim')`.

Cocotb port names: `dut.clk`, `dut.rst`, `dut.en`, `dut.bit_in`, `dut.crc`.
(No reserved-word collision — `bit_in` is safe as a dotted attribute.)
