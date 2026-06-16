# Loop Status

Shared coordination file. Each agent updates **only its own section**. The human reads
this to gate each turn.

## Current

- Module: `nco`
- Phase: `awaiting_verification`
- Last actor: Architect

## Architect

- Iteration: 1
- State: `awaiting_verification`
- Last change: Wrote `spec/spec.md` (NCO phase accumulator, PHASE_WIDTH=24, unsigned,
  wrapping adder, synchronous reset, enable) and `rtl/nco.v`. Yosys `check -assert`
  0 problems.
- ARCHITECT_VAULT_PATH: ~/Axiom-vault

## Verifier

- Iteration: 1
- State: `verified`
- Last change: Added `tb/test_fifo.py` and ran Cocotb with `DUT=fifo`. Simulation
  passed with reset, reset priority, empty-read ignore, fill/full behavior, ignored
  full writes, simultaneous read/write, pointer wrap, drain ordering, and 500 randomized
  cycles. Yosys `check -assert` passed with 0 reported problems.
- Simulation layout: run from repo root with `tb/` on `PYTHONPATH`; simulator build
  output goes to `/tmp/axiom-$(DUT)-sim_build` to avoid the workspace path space.
- Simulator used: `SIM=icarus` by default. `SIM=verilator` reaches C++ compile but the
  local Command Line Tools C++ setup cannot compile `#include <memory>`; this is a
  host toolchain issue, not a hardware failure.
- VAULT_PATH: /Users/meetbhadra/ FPGA project/verifier-vault

## Questions for Manager

- _none_

## Needs Human

- _none_
