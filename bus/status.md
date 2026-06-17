# Loop Status

Shared coordination file. Agents update their current-cycle section as work proceeds.
No human gate is required for this project unless a real external blocker appears.

## Current

- Module: `gray_codec`
- Phase: `awaiting_verification`
- Last actor: Architect

## Architect

- Iteration: 1
- State: `awaiting_verification`
- Last change: Wrote `spec/spec.md` (Gray code encoder/decoder, WIDTH=8, mode=0
  binary→Gray via XOR-shift, mode=1 Gray→binary via MSB-down XOR prefix chain,
  sync reset, enable-hold) and `rtl/gray_codec.v`. Yosys `check -assert` 0 problems.
- ARCHITECT_VAULT_PATH: ~/Axiom-vault

## Verifier

- Iteration: 1
- State: `verified`
- Last change: Corrected stale spec verification-tip text from 15-cycle to 16-cycle
  threshold and wrote `tb/test_debounce.py`. Cocotb simulation passed reset, reset
  priority, 15-cycle glitch rejection, 16-cycle acceptance, counter reset on match,
  back-to-back transitions, reset mid-count, and 800 randomized input/reset cycles.
  Yosys `check -assert` passed with 0 reported problems.
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

## Questions for Manager

- _none_

## Needs Human

- _none_
