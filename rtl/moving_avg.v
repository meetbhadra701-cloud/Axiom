// moving_avg.v — Power-of-2 sliding-window moving average.
// avg_out = sum(last N samples) >> LOG2N, registered. avg_valid strobes with en.

`default_nettype none

module moving_avg #(
    parameter DATA_W = 8,
    parameter LOG2N  = 3
) (
    input  wire             clk,
    input  wire             rst,    // synchronous, active-high
    input  wire             en,
    input  wire [DATA_W-1:0] x_in,
    output reg  [DATA_W-1:0] avg_out,
    output reg               avg_valid
);

    localparam N     = 1 << LOG2N;
    localparam ACC_W = DATA_W + LOG2N;

    reg [DATA_W-1:0] sr  [0:N-1]; // shift register; sr[0]=newest, sr[N-1]=oldest
    reg [ACC_W-1:0]  acc;

    // Oldest sample being evicted this cycle
    wire [DATA_W-1:0] evicted;
    assign evicted = sr[N-1];

    // Full-precision running sum (uses current acc and current sr[N-1])
    wire [ACC_W-1:0] acc_next;
    assign acc_next = acc
                    + {{(LOG2N){1'b0}}, x_in}
                    - {{(LOG2N){1'b0}}, evicted};

    // Stage 0: new sample enters the shift register head
    always @(posedge clk) begin
        if (rst)      sr[0] <= {DATA_W{1'b0}};
        else if (en)  sr[0] <= x_in;
    end

    // Stages 1..N-1: each stage takes the previous (stage-zero-split pattern)
    genvar g;
    generate
        for (g = 1; g < N; g = g + 1) begin : shift
            always @(posedge clk) begin
                if (rst)      sr[g] <= {DATA_W{1'b0}};
                else if (en)  sr[g] <= sr[g-1];
            end
        end
    endgenerate

    // Accumulator and registered output
    always @(posedge clk) begin
        if (rst) begin
            acc       <= {ACC_W{1'b0}};
            avg_out   <= {DATA_W{1'b0}};
            avg_valid <= 1'b0;
        end else if (en) begin
            acc       <= acc_next;
            avg_out   <= acc_next[ACC_W-1:LOG2N];
            avg_valid <= 1'b1;
        end else begin
            avg_valid <= 1'b0;
            // acc, avg_out: hold
        end
    end

endmodule

`default_nettype wire
