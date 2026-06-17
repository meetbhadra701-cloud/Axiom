import random

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer


WIDTH = 8
MASK = (1 << WIDTH) - 1


def encode_ref(value):
    value &= MASK
    if value == 0:
        return 0, 0
    return value.bit_length() - 1, 1


def drive(dut, rst, en, value):
    dut.rst.value = rst
    dut.en.value = en
    getattr(dut, "in").value = value & MASK


async def sample_after_edge(dut):
    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")
    return int(dut.out.value), int(dut.valid.value)


async def apply_cycle(dut, expected_out, expected_valid, rst, en, value, label):
    drive(dut, rst, en, value)
    got_out, got_valid = await sample_after_edge(dut)

    if rst:
        expected_out, expected_valid = 0, 0
    elif en:
        expected_out, expected_valid = encode_ref(value)

    assert got_out == expected_out, (
        f"{label}: in={value:#04x} rst={rst} en={en} got out={got_out}, "
        f"expected {expected_out}"
    )
    assert got_valid == expected_valid, (
        f"{label}: in={value:#04x} rst={rst} en={en} got valid={got_valid}, "
        f"expected {expected_valid}"
    )
    return expected_out, expected_valid


@cocotb.test()
async def test_prio_enc_spec_behavior(dut):
    """Verify registered highest-index priority encoder behavior."""

    random.seed(0x5010E)
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())

    drive(dut, rst=0, en=0, value=0)
    expected_out, expected_valid = 0, 0

    expected_out, expected_valid = await apply_cycle(
        dut, expected_out, expected_valid, rst=1, en=0, value=0xFF,
        label="initial reset"
    )
    expected_out, expected_valid = await apply_cycle(
        dut, expected_out, expected_valid, rst=1, en=1, value=0x80,
        label="reset priority over enable"
    )

    directed = [
        (0x00, 0, 0, "zero input"),
        (0x01, 0, 1, "single bit 0"),
        (0x08, 3, 1, "single bit 3"),
        (0x80, 7, 1, "single bit 7"),
        (0xA4, 7, 1, "highest wins"),
        (0x7E, 6, 1, "middle multi-bit"),
        (0xFF, 7, 1, "all ones"),
    ]
    for value, out, valid, label in directed:
        assert encode_ref(value) == (out, valid)
        expected_out, expected_valid = await apply_cycle(
            dut, expected_out, expected_valid, rst=0, en=1, value=value, label=label
        )

    held_out, held_valid = expected_out, expected_valid
    expected_out, expected_valid = await apply_cycle(
        dut, expected_out, expected_valid, rst=0, en=0, value=0x00,
        label="hold ignores zero"
    )
    assert (expected_out, expected_valid) == (held_out, held_valid)
    expected_out, expected_valid = await apply_cycle(
        dut, expected_out, expected_valid, rst=0, en=0, value=0x80,
        label="hold ignores new high bit"
    )
    assert (expected_out, expected_valid) == (held_out, held_valid)

    for bit in range(WIDTH):
        value = 1 << bit
        expected_out, expected_valid = await apply_cycle(
            dut, expected_out, expected_valid, rst=0, en=1, value=value,
            label=f"single-bit sweep {bit}"
        )
        assert (expected_out, expected_valid) == (bit, 1)

    for value in range(256):
        expected_out, expected_valid = await apply_cycle(
            dut, expected_out, expected_valid, rst=0, en=1, value=value,
            label=f"exhaustive {value:#04x}"
        )
        assert (expected_out, expected_valid) == encode_ref(value)

    for cycle in range(500):
        rst = 1 if cycle in (207, 208) or random.randrange(150) == 0 else 0
        en = random.randrange(2)
        value = random.randrange(256)
        expected_out, expected_valid = await apply_cycle(
            dut, expected_out, expected_valid, rst=rst, en=en, value=value,
            label=f"random cycle {cycle}"
        )
