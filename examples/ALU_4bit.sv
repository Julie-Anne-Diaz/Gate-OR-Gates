// Abhiram Pinnity
// Description: 4 bit sel ALU
module ALU_4bit #(
    parameter WIDTH = 4
)(
    input logic [WIDTH-1:0] in1,
    input logic [WIDTH-1:0] in2,
    input logic [3:0] sel,
    output logic [WIDTH-1:0] out1
);
always_comb
case (sel)
    4'b0000: out1 = in1 & in2;
    4'b0001: out1 = in1 | in2;
    4'b0010: out1 = ~in1;
    4'b0011: out1 = ~(in1 | in2);
    4'b0100: out1 = ~(in1 & in2);
    4'b0101: out1 = in1 ^ in2;
    4'b0110: out1 = ~(in1 ^ in2);
    4'b0111: out1 = in1 << 1;
    4'b1000: out1 = in1 >> 1;
    4'b1001: out1 = ~in1 + 1;
    4'b1010: begin
        for (integer i = 0; i < WIDTH; i++)
            out1[i] = in1[WIDTH-1-i];
    end
    4'b1011: begin
        for (integer i = 0; i < WIDTH; i++)
            out1[i] = in2[WIDTH-1-i];
    end
    4'b1100: out1 = in1 + 1;
    4'b1101: out1 = in1 - 1;
    4'b1110: out1 = in1;
    4'b1111: out1 = in2;
    default: out1 = 4'b0000;
endcase
endmodule
