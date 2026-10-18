module switch_bridge (
    input wire [9:0] SW,
    input wire [1:0] KEY,
    output wire [11:0] GPIO,
    output wire [9:0] LEDR
);
    assign GPIO[9:0] = SW;
    // DE10-Lite buttons are active LOW; Arduino receives HIGH when pressed.
    assign GPIO[11:10] = ~KEY;
    assign LEDR = SW;
endmodule
