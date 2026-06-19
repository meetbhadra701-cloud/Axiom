# Loop Status

Shared coordination file. Agents update their current-cycle section as work proceeds.
No human gate is required for this project unless a real external blocker appears.

## Current

- Module: `moving_avg` (module 25 — final v1.0 module)
- Phase: `verified`
- Last actor: Verifier

## Architect

- Iteration: 1
- State: `verified`
- Last change: Wrote `spec/spec.md` (power-of-2 sliding-window moving average, DATA_W=8
  LOG2N=3 N=8) and `rtl/moving_avg.v`. Shift register (stage-0-split pattern); running
  sum in 11-bit accumulator; evicted = sr[N-1] wire; acc_next = acc + x_in - evicted;
  avg_out = acc_next[10:3]; avg_valid strobes with en. Yosys `check -assert` 0 problems.
- ARCHITECT_VAULT_PATH: ~/Axiom-vault

## Verifier

- Iteration: 1
- State: `verified`
- Last change: Wrote `tb/test_moving_avg.py`. Cocotb simulation passed for default
  DATA_W=8/LOG2N=3 and for an override of LOG2N=2 (N=4). Coverage includes reset,
  reset priority, avg_valid strobe behavior, enable-low hold, constant-fill average,
  push-after-full-window update, zero-to-max step response, all-max steady state,
  N=4 parameterized window behavior, randomized sample sequences, and randomized
  reset/enable/sample cycles against a Python queue-plus-accumulator model. Yosys
  `check -assert` passed with 0 reported problems.
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
- `crc8`
- `one_hot`
- `iir_biquad`
- `uart_tx`
- `moving_avg`

## Questions for Manager

- _none_

## Needs Human

- _none_
