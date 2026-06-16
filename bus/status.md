# Loop Status

Shared coordination file. Each agent updates **only its own section**. The human reads
this to gate each turn.

## Current

- Module: `lfsr`
- Phase: `awaiting_verification`
- Last actor: Architect

## Architect

- Iteration: 2
- State: `awaiting_verification`
- Last change: Wrote `spec/spec.md` (16-bit Galois LFSR, POLY=16'hB400 for period-65535
  maximal sequence, SEED=1, Galois XOR-feedback step, sync reset, enable). Fixed v1
  feedback bit from old MSB to old LSB for the standard right-shift `16'hB400` sequence.
- ARCHITECT_VAULT_PATH: ~/Axiom-vault

## Verifier

- Iteration: 1
- State: `awaiting_rerun`
- Last change: Filed v1 feedback-bit bug. Awaiting v2 verification rerun.
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
