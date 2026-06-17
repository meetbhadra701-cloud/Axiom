import itertools
import random

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer


PORTS = 4
MASK = (1 << PORTS) - 1


def choose_winner(req, ptr):
    req &= MASK
    for idx in range(ptr, PORTS):
        if req & (1 << idx):
            return idx
    for idx in range(PORTS):
        if req & (1 << idx):
            return idx
    return None


def model_step(ptr, grant_idx, rst, req):
    if rst:
        return 0, 0, 0, 0

    winner = choose_winner(req, ptr)
    if winner is None:
        return ptr, 0, grant_idx, 0

    return (winner + 1) % PORTS, 1 << winner, winner, 1


def drive(dut, rst, req):
    dut.rst.value = rst
    dut.req.value = req & MASK


async def sample_after_edge(dut):
    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")
    return int(dut.grant.value) & MASK, int(dut.grant_idx.value)


async def apply_cycle(dut, ptr, grant_idx, rst, req, label):
    drive(dut, rst, req)
    got_grant, got_idx = await sample_after_edge(dut)
    ptr, expected_grant, grant_idx, expected_any = model_step(ptr, grant_idx, rst, req)

    assert got_grant == expected_grant, (
        f"{label}: rst={rst} req={req:#03x} got grant={got_grant:04b}, "
        f"expected {expected_grant:04b}"
    )
    assert got_idx == grant_idx, (
        f"{label}: rst={rst} req={req:#03x} got grant_idx={got_idx}, "
        f"expected {grant_idx}"
    )
    assert got_grant == 0 or got_grant & (got_grant - 1) == 0, (
        f"{label}: grant is not one-hot or zero: {got_grant:04b}"
    )
    if expected_any:
        assert got_grant == (1 << got_idx), (
            f"{label}: grant {got_grant:04b} does not match grant_idx {got_idx}"
        )

    return ptr, grant_idx


async def reset_model_and_dut(dut):
    ptr, grant_idx = 0, 0
    ptr, grant_idx = await apply_cycle(dut, ptr, grant_idx, rst=1, req=0xF, label="reset")
    return ptr, grant_idx


@cocotb.test()
async def test_rr_arb_spec_behavior(dut):
    """Verify registered round-robin arbitration with a Python pointer model."""

    random.seed(0xA4817)
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())

    drive(dut, rst=0, req=0)
    ptr, grant_idx = await reset_model_and_dut(dut)

    # Single requestor: grant is stable, but the internal ptr moves past it then wraps.
    for cycle in range(6):
        ptr, grant_idx = await apply_cycle(
            dut, ptr, grant_idx, rst=0, req=0x1, label=f"single requestor {cycle}"
        )

    ptr, grant_idx = await reset_model_and_dut(dut)
    grants = []
    for cycle in range(8):
        ptr, grant_idx = await apply_cycle(
            dut, ptr, grant_idx, rst=0, req=0xF, label=f"all requestors {cycle}"
        )
        grants.append(int(dut.grant.value) & MASK)
    assert grants == [0x1, 0x2, 0x4, 0x8, 0x1, 0x2, 0x4, 0x8], (
        f"all-requestor round-robin sequence got {[f'{g:04b}' for g in grants]}"
    )
    for window_start in range(0, 8, PORTS):
        assert sorted(grants[window_start:window_start + PORTS]) == [0x1, 0x2, 0x4, 0x8]

    ptr, grant_idx = await reset_model_and_dut(dut)
    wrap_grants = []
    for cycle in range(6):
        ptr, grant_idx = await apply_cycle(
            dut, ptr, grant_idx, rst=0, req=0x9, label=f"wrap ports 0 and 3 {cycle}"
        )
        wrap_grants.append(int(dut.grant.value) & MASK)
    assert wrap_grants == [0x1, 0x8, 0x1, 0x8, 0x1, 0x8]

    ptr, grant_idx = await reset_model_and_dut(dut)
    sparse_grants = []
    for cycle in range(6):
        ptr, grant_idx = await apply_cycle(
            dut, ptr, grant_idx, rst=0, req=0x5, label=f"ports 0 and 2 {cycle}"
        )
        sparse_grants.append(int(dut.grant.value) & MASK)
    assert sparse_grants == [0x1, 0x4, 0x1, 0x4, 0x1, 0x4]

    held_ptr, held_idx = ptr, grant_idx
    for cycle in range(3):
        ptr, grant_idx = await apply_cycle(
            dut, ptr, grant_idx, rst=0, req=0x0, label=f"idle hold {cycle}"
        )
        assert (ptr, grant_idx) == (held_ptr, held_idx)
        assert int(dut.grant.value) == 0
    ptr, grant_idx = await apply_cycle(
        dut, ptr, grant_idx, rst=0, req=0x5, label="after idle resumes same pointer"
    )

    ptr, grant_idx = await reset_model_and_dut(dut)
    for req_seq in itertools.product(range(16), repeat=2):
        for req in req_seq:
            ptr, grant_idx = await apply_cycle(
                dut, ptr, grant_idx, rst=0, req=req,
                label=f"exhaustive pair {req_seq[0]:#03x},{req_seq[1]:#03x}"
            )

    ptr, grant_idx = await reset_model_and_dut(dut)
    continuous_wait = [0 for _ in range(PORTS)]
    for cycle in range(800):
        rst = 1 if cycle in (311, 312) or random.randrange(220) == 0 else 0
        req = random.randrange(16)
        if 420 <= cycle < 440:
            req = 0xF

        ptr, grant_idx = await apply_cycle(
            dut, ptr, grant_idx, rst=rst, req=req, label=f"random cycle {cycle}"
        )
        grant = int(dut.grant.value) & MASK

        if rst:
            continuous_wait = [0 for _ in range(PORTS)]
            continue

        for port in range(PORTS):
            if req & (1 << port):
                if grant == (1 << port):
                    continuous_wait[port] = 0
                else:
                    continuous_wait[port] += 1
                    assert continuous_wait[port] <= PORTS - 1, (
                        f"port {port} requested continuously for "
                        f"{continuous_wait[port]} cycles without grant"
                    )
            else:
                continuous_wait[port] = 0
