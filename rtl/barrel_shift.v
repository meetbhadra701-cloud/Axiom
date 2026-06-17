// barrel_shift.v — Synchronous signed arithmetic barrel shifter.
// dir=0: logical left shift (<<); dir=1: arithmetic right shift (>>>).
// `in` declared signed so Verilog >>> sign-extends correctly.

`default_nettype none

module barrel_shift #(
    parameter WIDTH       = 16,
    parameter SHAMT_WIDTH = 4
) (
    input  wire                       clk,
    input  wire                       rst,    // synchronous, active-high
    input  wire                       en,
    input  wire signed [WIDTH-1:0]    in,
    input  wire [SHAMT_WIDTH-1:0]     shamt,
    input  wire                       dir,    // 0=left, 1=arithmetic-right
    output reg  signed [WIDTH-1:0]    out
);

    always @(posedge clk) begin
        if (rst)
            out <= {WIDTH{1'b0}};
        else if (en)
            out <= dir ? (in >>> shamt) : (in << shamt);
        // else: hold
    end

endmodule

`default_nettype wire
