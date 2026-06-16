import random

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer


A_WIDTH = 8
B_WIDTH = 8
ACC_WIDTH = 32
ACC_MODULUS = 1 << ACC_WIDTH


def to_bits(value, width):
    return value & ((1 << width) - 1)


def from_bits(bits, width):
    sign = 1 << (width - 1)
    return (bits ^ sign) - sign


def acc_bits(value):
    return to_bits(value, ACC_WIDTH)


async def sample_after_edge(dut):
    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")
    return int(dut.acc.value) & (ACC_MODULUS - 1)


def drive_inputs(dut, rst, clear, en, a, b):
    dut.rst.value = rst
    dut.clear.value = clear
    dut.en.value = en
    dut.a.value = to_bits(a, A_WIDTH)
    dut.b.value = to_bits(b, B_WIDTH)


async def apply_cycle(dut, rst, clear, en, a, b, expected, label):
    drive_inputs(dut, rst, clear, en, a, b)
    got = await sample_after_edge(dut)
    want = acc_bits(expected)
    assert got == want, (
        f"{label}: rst={rst} clear={clear} en={en} a={a} b={b} "
        f"got raw={got:#010x} signed={from_bits(got, ACC_WIDTH)} "
        f"expected raw={want:#010x} signed={from_bits(want, ACC_WIDTH)}"
    )


@cocotb.test()
async def test_mac_spec_behavior(dut):
    """Verify signed MAC behavior against an independent Python model."""

    random.seed(0xA710)
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())

    drive_inputs(dut, rst=0, clear=0, en=0, a=0, b=0)
    expected = 0

    await apply_cycle(dut, 1, 0, 0, 7, -3, expected, "initial reset")

    # Reset has priority over clear and enable.
    expected = 0
    await apply_cycle(dut, 1, 1, 1, 127, 127, expected, "reset priority")

    # Signed accumulation cases.
    for cycle, (a, b) in enumerate([(3, 4), (-5, 6), (-7, -8), (127, -128)]):
        expected = from_bits(acc_bits(expected + a * b), ACC_WIDTH)
        await apply_cycle(dut, 0, 0, 1, a, b, expected, f"signed accumulate {cycle}")

    # Hold ignores changing inputs when enable is low.
    for cycle, (a, b) in enumerate([(100, 100), (-128, 127), (1, -1)]):
        await apply_cycle(dut, 0, 0, 0, a, b, expected, f"hold {cycle}")

    # Clear has priority over enable.
    expected = 0
    await apply_cycle(dut, 0, 1, 1, 127, 127, expected, "clear priority")

    # Randomized reference-model run with resets, clears, holds, and signed inputs.
    for cycle in range(300):
        rst = 1 if cycle in (19, 20) or random.randrange(80) == 0 else 0
        clear = 1 if cycle in (77, 78) or random.randrange(64) == 0 else 0
        en = random.randrange(2)
        a = random.randrange(-(1 << (A_WIDTH - 1)), 1 << (A_WIDTH - 1))
        b = random.randrange(-(1 << (B_WIDTH - 1)), 1 << (B_WIDTH - 1))

        if rst:
            expected = 0
        elif clear:
            expected = 0
        elif en:
            expected = from_bits(acc_bits(expected + a * b), ACC_WIDTH)

        await apply_cycle(dut, rst, clear, en, a, b, expected, f"random {cycle}")

    # Drive enough positive products to prove two's-complement accumulator wrap.
    expected = 0
    await apply_cycle(dut, 0, 1, 0, 0, 0, expected, "wrap setup clear")

    product = 127 * 127
    wrap_seen = False
    for cycle in range(135000):
        previous = expected
        expected = from_bits(acc_bits(expected + product), ACC_WIDTH)
        if previous >= 0 and expected < 0:
            wrap_seen = True
        await apply_cycle(dut, 0, 0, 1, 127, 127, expected, f"wrap stress {cycle}")

    assert wrap_seen, "wrap stress did not cross signed positive to negative range"
