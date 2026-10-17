//Abhiram Pinnity
// Description: Seq sync reset NAND gate

module NAND_GATE_sync#(
    parameter WIDTH = 4
)(
    input logic clk,
    input logic rst,
    input logic[WIDTH-1:0] in1,
    input logic[WIDTH-1:0] in2,
    output logic[WIDTH-1:0] out1
);

always_ff @(posedge clk) begin 
    if(rst) begin
        out1 <= 1'b0;
    end
    else begin
        out1 <= ~(in1 & in2);
    end   
end

endmodule