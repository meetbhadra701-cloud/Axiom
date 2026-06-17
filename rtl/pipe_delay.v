// pipe_delay.v — Parameterized synchronous pipeline delay line.
// d_out appears DEPTH enabled clock cycles after d_in.
// All stages reset to 0 and freeze together when en=0.

`default_nettype none

module pipe_delay #(
    parameter WIDTH = 8,
    parameter DEPTH = 4
) (
    input  wire             clk,
    input  wire             rst,    // synchronous, active-high
    input  wire             en,
    input  wire [WIDTH-1:0] d_in,
    output wire [WIDTH-1:0] d_out   // combinational tap of last stage
);

    reg [WIDTH-1:0] pipe [0:DEPTH-1];

    always @(posedge clk) begin
        if (rst)
            pipe[0] <= {WIDTH{1'b0}};
        else if (en)
            pipe[0] <= d_in;
        // else: hold
    end

    genvar g;
    generate
        for (g = 1; g < DEPTH; g = g + 1) begin : stage
            always @(posedge clk) begin
                if (rst)
                    pipe[g] <= {WIDTH{1'b0}};
                else if (en)
                    pipe[g] <= pipe[g-1];
                // else: hold
            end
        end
    endgenerate

    assign d_out = pipe[DEPTH-1];

endmodule

`default_nettype wire
