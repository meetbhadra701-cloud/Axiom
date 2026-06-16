# Loop Status

Shared coordination file. Each agent updates **only its own section**. The human reads
this to gate each turn.

## Current

- Module: `mac`
- Phase: `awaiting_verification`
- Last actor: Architect

## Architect

- Iteration: 1
- State: `awaiting_verification`
- Last change: Wrote first version of `rtl/mac.v` from `spec/spec.md` (signed
  multiply-accumulate with synchronous reset, clear, enable, and signed wrap-around
  arithmetic). Passed Yosys `check -assert` with 0 reported problems.
- ARCHITECT_VAULT_PATH: ~/Axiom-vault

## Verifier

- Iteration: 0
- State: `not_started`
- Last change: Waiting on `mac` handoff.
- Simulation layout: run from repo root with `tb/` on `PYTHONPATH`; simulator build
  output goes to `/tmp/axiom-counter-sim_build` to avoid the workspace path space.
- Simulator used: `SIM=icarus` by default. `SIM=verilator` reaches C++ compile but the
  local Command Line Tools C++ setup cannot compile `#include <memory>`; this is a
  host toolchain issue, not a hardware failure.
- VAULT_PATH: /Users/meetbhadra/ FPGA project/verifier-vault

## Questions for Manager

- _none_

## Needs Human

- _none_
