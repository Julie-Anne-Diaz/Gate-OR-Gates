module tick_gen #(
    parameter DIV = 50_000_000     // 50 MHz -> 1 Hz
)(
    input  logic clk, rst,
    output logic tick
);
    logic [$clog2(DIV)-1:0] cnt;
    always_ff @(posedge clk or posedge rst) begin
        if (rst) begin
            cnt  <= '0;
            tick <= 1'b0;
        end else if (cnt == DIV - 1) begin
            cnt  <= '0;
            tick <= 1'b1;
        end else begin
            cnt  <= cnt + 1'b1;
            tick <= 1'b0;
        end
    end
endmodule