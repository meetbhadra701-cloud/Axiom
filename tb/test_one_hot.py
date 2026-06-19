import os
import random

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer


N = int(os.getenv("ONE_HOT_N", "8"))
LOG2W = int(os.getenv("ONE_HOT_LOG2W", "3"))
MASK = (1 << N) - 1


def ref(idx):
    return (1 << idx) & MASK


def popcount(value):
    return bin(value & MASK).count("1")


def drive(dut, rst, en, idx):
    dut.rst.value = rst
    dut.en.value = en
    getattr(dut, "in").value = idx & ((1 << LOG2W) - 1)


async def sample_after_edge(dut):
    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")
    return int(dut.out.value) & MASK


async def apply_cycle(dut, expected, rst, en, idx, label):
    drive(dut, rst, en, idx)
    got = await sample_after_edge(dut)

    if rst:
        expected = 0
    elif en:
        expected = ref(idx)

    assert got == expected, (
        f"{label}: rst={rst} en={en} in={idx} got out={got:#0{N // 4 + 4}x}, "
        f"expected {expected:#0{N // 4 + 4}x}"
    )
    if en and not rst:
        assert popcount(got) == 1, f"{label}: out should be one-hot, got {got:b}"
    return expected


@cocotb.test()
async def test_one_hot_spec_behavior(dut):
    """Verify registered binary-to-one-hot decode behavior."""

    random.seed(0x01E047 + N)
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())

    drive(dut, rst=0, en=0, idx=0)
    expected = 0

    expected = await apply_cycle(
        dut, expected, rst=1, en=0, idx=N - 1, label="initial reset"
    )
    expected = await apply_cycle(
        dut, expected, rst=1, en=1, idx=min(5, N - 1), label="reset priority"
    )

    directed_indices = [0, min(1, N - 1), min(3, N - 1), N - 1]
    seen = set()
    for idx in directed_indices:
        if idx in seen:
            continue
        seen.add(idx)
        expected = await apply_cycle(
            dut, expected, rst=0, en=1, idx=idx, label=f"directed index {idx}"
        )

    held = expected
    for cycle, idx in enumerate([0, N - 1, N // 2]):
        expected = await apply_cycle(
            dut, expected, rst=0, en=0, idx=idx, label=f"hold cycle {cycle}"
        )
        assert expected == held

    for idx in range(N):
        expected = await apply_cycle(
            dut, expected, rst=0, en=1, idx=idx, label=f"all indices {idx}"
        )
        assert expected == ref(idx)

    expected = await apply_cycle(
        dut, expected, rst=1, en=1, idx=N - 1, label="reset clears active output"
    )
    assert expected == 0

    for cycle in range(500):
        rst = 1 if cycle in (199, 200) or random.randrange(160) == 0 else 0
        en = random.randrange(2)
        idx = random.randrange(N)
        expected = await apply_cycle(
            dut, expected, rst=rst, en=en, idx=idx, label=f"random cycle {cycle}"
        )
