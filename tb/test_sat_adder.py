import random

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer


WIDTH = 16
MIN_VAL = -(1 << (WIDTH - 1))
MAX_VAL = (1 << (WIDTH - 1)) - 1
MASK = (1 << WIDTH) - 1


def to_bits(value):
    return value & MASK


def from_bits(bits):
    sign = 1 << (WIDTH - 1)
    return (bits ^ sign) - sign


def saturating_add(a, b):
    result = a + b
    if result > MAX_VAL:
        return MAX_VAL
    if result < MIN_VAL:
        return MIN_VAL
    return result


async def sample_after_edge(dut):
    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")
    return from_bits(int(dut.sum.value) & MASK)


def drive(dut, rst, en, a, b):
    dut.rst.value = rst
    dut.en.value = en
    dut.a.value = to_bits(a)
    dut.b.value = to_bits(b)


async def apply_cycle(dut, rst, en, a, b, expected, label):
    if rst:
        expected = 0
    elif en:
        expected = saturating_add(a, b)

    drive(dut, rst, en, a, b)
    got = await sample_after_edge(dut)
    assert got == expected, (
        f"{label}: rst={rst} en={en} a={a} b={b} got sum={got} expected {expected}"
    )
    return expected


@cocotb.test()
async def test_sat_adder_spec_behavior(dut):
    """Verify saturating signed addition against a Python clipping model."""

    random.seed(0x5A7A)
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())

    drive(dut, rst=0, en=0, a=0, b=0)
    expected = 0

    expected = await apply_cycle(dut, 1, 0, MAX_VAL, MAX_VAL, expected, "initial reset")
    expected = await apply_cycle(dut, 1, 1, MIN_VAL, MIN_VAL, expected, "reset priority")

    for cycle, (a, b) in enumerate([(1, 2), (MAX_VAL, 1), (MIN_VAL, -1), (-7, 4)]):
        expected = await apply_cycle(dut, 0, 0, a, b, expected, f"hold {cycle}")

    directed = [
        (0, 0),
        (1, 2),
        (-1, -2),
        (1234, -234),
        (-1234, 234),
        (MAX_VAL, 0),
        (MIN_VAL, 0),
        (MAX_VAL, 1),
        (MAX_VAL, MAX_VAL),
        (MAX_VAL, -1),
        (MIN_VAL, -1),
        (MIN_VAL, MIN_VAL),
        (MIN_VAL, 1),
        (20000, 10000),
        (-20000, -10000),
        (20000, -10000),
        (-20000, 10000),
    ]
    for cycle, (a, b) in enumerate(directed):
        expected = await apply_cycle(dut, 0, 1, a, b, expected, f"directed {cycle}")

    for cycle in range(600):
        rst = 1 if cycle in (211, 212) or random.randrange(120) == 0 else 0
        en = random.randrange(2)
        a = random.randrange(MIN_VAL, MAX_VAL + 1)
        b = random.randrange(MIN_VAL, MAX_VAL + 1)
        expected = await apply_cycle(dut, rst, en, a, b, expected, f"random {cycle}")
