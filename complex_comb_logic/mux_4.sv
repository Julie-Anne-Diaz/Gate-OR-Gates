//Abhiram Pinnity
// Description: Structural 4 to 1 mux using 2 to 1 muxes

module mux_4#(
    parameter WIDTH = 4
)(
    input logic[WIDTH-1:0] in1,
    input logic[WIDTH-1:0] in2,
    input logic[WIDTH-1:0] in3,
    input logic[WIDTH-1:0] in4,
    input logic [1:0] sel,
    output logic[WIDTH-1:0] out1
);

logic[WIDTH-1:0] mux1_out;
logic[WIDTH-1:0] mux2_out;

    mux_2 mux1 (
        .in1(in1),
        .in2(in2),
        .sel(sel[0]),
        .out1(mux1_out)
    );

    mux_2 mux2 (
        .in1(in3),
        .in2(in4),
        .sel(sel[0]),
        .out1(mux2_out)
    );

    mux_2 mux3 (
        .in1(mux1_out),
        .in2(mux2_out),
        .sel(sel[1]),
        .out1(out1)
    );


endmodule