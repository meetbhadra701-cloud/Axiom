import random

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer


WIDTH = 8
PERIOD_MAX = 1 << WIDTH
MASK = PERIOD_MAX - 1


def effective_divisor(divisor):
    return PERIOD_MAX if (divisor & MASK) == 0 else divisor & MASK


async def sample_after_edge(dut):
    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")
    return int(dut.strobe.value)


def drive(dut, rst, en, divisor):
    dut.rst.value = rst
    dut.en.value = en
    dut.divisor.value = divisor & MASK


def model_step(counter, strobe, rst, en, divisor):
    if rst:
        return 0, 0
    if en:
        if counter == ((divisor - 1) & MASK):
            return 0, 1
        return (counter + 1) & MASK, 0
    return counter, strobe


async def apply_cycle(dut, rst, en, divisor, counter, strobe, label):
    counter, strobe = model_step(counter, strobe, rst, en, divisor)
    drive(dut, rst, en, divisor)
    got = await sample_after_edge(dut)
    assert got == strobe, (
        f"{label}: rst={rst} en={en} divisor={divisor} counter_model={counter} "
        f"got strobe={got} expected {strobe}"
    )
    return counter, strobe


async def reset_model_and_dut(dut, divisor=1):
    drive(dut, rst=1, en=0, divisor=divisor)
    got = await sample_after_edge(dut)
    assert got == 0, f"reset got strobe={got}, expected 0"
    return 0, 0


async def enabled_window(dut, divisor, cycles, counter, strobe, label):
    observed = []
    for cycle in range(cycles):
        counter, strobe = await apply_cycle(
            dut, 0, 1, divisor, counter, strobe, f"{label} {cycle}"
        )
        observed.append(strobe)
    return counter, strobe, observed


def pulse_indices(bits):
    return [idx for idx, bit in enumerate(bits) if bit]


@cocotb.test()
async def test_strobe_gen_spec_behavior(dut):
    """Verify programmable strobe period, width, reset, and hold behavior."""

    random.seed(0x57B0)
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())

    drive(dut, rst=0, en=0, divisor=1)
    counter = 0
    strobe = 0

    counter, strobe = await reset_model_and_dut(dut)
    counter, strobe = await apply_cycle(dut, 1, 1, 1, counter, strobe, "reset priority")

    counter, strobe = await reset_model_and_dut(dut, divisor=1)
    counter, strobe, observed = await enabled_window(
        dut, 1, 16, counter, strobe, "divisor one"
    )
    assert observed == [1] * 16

    for divisor in [2, 3, 4, 5, 8, 17, 64, 127, 255, 0]:
        period = effective_divisor(divisor)
        counter, strobe = await reset_model_and_dut(dut, divisor=divisor)
        counter, strobe, observed = await enabled_window(
            dut, divisor, period * 3, counter, strobe, f"period {divisor}"
        )
        expected_indices = [period - 1, (2 * period) - 1, (3 * period) - 1]
        assert pulse_indices(observed) == expected_indices, (
            f"divisor {divisor}: got pulse indices {pulse_indices(observed)} "
            f"expected {expected_indices}"
        )
        for idx in expected_indices:
            if idx + 1 < len(observed):
                assert observed[idx + 1] == 0, (
                    f"divisor {divisor}: strobe wider than one enabled cycle at {idx}"
                )

    # Hold preserves both counter and strobe, including the case where strobe is high.
    counter, strobe = await reset_model_and_dut(dut, divisor=4)
    counter, strobe, observed = await enabled_window(dut, 4, 4, counter, strobe, "to pulse")
    assert observed[-1] == 1
    for cycle in range(3):
        counter, strobe = await apply_cycle(
            dut, 0, 0, 4, counter, strobe, f"hold high strobe {cycle}"
        )
        assert strobe == 1
    counter, strobe = await apply_cycle(dut, 0, 1, 4, counter, strobe, "resume after hold")
    assert strobe == 0

    counter, strobe = await reset_model_and_dut(dut, divisor=7)
    for cycle in range(600):
        rst = 1 if cycle in (211, 212) or random.randrange(120) == 0 else 0
        en = random.randrange(2)
        divisor = random.randrange(PERIOD_MAX)
        counter, strobe = await apply_cycle(
            dut, rst, en, divisor, counter, strobe, f"random {cycle}"
        )
