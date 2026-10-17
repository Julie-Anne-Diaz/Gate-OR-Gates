// Name: Abhiram Pinnity
// Description: This is an clock gen

module clk_gen #(
    parameter int ms_period = 10   
)(
    input  logic clk50MHz, // board clock
    input  logic rst, // active high
    input  logic button_n, // active low
    output logic clk_out
);

    logic clk_out_div;
    integer count = 0;

    clk_div #(
        .clk_in_freq(50000000),
        .clk_out_freq(1)
    )
    clk_div1 (
        .clk_in(clk50MHz),
        .rst(rst),
        .clk_out(clk_out_div)
    );

    always_ff @(posedge clk_out_div) begin
        if(rst) begin
            count <= 0;
            clk_out <= 1'b0;
        end

        else if (!button_n) begin
            if(count == ms_period) begin
                count <= 1;
                clk_out <= 1'b1;
            end
            else begin
                count <= count + 1;
                clk_out <= 1'b0;
            end
        end

        else begin
            count <= 0;
            clk_out <= 1'b0;
        end
    end

endmodule
