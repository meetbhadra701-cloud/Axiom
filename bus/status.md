# Loop Status

Shared coordination file. Agents update their current-cycle section as work proceeds.
No human gate is required for this project unless a real external blocker appears.

## Current

- Module: `one_hot`
- Phase: `awaiting_verification`
- Last actor: Architect

## Architect

- Iteration: 1
- State: `awaiting_verification`
- Last change: Wrote `spec/spec.md` (binary-to-one-hot decoder, N=8 LOG2W=3 defaults)
  and `rtl/one_hot.v`. Combinational decode via `{{(N-1){1'b0}}, 1'b1} << in`; single
  always block registers the result; priority rst > en > hold. Yosys `check -assert`
  0 problems. Synthesizes to 8 SDFFE + combinational shift logic.
- ARCHITECT_VAULT_PATH: ~/Axiom-vault

## Verifier

- Iteration: 1
- State: `verified`
- Last change: Corrected the `0x01` byte vector note in `spec/spec.md`/`bus/to_verifier.md`
  (`0x8C` after one bit, `0x5E` after the full byte), then wrote `tb/test_crc8.py`.
  Cocotb simulation passed reset, reset priority, hold, zero byte, directed CRC vectors,
  `"123456789"` check value `0xA1`, 50 randomized byte strings, and 400 randomized
  reset/enable/bit cycles against a manual CRC-8/MAXIM reference. Yosys `check -assert`
  passed with 0 reported problems.
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

## Questions for Manager

- _none_

## Needs Human

- _none_
