//Abhiram Pinnity
// Description: Structurally combined module that allows easy tb check of gate logic

module ALL_GATES_async#(
    parameter WIDTH = 4
)(
    input logic clk,
    input logic rst,
    input logic[WIDTH-1:0] in1,
    input logic[WIDTH-1:0] in2,
    output logic[WIDTH-1:0] out_AND,
    output logic[WIDTH-1:0] out_OR,
    output logic[WIDTH-1:0] out_NOT,
    output logic[WIDTH-1:0] out_NAND,
    output logic[WIDTH-1:0] out_NOR,
    output logic[WIDTH-1:0] out_XOR,
    output logic[WIDTH-1:0] out_XNOR
);

AND_GATE_async and1(
    .clk(clk),
    .rst(rst),
    .in1(in1),
    .in2(in2),
    .out1(out_AND)
);

OR_GATE_async or1(
    .clk(clk),
    .rst(rst),
    .in1(in1),
    .in2(in2),
    .out1(out_OR)
);

NOT_GATE_async not1(
    .clk(clk),
    .rst(rst),
    .in1(in1),
    .out1(out_NOT)
);

NAND_GATE_async nand1(
    .clk(clk),
    .rst(rst),
    .in1(in1),
    .in2(in2),
    .out1(out_NAND)
);

NOR_GATE_async NOR1(
    .clk(clk),
    .rst(rst),
    .in1(in1),
    .in2(in2),
    .out1(out_NOR)
);

XOR_GATE_async xor1(
    .clk(clk),
    .rst(rst),
    .in1(in1),
    .in2(in2),
    .out1(out_XOR)
);

XNOR_GATE_async xnor1(
    .clk(clk),
    .rst(rst),
    .in1(in1),
    .in2(in2),
    .out1(out_XNOR)
);

endmodule