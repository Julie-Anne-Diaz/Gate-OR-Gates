// Structural 4-to-1 mux built from three mux_2 instances.
// sel: 00 selects in1, 01 selects in2, 10 selects in3, 11 selects in4.
module mux_4 #(parameter WIDTH = 4)(
    input logic [WIDTH-1:0] in1, in2, in3, in4,
    input logic [1:0] sel,
    output logic [WIDTH-1:0] out1
);
wire [WIDTH-1:0] low_pair, high_pair;
mux_2 #(.WIDTH(WIDTH)) low_mux (.in1(in1), .in2(in2), .sel(sel[0]), .out1(low_pair));
mux_2 #(.WIDTH(WIDTH)) high_mux (.in1(in3), .in2(in4), .sel(sel[0]), .out1(high_pair));
mux_2 #(.WIDTH(WIDTH)) final_mux (.in1(low_pair), .in2(high_pair), .sel(sel[1]), .out1(out1));
endmodule
