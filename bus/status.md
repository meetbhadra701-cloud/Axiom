# Loop Status

Shared coordination file. Each agent updates **only its own section**. The human reads
this to gate each turn.

## Current

- Module: `fir`
- Phase: `bug_reported`
- Last actor: Verifier

## Architect

- Iteration: 1
- State: `awaiting_verification`
- Last change: Wrote `spec/spec.md` (4-tap direct-form FIR filter, fixed signed
  coefficients, shift-register delay line, combinational multiply-and-sum, registered
  output). Wrote `rtl/fir.v`. Yosys `check -assert` 0 problems.
- ARCHITECT_VAULT_PATH: ~/Axiom-vault

## Verifier

- Iteration: 1
- State: `failed`
- Last change: Added `tb/test_fir.py` and ran Cocotb with `DUT=fir`. Simulation failed
  on the impulse-response coefficient-order check: cycle `impulse 1` got `y=1`, expected
  `y=2` for delay `[1, 0, 0, 0]`.
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
