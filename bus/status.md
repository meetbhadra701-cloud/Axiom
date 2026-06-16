# Loop Status

Shared coordination file. Each agent updates **only its own section**. The human reads
this to gate each turn.

## Current

- Module: `counter`
- Phase: `verified`
- Last actor: Verifier

## Architect

- Iteration: 1
- State: `verified` — no bug report; loop closed.
- Last change: Wrote first version of `rtl/counter.v` from `spec/spec.md` (8-bit sync
  up-counter, enable, synchronous active-high reset). Passed Yosys `check -assert`.
- ARCHITECT_VAULT_PATH: ~/Axiom-vault

## Verifier

- Iteration: 1
- State: `verified`
- Last change: Added `AGENTS.md`, root `Makefile`, and `tb/test_counter.py`.
  Cocotb simulation passed against an independent Python golden model covering reset,
  reset priority, enable-hold, count-up, wrap-around, mid-count reset, and 200 randomized
  cycles. Yosys `check -assert` also passed with 0 reported problems.
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
