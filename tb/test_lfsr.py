import random

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer


WIDTH = 16
POLY = 0xB400
SEED = 1
MASK = (1 << WIDTH) - 1
PERIOD = (1 << WIDTH) - 1


def galois_step(state):
    feedback = state & 1
    return ((state >> 1) ^ (POLY if feedback else 0)) & MASK


async def sample_after_edge(dut):
    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")
    return int(dut.out.value) & MASK


def drive(dut, rst, en):
    dut.rst.value = rst
    dut.en.value = en


async def apply_cycle(dut, rst, en, expected, label):
    if rst:
        expected = SEED
    elif en:
        expected = galois_step(expected)

    drive(dut, rst, en)
    got = await sample_after_edge(dut)
    assert got == expected, (
        f"{label}: rst={rst} en={en} got out={got:#06x} expected {expected:#06x}"
    )
    return expected


@cocotb.test()
async def test_lfsr_spec_behavior(dut):
    """Verify default 16-bit Galois LFSR sequence and maximal period."""

    random.seed(0x1F5A)
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())

    drive(dut, rst=0, en=0)
    expected = 0

    expected = await apply_cycle(dut, 1, 0, expected, "initial reset")
    expected = await apply_cycle(dut, 1, 1, expected, "reset priority")

    for cycle in range(4):
        expected = await apply_cycle(dut, 0, 0, expected, f"hold {cycle}")

    for cycle in range(64):
        expected = await apply_cycle(dut, 0, 1, expected, f"first steps {cycle}")
        assert expected != 0, f"golden model reached forbidden zero at step {cycle}"

    for cycle in range(100):
        rst = 1 if cycle in (17, 18) or random.randrange(50) == 0 else 0
        en = random.randrange(2)
        expected = await apply_cycle(dut, rst, en, expected, f"random {cycle}")

    expected = await apply_cycle(dut, 1, 0, expected, "period reset")
    seen = set()
    for step in range(PERIOD):
        assert expected not in seen, f"state repeated early at step {step}: {expected:#06x}"
        assert expected != 0, f"entered forbidden zero state at step {step}"
        seen.add(expected)
        expected = await apply_cycle(dut, 0, 1, expected, f"period {step}")

    assert expected == SEED, f"period did not return to seed: got {expected:#06x}"
    assert len(seen) == PERIOD, f"period length got {len(seen)} expected {PERIOD}"
