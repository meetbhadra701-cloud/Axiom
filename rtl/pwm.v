// pwm.v — Synchronous pulse-width modulator.
// Internal free-running counter compared against duty to produce a 1-bit output.
// Pre-increment comparison: pwm_out registered alongside counter increment.

`default_nettype none

module pwm #(
    parameter WIDTH = 8
) (
    input  wire             clk,
    input  wire             rst,      // synchronous, active-high; resets counter + output
    input  wire             en,       // counter advances and output updates only when high
    input  wire [WIDTH-1:0] duty,     // unsigned duty-cycle threshold
    output reg              pwm_out   // registered PWM bit
);

    reg [WIDTH-1:0] counter;

    always @(posedge clk) begin
        if (rst) begin
            counter <= {WIDTH{1'b0}};
            pwm_out <= 1'b0;
        end else if (en) begin
            pwm_out <= (counter < duty);   // pre-increment comparison
            counter <= counter + 1'b1;     // wraps naturally at 2^WIDTH
        end
        // else: hold
    end

endmodule

`default_nettype wire
