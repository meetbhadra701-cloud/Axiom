import os
import random

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer


WIDTH = 8
MASK = (1 << WIDTH) - 1
DEPTH = int(os.getenv("PIPE_DELAY_DEPTH", "4"))


def update_model(stages, rst, en, d_in):
    if rst:
        return [0 for _ in stages]
    if en:
        return [d_in & MASK] + stages[:-1]
    return list(stages)


def drive(dut, rst, en, d_in):
    dut.rst.value = rst
    dut.en.value = en
    dut.d_in.value = d_in & MASK


async def check_output(dut, stages, label):
    await Timer(1, unit="ns")
    got = int(dut.d_out.value) & MASK
    expected = stages[-1] & MASK
    assert got == expected, (
        f"{label}: got d_out={got:#04x}, expected {expected:#04x}, "
        f"model stages={[hex(v) for v in stages]}"
    )


async def apply_cycle(dut, stages, rst, en, d_in, label):
    drive(dut, rst, en, d_in)
    await RisingEdge(dut.clk)
    stages = update_model(stages, rst, en, d_in)
    await check_output(dut, stages, label)
    return stages


@cocotb.test()
async def test_pipe_delay_spec_behavior(dut):
    """Verify enabled-cycle latency, reset, and hold behavior."""

    random.seed(0xD314A7 + DEPTH)
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())

    stages = [0 for _ in range(DEPTH)]
    drive(dut, rst=0, en=0, d_in=0)

    stages = await apply_cycle(dut, stages, rst=1, en=0, d_in=0xFF, label="initial reset")
    stages = await apply_cycle(
        dut, stages, rst=1, en=1, d_in=0xA5, label="reset priority over enable"
    )

    held = list(stages)
    for cycle, value in enumerate([0x11, 0x22, 0x33]):
        stages = await apply_cycle(
            dut, stages, rst=0, en=0, d_in=value, label=f"hold cycle {cycle}"
        )
        assert stages == held

    if DEPTH == 4:
        stages = await apply_cycle(
            dut, stages, rst=1, en=0, d_in=0, label="reset before single pulse"
        )
        pulse_inputs = [0xAB, 0x00, 0x00, 0x00, 0x00, 0x00]
        pulse_outputs = []
        for cycle, value in enumerate(pulse_inputs):
            stages = await apply_cycle(
                dut, stages, rst=0, en=1, d_in=value, label=f"single pulse {cycle}"
            )
            pulse_outputs.append(int(dut.d_out.value) & MASK)
        assert pulse_outputs == [0x00, 0x00, 0x00, 0xAB, 0x00, 0x00], (
            f"single-cycle pulse output trace got {[hex(v) for v in pulse_outputs]}"
        )

        stages = await apply_cycle(
            dut, stages, rst=1, en=0, d_in=0, label="reset before sequence"
        )
        sequence = [1, 2, 3, 4, 5, 0, 0, 0, 0]
        observed = []
        for cycle, value in enumerate(sequence):
            stages = await apply_cycle(
                dut, stages, rst=0, en=1, d_in=value, label=f"sequence {cycle}"
            )
            observed.append(int(dut.d_out.value) & MASK)
        assert observed == [0, 0, 0, 1, 2, 3, 4, 5, 0], (
            f"sequence output trace got {observed}"
        )

        stages = await apply_cycle(
            dut, stages, rst=1, en=0, d_in=0, label="reset before enable gating"
        )
        gated_steps = [
            (1, 0x10),
            (1, 0x20),
            (0, 0xEE),
            (0, 0xDD),
            (1, 0x30),
            (1, 0x40),
            (1, 0x50),
            (1, 0x60),
        ]
        observed = []
        for cycle, (en, value) in enumerate(gated_steps):
            before = list(stages)
            stages = await apply_cycle(
                dut, stages, rst=0, en=en, d_in=value, label=f"enable gated {cycle}"
            )
            if not en:
                assert stages == before
            observed.append(int(dut.d_out.value) & MASK)
        assert observed == [0, 0, 0, 0, 0, 0x10, 0x20, 0x30], (
            f"enable-gated trace got {[hex(v) for v in observed]}"
        )

    if DEPTH == 1:
        stages = await apply_cycle(
            dut, stages, rst=1, en=0, d_in=0, label="reset before depth1"
        )
        for cycle, value in enumerate([0x12, 0x34, 0x56, 0x78]):
            stages = await apply_cycle(
                dut, stages, rst=0, en=1, d_in=value, label=f"depth1 value {cycle}"
            )
            assert int(dut.d_out.value) == value

    stages = await apply_cycle(dut, stages, rst=1, en=0, d_in=0, label="reset before random")
    for cycle in range(600):
        rst = 1 if cycle in (251, 252) or random.randrange(180) == 0 else 0
        en = random.randrange(2)
        d_in = random.randrange(256)
        before = list(stages)
        stages = await apply_cycle(
            dut, stages, rst=rst, en=en, d_in=d_in, label=f"random cycle {cycle}"
        )
        if not rst and not en:
            assert stages == before
