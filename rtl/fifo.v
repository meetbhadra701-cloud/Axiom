// fifo.v — Parameterizable synchronous FIFO buffer.
// Authored by the Architect from spec/spec.md. Synthesizable Verilog-2001 (CLAUDE.md §3).
//
// Transparent read: dout is combinational wire from mem[rd_ptr].
// DEPTH must be a power of 2; PTR_WIDTH = $clog2(DEPTH).
// Simultaneous read+write when both valid: count unchanged, both pointers advance.

`default_nettype none

module fifo #(
    parameter WIDTH = 8,
    parameter DEPTH = 16
) (
    input  wire             clk,
    input  wire             rst,    // synchronous, active-high
    input  wire             wr_en,
    input  wire             rd_en,
    input  wire [WIDTH-1:0] din,
    output wire [WIDTH-1:0] dout,   // transparent: mem[rd_ptr], combinational
    output reg              full,
    output reg              empty
);

    // Pointer width: clog2(DEPTH). Works because DEPTH is a power of 2.
    localparam PTR_WIDTH = $clog2(DEPTH);

    reg [WIDTH-1:0]     mem  [0:DEPTH-1];
    reg [PTR_WIDTH-1:0] wr_ptr;
    reg [PTR_WIDTH-1:0] rd_ptr;
    reg [PTR_WIDTH:0]   count;      // one extra bit to distinguish full from empty

    // Transparent output: no registered dout, avoids read latency of one cycle.
    assign dout = mem[rd_ptr];

    // Decoded control: only act when the operation is valid.
    wire do_write = wr_en && !full;
    wire do_read  = rd_en && !empty;

    integer k;
    always @(posedge clk) begin
        if (rst) begin
            wr_ptr <= {PTR_WIDTH{1'b0}};
            rd_ptr <= {PTR_WIDTH{1'b0}};
            count  <= {(PTR_WIDTH+1){1'b0}};
            full   <= 1'b0;
            empty  <= 1'b1;
        end else begin
            // Write port.
            if (do_write) begin
                mem[wr_ptr] <= din;
                wr_ptr      <= wr_ptr + 1'b1;
            end

            // Read port.
            if (do_read)
                rd_ptr <= rd_ptr + 1'b1;

            // Count and flags (simultaneous R+W → count unchanged).
            if (do_write && !do_read)
                count <= count + 1'b1;
            else if (do_read && !do_write)
                count <= count - 1'b1;
            // else (both or neither): count unchanged

            // Flags are registered and reflect the count AFTER this cycle's update.
            full  <= (do_write && !do_read) ? (count == DEPTH - 1) :
                     (!do_read && !do_write) ? (count == DEPTH)     : 1'b0;
            empty <= (do_read && !do_write) ? (count == 1)          :
                     (!do_read && !do_write) ? (count == 0)          : 1'b0;
        end
    end

endmodule

`default_nettype wire
