import random

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer


WIDTH = 8
MASK = (1 << WIDTH) - 1


def gray_encode(value):
    value &= MASK
    return (value ^ (value >> 1)) & MASK


def gray_decode(value):
    value &= MASK
    decoded = value
    shift = value >> 1
    while shift:
        decoded ^= shift
        shift >>= 1
    return decoded & MASK


def popcount(value):
    return bin(value & MASK).count("1")


async def sample_after_edge(dut):
    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")
    return int(dut.result.value) & MASK


def drive(dut, rst, en, mode, data):
    dut.rst.value = rst
    dut.en.value = en
    dut.mode.value = mode & 1
    dut.data.value = data & MASK


async def apply_cycle(dut, rst, en, mode, data, expected, label):
    if rst:
        expected = 0
    elif en:
        expected = gray_decode(data) if mode else gray_encode(data)

    drive(dut, rst, en, mode, data)
    got = await sample_after_edge(dut)
    assert got == expected, (
        f"{label}: rst={rst} en={en} mode={mode} data={data:#04x} "
        f"got result={got:#04x} expected {expected:#04x}"
    )
    return expected


@cocotb.test()
async def test_gray_codec_spec_behavior(dut):
    """Verify registered Gray encode/decode behavior exhaustively for WIDTH=8."""

    random.seed(0x6A4A)
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())

    drive(dut, rst=0, en=0, mode=0, data=0)
    expected = 0

    expected = await apply_cycle(dut, 1, 0, 0, 0xFF, expected, "initial reset")
    expected = await apply_cycle(dut, 1, 1, 1, 0x80, expected, "reset priority")

    for cycle, args in enumerate([(0, 0x01), (1, 0x01), (0, 0xFF), (1, 0x80)]):
        expected = await apply_cycle(
            dut, 0, 0, args[0], args[1], expected, f"hold {cycle}"
        )

    directed_encode = {
        0x00: 0x00,
        0x01: 0x01,
        0x02: 0x03,
        0x03: 0x02,
        0x04: 0x06,
        0x7F: 0x40,
        0x80: 0xC0,
        0xFF: 0x80,
    }
    for value, encoded in directed_encode.items():
        assert gray_encode(value) == encoded
        expected = await apply_cycle(
            dut, 0, 1, 0, value, expected, f"directed encode {value:#04x}"
        )

    for value in range(256):
        encoded = gray_encode(value)
        decoded = gray_decode(encoded)
        assert decoded == value, (
            f"Python round-trip failed for {value:#04x}: encoded {encoded:#04x}, "
            f"decoded {decoded:#04x}"
        )

        expected = await apply_cycle(dut, 0, 1, 0, value, expected, f"encode {value:#04x}")
        assert expected == encoded

        expected = await apply_cycle(
            dut, 0, 1, 1, encoded, expected, f"decode encoded {value:#04x}"
        )
        assert expected == value

    for value in range(255):
        diff = gray_encode(value) ^ gray_encode(value + 1)
        assert popcount(diff) == 1, (
            f"Gray adjacency failed for {value:#04x}->{value + 1:#04x}: diff {diff:#04x}"
        )

    # Exhaustive decode mode for arbitrary Gray-code inputs, including invalid sequence order.
    for gray in range(256):
        expected = await apply_cycle(dut, 0, 1, 1, gray, expected, f"decode {gray:#04x}")
        assert expected == gray_decode(gray)

    # Mode switching updates only on enabled cycles.
    expected = await apply_cycle(dut, 0, 1, 0, 0x55, expected, "mode encode")
    held = expected
    expected = await apply_cycle(dut, 0, 0, 1, 0x55, expected, "mode switch hold")
    assert expected == held
    expected = await apply_cycle(dut, 0, 1, 1, 0x55, expected, "mode decode")
    assert expected == gray_decode(0x55)

    for cycle in range(500):
        rst = 1 if cycle in (211, 212) or random.randrange(120) == 0 else 0
        en = random.randrange(2)
        mode = random.randrange(2)
        data = random.randrange(256)
        expected = await apply_cycle(
            dut, rst, en, mode, data, expected, f"random {cycle}"
        )
