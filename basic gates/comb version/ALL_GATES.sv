//Abhiram Pinnity
// Description: Structurally combined module that allows easy tb check of gate logic

module ALL_GATES#(
    parameter WIDTH = 4
)(
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

AND_GATE and1(
    .in1(in1),
    .in2(in2),
    .out1(out_AND)
);

OR_GATE or1(
    .in1(in1),
    .in2(in2),
    .out1(out_OR)
);

NOT_GATE not1(
    .in1(in1),
    .out1(out_NOT)
);

NAND_GATE nand1(
    .in1(in1),
    .in2(in2),
    .out1(out_NAND)
);

NOR_GATE NOR1(
    .in1(in1),
    .in2(in2),
    .out1(out_NOR)
);

XOR_GATE xor1(
    .in1(in1),
    .in2(in2),
    .out1(out_XOR)
);

XNOR_GATE xnor1(
    .in1(in1),
    .in2(in2),
    .out1(out_XNOR)
);

endmodule