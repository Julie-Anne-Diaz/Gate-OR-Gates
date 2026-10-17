// Abhiram Pinnity
// Description: Combinational 2 to 1 mux
module mux_2 #(
    parameter WIDTH = 4
)(
    input logic [WIDTH-1:0] in1,
    input logic [WIDTH-1:0] in2,
    input logic sel,
    output logic [WIDTH-1:0] out1
);
always_comb begin
    if (sel) out1 = in2;
    else out1 = in1;
end
endmodule
