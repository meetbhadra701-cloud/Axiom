import random

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer


WIDTH = 16
SHAMT_WIDTH = 4
MASK = (1 << WIDTH) - 1
MIN_VAL = -(1 << (WIDTH - 1))
MAX_VAL = (1 << (WIDTH - 1)) - 1


def to_bits(value):
    return value & MASK


def from_bits(bits):
    sign = 1 << (WIDTH - 1)
    return (bits ^ sign) - sign


def ref_shift(value, shamt, direction):
    value = from_bits(to_bits(value))
    shamt &= (1 << SHAMT_WIDTH) - 1
    if direction:
        return from_bits(to_bits(value >> shamt))
    return from_bits(to_bits(value << shamt))


async def sample_after_edge(dut):
    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")
    return from_bits(int(dut.out.value) & MASK)


def drive(dut, rst, en, value, shamt, direction):
    dut.rst.value = rst
    dut.en.value = en
    getattr(dut, "in").value = to_bits(value)
    dut.shamt.value = shamt & ((1 << SHAMT_WIDTH) - 1)
    dut.dir.value = direction


async def apply_cycle(dut, rst, en, value, shamt, direction, expected, label):
    if rst:
        expected = 0
    elif en:
        expected = ref_shift(value, shamt, direction)

    drive(dut, rst, en, value, shamt, direction)
    got = await sample_after_edge(dut)
    assert got == expected, (
        f"{label}: rst={rst} en={en} in={value} shamt={shamt} dir={direction} "
        f"got out={got} expected {expected}"
    )
    return expected


@cocotb.test()
async def test_barrel_shift_spec_behavior(dut):
    """Verify signed arithmetic right shift and wrapping left shift behavior."""

    random.seed(0xBA55)
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())

    drive(dut, rst=0, en=0, value=0, shamt=0, direction=0)
    expected = 0

    expected = await apply_cycle(dut, 1, 0, 123, 3, 0, expected, "initial reset")
    expected = await apply_cycle(dut, 1, 1, -8, 3, 1, expected, "reset priority")

    for cycle, args in enumerate([(1, 3, 0), (-8, 3, 1), (MAX_VAL, 15, 0)]):
        expected = await apply_cycle(
            dut, 0, 0, args[0], args[1], args[2], expected, f"hold {cycle}"
        )

    directed = [
        (1234, 0, 0, 1234),
        (-1234, 0, 0, -1234),
        (1234, 0, 1, 1234),
        (-1234, 0, 1, -1234),
        (1, 3, 0, 8),
        (16384, 1, 0, MIN_VAL),
        (-32768, 1, 0, 0),
        (8, 3, 1, 1),
        (-8, 3, 1, -1),
        (-1, 1, 1, -1),
        (-1, 15, 1, -1),
        (MAX_VAL, 15, 1, 0),
        (MIN_VAL, 15, 1, -1),
        (MAX_VAL, 15, 0, -32768),
    ]
    for cycle, (value, shamt, direction, expected_direct) in enumerate(directed):
        assert ref_shift(value, shamt, direction) == expected_direct
        expected = await apply_cycle(
            dut, 0, 1, value, shamt, direction, expected, f"directed {cycle}"
        )

    for cycle in range(600):
        rst = 1 if cycle in (197, 198) or random.randrange(120) == 0 else 0
        en = random.randrange(2)
        value = random.randrange(MIN_VAL, MAX_VAL + 1)
        shamt = random.randrange(1 << SHAMT_WIDTH)
        direction = random.randrange(2)
        expected = await apply_cycle(
            dut, rst, en, value, shamt, direction, expected, f"random {cycle}"
        )
