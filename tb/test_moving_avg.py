import os
import random
from collections import deque

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer


DATA_W = int(os.getenv("MOVING_AVG_DATA_W", "8"))
LOG2N = int(os.getenv("MOVING_AVG_LOG2N", "3"))
N = 1 << LOG2N
MASK = (1 << DATA_W) - 1


class MovingAverageModel:
    def __init__(self):
        self.window = deque([0] * N, maxlen=N)
        self.acc = 0
        self.avg_out = 0
        self.avg_valid = 0

    def reset(self):
        self.window = deque([0] * N, maxlen=N)
        self.acc = 0
        self.avg_out = 0
        self.avg_valid = 0

    def step(self, rst, en, sample):
        sample &= MASK
        if rst:
            self.reset()
        elif en:
            evicted = self.window[0]
            self.acc = self.acc + sample - evicted
            self.window.append(sample)
            self.avg_out = (self.acc >> LOG2N) & MASK
            self.avg_valid = 1
        else:
            self.avg_valid = 0
        return self.avg_out, self.avg_valid


def drive(dut, rst, en, sample):
    dut.rst.value = rst
    dut.en.value = en
    dut.x_in.value = sample & MASK


async def sample_after_edge(dut):
    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")
    return int(dut.avg_out.value) & MASK, int(dut.avg_valid.value)


async def apply_cycle(dut, model, rst, en, sample, label):
    drive(dut, rst, en, sample)
    got_avg, got_valid = await sample_after_edge(dut)
    exp_avg, exp_valid = model.step(rst, en, sample)

    assert got_avg == exp_avg, (
        f"{label}: got avg_out={got_avg}, expected {exp_avg}; "
        f"rst={rst} en={en} sample={sample & MASK} acc={model.acc} "
        f"window={list(model.window)}"
    )
    assert got_valid == exp_valid, (
        f"{label}: got avg_valid={got_valid}, expected {exp_valid}"
    )
    return got_avg, got_valid


async def reset_filter(dut, model):
    return await apply_cycle(dut, model, rst=1, en=0, sample=MASK, label="reset")


async def run_samples(dut, samples, label):
    model = MovingAverageModel()
    await reset_filter(dut, model)
    avgs = []
    for idx, sample in enumerate(samples):
        avg, valid = await apply_cycle(
            dut, model, rst=0, en=1, sample=sample, label=f"{label} sample {idx}"
        )
        assert valid == 1
        avgs.append(avg)
    return avgs


@cocotb.test()
async def test_moving_avg_spec_behavior(dut):
    """Verify sliding-window moving average against a queue model."""

    random.seed(0xA6A6E + N)
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())

    model = MovingAverageModel()
    drive(dut, rst=0, en=0, sample=0)
    await reset_filter(dut, model)

    await apply_cycle(dut, model, rst=1, en=1, sample=MASK, label="reset priority")

    # Hold: avg_valid drops, but avg_out/window/acc hold.
    await apply_cycle(dut, model, rst=0, en=1, sample=min(32, MASK), label="pre-hold")
    held_avg = int(dut.avg_out.value) & MASK
    held_acc = model.acc
    held_window = list(model.window)
    for idx, sample in enumerate([MASK, 0, MASK // 2]):
        avg, valid = await apply_cycle(dut, model, rst=0, en=0, sample=sample, label=f"hold {idx}")
        assert avg == held_avg
        assert valid == 0
        assert model.acc == held_acc
        assert list(model.window) == held_window

    if DATA_W == 8 and LOG2N == 3:
        avgs = await run_samples(dut, [8] * 8, "constant 8")
        assert avgs[-1] == 8

        model = MovingAverageModel()
        await reset_filter(dut, model)
        for idx in range(8):
            await apply_cycle(dut, model, rst=0, en=1, sample=8, label=f"fill 8s {idx}")
        avg, valid = await apply_cycle(dut, model, rst=0, en=1, sample=16, label="push 16")
        assert (avg, valid) == (9, 1)

        avgs = await run_samples(dut, [0] * 8 + [255] * 8, "zero to max step")
        assert avgs[-8:] == [31, 63, 95, 127, 159, 191, 223, 255]

        avgs = await run_samples(dut, [255] * 16, "all max")
        assert avgs[7:] == [255] * 9

    if DATA_W == 8 and LOG2N == 2:
        avgs = await run_samples(dut, [4, 8, 12, 16, 20, 24], "n4 sequence")
        assert avgs == [1, 3, 6, 10, 14, 18]

    for case in range(40):
        samples = [random.randrange(MASK + 1) for _ in range(random.randrange(1, 40))]
        avgs = await run_samples(dut, samples, f"random sequence {case}")
        ref = MovingAverageModel()
        expected = [ref.step(0, 1, sample)[0] for sample in samples]
        assert avgs == expected

    model = MovingAverageModel()
    await reset_filter(dut, model)
    for cycle in range(400):
        rst = 1 if cycle in (177, 178) or random.randrange(180) == 0 else 0
        en = random.randrange(2)
        sample = random.randrange(MASK + 1)
        await apply_cycle(dut, model, rst, en, sample, f"random control {cycle}")
