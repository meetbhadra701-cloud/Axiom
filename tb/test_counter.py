import random

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer


WIDTH = 8
MODULUS = 1 << WIDTH
MAX_COUNT = MODULUS - 1


async def sample_after_edge(dut):
    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")
    return int(dut.count.value)


async def apply_cycle(dut, rst, en, expected, label):
    dut.rst.value = rst
    dut.en.value = en
    got = await sample_after_edge(dut)
    assert got == expected, (
        f"{label}: rst={rst} en={en} got count={got:#04x} expected {expected:#04x}"
    )


@cocotb.test()
async def test_counter_spec_behavior(dut):
    """Verify counter behavior against an independent Python golden model."""

    random.seed(0xA710)
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())

    dut.rst.value = 0
    dut.en.value = 0

    expected = 0

    # Defined starting state: synchronous active-high reset.
    await apply_cycle(dut, rst=1, en=0, expected=0, label="initial reset")
    expected = 0

    # Reset has priority over enable.
    await apply_cycle(dut, rst=1, en=1, expected=0, label="reset priority")
    expected = 0

    # Enable low holds the registered value.
    for cycle in range(4):
        await apply_cycle(dut, rst=0, en=0, expected=expected, label=f"hold {cycle}")

    # Enabled cycles count up by one.
    for cycle in range(20):
        expected = (expected + 1) % MODULUS
        await apply_cycle(dut, rst=0, en=1, expected=expected, label=f"count up {cycle}")

    # Mid-count reset clears on the next rising edge.
    await apply_cycle(dut, rst=1, en=0, expected=0, label="mid-count reset")
    expected = 0

    # Walk to wrap-around and check 255 -> 0.
    for cycle in range(MAX_COUNT):
        expected = (expected + 1) % MODULUS
        await apply_cycle(dut, rst=0, en=1, expected=expected, label=f"pre-wrap {cycle}")

    expected = 0
    await apply_cycle(dut, rst=0, en=1, expected=expected, label="wrap 0xff to 0x00")

    # Randomized golden-model run with enable toggles and back-to-back resets.
    for cycle in range(200):
        if cycle in (17, 18, 93):
            rst = 1
        else:
            rst = 1 if random.randrange(32) == 0 else 0
        en = random.randrange(2)

        if rst:
            expected = 0
        elif en:
            expected = (expected + 1) % MODULUS

        await apply_cycle(dut, rst=rst, en=en, expected=expected, label=f"random {cycle}")
