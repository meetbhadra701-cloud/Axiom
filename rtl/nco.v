// nco.v — Numerically Controlled Oscillator (DDS phase accumulator).
// Authored by the Architect from spec/spec.md. Synthesizable Verilog-2001 (CLAUDE.md §3).
//
// phase_out += phase_inc each enabled clock edge, wrapping modulo 2^PHASE_WIDTH.
// High bits of phase_out form a sawtooth; feed to a sine LUT for DDS sine output.

`default_nettype none

module nco #(
    parameter PHASE_WIDTH = 24
) (
    input  wire                    clk,
    input  wire                    rst,         // synchronous, active-high
    input  wire                    en,          // accumulator enable
    input  wire [PHASE_WIDTH-1:0]  phase_inc,   // unsigned frequency word
    output reg  [PHASE_WIDTH-1:0]  phase_out    // registered unsigned phase accumulator
);

    always @(posedge clk) begin
        if (rst)
            phase_out <= {PHASE_WIDTH{1'b0}};
        else if (en)
            phase_out <= phase_out + phase_inc;  // natural wrap at 2^PHASE_WIDTH
        // else: hold
    end

endmodule

`default_nettype wire
