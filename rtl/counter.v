// counter.v — 8-bit synchronous up-counter with enable and synchronous active-high reset.
// Authored by the Architect from spec/spec.md. Synthesizable Verilog-2001 only (CLAUDE.md §3).
//
// Behavior, per rising edge of clk (priority: reset > enable > hold):
//   rst==1            -> count <= 0
//   else if en==1     -> count <= count + 1   (wraps modulo 2**WIDTH)
//   else              -> count holds

`default_nettype none

module counter #(
    parameter WIDTH = 8
) (
    input  wire             clk,    // clock; all state updates on posedge
    input  wire             rst,    // synchronous, active-high reset
    input  wire             en,     // count enable (active-high)
    output reg  [WIDTH-1:0] count   // registered counter value
);

    // Single sequential block, single driver for `count`, non-blocking assignment.
    // Synchronous reset: rst is sampled on the clock edge and is NOT in the
    // sensitivity list, so no asynchronous behavior and no inferred latch.
    always @(posedge clk) begin
        if (rst)
            count <= {WIDTH{1'b0}};   // clear to 0
        else if (en)
            count <= count + 1'b1;    // increment; natural wrap at 2**WIDTH-1 -> 0
        // else: hold (no assignment needed in a clocked block — the FF retains value)
    end

endmodule

`default_nettype wire
