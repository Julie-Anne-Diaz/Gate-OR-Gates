//Abhiram Pinnity
// Description: Combinational 4 bit Full adder

module Full_Adder(
    input logic in1,
    input logic in2,
    input logic C_in,
    output logic C_out,
    output logic out1
);

logic[1:0] wholeoutput;

always_comb begin
    wholeoutput = {1'b0, in1} + {1'b0, in2} + C_in;
    C_out = wholeoutput[1];
    out1 = wholeoutput[0];
end

endmodule