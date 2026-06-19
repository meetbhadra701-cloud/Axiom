# Loop Status

Shared coordination file. Agents update their current-cycle section as work proceeds.
No human gate is required for this project unless a real external blocker appears.

## Current

- Module: `uart_tx`
- Phase: `verified`
- Last actor: Verifier

## Architect

- Iteration: 1
- State: `verified`
- Last change: Wrote `spec/spec.md` (8-N-1 UART TX, CLKS_PER_BIT=868, CLKDIV_W=10) and
  `rtl/uart_tx.v`. 4-state FSM (IDLE/START/DATA/STOP) in a single always block; 10-bit
  baud counter; 3-bit bit_idx; data latched on en&~busy; tx pre-set on each state
  transition so it's stable for the full baud period; busy low in IDLE. Yosys
  `check -assert` 0 problems.
- ARCHITECT_VAULT_PATH: ~/Axiom-vault

## Verifier

- Iteration: 1
- State: `verified`
- Last change: Wrote `tb/test_uart_tx.py`. Cocotb initially caught a missed back-to-back
  load on the stop-bit completion edge; verifier fixed the STOP terminal branch. Final
  simulation passed reset, directed 0x55/0xAA/0x00/0xFF frames, baud-midpoint sampling,
  exact busy duration, ignored `en` while busy, random 20-byte stream deserialisation,
  and back-to-back start. Yosys `check -assert` passed with 0 reported problems.
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

## Questions for Manager

- _none_

## Needs Human

- _none_
