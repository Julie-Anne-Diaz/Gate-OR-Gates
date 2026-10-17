//Abhiram Pinnity
// Description: RALU

module shift_reg_async(
    input logic clk,
    input logic rst,
    input logic in1,
    output logic out1
);

logic out1_r;
logic out2_r;
logic out3_r;
logic out4_r;

always_ff @(posedge clk or posedge rst)
begin
    if(rst) begin
        out1_r <= 1'b0;
        out2_r <= 1'b0;
        out3_r <= 1'b0;
        out4_r <= 1'b0;
    end
    else begin
        out1_r <= in1;
        out2_r <= out1_r;
        out3_r <= out2_r;
        out4_r <= out3_r;
    end  
end

assign out1 = out4_r;

endmodule