// strobe_gen.v — Programmable clock-enable rate divider.
// Fires a 1-cycle strobe pulse every `divisor` enabled clock cycles.
// divisor=0 is treated as 2^WIDTH (natural carry-free wrap).

`default_nettype none

module strobe_gen #(
    parameter WIDTH = 8
) (
    input  wire             clk,
    input  wire             rst,              // synchronous, active-high
    input  wire             en,
    input  wire [WIDTH-1:0] divisor,          // cycles per strobe; 0 = 2^WIDTH
    output reg              strobe            // 1-cycle pulse each period
);

    reg [WIDTH-1:0] counter;

    always @(posedge clk) begin
        if (rst) begin
            counter <= {WIDTH{1'b0}};
            strobe  <= 1'b0;
        end else if (en) begin
            if (counter == divisor - 1'b1) begin
                counter <= {WIDTH{1'b0}};
                strobe  <= 1'b1;
            end else begin
                counter <= counter + 1'b1;
                strobe  <= 1'b0;
            end
        end
        // else: hold counter and strobe
    end

endmodule

`default_nettype wire
