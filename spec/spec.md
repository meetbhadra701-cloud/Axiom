# Spec — gray_codec (Gray Code Encoder / Decoder)

**Status:** authoritative. Ground truth for Architect and Verifier.
Previous specs archived in `spec/`.

## Purpose

Registered binary ↔ Gray code converter. `mode=0` encodes binary to Gray;
`mode=1` decodes Gray back to binary. Primary FPGA use-case: Gray-coding FIFO
write/read pointers before they cross clock domains — only one bit changes per
pointer increment, so a metastable sample in the receiving domain still resolves
to one of two adjacent valid pointer values.

## Parameters

| Parameter | Default | Description |
|---|---:|---|
| `WIDTH`   | 8 | Data width for both input and output. |

## Ports

| Port     | Direction | Width   | Description |
|---|---|---:|---|
| `clk`    | input  | 1       | Clock. |
| `rst`    | input  | 1       | Synchronous, active-high reset. |
| `en`     | input  | 1       | Sample enable. |
| `mode`   | input  | 1       | 0 = encode (binary→Gray); 1 = decode (Gray→binary). |
| `data`   | input  | `WIDTH` | Input value. |
| `result` | output | `WIDTH` | Registered converted output. |

## Behaviour

All state changes on `posedge clk`. Priority: **reset > enable > hold**.

1. If `rst == 1`: `result <= 0`.
2. Else if `en == 1`: `result <= mode ? decode(data) : encode(data)`.
3. Else: hold.

### Encode (binary → Gray)

```
gray[WIDTH-1:0] = bin[WIDTH-1:0] ^ (bin[WIDTH-1:0] >> 1)
```

The MSB is unchanged; each lower bit is XOR of that bit and the one above.

### Decode (Gray → binary)

The MSB is unchanged; each lower bit is XOR of the decoded bit above and the Gray bit:

```
bin[WIDTH-1]   = gray[WIDTH-1]
bin[WIDTH-2]   = bin[WIDTH-1]  ^ gray[WIDTH-2]
bin[WIDTH-3]   = bin[WIDTH-2]  ^ gray[WIDTH-3]
  ...
bin[0]         = bin[1]        ^ gray[0]
```

This is a serial XOR prefix chain — O(WIDTH) gates but no feedback loops; purely
combinational.

## Synthesis notes

- Encode: single `assign` using `>>` and `^`.
- Decode: `generate` loop of `assign` statements chaining `decoded[i] = decoded[i+1] ^ data[i]`.
  The chain resolves combinationally (no loops, no latches).
- The registered stage is a single `always @(posedge clk)` selecting between the two wires.
- No `initial`, no `#` delays, no inferred latches.
- Yosys `check -assert` must report 0 problems.

## Verification tips (for Verifier)

For WIDTH=8:

1. **Reset:** result=0 after rst=1.
2. **Hold:** en=0 preserves result.
3. **Encode identity:** `encode(0)` = 0; `encode(1)` = 1; `encode(2)` = 3; `encode(3)` = 2;
   `encode(255)` = 128 (`0xFF` → `0x80`).
4. **Decode identity:** `decode(encode(x))` = x for all x in 0..255.
5. **Encode round-trip:** for all 256 values, encode then decode returns the original.
6. **Single-bit change:** for consecutive binary values n and n+1, `encode(n)` and
   `encode(n+1)` differ in exactly one bit (the defining Gray code property).
7. **Mode switch:** change mode mid-run and verify result updates on the next en=1 cycle.
8. **Exhaustive:** iterate all 256 inputs in both modes; compare against Python
   reference: encode = `n ^ (n >> 1)`; decode = Python prefix-XOR reduction.
