// prio_enc.v — Registered priority encoder.
// Scans in[WIDTH-1:0]; highest-index set bit wins.
// Combinational always@(*) feeds a registered output stage to avoid latches.

`default_nettype none

module prio_enc #(
    parameter WIDTH = 8,
    parameter LOG2W = 3     // must satisfy 2^LOG2W == WIDTH
) (
    input  wire             clk,
    input  wire             rst,      // synchronous, active-high
    input  wire             en,
    input  wire [WIDTH-1:0] in,       // request bits; bit[WIDTH-1] = highest priority
    output reg  [LOG2W-1:0] out,      // index of highest-priority set bit
    output reg              valid     // any bit set
);

    // Combinational encoder: scan low-to-high; last found wins (= highest index).
    reg [LOG2W-1:0] enc_out;
    reg             enc_valid;
    integer         i;

    always @(*) begin
        enc_out   = {LOG2W{1'b0}};
        enc_valid = 1'b0;
        for (i = 0; i < WIDTH; i = i + 1) begin
            if (in[i]) begin
                enc_out   = i[LOG2W-1:0];
                enc_valid = 1'b1;
            end
        end
    end

    // Registered output stage.
    always @(posedge clk) begin
        if (rst) begin
            out   <= {LOG2W{1'b0}};
            valid <= 1'b0;
        end else if (en) begin
            out   <= enc_out;
            valid <= enc_valid;
        end
        // else: hold
    end

endmodule

`default_nettype wire
