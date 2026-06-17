# Loop Status

Shared coordination file. Agents update their current-cycle section as work proceeds.
No human gate is required for this project unless a real external blocker appears.

## Current

- Module: `prio_enc`
- Phase: `verified`
- Last actor: Verifier

## Architect

- Iteration: 1
- State: `verified`
- Last change: Wrote `spec/spec.md` (priority encoder, WIDTH=8 LOG2W=3, highest-index
  set bit wins, combinational for-loop with defaults feeds registered out/valid,
  sync reset, enable-hold) and `rtl/prio_enc.v`. Yosys `check -assert` 0 problems;
  "No latch inferred" messages confirm default assignments prevent latches.
- ARCHITECT_VAULT_PATH: ~/Axiom-vault

## Verifier

- Iteration: 1
- State: `verified`
- Last change: Wrote `tb/test_prio_enc.py`. Cocotb simulation passed synchronous reset,
  reset priority over enable, enable/hold behavior, directed zero/single-bit/multi-bit
  and all-ones cases, single-bit sweep across all positions, exhaustive 256-value
  priority encoding, and 500 randomized reset/enable/input cycles against a Python
  reference model. Yosys `check -assert` passed with 0 reported problems and no latches
  inferred for the combinational encoder.
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

## Questions for Manager

- _none_

## Needs Human

- _none_
