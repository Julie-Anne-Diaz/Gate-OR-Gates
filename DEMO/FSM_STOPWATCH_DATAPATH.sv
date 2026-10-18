
module FSM_STOPWATCH_DATAPATH#(
    parameter WIDTH = 16,
    parameter MAX = 9999
)
(
    input  logic clk,
    input  logic rst,

    input logic tick,
    input logic run_en,
    input logic lap_en,
    input logic stop_sel,

    output logic[WIDTH-1: 0] count,
    output logic[WIDTH-1: 0] lap_count
);

    // State and counter registers
always_ff @(posedge clk or posedge rst) begin
    if (rst) begin
        count     <= 1'b0;
        lap_count <= 1'b0;
    end
    else begin
        // Counter
        if (stop_sel) begin
            count <= 1'b0;
            lap_count <= 1'b0;
        end
        else if (run_en && tick) begin
            count <= (count == MAX) ? '0 : count + 1'b1;
        end

        // Lap register
        if (lap_en) begin
                lap_count <= count;
        end
    end
end

endmodule