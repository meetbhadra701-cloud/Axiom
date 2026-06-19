import random

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer


POLY_REFLECTED = 0x8C


def crc8_maxim_bytes(data, crc=0):
    crc &= 0xFF
    for byte in data:
        for _ in range(8):
            bit = byte & 1
            byte >>= 1
            crc = crc8_maxim_bit(crc, bit)
    return crc & 0xFF


def crc8_maxim_bit(crc, bit):
    feedback = (crc ^ (bit & 1)) & 1
    crc >>= 1
    if feedback:
        crc ^= POLY_REFLECTED
    return crc & 0xFF


def bits_lsb_first(data):
    for byte in data:
        for bit_index in range(8):
            yield (byte >> bit_index) & 1


def drive(dut, rst, en, bit):
    dut.rst.value = rst
    dut.en.value = en
    dut.bit_in.value = bit & 1


async def sample_after_edge(dut):
    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")
    return int(dut.crc.value) & 0xFF


async def apply_cycle(dut, expected, rst, en, bit, label):
    drive(dut, rst, en, bit)
    got = await sample_after_edge(dut)

    if rst:
        expected = 0
    elif en:
        expected = crc8_maxim_bit(expected, bit)

    assert got == expected, (
        f"{label}: rst={rst} en={en} bit={bit} got crc={got:#04x}, "
        f"expected {expected:#04x}"
    )
    return expected


async def reset_crc(dut):
    return await apply_cycle(dut, 0, rst=1, en=0, bit=1, label="reset")


async def feed_bits(dut, expected, bits, label):
    for bit_index, bit in enumerate(bits):
        expected = await apply_cycle(
            dut, expected, rst=0, en=1, bit=bit, label=f"{label} bit {bit_index}"
        )
    return expected


async def feed_bytes(dut, expected, data, label):
    return await feed_bits(dut, expected, bits_lsb_first(data), label)


@cocotb.test()
async def test_crc8_maxim_spec_behavior(dut):
    """Verify CRC-8/MAXIM reflected bit-serial recurrence."""

    random.seed(0xC8A11A5)
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())

    drive(dut, rst=0, en=0, bit=0)
    expected = await reset_crc(dut)

    expected = await apply_cycle(
        dut, expected, rst=1, en=1, bit=1, label="reset priority over enable"
    )
    assert expected == 0

    held = expected
    for cycle, bit in enumerate([1, 0, 1, 1]):
        expected = await apply_cycle(
            dut, expected, rst=0, en=0, bit=bit, label=f"hold cycle {cycle}"
        )
        assert expected == held

    expected = await reset_crc(dut)
    expected = await feed_bytes(dut, expected, [0x00], "zero byte")
    assert expected == 0x00

    expected = await reset_crc(dut)
    expected = await feed_bits(dut, expected, [1], "single leading one")
    assert expected == 0x8C

    expected = await reset_crc(dut)
    expected = await feed_bytes(dut, expected, [0x01], "byte 0x01")
    assert expected == 0x5E

    expected = await reset_crc(dut)
    expected = await feed_bytes(dut, expected, [0xFF], "byte 0xFF")
    assert expected == 0x35

    expected = await reset_crc(dut)
    check_data = b"123456789"
    expected = await feed_bytes(dut, expected, check_data, "check string")
    assert expected == 0xA1

    for case in range(50):
        data = bytes(random.randrange(256) for _ in range(random.randrange(1, 18)))
        expected = await reset_crc(dut)
        expected = await feed_bytes(dut, expected, data, f"random bytes {case}")
        assert expected == crc8_maxim_bytes(data), (
            f"random bytes {case}: data={data.hex()} got {expected:#04x}, "
            f"expected {crc8_maxim_bytes(data):#04x}"
        )

    expected = await reset_crc(dut)
    for cycle in range(400):
        rst = 1 if cycle in (173, 174) or random.randrange(160) == 0 else 0
        en = random.randrange(2)
        bit = random.randrange(2)
        expected = await apply_cycle(
            dut, expected, rst=rst, en=en, bit=bit, label=f"random bit cycle {cycle}"
        )
