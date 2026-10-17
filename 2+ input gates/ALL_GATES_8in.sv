//Abhiram Pinnity
// Description: Structurally combined module that allows easy tb check of gate logic

module ALL_GATES_8in#(
    parameter WIDTH = 4
)(
    input logic[WIDTH-1:0] in1,
    input logic[WIDTH-1:0] in2,
    input logic[WIDTH-1:0] in3,
    input logic[WIDTH-1:0] in4,
    input logic[WIDTH-1:0] in5,
    input logic[WIDTH-1:0] in6,
    input logic[WIDTH-1:0] in7,
    input logic[WIDTH-1:0] in8,
    output logic[WIDTH-1:0] out_AND,
    output logic[WIDTH-1:0] out_OR,
    output logic[WIDTH-1:0] out_NOT,
    output logic[WIDTH-1:0] out_NAND,
    output logic[WIDTH-1:0] out_NOR,
    output logic[WIDTH-1:0] out_XOR,
    output logic[WIDTH-1:0] out_XNOR
);

AND_GATE_8in and1(
    .in1(in1),
    .in2(in2),
    .in3(in3),
    .in4(in4),
    .in5(in5),
    .in6(in6),
    .in7(in7),
    .in8(in8),
    .out1(out_AND)
);

OR_GATE_8in or1(
    .in1(in1),
    .in2(in2),
    .in3(in3),
    .in4(in4),
    .in5(in5),
    .in6(in6),
    .in7(in7),
    .in8(in8),
    .out1(out_OR)
);

NOT_GATE_8in not1(
    .in1(in1),
    .out1(out_NOT)
);

NAND_GATE_8in nand1(
    .in1(in1),
    .in2(in2),
    .in3(in3),
    .in4(in4),
    .in5(in5),
    .in6(in6),
    .in7(in7),
    .in8(in8),
    .out1(out_NAND)
);

NOR_GATE_8in NOR1(
    .in1(in1),
    .in2(in2),
    .in3(in3),
    .in4(in4),
    .in5(in5),
    .in6(in6),
    .in7(in7),
    .in8(in8),
    .out1(out_NOR)
);

XOR_GATE_8in xor1(
    .in1(in1),
    .in2(in2),
    .in3(in3),
    .in4(in4),
    .in5(in5),
    .in6(in6),
    .in7(in7),
    .in8(in8),
    .out1(out_XOR)
);

XNOR_GATE_8in xnor1(
    .in1(in1),
    .in2(in2),
    .in3(in3),
    .in4(in4),
    .in5(in5),
    .in6(in6),
    .in7(in7),
    .in8(in8),
    .out1(out_XNOR)
);

endmodule