// delta_sigma.v — First-order delta-sigma (ΔΣ) modulator.
// Accumulates unsigned input; carry out of the WIDTH-bit acc becomes the PDM bit.
// Time-average of ds_out equals in / 2^WIDTH.

`default_nettype none

module delta_sigma #(
    parameter WIDTH = 8
) (
    input  wire             clk,
    input  wire             rst,     // synchronous, active-high
    input  wire             en,
    input  wire [WIDTH-1:0] in,      // unsigned input sample
    output reg              ds_out   // registered 1-bit PDM output
);

    // WIDTH+1 accumulator: bit WIDTH is the carry (next ds_out).
    // On each enabled cycle, clear the carry then add in:
    //   {carry, lower} = 0..acc[WIDTH-1:0] + in
    reg [WIDTH:0] acc;

    always @(posedge clk) begin
        if (rst) begin
            acc    <= {(WIDTH+1){1'b0}};
            ds_out <= 1'b0;
        end else if (en) begin
            acc    <= {1'b0, acc[WIDTH-1:0]} + {1'b0, in};
            ds_out <= acc[WIDTH];   // carry from the previous addition
        end
        // else: hold
    end

endmodule

`default_nettype wire
