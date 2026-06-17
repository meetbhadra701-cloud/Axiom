// rr_arb.v — Synchronous round-robin arbiter.
// Two-pass scan: first from ptr→PORTS-1, then wrap 0→ptr-1.
// Priority pointer advances past the winner each cycle; no starvation.

`default_nettype none

module rr_arb #(
    parameter PORTS = 4,
    parameter LOG2P = 2     // must satisfy 2^LOG2P == PORTS
) (
    input  wire              clk,
    input  wire              rst,        // synchronous, active-high
    input  wire [PORTS-1:0]  req,        // request bits
    output reg  [PORTS-1:0]  grant,      // registered one-hot grant
    output reg  [LOG2P-1:0]  grant_idx   // registered binary index of winner
);

    localparam [LOG2P-1:0] MAX_PORT = PORTS - 1;   // highest valid port index

    reg [LOG2P-1:0] ptr;    // scan start pointer (rotates after each grant)

    // Combinational winner selection.
    reg [LOG2P-1:0] next_enc;
    reg             next_any;
    reg             found;
    integer         i;

    always @(*) begin
        next_enc = {LOG2P{1'b0}};
        next_any = 1'b0;
        found    = 1'b0;

        // Pass 1: lowest set bit at index >= ptr
        for (i = 0; i < PORTS; i = i + 1) begin
            if (!found && (i[LOG2P-1:0] >= ptr) && req[i]) begin
                next_enc = i[LOG2P-1:0];
                next_any = 1'b1;
                found    = 1'b1;
            end
        end

        // Pass 2 (wrap): lowest set bit anywhere — only reached when Pass 1 found nothing
        for (i = 0; i < PORTS; i = i + 1) begin
            if (!found && req[i]) begin
                next_enc = i[LOG2P-1:0];
                next_any = 1'b1;
                found    = 1'b1;
            end
        end
    end

    // Registered outputs and pointer update.
    always @(posedge clk) begin
        if (rst) begin
            grant     <= {PORTS{1'b0}};
            grant_idx <= {LOG2P{1'b0}};
            ptr       <= {LOG2P{1'b0}};
        end else begin
            if (next_any) begin
                grant     <= ({{(PORTS-1){1'b0}}, 1'b1}) << next_enc;
                grant_idx <= next_enc;
                ptr       <= (next_enc == MAX_PORT) ? {LOG2P{1'b0}}
                                                    : next_enc + 1'b1;
            end else begin
                grant <= {PORTS{1'b0}};
                // grant_idx and ptr unchanged when idle
            end
        end
    end

endmodule

`default_nettype wire
