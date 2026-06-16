// mac.v - signed multiply-accumulate with synchronous reset and clear.
// Synthesizable Verilog/SystemVerilog subset.

`default_nettype none

module mac #(
    parameter A_WIDTH = 8,
    parameter B_WIDTH = 8,
    parameter ACC_WIDTH = 32
) (
    input  wire                           clk,
    input  wire                           rst,
    input  wire                           clear,
    input  wire                           en,
    input  wire signed [A_WIDTH-1:0]      a,
    input  wire signed [B_WIDTH-1:0]      b,
    output reg  signed [ACC_WIDTH-1:0]    acc
);

    localparam PRODUCT_WIDTH = A_WIDTH + B_WIDTH;

    wire signed [PRODUCT_WIDTH-1:0] product;
    wire signed [ACC_WIDTH-1:0] product_ext;

    assign product = a * b;
    assign product_ext = {{(ACC_WIDTH-PRODUCT_WIDTH){product[PRODUCT_WIDTH-1]}}, product};

    always @(posedge clk) begin
        if (rst)
            acc <= {ACC_WIDTH{1'b0}};
        else if (clear)
            acc <= {ACC_WIDTH{1'b0}};
        else if (en)
            acc <= acc + product_ext;
    end

endmodule

`default_nettype wire
