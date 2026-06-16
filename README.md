# Axiom

An autonomous, multi-agent AI pipeline that writes, simulates, and verifies synthesizable
Verilog hardware. Two AI agents collaborate in **one shared repo**, coordinating through
human-gated `bus/` files:

- **The Architect** (Claude Code, see [`CLAUDE.md`](CLAUDE.md)) — designs the RTL in `rtl/`.
- **The Verifier** (Codex, see `AGENTS.md`) — writes cocotb tests in `tb/` and runs them.

The loop is **turn-based and human-gated**: the Architect writes → a human approves →
the Verifier tests → a human approves → the Architect fixes, and so on. Neither agent
starts the next cycle on its own, and neither edits the other's files.

## Layout

```
spec/spec.md   source of truth (the design spec)
rtl/<mod>.v    Architect's synthesizable Verilog
tb/test_*.py   Verifier's cocotb tests        (Verifier-owned)
Makefile       cocotb + simulator driver      (Verifier-owned)
synth/check.ys Yosys synthesis self-check     (Architect)
bus/           to_architect.md / to_verifier.md / status.md  (shared coordination)
```

## Toolchain

- **Icarus Verilog** (`iverilog`) — simulation (cocotb default `SIM=icarus`).
- **Verilator** — alternative simulator.
- **Yosys** — synthesis + `check -assert` (no latches/loops/multi-driven nets).
- **cocotb** (Python) — testbench framework, installed in a `.venv` outside the repo.

```bash
# synthesis self-check (Architect)
yosys -s synth/check.ys

# simulate (Verifier; once a tb/test_<mod>.py + Makefile exist)
source ../.venv/bin/activate
make            # or: make SIM=icarus
```

## First module

`counter` — an 8-bit synchronous up-counter with enable and synchronous active-high
reset. See [`spec/spec.md`](spec/spec.md). Small by design, to prove the loop end-to-end.
