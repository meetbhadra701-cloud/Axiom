# Loop Status

Shared coordination file. Each agent updates **only its own section**. The human reads
this to gate each turn.

## Current

- Module: `lfsr`
- Phase: `bug_reported`
- Last actor: Verifier

## Architect

- Iteration: 1
- State: `awaiting_verification`
- Last change: Wrote `spec/spec.md` (16-bit Galois LFSR, POLY=16'hB400 for period-65535
  maximal sequence, SEED=1, Galois XOR-feedback step, sync reset, enable) and
  `rtl/lfsr.v`. Yosys `check -assert` 0 problems.
- ARCHITECT_VAULT_PATH: ~/Axiom-vault

## Verifier

- Iteration: 1
- State: `failed`
- Last change: Added `tb/test_lfsr.py` and ran Cocotb with `DUT=lfsr`. Simulation failed
  on first enabled step after reset: got `out=0x0000`, expected `0xb400` for the
  maximal-length `16'hB400` right-shift Galois sequence from seed `1`.
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
