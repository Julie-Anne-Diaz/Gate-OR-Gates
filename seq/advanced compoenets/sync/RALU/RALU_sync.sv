//Abhiram Pinnity
// Description: RALU

module RALU_async#(
    parameter WIDTH = 4
)(
    input logic clk,
    input logic rst,
    input logic[WIDTH-1:0] in1,
    input logic[WIDTH-1:0] in2,
    input logic [3:0] sel,
    output logic[WIDTH-1:0] out1
);

logic[WIDTH-1:0] in1_r;
logic[WIDTH-1:0] in2_r;
logic[WIDTH-1:0] out1_r;

always_ff @(posedge clk)
begin
    if(rst) begin
        in1_r <= 1'b0;
        in2_r <= 1'b0;
        out1_r <= 1'b0;
    end
    else begin
        case(sel)
            //and
                4'b0000: begin
                    out1_r <= in1_r & in2_r;
                end
            //or
                4'b0001: begin
                    out1_r <= in1_r | in2_r;
                end
            //not
                4'b0010: begin
                    out1_r <= ~in1_r;
                end
            //Hold
                4'b0011: begin
                    //mbappe special
                end
            //add w/0 carry
                4'b0100: begin
                out1_r <= in1_r + in2_r;
                end
            //XOR
                4'b0101: begin
                    out1_r <= (in1_r ^ in2_r);
                end
            //subtract
                4'b0110: begin
                    out1_r <= in1_r - in2_r;
                end
            //Left Shift of in1
                4'b0111: begin
                    out1_r <= in1_r << 1;
                end
            //Right Shift of in1
                4'b1000: begin
                    out1_r <= in1_r >> 1;
                end
            //2's compliment of in1
                4'b1001: begin
                    out1_r <= ~(in1_r) + 1;
                end
            //Load in2 into in1
                4'b1010: begin
                    in1_r <= in2_r;
                end
            //load output back to in1
                4'b1011: begin
                    in1_r <= out1_r;
                end
            //increment In1
                4'b1100: begin
                    out1_r <= in1_r + 1;
                end
            //Decrement In1
                4'b1101: begin
                    out1_r <= in1_r - 1;
                end
            //Wire In1
                4'b1110: begin
                    out1_r <= in1_r;
                end
            //load inputs
                4'b1111: begin
                    in1_r <= in1;
                    in2_r <= in2;
                end
            //default
                default: 
                    out1_r <= 1'b0;
        endcase
    end

end

assign out1 = out1_r;

endmodule