//Abhiram Pinnity
// Description: Seq async reset NOT gate

module NOT_GATE_async#(
    parameter WIDTH = 4
)(
    input logic clk,
    input logic rst,
    input logic[WIDTH-1:0] in1,
    output logic[WIDTH-1:0] out1
);

always_ff @(posedge clk or posedge rst) begin 
    if(rst) begin
        out1 <= 1'b0;
    end
    else begin
        out1 <= ~(in1);
    end   
end

endmodule