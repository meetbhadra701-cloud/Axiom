// shift_reg.v — Universal left-shifting shift register.
// Left-shift: serial_in enters at sr[0]; sr[WIDTH-1] (MSB) exits via serial_out.
// load preloads parallel_in (priority over en).
// All outputs are combinational taps of the sr register.

`default_nettype none

module shift_reg #(
    parameter WIDTH = 8
) (
    input  wire             clk,
    input  wire             rst,              // synchronous, active-high
    input  wire             load,             // parallel load (priority over en)
    input  wire             en,               // shift enable
    input  wire             serial_in,        // enters at sr[0] on each shift
    input  wire [WIDTH-1:0] parallel_in,
    output wire             serial_out,       // sr[WIDTH-1] — MSB exits first
    output wire [WIDTH-1:0] parallel_out      // full register (combinational)
);

    reg [WIDTH-1:0] sr;

    always @(posedge clk) begin
        if (rst)
            sr <= {WIDTH{1'b0}};
        else if (load)
            sr <= parallel_in;
        else if (en)
            sr <= {sr[WIDTH-2:0], serial_in};  // left-shift
        // else: hold
    end

    assign serial_out   = sr[WIDTH-1];
    assign parallel_out = sr;

endmodule

`default_nettype wire
