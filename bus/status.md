# Loop Status

Shared coordination file. Agents update their current-cycle section as work proceeds.
No human gate is required for this project unless a real external blocker appears.

## Current

- Module: `barrel_shift`
- Phase: `verified`
- Last actor: Verifier

## Architect

- Iteration: 1
- State: `verified`
- Last change: Wrote `spec/spec.md` (signed arithmetic barrel shifter, WIDTH=16,
  SHAMT_WIDTH=4, dir=0 left shift / dir=1 arithmetic right shift, sync reset,
  enable-hold) and `rtl/barrel_shift.v`. Yosys `check -assert` 0 problems.
- ARCHITECT_VAULT_PATH: ~/Axiom-vault

## Verifier

- Iteration: 1
- State: `verified`
- Last change: Wrote and ran `tb/test_barrel_shift.py`. Cocotb simulation passed reset,
  reset priority, enable-hold, left/right shift-by-zero identity, wrapping left shifts,
  arithmetic right shifts with sign extension, max shift cases, and 600 randomized
  signed reference-model cycles. Yosys `check -assert` passed with 0 reported problems.
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

## Questions for Manager

- _none_

## Needs Human

- _none_
