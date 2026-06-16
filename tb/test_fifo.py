from collections import deque
import random

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer


WIDTH = 8
DEPTH = 16
MASK = (1 << WIDTH) - 1


async def sample_after_edge(dut):
    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")
    return dut.dout.value, int(dut.full.value), int(dut.empty.value)


def expected_flags(model):
    return int(len(model) == DEPTH), int(len(model) == 0)


def expected_dout(model):
    return model[0] if model else None


def drive(dut, rst, wr_en, rd_en, din):
    dut.rst.value = rst
    dut.wr_en.value = wr_en
    dut.rd_en.value = rd_en
    dut.din.value = din & MASK


async def apply_cycle(dut, rst, wr_en, rd_en, din, model, label):
    pre_full, pre_empty = expected_flags(model)
    can_write = bool(wr_en and not pre_full)
    can_read = bool(rd_en and not pre_empty)

    next_model = deque(model, maxlen=DEPTH)
    if rst:
        next_model.clear()
    else:
        if can_read:
            next_model.popleft()
        if can_write:
            next_model.append(din & MASK)

    drive(dut, rst, wr_en, rd_en, din)
    got_dout_value, got_full, got_empty = await sample_after_edge(dut)

    want_full, want_empty = expected_flags(next_model)
    assert got_full == want_full, (
        f"{label}: full got {got_full} expected {want_full}; "
        f"pre={list(model)} next={list(next_model)}"
    )
    assert got_empty == want_empty, (
        f"{label}: empty got {got_empty} expected {want_empty}; "
        f"pre={list(model)} next={list(next_model)}"
    )

    want_dout = expected_dout(next_model)
    if want_dout is not None:
        got_dout = int(got_dout_value) & MASK
        assert got_dout == want_dout, (
            f"{label}: dout got {got_dout:#04x} expected {want_dout:#04x}; "
            f"pre={list(model)} next={list(next_model)}"
        )

    return next_model


@cocotb.test()
async def test_fifo_spec_behavior(dut):
    """Verify synchronous FIFO behavior with a Python queue model."""

    random.seed(0xF1F0)
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())

    drive(dut, rst=0, wr_en=0, rd_en=0, din=0)
    model = deque(maxlen=DEPTH)

    model = await apply_cycle(dut, 1, 0, 0, 0xAA, model, "initial reset")
    model = await apply_cycle(dut, 1, 1, 1, 0x55, model, "reset priority")

    # Empty read is ignored.
    model = await apply_cycle(dut, 0, 0, 1, 0x00, model, "read while empty")

    # Fill FIFO and check transparent read tracks queue head.
    for value in range(DEPTH):
        model = await apply_cycle(dut, 0, 1, 0, value, model, f"fill {value}")

    assert len(model) == DEPTH

    # Write while full is ignored.
    before = list(model)
    model = await apply_cycle(dut, 0, 1, 0, 0xFE, model, "write while full")
    assert list(model) == before

    # Simultaneous read/write while full: read succeeds, write ignored because full was high.
    model = await apply_cycle(dut, 0, 1, 1, 0xA0, model, "simul while full")
    assert len(model) == DEPTH - 1

    # Simultaneous read/write when neither full nor empty: count unchanged and order preserved.
    before_len = len(model)
    for cycle in range(20):
        din = 0x80 + cycle
        model = await apply_cycle(dut, 0, 1, 1, din, model, f"simul normal {cycle}")
        assert len(model) == before_len

    # Drain to empty and verify ordering.
    while model:
        model = await apply_cycle(dut, 0, 0, 1, 0x00, model, f"drain {len(model)}")

    # Wrap pointers through multiple fill/drain rounds.
    for round_idx in range(3):
        for step in range(DEPTH):
            value = (round_idx * 37 + step * 11) & MASK
            model = await apply_cycle(dut, 0, 1, 0, value, model, f"wrap fill {round_idx}.{step}")
        for step in range(DEPTH):
            model = await apply_cycle(dut, 0, 0, 1, 0, model, f"wrap drain {round_idx}.{step}")

    # Randomized stress with reset, ignored ops, and simultaneous valid ops.
    for cycle in range(500):
        rst = 1 if cycle in (101, 102) or random.randrange(120) == 0 else 0
        wr_en = random.randrange(2)
        rd_en = random.randrange(2)
        din = random.randrange(256)
        model = await apply_cycle(dut, rst, wr_en, rd_en, din, model, f"random {cycle}")
