import random

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer


SAMPLE_WIDTH = 8
LO_WIDTH = 8
OUT_WIDTH = 16
OUT_MASK = (1 << OUT_WIDTH) - 1


def to_bits(value, width):
    return value & ((1 << width) - 1)


def from_bits(bits, width):
    sign = 1 << (width - 1)
    return (bits ^ sign) - sign


def wrap_out(value):
    return from_bits(value & OUT_MASK, OUT_WIDTH)


async def sample_after_edge(dut):
    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")
    return from_bits(int(dut.mixed.value) & OUT_MASK, OUT_WIDTH)


def drive(dut, rst, en, sample, lo):
    dut.rst.value = rst
    dut.en.value = en
    dut.sample.value = to_bits(sample, SAMPLE_WIDTH)
    dut.lo.value = to_bits(lo, LO_WIDTH)


async def apply_cycle(dut, rst, en, sample, lo, expected, label):
    if rst:
        expected = 0
    elif en:
        expected = wrap_out(sample * lo)

    drive(dut, rst, en, sample, lo)
    got = await sample_after_edge(dut)
    assert got == expected, (
        f"{label}: rst={rst} en={en} sample={sample} lo={lo} "
        f"got mixed={got} expected {expected}"
    )
    return expected


@cocotb.test()
async def test_mixer_spec_behavior(dut):
    """Verify signed mixer behavior against the spec-defined product model."""

    random.seed(0xA11D)
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())

    drive(dut, rst=0, en=0, sample=0, lo=0)
    expected = 0

    expected = await apply_cycle(dut, 1, 0, 127, 127, expected, "initial reset")
    expected = await apply_cycle(dut, 1, 1, -128, -128, expected, "reset priority")

    for cycle, (sample, lo) in enumerate([(1, 2), (-3, 4), (127, -1)]):
        expected = await apply_cycle(dut, 0, 0, sample, lo, expected, f"hold {cycle}")

    directed = [
        (0, 127),
        (1, 127),
        (-1, 127),
        (127, 127),
        (-128, 127),
        (127, -128),
        (-128, -128),
        (-7, -9),
        (12, -11),
    ]
    for cycle, (sample, lo) in enumerate(directed):
        expected = await apply_cycle(dut, 0, 1, sample, lo, expected, f"directed {cycle}")

    for cycle in range(500):
        rst = 1 if cycle in (113, 114) or random.randrange(100) == 0 else 0
        en = random.randrange(2)
        sample = random.randrange(-(1 << (SAMPLE_WIDTH - 1)), 1 << (SAMPLE_WIDTH - 1))
        lo = random.randrange(-(1 << (LO_WIDTH - 1)), 1 << (LO_WIDTH - 1))
        expected = await apply_cycle(dut, rst, en, sample, lo, expected, f"random {cycle}")
