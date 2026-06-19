import random

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer


CLKS_PER_BIT = 4


def frame_bits(byte):
    return [0] + [(byte >> bit) & 1 for bit in range(8)] + [1]


def drive(dut, rst, en, data):
    dut.rst.value = rst
    dut.en.value = en
    dut.data.value = data & 0xFF


async def tick(dut):
    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")
    return int(dut.tx.value), int(dut.busy.value)


async def reset_uart(dut):
    drive(dut, rst=1, en=0, data=0x00)
    tx, busy = await tick(dut)
    assert (tx, busy) == (1, 0)
    drive(dut, rst=0, en=0, data=0x00)


async def start_byte(dut, byte):
    drive(dut, rst=0, en=1, data=byte)
    tx, busy = await tick(dut)
    assert (tx, busy) == (0, 1), f"start byte {byte:#04x}: got tx={tx} busy={busy}"
    drive(dut, rst=0, en=0, data=byte)
    return [tx], [busy]


async def capture_frame_after_start(dut, byte, label):
    tx_trace, busy_trace = await start_byte(dut, byte)
    for cycle in range(1, 10 * CLKS_PER_BIT + 1):
        tx, busy = await tick(dut)
        tx_trace.append(tx)
        busy_trace.append(busy)

    expected_bits = frame_bits(byte)
    sampled = [tx_trace[bit * CLKS_PER_BIT + CLKS_PER_BIT // 2] for bit in range(10)]
    assert sampled == expected_bits, (
        f"{label}: sampled bits {sampled}, expected {expected_bits}, trace={tx_trace}"
    )

    assert busy_trace[: 10 * CLKS_PER_BIT] == [1] * (10 * CLKS_PER_BIT), (
        f"{label}: busy should stay high through frame, got {busy_trace}"
    )
    assert busy_trace[10 * CLKS_PER_BIT] == 0, (
        f"{label}: busy should drop after 10 bit periods"
    )
    assert tx_trace[10 * CLKS_PER_BIT] == 1
    return tx_trace, busy_trace


async def run_frame_with_mid_busy_en(dut, byte, ignored_byte):
    tx_trace, busy_trace = await start_byte(dut, byte)
    for cycle in range(1, 10 * CLKS_PER_BIT + 1):
        en = 1 if cycle in (3, 11, 22) else 0
        drive(dut, rst=0, en=en, data=ignored_byte)
        tx, busy = await tick(dut)
        tx_trace.append(tx)
        busy_trace.append(busy)
    sampled = [tx_trace[bit * CLKS_PER_BIT + CLKS_PER_BIT // 2] for bit in range(10)]
    assert sampled == frame_bits(byte), (
        f"en while busy corrupted frame: got {sampled}, expected {frame_bits(byte)}"
    )
    assert busy_trace[10 * CLKS_PER_BIT] == 0


def uart_rx_sample(tx_trace, clks_per_bit):
    i = 0
    rx_bytes = []
    while i < len(tx_trace):
        if tx_trace[i] == 0:
            start_mid = i + clks_per_bit // 2
            if start_mid >= len(tx_trace) or tx_trace[start_mid] != 0:
                i += 1
                continue
            bits = []
            complete = True
            for bit_index in range(8):
                sample_at = start_mid + (bit_index + 1) * clks_per_bit
                if sample_at >= len(tx_trace):
                    complete = False
                    break
                bits.append(tx_trace[sample_at])
            stop_at = start_mid + 9 * clks_per_bit
            if complete and stop_at < len(tx_trace) and tx_trace[stop_at] == 1:
                rx_bytes.append(sum(bit << idx for idx, bit in enumerate(bits)))
                i = stop_at + clks_per_bit // 2
            else:
                i += 1
        else:
            i += 1
    return rx_bytes


@cocotb.test()
async def test_uart_tx_spec_behavior(dut):
    """Verify 8-N-1 UART transmit timing with CLKS_PER_BIT=4."""

    random.seed(0xA117)
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())

    await reset_uart(dut)

    for byte in (0x55, 0xAA, 0x00, 0xFF):
        await capture_frame_after_start(dut, byte, f"directed {byte:#04x}")
        await tick(dut)

    await reset_uart(dut)
    await run_frame_with_mid_busy_en(dut, 0xA5, 0x3C)

    await reset_uart(dut)
    tx_trace = []
    sent = []
    for byte in [random.randrange(256) for _ in range(20)]:
        sent.append(byte)
        frame_tx, _ = await capture_frame_after_start(dut, byte, f"random byte {byte:#04x}")
        tx_trace.extend(frame_tx[:-1])
        await tick(dut)
        tx_trace.append(int(dut.tx.value))
    decoded = uart_rx_sample(tx_trace, CLKS_PER_BIT)
    assert decoded == sent, f"decoded random stream {decoded}, expected {sent}"

    await reset_uart(dut)
    first_tx, first_busy = await start_byte(dut, 0x12)
    # Advance to the final stop-bit cycle. Assert en for the next byte on the edge where
    # the spec says IDLE is re-entered and a back-to-back byte may begin.
    for cycle in range(1, 10 * CLKS_PER_BIT):
        drive(dut, rst=0, en=0, data=0x34)
        tx, busy = await tick(dut)
        first_tx.append(tx)
        first_busy.append(busy)

    drive(dut, rst=0, en=1, data=0x34)
    tx, busy = await tick(dut)
    assert (tx, busy) == (0, 1), (
        "back-to-back en on frame-completion edge should start next byte immediately; "
        f"got tx={tx} busy={busy}"
    )
