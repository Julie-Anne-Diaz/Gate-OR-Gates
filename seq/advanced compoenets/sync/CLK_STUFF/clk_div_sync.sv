// Name: Abhiram Pinnity
// Description: This is an clock div

module clk_div #(
    parameter int clk_in_freq  = 50000000,   // default input clock frequency
    parameter int clk_out_freq = 1      // default desired output frequency
)(
    input  logic clk_in,
    input  logic rst,
    output logic clk_out
);

localparam int half_way = clk_in_freq/(2*clk_out_freq);
int count;
logic temp_clk_out;

always_ff @ (posedge clk_in) begin
    if(rst) begin
        count <= 0;
        temp_clk_out <= 0;
    end
    else begin
        if(count == half_way-1) begin
            temp_clk_out <= ~temp_clk_out;
            count <= 0;
        end
        else begin
            count <= count + 1;
        end
    end
end

assign clk_out = temp_clk_out;

endmodule
