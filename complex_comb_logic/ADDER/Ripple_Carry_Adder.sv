//Abhiram Pinnity
// Description: Structural 8 input ripple carry adder using full adder

module Ripple_Carry_Adder(
    input logic in1,
    input logic in2,
    input logic in3,
    input logic in4,
    input logic in5,
    input logic in6,
    input logic in7,
    input logic in8,
    input logic C_in,
    output logic C_out,
    output logic[3:0] out1
);

logic[2:0] Carry;


    Full_Adder Adder1 (
        .in1(in1),
        .in2(in2),
        .C_in(C_in),
        .C_out(Carry[0]),
        .out1(out1[0])
    );

    Full_Adder Adder2 (
        .in1(in3),
        .in2(in4),
        .C_in(Carry[0]),
        .C_out(Carry[1]),
        .out1(out1[1])
    );

    Full_Adder Adder3 (
        .in1(in5),
        .in2(in6),
        .C_in(Carry[1]),
        .C_out(Carry[2]),
        .out1(out1[2])
    );

    Full_Adder Adder4 (
        .in1(in7),
        .in2(in8),
        .C_in(Carry[2]),
        .C_out(C_out),
        .out1(out1[3])
    );


endmodule