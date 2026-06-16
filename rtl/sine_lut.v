// sine_lut.v — Quarter-wave ROM sine lookup table.
// Maps ADDR_WIDTH-bit phase to DATA_WIDTH-bit signed sine amplitude.
// Top 2 bits of phase_in select quadrant; symmetry reconstructs the full cycle.
// One pipeline register: sin_out valid one clock after phase_in.
//
// ROM init via `initial` is the single permitted exception to no-initial rule;
// all FPGA synthesis tools infer block/distributed RAM from this pattern.

`default_nettype none

module sine_lut #(
    parameter ADDR_WIDTH = 8,                    // phase bits consumed
    parameter DATA_WIDTH = 8                     // amplitude bits (signed output)
) (
    input  wire                      clk,
    input  wire [ADDR_WIDTH-1:0]     phase_in,   // unsigned phase
    output reg  signed [DATA_WIDTH-1:0] sin_out  // signed amplitude, registered
);

    localparam DEPTH = 1 << (ADDR_WIDTH - 2);    // quarter-wave depth (64 for default)

    // Quarter-wave ROM: unsigned values 0..(2^(DATA_WIDTH-1)-1)
    reg [DATA_WIDTH-1:0] lut [0:DEPTH-1];

    initial begin
        lut[0] = 8'd2;
        lut[1] = 8'd5;
        lut[2] = 8'd8;
        lut[3] = 8'd11;
        lut[4] = 8'd14;
        lut[5] = 8'd17;
        lut[6] = 8'd20;
        lut[7] = 8'd23;
        lut[8] = 8'd26;
        lut[9] = 8'd29;
        lut[10] = 8'd32;
        lut[11] = 8'd35;
        lut[12] = 8'd38;
        lut[13] = 8'd41;
        lut[14] = 8'd44;
        lut[15] = 8'd47;
        lut[16] = 8'd50;
        lut[17] = 8'd53;
        lut[18] = 8'd56;
        lut[19] = 8'd58;
        lut[20] = 8'd61;
        lut[21] = 8'd64;
        lut[22] = 8'd67;
        lut[23] = 8'd69;
        lut[24] = 8'd72;
        lut[25] = 8'd74;
        lut[26] = 8'd77;
        lut[27] = 8'd79;
        lut[28] = 8'd82;
        lut[29] = 8'd84;
        lut[30] = 8'd86;
        lut[31] = 8'd89;
        lut[32] = 8'd91;
        lut[33] = 8'd93;
        lut[34] = 8'd95;
        lut[35] = 8'd97;
        lut[36] = 8'd99;
        lut[37] = 8'd101;
        lut[38] = 8'd103;
        lut[39] = 8'd105;
        lut[40] = 8'd106;
        lut[41] = 8'd108;
        lut[42] = 8'd110;
        lut[43] = 8'd111;
        lut[44] = 8'd113;
        lut[45] = 8'd114;
        lut[46] = 8'd115;
        lut[47] = 8'd117;
        lut[48] = 8'd118;
        lut[49] = 8'd119;
        lut[50] = 8'd120;
        lut[51] = 8'd121;
        lut[52] = 8'd122;
        lut[53] = 8'd123;
        lut[54] = 8'd124;
        lut[55] = 8'd124;
        lut[56] = 8'd125;
        lut[57] = 8'd125;
        lut[58] = 8'd126;
        lut[59] = 8'd126;
        lut[60] = 8'd127;
        lut[61] = 8'd127;
        lut[62] = 8'd127;
        lut[63] = 8'd127;
    end

    // Combinational quadrant decode
    wire [1:0]              quad;
    wire [ADDR_WIDTH-3:0]   fwd_idx;   // forward index (Q0/Q2)
    wire [ADDR_WIDTH-3:0]   mir_idx;   // mirrored index (Q1/Q3)
    wire [ADDR_WIDTH-3:0]   rom_idx;   // final ROM address
    wire                    negate;

    assign quad    = phase_in[ADDR_WIDTH-1:ADDR_WIDTH-2];
    assign fwd_idx = phase_in[ADDR_WIDTH-3:0];
    assign mir_idx = ~fwd_idx;
    assign rom_idx = quad[0] ? mir_idx : fwd_idx;   // Q1/Q3 mirror
    assign negate  = quad[1];                        // Q2/Q3 negate

    wire [DATA_WIDTH-1:0] raw = lut[rom_idx];

    // Registered output with quadrant sign
    always @(posedge clk) begin
        if (negate)
            sin_out <= -$signed({1'b0, raw});   // two's-complement negation
        else
            sin_out <= $signed({1'b0, raw});    // zero-extend to signed
    end

endmodule

`default_nettype wire
