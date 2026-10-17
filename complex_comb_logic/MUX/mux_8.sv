//Abhiram Pinnity
// Description: Structural 8 to 1 mux using 4 to 1 muxes

module mux_8#(
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
    input logic [2:0] sel,
    output logic[WIDTH-1:0] out1
);

logic[WIDTH-1:0] mux1_out;
logic[WIDTH-1:0] mux2_out;

    mux_4 mux1 (
        .in1(in1),
        .in2(in2),
        .in3(in3),
        .in4(in4),
        .sel(sel[1:0]),
        .out1(mux1_out)
    );

    mux_4 mux2 (
        .in1(in5),
        .in2(in6),
        .in3(in7),
        .in4(in8),
        .sel(sel[1:0]),
        .out1(mux2_out)
    );

    mux_2 mux3 (
        .in1(mux1_out),
        .in2(mux2_out),
        .sel(sel[2]),
        .out1(out1)
    );


endmodule