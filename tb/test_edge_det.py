import random

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer


def model_step(pipe0, pipe1, rst, sig_in):
    if rst:
        return 0, 0, 0, 0, 0
    rise = pipe0 & (1 - pipe1)
    fall = (1 - pipe0) & pipe1
    any_edge = pipe0 ^ pipe1
    return sig_in & 1, pipe0, rise, fall, any_edge


async def sample_after_edge(dut):
    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")
    return int(dut.rise.value), int(dut.fall.value), int(dut.any_edge.value)


def drive(dut, rst, sig_in):
    dut.rst.value = rst
    dut.sig_in.value = sig_in & 1


async def apply_cycle(dut, rst, sig_in, pipe0, pipe1, label):
    pipe0, pipe1, rise, fall, any_edge = model_step(pipe0, pipe1, rst, sig_in)
    drive(dut, rst, sig_in)
    got = await sample_after_edge(dut)
    expected = (rise, fall, any_edge)
    assert got == expected, (
        f"{label}: rst={rst} sig_in={sig_in} got rise/fall/any={got} "
        f"expected {expected} model_pipe=({pipe0},{pipe1})"
    )
    assert got[2] == (got[0] | got[1]), f"{label}: any_edge != rise|fall for {got}"
    return pipe0, pipe1


async def reset_model_and_dut(dut):
    drive(dut, rst=1, sig_in=0)
    got = await sample_after_edge(dut)
    assert got == (0, 0, 0), f"reset got {got}, expected all zero"
    return 0, 0


@cocotb.test()
async def test_edge_det_spec_behavior(dut):
    """Verify registered two-stage edge detector behavior."""

    random.seed(0xE9DE)
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())

    drive(dut, rst=0, sig_in=0)
    pipe0 = 0
    pipe1 = 0

    pipe0, pipe1 = await reset_model_and_dut(dut)
    pipe0, pipe1 = await apply_cycle(dut, 1, 1, pipe0, pipe1, "reset priority")

    # Sustained low produces no pulses.
    for cycle in range(4):
        pipe0, pipe1 = await apply_cycle(dut, 0, 0, pipe0, pipe1, f"low {cycle}")

    # 0 -> 1 transition: rise appears after the pipe pair contains 1,0.
    observed = []
    for cycle, sig in enumerate([1, 1, 1, 1]):
        pipe0, pipe1 = await apply_cycle(dut, 0, sig, pipe0, pipe1, f"rise {cycle}")
        observed.append((int(dut.rise.value), int(dut.fall.value), int(dut.any_edge.value)))
    assert observed == [(0, 0, 0), (1, 0, 1), (0, 0, 0), (0, 0, 0)]

    # 1 -> 0 transition.
    observed = []
    for cycle, sig in enumerate([0, 0, 0, 0]):
        pipe0, pipe1 = await apply_cycle(dut, 0, sig, pipe0, pipe1, f"fall {cycle}")
        observed.append((int(dut.rise.value), int(dut.fall.value), int(dut.any_edge.value)))
    assert observed == [(0, 0, 0), (0, 1, 1), (0, 0, 0), (0, 0, 0)]

    # 1-cycle pulse: rise then fall on consecutive output cycles.
    pipe0, pipe1 = await reset_model_and_dut(dut)
    observed = []
    for cycle, sig in enumerate([0, 1, 0, 0, 0]):
        pipe0, pipe1 = await apply_cycle(dut, 0, sig, pipe0, pipe1, f"glitch {cycle}")
        observed.append((int(dut.rise.value), int(dut.fall.value), int(dut.any_edge.value)))
    assert observed == [
        (0, 0, 0),
        (0, 0, 0),
        (1, 0, 1),
        (0, 1, 1),
        (0, 0, 0),
    ]

    # Reset clears an in-flight transition before it can appear.
    pipe0, pipe1 = await reset_model_and_dut(dut)
    pipe0, pipe1 = await apply_cycle(dut, 0, 1, pipe0, pipe1, "inflight capture")
    pipe0, pipe1 = await apply_cycle(dut, 1, 1, pipe0, pipe1, "inflight reset")
    pipe0, pipe1 = await apply_cycle(dut, 0, 1, pipe0, pipe1, "after reset high")
    pipe0, pipe1 = await apply_cycle(dut, 0, 1, pipe0, pipe1, "after reset rise")
    assert (int(dut.rise.value), int(dut.fall.value), int(dut.any_edge.value)) == (1, 0, 1)

    pipe0, pipe1 = await reset_model_and_dut(dut)
    for cycle in range(600):
        rst = 1 if cycle in (211, 212) or random.randrange(120) == 0 else 0
        sig_in = random.randrange(2)
        pipe0, pipe1 = await apply_cycle(dut, rst, sig_in, pipe0, pipe1, f"random {cycle}")
