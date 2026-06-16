import math

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer


ADDR_WIDTH = 8
DATA_WIDTH = 8
PHASES = 1 << ADDR_WIDTH
DEPTH = 1 << (ADDR_WIDTH - 2)
DATA_MASK = (1 << DATA_WIDTH) - 1
MAX_POS = (1 << (DATA_WIDTH - 1)) - 1


def from_bits(bits, width):
    sign = 1 << (width - 1)
    return (bits ^ sign) - sign


def lut_value(index):
    angle = (index + 0.5) * math.pi / (2 * DEPTH)
    return int(math.floor(MAX_POS * math.sin(angle) + 0.5))


LUT = [lut_value(index) for index in range(DEPTH)]


def expected_sine(phase):
    quad = (phase >> (ADDR_WIDTH - 2)) & 0x3
    idx = phase & (DEPTH - 1)
    rom_idx = (~idx) & (DEPTH - 1) if quad & 1 else idx
    raw = LUT[rom_idx]
    return -raw if quad & 2 else raw


async def sample_after_edge(dut):
    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")
    return from_bits(int(dut.sin_out.value) & DATA_MASK, DATA_WIDTH)


@cocotb.test()
async def test_sine_lut_spec_behavior(dut):
    """Verify default sine LUT against the spec formula and quadrant symmetry."""

    assert LUT[0] == 2
    assert LUT[-1] == 127

    dut.phase_in.value = 0
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")

    got = await sample_after_edge(dut)
    assert got == 2, f"phase 0 anchor got {got}, expected 2"

    # Registered output: changing phase_in between clocks must not change sin_out
    # until the next rising edge.
    dut.phase_in.value = 64
    await Timer(1, unit="ns")
    held = from_bits(int(dut.sin_out.value) & DATA_MASK, DATA_WIDTH)
    assert held == 2, f"sin_out changed before the next clock: got {held}, expected 2"
    got = await sample_after_edge(dut)
    assert got == 127, f"phase 64 anchor got {got}, expected 127"

    anchors = {0: 2, 64: 127, 128: -2, 192: -127}
    for phase, expected in anchors.items():
        dut.phase_in.value = phase
        got = await sample_after_edge(dut)
        assert got == expected, f"phase {phase} anchor got {got}, expected {expected}"

    observed = []
    for phase in range(PHASES):
        dut.phase_in.value = phase
        got = await sample_after_edge(dut)
        expected = expected_sine(phase)
        assert got == expected, f"phase {phase}: got {got}, expected {expected}"
        observed.append(got)

    assert min(observed) == -127
    assert max(observed) == 127
    assert -128 not in observed
    assert sum(observed) == 0

    q0 = observed[0:64]
    q1 = observed[64:128]
    q2 = observed[128:192]
    q3 = observed[192:256]

    assert q0 == LUT
    assert q1 == list(reversed(LUT))
    assert q2 == [-value for value in LUT]
    assert q3 == [-value for value in reversed(LUT)]

    assert all(left <= right for left, right in zip(q0, q0[1:]))
    assert all(left >= right for left, right in zip(q1, q1[1:]))
    assert all(left >= right for left, right in zip(q2, q2[1:]))
    assert all(left <= right for left, right in zip(q3, q3[1:]))
