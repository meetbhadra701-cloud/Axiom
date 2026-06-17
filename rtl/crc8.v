// crc8.v — CRC-8/MAXIM (Dallas 1-Wire) bit-serial accumulator.
// Reflected polynomial 0x8C (normal 0x31 = x^8+x^5+x^4+1). Init 0x00.
// Feed bits LSB-first; crc holds the running checksum.

`default_nettype none

module crc8 (
    input  wire       clk,
    input  wire       rst,     // synchronous, active-high; clears crc to 0x00
    input  wire       en,      // shift enable; advance one bit per cycle
    input  wire       bit_in,  // next data bit (LSB of each byte first)
    output reg  [7:0] crc      // running CRC-8/MAXIM value
);

    wire feedback;
    assign feedback = crc[0] ^ bit_in;

    always @(posedge clk) begin
        if (rst) begin
            crc <= 8'h00;
        end else if (en) begin
            crc[0] <= crc[1];
            crc[1] <= crc[2];
            crc[2] <= crc[3] ^ feedback;   // poly tap bit 2 (0x8C = 10001100b)
            crc[3] <= crc[4] ^ feedback;   // poly tap bit 3
            crc[4] <= crc[5];
            crc[5] <= crc[6];
            crc[6] <= crc[7];
            crc[7] <= feedback;            // poly tap bit 7 (MSB of 0x8C)
        end
        // else: hold
    end

endmodule

`default_nettype wire
