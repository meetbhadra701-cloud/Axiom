// uart_tx.v — 8-N-1 UART transmitter.
// Start bit (0), 8 data bits LSB-first, stop bit (1). Baud set by CLKS_PER_BIT.
// en is ignored when busy. tx idles at 1 (mark).

`default_nettype none

module uart_tx #(
    parameter CLKS_PER_BIT = 868,  // baud divisor (868 → 115200 @ 100 MHz)
    parameter CLKDIV_W     = 10    // ceil(log2(CLKS_PER_BIT)); explicit per library convention
) (
    input  wire       clk,
    input  wire       rst,
    input  wire       en,       // load strobe; ignored when busy=1
    input  wire [7:0] data,     // byte to transmit; latched on en & ~busy
    output reg        tx,       // UART serial output; idle = 1
    output reg        busy      // high while transmitting
);

    localparam [1:0]          IDLE  = 2'd0,
                               START = 2'd1,
                               DATA  = 2'd2,
                               STOP  = 2'd3;

    localparam [CLKDIV_W-1:0] CLKDIV_MAX = CLKS_PER_BIT - 1;

    reg [1:0]          state;
    reg [CLKDIV_W-1:0] baud_cnt;
    reg [2:0]          bit_idx;
    reg [7:0]          data_reg;

    always @(posedge clk) begin
        if (rst) begin
            state    <= IDLE;
            baud_cnt <= {CLKDIV_W{1'b0}};
            bit_idx  <= 3'd0;
            data_reg <= 8'h00;
            tx       <= 1'b1;
            busy     <= 1'b0;
        end else begin
            case (state)
                IDLE: begin
                    if (en) begin
                        data_reg <= data;
                        baud_cnt <= {CLKDIV_W{1'b0}};
                        state    <= START;
                        tx       <= 1'b0;
                        busy     <= 1'b1;
                    end else begin
                        tx   <= 1'b1;
                        busy <= 1'b0;
                    end
                end

                START: begin
                    if (baud_cnt == CLKDIV_MAX) begin
                        baud_cnt <= {CLKDIV_W{1'b0}};
                        bit_idx  <= 3'd0;
                        state    <= DATA;
                        tx       <= data_reg[0];
                    end else begin
                        baud_cnt <= baud_cnt + 1'b1;
                    end
                end

                DATA: begin
                    if (baud_cnt == CLKDIV_MAX) begin
                        baud_cnt <= {CLKDIV_W{1'b0}};
                        if (bit_idx == 3'd7) begin
                            state <= STOP;
                            tx    <= 1'b1;
                        end else begin
                            bit_idx <= bit_idx + 1'b1;
                            tx      <= data_reg[bit_idx + 1'b1];
                        end
                    end else begin
                        baud_cnt <= baud_cnt + 1'b1;
                    end
                end

                STOP: begin
                    if (baud_cnt == CLKDIV_MAX) begin
                        baud_cnt <= {CLKDIV_W{1'b0}};
                        state    <= IDLE;
                        busy     <= 1'b0;
                    end else begin
                        baud_cnt <= baud_cnt + 1'b1;
                    end
                end

                default: begin
                    state <= IDLE;
                    tx    <= 1'b1;
                    busy  <= 1'b0;
                end
            endcase
        end
    end

endmodule

`default_nettype wire
