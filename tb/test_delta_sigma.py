import random

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer


WIDTH = 8
PERIOD = 1 << WIDTH
MASK = PERIOD - 1


async def sample_after_edge(dut):
    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")
    return int(dut.ds_out.value)


def drive(dut, rst, en, value):
    dut.rst.value = rst
    dut.en.value = en
    getattr(dut, "in").value = value & MASK


def model_step(acc, out, rst, en, value):
    if rst:
        return 0, 0
    if en:
        next_acc = (acc & MASK) + (value & MASK)
        next_out = (acc >> WIDTH) & 1
        return next_acc, next_out
    return acc, out


async def apply_cycle(dut, rst, en, value, acc, out, label):
    acc, out = model_step(acc, out, rst, en, value)
    drive(dut, rst, en, value)
    got = await sample_after_edge(dut)
    assert got == out, (
        f"{label}: rst={rst} en={en} in={value} got ds_out={got} "
        f"expected {out} model_acc={acc:#05x}"
    )
    return acc, out


async def reset_model_and_dut(dut):
    drive(dut, rst=1, en=0, value=0)
    got = await sample_after_edge(dut)
    assert got == 0, f"reset got ds_out={got}, expected 0"
    return 0, 0


async def enabled_window(dut, value, acc, out, cycles, label):
    observed = []
    for cycle in range(cycles):
        acc, out = await apply_cycle(dut, 0, 1, value, acc, out, f"{label} {cycle}")
        observed.append(out)
    return acc, out, observed


@cocotb.test()
async def test_delta_sigma_spec_behavior(dut):
    """Verify first-order delta-sigma behavior and settled density."""

    random.seed(0xD51A)
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())

    drive(dut, rst=0, en=0, value=0)
    acc = 0
    out = 0

    acc, out = await reset_model_and_dut(dut)
    acc, out = await apply_cycle(dut, 1, 1, 255, acc, out, "reset priority")

    for cycle, value in enumerate([1, 64, 128, 255]):
        acc, out = await apply_cycle(dut, 0, 0, value, acc, out, f"hold {cycle}")

    acc, out = await reset_model_and_dut(dut)
    acc, out, observed = await enabled_window(dut, 0, acc, out, PERIOD * 2, "zero")
    assert sum(observed) == 0

    # The first post-reset period is one output-latency cycle short for nonzero inputs
    # because ds_out reports the previous carry. Subsequent full periods have exact density.
    for value in [1, 2, 3, 17, 64, 127, 128, 129, 200, 254, 255]:
        acc, out = await reset_model_and_dut(dut)
        acc, out, first = await enabled_window(dut, value, acc, out, PERIOD, f"first {value}")
        assert sum(first) == max(value - 1, 0), (
            f"first period for {value}: got {sum(first)} ones expected {max(value - 1, 0)}"
        )
        acc, out, settled = await enabled_window(
            dut, value, acc, out, PERIOD, f"settled {value}"
        )
        assert sum(settled) == value, (
            f"settled period for {value}: got {sum(settled)} ones expected {value}"
        )

    # Full settled density sweep over all 8-bit values.
    for value in range(PERIOD):
        acc, out = await reset_model_and_dut(dut)
        acc, out, _ = await enabled_window(dut, value, acc, out, PERIOD, f"warm {value}")
        acc, out, observed = await enabled_window(
            dut, value, acc, out, PERIOD, f"density {value}"
        )
        assert sum(observed) == value, (
            f"density sweep value {value}: got {sum(observed)} ones expected {value}"
        )

    acc, out = await reset_model_and_dut(dut)
    for cycle in range(600):
        rst = 1 if cycle in (211, 212) or random.randrange(120) == 0 else 0
        en = random.randrange(2)
        value = random.randrange(PERIOD)
        acc, out = await apply_cycle(dut, rst, en, value, acc, out, f"random {cycle}")
