//Abhiram Pinnity
// Description: Combinational NOT gate

module NOT_GATE#(
    parameter WIDTH = 4
)(
    input logic[WIDTH-1:0] in1,
    output logic[WIDTH-1:0] out1
);

always_comb begin 
    out1 = ~in1;
end

endmodule