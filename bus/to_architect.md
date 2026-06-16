# To Architect

## Bug report - lfsr - iteration 1

- Test: `test_lfsr_spec_behavior`
- Symptom: first enabled step after reset locks into zero.
- Got: `out = 0x0000`
- Expected: `out = 0xb400` from seed `0x0001` using maximal-length `POLY=16'hB400`.
- Likely area: feedback bit. `POLY=16'hB400` with `SEED=1` is maximal for right-shift
  Galois when feedback is old LSB, not old MSB.
