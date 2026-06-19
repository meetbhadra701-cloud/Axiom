# Loop Status

Shared coordination file. Agents update their current-cycle section as work proceeds.
No human gate is required for this project unless a real external blocker appears.

## Current

- **STATUS: v1.0 POST-AUDIT CLEAN — 25/25 tests pass under correct invocation**
- Post-audit fix commit: current branch head after merge to `main`
- Last module: `moving_avg` (module 25), verified and merged 2026-06-18
- Post-audit branch: `fix/v1.0-post-audit`
- Audit reference: `/Users/meetbhadra/ FPGA project/verifier-vault/AUDIT_v1.0.md`

## Architect

- State: `v1.0 complete`
- Vault index: `~/Axiom-vault/00-Index/axiom_v1_library_index.md`
- ARCHITECT_VAULT_PATH: ~/Axiom-vault

## Verifier

- Iteration: 1
- State: `post-audit clean`
- Last change: Added `tb/run_uart_tx.py`, a self-contained cocotb runner for `uart_tx`
  that passes `CLKS_PER_BIT=4` and `CLKDIV_W=2` into the DUT build, uses `SIM=icarus`,
  sets timescale to `1ns/1ps`, points `PYTHONPATH` at `tb/`, and writes sim output to
  `/tmp/axiom-uart_tx-sim_build`. Result: `TESTS=1 PASS=1 FAIL=0 SKIP=0`. Local note:
  the shell has no bare `python`; `python3 tb/run_uart_tx.py` passes by re-execing into
  the cocotb venv, and `PATH="/tmp/axiom-cocotb-venv/bin:$PATH" python tb/run_uart_tx.py`
  passes exactly.
- Post-audit advisory acknowledgements: `sine_lut` ROM `initial` block is approved;
  `iir_biquad` DSP inference is a future target-synthesis check; `fifo` pointer logic
  had no observed simulation failure; Makefile path-space breakage is acknowledged and
  Python runners are the workaround.
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
