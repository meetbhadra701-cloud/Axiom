import random

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer


PHASE_WIDTH = 24
MODULUS = 1 << PHASE_WIDTH
MASK = MODULUS - 1
NYQUIST_INC = 1 << (PHASE_WIDTH - 1)


async def sample_after_edge(dut):
    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")
    return int(dut.phase_out.value) & MASK


def drive(dut, rst, en, phase_inc):
    dut.rst.value = rst
    dut.en.value = en
    dut.phase_inc.value = phase_inc & MASK


async def apply_cycle(dut, rst, en, phase_inc, expected, label):
    if rst:
        expected = 0
    elif en:
        expected = (expected + phase_inc) & MASK

    drive(dut, rst, en, phase_inc)
    got = await sample_after_edge(dut)
    assert got == expected, (
        f"{label}: rst={rst} en={en} phase_inc={phase_inc:#08x} "
        f"got phase_out={got:#08x} expected {expected:#08x}"
    )
    return expected


@cocotb.test()
async def test_nco_spec_behavior(dut):
    """Verify NCO phase accumulator behavior against a Python model."""

    random.seed(0x0C0)
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())

    drive(dut, rst=0, en=0, phase_inc=0)
    expected = 0

    expected = await apply_cycle(dut, 1, 0, 0x123456, expected, "initial reset")
    expected = await apply_cycle(dut, 1, 1, 0xFFFFFF, expected, "reset priority")

    # Hold behavior with enable low.
    for cycle, inc in enumerate([1, 0x123, 0x800000, 0xFFFFFF]):
        expected = await apply_cycle(dut, 0, 0, inc, expected, f"hold {cycle}")

    # phase_inc = 0 holds the accumulator at its current value.
    for cycle in range(4):
        expected = await apply_cycle(dut, 0, 1, 0, expected, f"zero inc {cycle}")

    # Basic accumulation.
    for cycle, inc in enumerate([1, 2, 3, 0x1000, 0xABCDE]):
        expected = await apply_cycle(dut, 0, 1, inc, expected, f"accumulate {cycle}")

    # Explicit wrap-around.
    expected = await apply_cycle(dut, 1, 0, 0, expected, "wrap reset")
    expected = await apply_cycle(dut, 0, 1, MASK - 2, expected, "near max")
    expected = await apply_cycle(dut, 0, 1, 5, expected, "wrap add")
    assert expected == 2, f"wrap model sanity expected 0x000002, got {expected:#08x}"

    # Nyquist increment toggles between 0 and midpoint after reset.
    expected = await apply_cycle(dut, 1, 0, 0, expected, "nyquist reset")
    observed = []
    for cycle in range(8):
        expected = await apply_cycle(dut, 0, 1, NYQUIST_INC, expected, f"nyquist {cycle}")
        observed.append(expected)
    assert observed == [NYQUIST_INC, 0, NYQUIST_INC, 0, NYQUIST_INC, 0, NYQUIST_INC, 0]

    # Randomized model check with resets, holds, and arbitrary unsigned increments.
    for cycle in range(500):
        rst = 1 if cycle in (101, 102) or random.randrange(100) == 0 else 0
        en = random.randrange(2)
        inc = random.randrange(MODULUS)
        expected = await apply_cycle(dut, rst, en, inc, expected, f"random {cycle}")
