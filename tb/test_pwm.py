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
    return int(dut.pwm_out.value)


def drive(dut, rst, en, duty):
    dut.rst.value = rst
    dut.en.value = en
    dut.duty.value = duty & MASK


async def apply_cycle(dut, rst, en, duty, counter, expected_out, label):
    if rst:
        expected_out = 0
        next_counter = 0
    elif en:
        expected_out = 1 if counter < duty else 0
        next_counter = (counter + 1) & MASK
    else:
        next_counter = counter

    drive(dut, rst, en, duty)
    got = await sample_after_edge(dut)
    assert got == expected_out, (
        f"{label}: rst={rst} en={en} duty={duty} counter_before={counter} "
        f"got pwm_out={got} expected {expected_out}"
    )
    return next_counter, expected_out


async def reset_model_and_dut(dut):
    drive(dut, rst=1, en=0, duty=0)
    got = await sample_after_edge(dut)
    assert got == 0, f"reset got pwm_out={got}, expected 0"
    return 0, 0


async def enabled_period(dut, duty, counter, expected_out, label):
    observed = []
    for cycle in range(PERIOD):
        counter, expected_out = await apply_cycle(
            dut, 0, 1, duty, counter, expected_out, f"{label} cycle {cycle}"
        )
        observed.append(expected_out)
    return counter, expected_out, observed


@cocotb.test()
async def test_pwm_spec_behavior(dut):
    """Verify PWM reset, hold, pre-increment compare, and period high counts."""

    random.seed(0x09A1)
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())

    drive(dut, rst=0, en=0, duty=0)
    counter = 0
    expected_out = 0

    counter, expected_out = await reset_model_and_dut(dut)
    counter, expected_out = await apply_cycle(
        dut, 1, 1, 255, counter, expected_out, "reset priority"
    )

    for cycle, duty in enumerate([1, 128, 255, 7]):
        counter, expected_out = await apply_cycle(
            dut, 0, 0, duty, counter, expected_out, f"hold {cycle}"
        )

    counter, expected_out = await reset_model_and_dut(dut)
    counter, expected_out, observed = await enabled_period(
        dut, 0, counter, expected_out, "duty zero"
    )
    assert sum(observed) == 0
    assert counter == 0

    counter, expected_out = await reset_model_and_dut(dut)
    counter, expected_out, observed = await enabled_period(
        dut, 255, counter, expected_out, "duty full-scale minus one"
    )
    assert sum(observed) == 255
    assert observed[:255] == [1] * 255
    assert observed[255] == 0
    assert counter == 0

    counter, expected_out = await reset_model_and_dut(dut)
    counter, expected_out, observed = await enabled_period(
        dut, 128, counter, expected_out, "duty half"
    )
    assert sum(observed) == 128
    assert observed[:128] == [1] * 128
    assert observed[128:] == [0] * 128
    assert counter == 0

    for duty in [1, 2, 3, 17, 64, 127, 129, 200, 254]:
        counter, expected_out = await reset_model_and_dut(dut)
        counter, expected_out, observed = await enabled_period(
            dut, duty, counter, expected_out, f"arbitrary duty {duty}"
        )
        assert sum(observed) == duty, (
            f"duty {duty}: got {sum(observed)} high cycles expected {duty}"
        )
        assert counter == 0

    counter, expected_out = await reset_model_and_dut(dut)
    for cycle in range(400):
        rst = 1 if cycle in (101, 102) or random.randrange(80) == 0 else 0
        en = random.randrange(2)
        duty = random.randrange(PERIOD)
        counter, expected_out = await apply_cycle(
            dut, rst, en, duty, counter, expected_out, f"random {cycle}"
        )
