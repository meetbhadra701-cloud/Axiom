// iir_biquad.v — 2nd-order IIR biquad, Direct Form I, signed fixed-point.
// y[n] = b0*x[n] + b1*x[n-1] + b2*x[n-2] - a1*y[n-1] - a2*y[n-2]
// Coefficients in Q1.FRAC_W format; truncates accumulator to DATA_W bits.

`default_nettype none

module iir_biquad #(
    parameter DATA_W = 16,
    parameter COEF_W = 16,
    parameter FRAC_W = 14
) (
    input  wire                      clk,
    input  wire                      rst,     // synchronous, active-high
    input  wire                      en,
    input  wire signed [DATA_W-1:0]  x_in,
    input  wire signed [COEF_W-1:0]  b0,
    input  wire signed [COEF_W-1:0]  b1,
    input  wire signed [COEF_W-1:0]  b2,
    input  wire signed [COEF_W-1:0]  a1,
    input  wire signed [COEF_W-1:0]  a2,
    output reg  signed [DATA_W-1:0]  y_out,
    output reg                       y_valid
);

    localparam ACC_W = DATA_W + COEF_W + 3; // 3 guard bits for 5 accumulated products

    // Delay registers
    reg signed [DATA_W-1:0] x1, x2; // x[n-1], x[n-2]
    reg signed [DATA_W-1:0] y1, y2; // y[n-1], y[n-2]

    // Full-precision accumulator
    wire signed [ACC_W-1:0] acc;
    assign acc = (b0 * x_in)
               + (b1 * x1)
               + (b2 * x2)
               - (a1 * y1)
               - (a2 * y2);

    // Truncate fractional bits to recover DATA_W-bit result
    wire signed [DATA_W-1:0] acc_trunc;
    assign acc_trunc = $signed(acc[FRAC_W + DATA_W - 1 : FRAC_W]);

    always @(posedge clk) begin
        if (rst) begin
            x1      <= {DATA_W{1'b0}};
            x2      <= {DATA_W{1'b0}};
            y1      <= {DATA_W{1'b0}};
            y2      <= {DATA_W{1'b0}};
            y_out   <= {DATA_W{1'b0}};
            y_valid <= 1'b0;
        end else if (en) begin
            x2      <= x1;
            x1      <= x_in;
            y2      <= y1;
            y1      <= acc_trunc;
            y_out   <= acc_trunc;
            y_valid <= 1'b1;
        end else begin
            y_valid <= 1'b0;
            // x1, x2, y1, y2, y_out: hold
        end
    end

endmodule

`default_nettype wire
