# To Verifier

v1 of `rtl/rr_arb.v` ready, spec in `spec/spec.md` (round-robin arbiter). Ready for simulation.

- Module: `rr_arb` (params `PORTS=4`, `LOG2P=2`)
- Top-level: `rr_arb`
- Ports: `clk`, `rst` (sync active-high), `req[3:0]`, registered `grant[3:0]` (one-hot),
  registered `grant_idx[1:0]` (binary index of winner)
- No `en` — arbiter runs every cycle.
- Algorithm: two-pass combinational scan (defaults prevent latches):
    Pass 1: lowest index ≥ ptr with req set → winner.
    Pass 2 (wrap): if Pass 1 found nothing, lowest index overall with req set → winner.
  After grant: ptr ← (winner+1) % PORTS. No requests → grant=0, ptr holds.
- Yosys `check -assert`: 0 problems. "No latch inferred" confirmed for all combinational regs.
- Iteration: 1

Verification tips:
- All 4 ports asserted (req=4'hF) for 8 cycles → grant sequence 0001,0010,0100,1000,0001,…
- Wrap: after granting port 3, ptr=0; port 0 granted next.
- Idle (req=0): grant=0, ptr holds.
- Two ports active (e.g. req=4'b0101, ports 0 and 2): alternates 0001,0100,0001,…
- No starvation: any port continuously asserting req gets granted within PORTS cycles.
- Reset: grant=0, grant_idx=0, ptr=0.
