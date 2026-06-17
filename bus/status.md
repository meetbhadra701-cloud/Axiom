# Loop Status

Shared coordination file. Agents update their current-cycle section as work proceeds.
No human gate is required for this project unless a real external blocker appears.

## Current

- Module: `edge_det`
- Phase: `verified`
- Last actor: Verifier

## Architect

- Iteration: 1
- State: `verified`
- Last change: Wrote `spec/spec.md` (two-stage synchronous edge detector, no params,
  registered rise/fall/any_edge outputs, 2-cycle latency, sync reset clears pipeline)
  and `rtl/edge_det.v`. Yosys `check -assert` 0 problems.
- ARCHITECT_VAULT_PATH: ~/Axiom-vault

## Verifier

- Iteration: 1
- State: `verified`
- Last change: Wrote and ran `tb/test_edge_det.py`. Cocotb simulation passed reset,
  reset priority, sustained high/low, registered rise/fall/any-edge pulses, 1-cycle
  input pulse behavior, reset clearing an in-flight transition, `any_edge == rise|fall`,
  and 600 randomized signal/reset cycles. Yosys `check -assert` passed with 0 reported
  problems.
- Simulation layout: run from repo root with `tb/` on `PYTHONPATH`; simulator build
  output goes to `/tmp/axiom-$(DUT)-sim_build` to avoid the workspace path space.
- Simulator used: `SIM=icarus` by default. `SIM=verilator` reaches C++ compile but the
  local Command Line Tools C++ setup cannot compile `#include <memory>`; this is a
  host toolchain issue, not a hardware failure.
- VAULT_PATH: /Users/meetbhadra/ FPGA project/verifier-vault

## Verified Modules On Main

- `counter`
- `mac`
- `fir`
- `fifo`
- `nco`
- `lfsr`
- `sine_lut`
- `mixer`
- `pwm`
- `sat_adder`
- `barrel_shift`
- `delta_sigma`
- `strobe_gen`
- `edge_det`

## Questions for Manager

- _none_

## Needs Human

- _none_
