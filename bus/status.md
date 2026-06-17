# Loop Status

Shared coordination file. Agents update their current-cycle section as work proceeds.
No human gate is required for this project unless a real external blocker appears.

## Current

- Module: `pipe_delay`
- Phase: `verified`
- Last actor: Verifier

## Architect

- Iteration: 1
- State: `verified`
- Last change: Wrote `spec/spec.md` (pipeline delay line, WIDTH=8 DEPTH=4, generate
  loop of DEPTH registered stages, d_out is combinational tap of last stage, latency
  measured in enabled cycles, sync reset, enable-hold) and `rtl/pipe_delay.v`.
  Yosys `check -assert` 0 problems.
- ARCHITECT_VAULT_PATH: ~/Axiom-vault

## Verifier

- Iteration: 1
- State: `verified`
- Last change: Split pipe stage 0 out of the generate loop to avoid a nonportable
  unreachable `pipe[-1]` elaboration warning, then wrote `tb/test_pipe_delay.py`.
  Cocotb simulation passed default DEPTH=4 and override DEPTH=1 runs covering reset,
  reset priority, hold/freeze, pulse latency, sequence latency, enable-gated paused
  latency, DEPTH=1 behavior, and 600 randomized reset/enable/data cycles against a
  Python stage model. Yosys `check -assert` passed with 0 reported problems.
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
- `pipe_delay`

## Questions for Manager

- _none_

## Needs Human

- _none_
