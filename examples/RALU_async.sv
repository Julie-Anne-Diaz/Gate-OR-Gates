// Abhiram Pinnity
// Description: RALU
module RALU_async #(
    parameter WIDTH = 4
)(
    input logic clk,
    input logic rst,
    input logic [WIDTH-1:0] in1,
    input logic [WIDTH-1:0] in2,
    input logic [3:0] sel,
    output logic [WIDTH-1:0] out1
);
    logic [WIDTH-1:0] in1_r;
    logic [WIDTH-1:0] in2_r;
    logic [WIDTH-1:0] out1_r;

    always_ff @(posedge clk or posedge rst) begin
        if (rst) begin
            in1_r <= 1'b0;
            in2_r <= 1'b0;
            out1_r <= 1'b0;
        end else begin
            case (sel)
                // AND
                4'b0000: out1_r <= in1_r & in2_r;
                // OR
                4'b0001: out1_r <= in1_r | in2_r;
                // NOT
                4'b0010: out1_r <= ~in1_r;
                // Hold -- mbappe special
                4'b0011: begin end
                // Add without carry
                4'b0100: out1_r <= in1_r + in2_r;
                // XOR
                4'b0101: out1_r <= in1_r ^ in2_r;
                // Subtract
                4'b0110: out1_r <= in1_r - in2_r;
                // Left shift of in1
                4'b0111: out1_r <= in1_r << 1;
                // Right shift of in1
                4'b1000: out1_r <= in1_r >> 1;
                // Two's complement of in1
                4'b1001: out1_r <= ~in1_r + 1;
                // Load in2 into in1
                4'b1010: in1_r <= in2_r;
                // Load output back into in1
                4'b1011: in1_r <= out1_r;
                // Increment in1
                4'b1100: out1_r <= in1_r + 1;
                // Decrement in1
                4'b1101: out1_r <= in1_r - 1;
                // Wire in1
                4'b1110: out1_r <= in1_r;
                // Load inputs
                4'b1111: begin
                    in1_r <= in1;
                    in2_r <= in2;
                end
                default: out1_r <= 1'b0;
            endcase
        end
    end

    assign out1 = out1_r;
endmodule
