// mixer.v - Signed DSP mixer.
// Multiplies a signed input sample by a signed local-oscillator sample.

`default_nettype none

module mixer #(
    parameter SAMPLE_WIDTH = 8,
    parameter LO_WIDTH     = 8,
    parameter OUT_WIDTH    = 16
) (
    input  wire                              clk,
    input  wire                              rst,
    input  wire                              en,
    input  wire signed [SAMPLE_WIDTH-1:0]    sample,
    input  wire signed [LO_WIDTH-1:0]        lo,
    output reg  signed [OUT_WIDTH-1:0]       mixed
);

    wire signed [SAMPLE_WIDTH+LO_WIDTH-1:0] product;

    assign product = sample * lo;

    always @(posedge clk) begin
        if (rst) begin
            mixed <= {OUT_WIDTH{1'b0}};
        end else if (en) begin
            mixed <= product;
        end else begin
            mixed <= mixed;
        end
    end

endmodule

`default_nettype wire
