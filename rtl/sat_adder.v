// sat_adder.v - Synchronous signed saturating adder.

`default_nettype none

module sat_adder #(
    parameter WIDTH = 16
) (
    input  wire                         clk,
    input  wire                         rst,
    input  wire                         en,
    input  wire signed [WIDTH-1:0]      a,
    input  wire signed [WIDTH-1:0]      b,
    output reg  signed [WIDTH-1:0]      sum
);

    localparam signed [WIDTH-1:0] SAT_MAX = {1'b0, {WIDTH-1{1'b1}}};
    localparam signed [WIDTH-1:0] SAT_MIN = {1'b1, {WIDTH-1{1'b0}}};

    wire signed [WIDTH:0] wide_a;
    wire signed [WIDTH:0] wide_b;
    wire signed [WIDTH:0] wide_sum;
    wire signed [WIDTH:0] wide_max;
    wire signed [WIDTH:0] wide_min;

    assign wide_a   = {a[WIDTH-1], a};
    assign wide_b   = {b[WIDTH-1], b};
    assign wide_sum = wide_a + wide_b;
    assign wide_max = {1'b0, SAT_MAX};
    assign wide_min = {1'b1, SAT_MIN};

    always @(posedge clk) begin
        if (rst) begin
            sum <= {WIDTH{1'b0}};
        end else if (en) begin
            if (wide_sum > wide_max) begin
                sum <= SAT_MAX;
            end else if (wide_sum < wide_min) begin
                sum <= SAT_MIN;
            end else begin
                sum <= wide_sum[WIDTH-1:0];
            end
        end
    end

endmodule

`default_nettype wire
