// one_hot.v — Registered binary-to-one-hot decoder.
// out[in] is set; all other bits are clear. Priority: rst > en > hold.

`default_nettype none

module one_hot #(
    parameter N     = 8,
    parameter LOG2W = 3
) (
    input  wire             clk,
    input  wire             rst,    // synchronous, active-high
    input  wire             en,
    input  wire [LOG2W-1:0] in,
    output reg  [N-1:0]     out
);

    wire [N-1:0] decoded;
    assign decoded = {{(N-1){1'b0}}, 1'b1} << in;

    always @(posedge clk) begin
        if (rst)      out <= {N{1'b0}};
        else if (en)  out <= decoded;
        // else: hold
    end

endmodule

`default_nettype wire
