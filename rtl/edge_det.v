// edge_det.v — Two-stage synchronous edge detector.
// pipe[0] = current sample, pipe[1] = previous sample.
// rise/fall/any_edge are registered: valid 2 clocks after input transition.

`default_nettype none

module edge_det (
    input  wire clk,
    input  wire rst,      // synchronous, active-high; clears pipeline and outputs
    input  wire sig_in,
    output reg  rise,     // 1-cycle pulse: 0→1 transition
    output reg  fall,     // 1-cycle pulse: 1→0 transition
    output reg  any_edge  // 1-cycle pulse: either transition
);

    reg [1:0] pipe;   // pipe[0] = most recent, pipe[1] = one cycle older

    always @(posedge clk) begin
        if (rst) begin
            pipe     <= 2'b00;
            rise     <= 1'b0;
            fall     <= 1'b0;
            any_edge <= 1'b0;
        end else begin
            pipe[0]  <= sig_in;
            pipe[1]  <= pipe[0];
            rise     <= pipe[0] & ~pipe[1];
            fall     <= ~pipe[0] & pipe[1];
            any_edge <= pipe[0] ^ pipe[1];
        end
    end

endmodule

`default_nettype wire
