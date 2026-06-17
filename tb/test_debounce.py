import random

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer


STABLE_BITS = 4
THRESHOLD = 1 << STABLE_BITS
COUNT_MAX = THRESHOLD - 1


def model_step(counter, sig_out, rst, sig_in):
    if rst:
        return 0, 0
    if sig_in == sig_out:
        return 0, sig_out
    if counter == COUNT_MAX:
        return 0, sig_in
    return counter + 1, sig_out


async def sample_after_edge(dut):
    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")
    return int(dut.sig_out.value)


def drive(dut, rst, sig_in):
    dut.rst.value = rst
    dut.sig_in.value = sig_in & 1


async def apply_cycle(dut, rst, sig_in, counter, sig_out, label):
    counter, sig_out = model_step(counter, sig_out, rst, sig_in)
    drive(dut, rst, sig_in)
    got = await sample_after_edge(dut)
    assert got == sig_out, (
        f"{label}: rst={rst} sig_in={sig_in} got sig_out={got} "
        f"expected {sig_out} model_counter={counter}"
    )
    return counter, sig_out


async def reset_model_and_dut(dut):
    drive(dut, rst=1, sig_in=0)
    got = await sample_after_edge(dut)
    assert got == 0, f"reset got sig_out={got}, expected 0"
    return 0, 0


async def run_signal(dut, sig_in, cycles, counter, sig_out, label):
    observed = []
    for cycle in range(cycles):
        counter, sig_out = await apply_cycle(
            dut, 0, sig_in, counter, sig_out, f"{label} {cycle}"
        )
        observed.append(sig_out)
    return counter, sig_out, observed


@cocotb.test()
async def test_debounce_spec_behavior(dut):
    """Verify 16-cycle debounce threshold and glitch rejection."""

    random.seed(0xDEB0)
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())

    drive(dut, rst=0, sig_in=0)
    counter = 0
    sig_out = 0

    counter, sig_out = await reset_model_and_dut(dut)
    counter, sig_out = await apply_cycle(dut, 1, 1, counter, sig_out, "reset priority")

    # 15 differing cycles are not enough.
    counter, sig_out = await reset_model_and_dut(dut)
    counter, sig_out, observed = await run_signal(
        dut, 1, THRESHOLD - 1, counter, sig_out, "short high glitch"
    )
    assert observed == [0] * (THRESHOLD - 1)
    counter, sig_out, observed = await run_signal(
        dut, 0, 2, counter, sig_out, "return low after short glitch"
    )
    assert observed == [0, 0]

    # The 16th consecutive differing cycle accepts the new value.
    counter, sig_out = await reset_model_and_dut(dut)
    counter, sig_out, observed = await run_signal(
        dut, 1, THRESHOLD, counter, sig_out, "clean rise"
    )
    assert observed[:-1] == [0] * (THRESHOLD - 1)
    assert observed[-1] == 1

    # Once accepted, matching input resets the counter and output remains stable.
    counter, sig_out, observed = await run_signal(
        dut, 1, 5, counter, sig_out, "sustained high"
    )
    assert observed == [1] * 5

    # 15 low cycles after a high output do not fall; the 16th does.
    counter, sig_out, observed = await run_signal(
        dut, 0, THRESHOLD - 1, counter, sig_out, "short low glitch"
    )
    assert observed == [1] * (THRESHOLD - 1)
    counter, sig_out, observed = await run_signal(
        dut, 0, 1, counter, sig_out, "clean fall final"
    )
    assert observed == [0]

    # Counter reset on match: partial high run, one low cycle, then full threshold needed.
    counter, sig_out = await reset_model_and_dut(dut)
    counter, sig_out, observed = await run_signal(
        dut, 1, 10, counter, sig_out, "partial high"
    )
    assert observed == [0] * 10
    counter, sig_out, observed = await run_signal(
        dut, 0, 1, counter, sig_out, "match reset"
    )
    assert observed == [0]
    counter, sig_out, observed = await run_signal(
        dut, 1, THRESHOLD - 1, counter, sig_out, "second short high"
    )
    assert observed == [0] * (THRESHOLD - 1)
    counter, sig_out, observed = await run_signal(
        dut, 1, 1, counter, sig_out, "second high accept"
    )
    assert observed == [1]

    # Back-to-back accepted transitions.
    counter, sig_out, observed = await run_signal(
        dut, 0, THRESHOLD, counter, sig_out, "back to low"
    )
    assert observed[:-1] == [1] * (THRESHOLD - 1)
    assert observed[-1] == 0

    # Reset clears a pending count and output.
    counter, sig_out = await reset_model_and_dut(dut)
    counter, sig_out, _ = await run_signal(dut, 1, 8, counter, sig_out, "pending high")
    counter, sig_out = await apply_cycle(dut, 1, 1, counter, sig_out, "mid-count reset")
    assert sig_out == 0
    counter, sig_out, observed = await run_signal(
        dut, 1, THRESHOLD - 1, counter, sig_out, "after reset short"
    )
    assert observed == [0] * (THRESHOLD - 1)

    counter, sig_out = await reset_model_and_dut(dut)
    for cycle in range(800):
        rst = 1 if cycle in (307, 308) or random.randrange(160) == 0 else 0
        sig_in = random.randrange(2)
        counter, sig_out = await apply_cycle(
            dut, rst, sig_in, counter, sig_out, f"random {cycle}"
        )
