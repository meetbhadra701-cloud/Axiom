// debounce.v — Synchronous signal debouncer.
// sig_out updates only when sig_in has differed from sig_out for 2^STABLE_BITS
// consecutive cycles. A glitch shorter than the threshold resets the counter.

`default_nettype none

module debounce #(
    parameter STABLE_BITS = 4    // counter width; threshold = 2^STABLE_BITS cycles
) (
    input  wire clk,
    input  wire rst,      // synchronous, active-high; clears counter, sig_out → 0
    input  wire sig_in,
    output reg  sig_out
);

    reg [STABLE_BITS-1:0] counter;

    always @(posedge clk) begin
        if (rst) begin
            counter <= {STABLE_BITS{1'b0}};
            sig_out <= 1'b0;
        end else begin
            if (sig_in == sig_out) begin
                counter <= {STABLE_BITS{1'b0}};   // stable — reset counter
            end else if (counter == {STABLE_BITS{1'b1}}) begin
                sig_out <= sig_in;                 // stable for threshold cycles — accept
                counter <= {STABLE_BITS{1'b0}};
            end else begin
                counter <= counter + 1'b1;         // still counting toward threshold
            end
        end
    end

endmodule

`default_nettype wire
