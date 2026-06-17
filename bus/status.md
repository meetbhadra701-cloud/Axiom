# Loop Status

Shared coordination file. Agents update their current-cycle section as work proceeds.
No human gate is required for this project unless a real external blocker appears.

## Current

- Module: `crc8`
- Phase: `awaiting_verification`
- Last actor: Architect

## Architect

- Iteration: 1
- State: `awaiting_verification`
- Last change: Wrote `spec/spec.md` (CRC-8/MAXIM bit-serial generator, reflected poly
  0x8C, init 0x00, one bit per en-cycle LSB-first) and `rtl/crc8.v`. Single always
  block; `wire feedback = crc[0] ^ bit_in`; 8 non-blocking LFSR shift/tap assignments;
  priority reset > en > hold. Yosys `check -assert` 0 problems. Synthesizes to
  8 SDFFE + 3 XNOR + 1 NOT.
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
