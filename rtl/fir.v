// fir.v — Parameterizable direct-form FIR filter with fixed signed coefficients.
// Authored by the Architect from spec/spec.md. Synthesizable Verilog-2001 (CLAUDE.md §3).
//
// On posedge clk, priority: rst > en > hold.
//   rst: clear delay line d[] and output y to 0.
//   en:  shift d[] <- {d[N_TAPS-2:0], x}, compute y = sum(d[i] * coef[i]).
//
// COEFFS is a flat (N_TAPS*COEF_WIDTH)-bit vector.
// coef[i] occupies bits [(i+1)*COEF_WIDTH-1 : i*COEF_WIDTH].
// Tap 0 = most recent sample (d[0] = x after shift).

`default_nettype none

module fir #(
    parameter                        N_TAPS     = 4,
    parameter                        DATA_WIDTH = 8,
    parameter                        COEF_WIDTH = 8,
    parameter                        OUT_WIDTH  = 32,
    parameter [N_TAPS*COEF_WIDTH-1:0] COEFFS    = {8'sd1, 8'sd2, 8'sd4, 8'sd2}
) (
    input  wire                        clk,
    input  wire                        rst,    // synchronous, active-high
    input  wire                        en,     // sample enable
    input  wire signed [DATA_WIDTH-1:0] x,     // signed input sample
    output reg  signed [OUT_WIDTH-1:0]  y      // registered signed filtered output
);

    // Packed delay line. Tap 0 (most recent sample) occupies the low DATA_WIDTH bits.
    reg signed [N_TAPS*DATA_WIDTH-1:0] delay_line;

    // Combinational partial products and accumulation.
    // Use a wire array for products; sum in always @(*) to avoid latches.
    wire signed [DATA_WIDTH+COEF_WIDTH-1:0] prod [0:N_TAPS-1];
    reg  signed [OUT_WIDTH-1:0]             acc_comb;

    genvar gi;
    generate
        for (gi = 0; gi < N_TAPS; gi = gi + 1) begin : PRODUCTS
            // Extract signed coefficient for tap gi.
            wire signed [COEF_WIDTH-1:0] coef_i;
            wire signed [DATA_WIDTH-1:0] sample_i;
            assign coef_i = COEFFS[gi*COEF_WIDTH +: COEF_WIDTH];
            assign sample_i = delay_line[gi*DATA_WIDTH +: DATA_WIDTH];
            assign prod[gi] = sample_i * coef_i;
        end
    endgenerate

    // Combinational sum: sign-extend each product to OUT_WIDTH, then sum.
    integer i;
    always @(*) begin
        acc_comb = {OUT_WIDTH{1'b0}};   // default — prevents latch
        for (i = 0; i < N_TAPS; i = i + 1)
            acc_comb = acc_comb +
                       {{(OUT_WIDTH-(DATA_WIDTH+COEF_WIDTH)){prod[i][DATA_WIDTH+COEF_WIDTH-1]}},
                        prod[i]};
    end

    // Sequential block: single driver for d[] and y, non-blocking only.
    always @(posedge clk) begin
        if (rst) begin
            y <= {OUT_WIDTH{1'b0}};
            delay_line <= {(N_TAPS*DATA_WIDTH){1'b0}};
        end else if (en) begin
            // Shift delay line: tap N_TAPS-1 is oldest.
            delay_line <= {delay_line[(N_TAPS-1)*DATA_WIDTH-1:0], x};
            y <= acc_comb;
        end
        // else: hold — no assignment needed in a clocked block
    end

endmodule

`default_nettype wire
