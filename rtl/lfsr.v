// lfsr.v — Galois-form maximal-length LFSR.
// Authored by the Architect from spec/spec.md. Synthesizable Verilog-2001 (CLAUDE.md §3).
//
// Galois step: next = (state >> 1) ^ (state[MSB] ? POLY : 0)
// Default POLY=16'hB400 gives a period-65535 sequence for WIDTH=16.
// SEED must be non-zero; all-zero state is a lock-up point.

`default_nettype none

module lfsr #(
    parameter              WIDTH = 16,
    parameter [WIDTH-1:0]  POLY  = 16'hB400,
    parameter [WIDTH-1:0]  SEED  = {{(WIDTH-1){1'b0}}, 1'b1}   // default = 1
) (
    input  wire             clk,
    input  wire             rst,    // synchronous, active-high; loads SEED
    input  wire             en,     // shift enable
    output reg  [WIDTH-1:0] out     // registered LFSR state
);

    // Galois next-state: combinational wire, one driver.
    wire [WIDTH-1:0] next_state;
    assign next_state = (out >> 1) ^ (out[WIDTH-1] ? POLY : {WIDTH{1'b0}});

    always @(posedge clk) begin
        if (rst)
            out <= SEED;
        else if (en)
            out <= next_state;
        // else: hold
    end

endmodule

`default_nettype wire
