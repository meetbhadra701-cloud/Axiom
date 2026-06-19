import random

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer


DATA_W = 16
COEF_W = 16
FRAC_W = 14
DATA_MASK = (1 << DATA_W) - 1
COEF_MASK = (1 << COEF_W) - 1


def to_signed(value, width):
    value &= (1 << width) - 1
    sign = 1 << (width - 1)
    return value - (1 << width) if value & sign else value


def data_s(value):
    return to_signed(value, DATA_W)


def coef_s(value):
    return to_signed(value, COEF_W)


def trunc_data_from_acc(acc):
    return data_s(acc >> FRAC_W)


class BiquadModel:
    def __init__(self):
        self.x1 = 0
        self.x2 = 0
        self.y1 = 0
        self.y2 = 0
        self.y_out = 0
        self.y_valid = 0

    def reset(self):
        self.x1 = self.x2 = self.y1 = self.y2 = 0
        self.y_out = 0
        self.y_valid = 0

    def step(self, rst, en, x_in, coeffs):
        x_in = data_s(x_in)
        b0, b1, b2, a1, a2 = [coef_s(c) for c in coeffs]

        if rst:
            self.reset()
        elif en:
            acc = (
                b0 * x_in
                + b1 * self.x1
                + b2 * self.x2
                - a1 * self.y1
                - a2 * self.y2
            )
            y = trunc_data_from_acc(acc)
            self.x2, self.x1 = self.x1, x_in
            self.y2, self.y1 = self.y1, y
            self.y_out = y
            self.y_valid = 1
        else:
            self.y_valid = 0

        return self.y_out, self.y_valid


def drive(dut, rst, en, x_in, coeffs):
    dut.rst.value = rst
    dut.en.value = en
    dut.x_in.value = data_s(x_in)
    dut.b0.value = coef_s(coeffs[0])
    dut.b1.value = coef_s(coeffs[1])
    dut.b2.value = coef_s(coeffs[2])
    dut.a1.value = coef_s(coeffs[3])
    dut.a2.value = coef_s(coeffs[4])


async def sample_after_edge(dut):
    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")
    return data_s(int(dut.y_out.value)), int(dut.y_valid.value)


async def apply_cycle(dut, model, rst, en, x_in, coeffs, label):
    drive(dut, rst, en, x_in, coeffs)
    got_y, got_valid = await sample_after_edge(dut)
    exp_y, exp_valid = model.step(rst, en, x_in, coeffs)

    assert got_y == exp_y, (
        f"{label}: got y_out={got_y}, expected {exp_y}; "
        f"rst={rst} en={en} x={data_s(x_in)} coeffs={[coef_s(c) for c in coeffs]}"
    )
    assert got_valid == exp_valid, (
        f"{label}: got y_valid={got_valid}, expected {exp_valid}"
    )
    return got_y, got_valid


async def reset_filter(dut, model, coeffs=(0, 0, 0, 0, 0)):
    return await apply_cycle(dut, model, rst=1, en=0, x_in=123, coeffs=coeffs, label="reset")


async def run_sequence(dut, coeffs, xs, label):
    model = BiquadModel()
    await reset_filter(dut, model, coeffs)
    ys = []
    for idx, x in enumerate(xs):
        y, valid = await apply_cycle(
            dut, model, rst=0, en=1, x_in=x, coeffs=coeffs, label=f"{label} sample {idx}"
        )
        assert valid == 1
        ys.append(y)
    return ys


@cocotb.test()
async def test_iir_biquad_spec_behavior(dut):
    """Verify signed fixed-point Direct Form I biquad behavior."""

    random.seed(0xB102AD)
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())

    zero = (0, 0, 0, 0, 0)
    model = BiquadModel()
    drive(dut, rst=0, en=0, x_in=0, coeffs=zero)

    await reset_filter(dut, model, zero)
    await apply_cycle(
        dut, model, rst=1, en=1, x_in=-32768, coeffs=(16384, 1, -1, 2, -2),
        label="reset priority"
    )

    identity = (1 << FRAC_W, 0, 0, 0, 0)
    ys = await run_sequence(dut, identity, [100, -100, 32767, -32768, 0, 1234], "identity")
    assert ys == [100, -100, 32767, -32768, 0, 1234]

    half_gain = (1 << (FRAC_W - 1), 0, 0, 0, 0)
    ys = await run_sequence(dut, half_gain, [1000, 1001, -1000, -1001], "half gain")
    assert ys == [500, 500, -500, -501]

    # y_valid drops on idle cycles, while y_out and internal delays hold.
    model = BiquadModel()
    await reset_filter(dut, model, identity)
    await apply_cycle(dut, model, 0, 1, 321, identity, "pre-hold active")
    held_y = data_s(int(dut.y_out.value))
    for idx, x in enumerate([999, -999, 111]):
        y, valid = await apply_cycle(dut, model, 0, 0, x, identity, f"hold {idx}")
        assert y == held_y
        assert valid == 0
    y, valid = await apply_cycle(dut, model, 0, 1, -222, identity, "post-hold active")
    assert (y, valid) == (-222, 1)

    dc_blocker = (16384, -32768, 16384, -31130, 14746)
    impulse = [12000] + [0] * 49
    ys = await run_sequence(dut, dc_blocker, impulse, "dc blocker impulse")
    ref_model = BiquadModel()
    ref_ys = [ref_model.step(0, 1, x, dc_blocker)[0] for x in impulse]
    assert ys == ref_ys

    # Stress expression width with large products and feedback terms.
    stress_coeffs = (32767, 32767, -32768, -32768, 32767)
    stress_xs = [32767, -32768, 30000, -30000, 12345, -23456, 11111, -11111]
    ys = await run_sequence(dut, stress_coeffs, stress_xs, "large accumulator stress")
    ref_model = BiquadModel()
    assert ys == [ref_model.step(0, 1, x, stress_coeffs)[0] for x in stress_xs]

    stable_coeff_sets = [
        (8192, 4096, 2048, -4096, 1024),
        (4096, -2048, 1024, 2048, -512),
        (12000, -6000, 3000, -5000, 2000),
    ]
    for case in range(60):
        coeffs = random.choice(stable_coeff_sets)
        xs = [random.randrange(-20000, 20001) for _ in range(random.randrange(1, 24))]
        ys = await run_sequence(dut, coeffs, xs, f"random sequence {case}")
        ref_model = BiquadModel()
        assert ys == [ref_model.step(0, 1, x, coeffs)[0] for x in xs]

    model = BiquadModel()
    await reset_filter(dut, model, dc_blocker)
    for cycle in range(300):
        rst = 1 if cycle in (133, 134) or random.randrange(180) == 0 else 0
        en = random.randrange(2)
        x = random.randrange(-16000, 16001)
        coeffs = random.choice(stable_coeff_sets)
        await apply_cycle(dut, model, rst, en, x, coeffs, f"random control {cycle}")
