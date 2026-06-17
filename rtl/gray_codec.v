// gray_codec.v — Registered binary ↔ Gray code converter.
// mode=0: encode binary→Gray (bin ^ (bin>>1)).
// mode=1: decode Gray→binary (serial XOR prefix chain from MSB).

`default_nettype none

module gray_codec #(
    parameter WIDTH = 8
) (
    input  wire             clk,
    input  wire             rst,        // synchronous, active-high
    input  wire             en,
    input  wire             mode,       // 0=encode, 1=decode
    input  wire [WIDTH-1:0] data,
    output reg  [WIDTH-1:0] result
);

    // Encode: each bit XOR with the bit above; MSB unchanged.
    wire [WIDTH-1:0] encoded;
    assign encoded = data ^ (data >> 1);

    // Decode: serial XOR prefix chain from MSB down.
    wire [WIDTH-1:0] decoded;
    assign decoded[WIDTH-1] = data[WIDTH-1];
    genvar i;
    generate
        for (i = WIDTH-2; i >= 0; i = i - 1) begin : dec_chain
            assign decoded[i] = decoded[i+1] ^ data[i];
        end
    endgenerate

    always @(posedge clk) begin
        if (rst)
            result <= {WIDTH{1'b0}};
        else if (en)
            result <= mode ? decoded : encoded;
        // else: hold
    end

endmodule

`default_nettype wire
