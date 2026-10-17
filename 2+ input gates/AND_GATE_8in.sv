//Abhiram Pinnity
// Description: Combinational AND gate

module AND_GATE_8in#(
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
    output logic[WIDTH-1:0] out1
);

always_comb begin 
    out1 = in1 & in2 & in3 & in4 & in5 & in6 & in7 & in8;
end

endmodule