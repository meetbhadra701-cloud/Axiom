import random

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer


WIDTH = 8
MASK = (1 << WIDTH) - 1


def update_model(expected, rst, load, en, serial_in, parallel_in):
    if rst:
        return 0
    if load:
        return parallel_in & MASK
    if en:
        return ((expected << 1) | (serial_in & 1)) & MASK
    return expected & MASK


def drive(dut, rst, load, en, serial_in, parallel_in):
    dut.rst.value = rst
    dut.load.value = load
    dut.en.value = en
    dut.serial_in.value = serial_in & 1
    dut.parallel_in.value = parallel_in & MASK


async def check_outputs(dut, expected, label):
    await Timer(1, unit="ns")
    got_parallel = int(dut.parallel_out.value) & MASK
    got_serial = int(dut.serial_out.value) & 1
    expected_serial = (expected >> (WIDTH - 1)) & 1

    assert got_parallel == expected, (
        f"{label}: parallel_out got {got_parallel:#04x}, expected {expected:#04x}"
    )
    assert got_serial == expected_serial, (
        f"{label}: serial_out got {got_serial}, expected MSB {expected_serial} "
        f"from sr={expected:#04x}"
    )


async def apply_cycle(dut, expected, rst, load, en, serial_in, parallel_in, label):
    drive(dut, rst, load, en, serial_in, parallel_in)
    await RisingEdge(dut.clk)
    expected = update_model(expected, rst, load, en, serial_in, parallel_in)
    await check_outputs(dut, expected, label)
    return expected


@cocotb.test()
async def test_shift_reg_spec_behavior(dut):
    """Verify reset/load/shift/hold behavior and combinational output taps."""

    random.seed(0x517A)
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())

    drive(dut, rst=0, load=0, en=0, serial_in=0, parallel_in=0)
    expected = 0

    expected = await apply_cycle(
        dut, expected, rst=1, load=0, en=0, serial_in=1, parallel_in=0xFF,
        label="initial reset"
    )
    expected = await apply_cycle(
        dut, expected, rst=1, load=1, en=1, serial_in=1, parallel_in=0xA5,
        label="reset priority over load and shift"
    )

    expected = await apply_cycle(
        dut, expected, rst=0, load=1, en=0, serial_in=0, parallel_in=0xA5,
        label="load A5"
    )
    assert int(dut.serial_out.value) == 1, "serial_out should expose MSB of loaded 0xA5"

    expected = await apply_cycle(
        dut, expected, rst=0, load=1, en=1, serial_in=1, parallel_in=0x3C,
        label="load priority over enabled shift"
    )
    assert expected == 0x3C

    held = expected
    expected = await apply_cycle(
        dut, expected, rst=0, load=0, en=0, serial_in=1, parallel_in=0x00,
        label="hold ignores serial input"
    )
    assert expected == held

    # PISO: serial_out is a combinational MSB tap before each enabled shift.
    expected = await apply_cycle(
        dut, expected, rst=0, load=1, en=0, serial_in=0, parallel_in=0xAB,
        label="load AB for PISO"
    )
    observed_bits = []
    for bit_index in range(WIDTH):
        await check_outputs(dut, expected, f"PISO pre-shift bit {bit_index}")
        observed_bits.append(int(dut.serial_out.value) & 1)
        expected = await apply_cycle(
            dut, expected, rst=0, load=0, en=1, serial_in=0, parallel_in=0,
            label=f"PISO shift {bit_index}"
        )
    assert observed_bits == [1, 0, 1, 0, 1, 0, 1, 1], (
        f"PISO sequence got {observed_bits}, expected MSB-first bits of 0xAB"
    )

    # SIPO: shifting MSB-first input bits into the LSB assembles 0xB4 after 8 cycles.
    expected = await apply_cycle(
        dut, expected, rst=1, load=0, en=0, serial_in=0, parallel_in=0,
        label="reset before SIPO"
    )
    for bit_index, bit in enumerate([1, 0, 1, 1, 0, 1, 0, 0]):
        expected = await apply_cycle(
            dut, expected, rst=0, load=0, en=1, serial_in=bit, parallel_in=0,
            label=f"SIPO shift bit {bit_index}"
        )
    assert expected == 0xB4
    await check_outputs(dut, 0xB4, "SIPO assembled word")

    expected = await apply_cycle(
        dut, expected, rst=0, load=1, en=0, serial_in=0, parallel_in=0xF0,
        label="load before mid-shift reset"
    )
    expected = await apply_cycle(
        dut, expected, rst=0, load=0, en=1, serial_in=1, parallel_in=0,
        label="shift before mid-shift reset"
    )
    expected = await apply_cycle(
        dut, expected, rst=1, load=0, en=1, serial_in=1, parallel_in=0xFF,
        label="mid-shift reset"
    )
    assert expected == 0

    for cycle in range(500):
        rst = 1 if cycle in (137, 138) or random.randrange(150) == 0 else 0
        load = random.randrange(2)
        en = random.randrange(2)
        serial_in = random.randrange(2)
        parallel_in = random.randrange(256)
        expected = await apply_cycle(
            dut, expected, rst, load, en, serial_in, parallel_in,
            label=f"random cycle {cycle}"
        )
