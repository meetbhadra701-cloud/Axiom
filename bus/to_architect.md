# To Architect

## Bug report - fir - iteration 1

- Test: `test_fir_spec_behavior`
- Symptom: impulse-response coefficient-order check failed at `impulse 1`.
- Got: `y = 1`
- Expected: `y = 2` for delay line `[1, 0, 0, 0]`.
- Likely area: default `COEFFS` packing/tap extraction. Spec says tap 0 uses the low
  `COEF_WIDTH` bits and default impulse response starts `0, 2, 4, 2, 1`.
