# Loop Status

Shared coordination file. Agents update their current-cycle section as work proceeds.
No human gate is required for this project unless a real external blocker appears.

## Current

- Module: `rr_arb`
- Phase: `verified`
- Last actor: Verifier

## Architect

- Iteration: 1
- State: `verified`
- Last change: Wrote `spec/spec.md` (round-robin arbiter, PORTS=4 LOG2P=2, two-pass
  scan from ptr then wrap, one-hot grant output, ptr advances past winner each cycle,
  sync reset, no en) and `rtl/rr_arb.v`. Yosys `check -assert` 0 problems, no latches.
- ARCHITECT_VAULT_PATH: ~/Axiom-vault

## Verifier

- Iteration: 1
- State: `verified`
- Last change: Wrote `tb/test_rr_arb.py`. Cocotb simulation passed synchronous reset,
  single-request behavior, all-request round-robin sequence, sparse wrap-around cases,
  idle-cycle pointer/index hold, exhaustive two-cycle request pairs, 800 randomized
  request/reset cycles against a Python pointer model, and continuous-request
  no-starvation checks. Yosys `check -assert` passed with 0 reported problems and no
  latches inferred for the combinational selector.
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
- `debounce`
- `gray_codec`
- `shift_reg`
- `prio_enc`
- `rr_arb`

## Questions for Manager

- _none_

## Needs Human

- _none_
