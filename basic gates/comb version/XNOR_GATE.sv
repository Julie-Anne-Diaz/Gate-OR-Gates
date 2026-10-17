//Abhiram Pinnity
// Description: Combinational XNOR gate

module XNOR_GATE#(
    parameter WIDTH = 4
)(
    input logic[WIDTH-1:0] in1,
    input logic[WIDTH-1:0] in2,
    output logic[WIDTH-1:0] out1
);

always_comb begin 
    out1 = ~(in1 ^ in2);
end

endmodule