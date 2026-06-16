import random

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer


N_TAPS = 4
DATA_WIDTH = 8
OUT_WIDTH = 32
COEFFS = [2, 4, 2, 1]
OUT_MASK = (1 << OUT_WIDTH) - 1


def to_bits(value, width):
    return value & ((1 << width) - 1)


def from_bits(bits, width):
    sign = 1 << (width - 1)
    return (bits ^ sign) - sign


def wrap_out(value):
    return from_bits(value & OUT_MASK, OUT_WIDTH)


def fir_sum(delay):
    return wrap_out(sum(sample * coef for sample, coef in zip(delay, COEFFS)))


async def sample_after_edge(dut):
    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")
    return from_bits(int(dut.y.value) & OUT_MASK, OUT_WIDTH)


def drive(dut, rst, en, x):
    dut.rst.value = rst
    dut.en.value = en
    dut.x.value = to_bits(x, DATA_WIDTH)


async def apply_cycle(dut, rst, en, x, delay, expected_y, label):
    # Spec says y is computed from the registered delay line; the new x shifts in
    # on the same edge and is visible to the next enabled output sample.
    if rst:
        expected = 0
    elif en:
        expected = fir_sum(delay)
    else:
        expected = expected_y

    drive(dut, rst, en, x)
    got = await sample_after_edge(dut)
    assert got == expected, (
        f"{label}: rst={rst} en={en} x={x} got y={got} expected {expected} "
        f"delay_before={delay}"
    )

    if rst:
        return [0] * N_TAPS, 0
    if en:
        return [x] + delay[:-1], expected
    return delay, expected


@cocotb.test()
async def test_fir_spec_behavior(dut):
    """Verify FIR behavior against the spec-defined direct-form model."""

    random.seed(0xF112)
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())

    drive(dut, rst=0, en=0, x=0)
    delay = [0] * N_TAPS
    expected_y = 0

    delay, expected_y = await apply_cycle(dut, 1, 0, 99, delay, expected_y, "initial reset")
    delay, expected_y = await apply_cycle(dut, 1, 1, -99, delay, expected_y, "reset priority")

    # Hold keeps both delay line and registered output stable.
    for cycle, x in enumerate([7, -8, 127]):
        delay, expected_y = await apply_cycle(
            dut, 0, 0, x, delay, expected_y, f"hold after reset {cycle}"
        )

    # Impulse response should reveal coefficient order: 0, 2, 4, 2, 1, 0.
    impulse = [1, 0, 0, 0, 0, 0]
    expected_response = [0, 2, 4, 2, 1, 0]
    observed = []
    for cycle, x in enumerate(impulse):
        delay_before = list(delay)
        delay, expected_y = await apply_cycle(
            dut, 0, 1, x, delay, expected_y, f"impulse {cycle}"
        )
        observed.append(fir_sum(delay_before))
    assert observed == expected_response, (
        f"internal golden impulse response mismatch: {observed} expected {expected_response}"
    )

    # Signed samples and mixed signs.
    for cycle, x in enumerate([-3, 5, -7, 11, 0, 0, 0, 0]):
        delay, expected_y = await apply_cycle(
            dut, 0, 1, x, delay, expected_y, f"signed sequence {cycle}"
        )

    # Randomized enable toggles and signed samples.
    for cycle in range(300):
        rst = 1 if cycle in (71, 72) or random.randrange(100) == 0 else 0
        en = random.randrange(2)
        x = random.randrange(-(1 << (DATA_WIDTH - 1)), 1 << (DATA_WIDTH - 1))
        delay, expected_y = await apply_cycle(
            dut, rst, en, x, delay, expected_y, f"random {cycle}"
        )

    # Default widths cannot overflow OUT_WIDTH: 4 * 127 * 127 is far below 32-bit range.
    for cycle, x in enumerate([127, 127, 127, 127, -128, -128, -128, -128]):
        delay, expected_y = await apply_cycle(
            dut, 0, 1, x, delay, expected_y, f"default range edge {cycle}"
        )
