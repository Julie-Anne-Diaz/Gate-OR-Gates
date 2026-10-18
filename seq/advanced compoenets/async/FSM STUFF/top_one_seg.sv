// Top level, version 2: one seven-segment display (lock only, no alarm output)
// Target: Terasic DE10-Lite (active-low keys and segments)
//
//   KEY[0]  : manual clock (press = one clock edge, board debounces it)
//   KEY[1]  : reset (press = reset)
//   SW[0]   : serial input bit "in"
//   HEX0    : lock (1 = locked, 0 = unlocked)
//   LEDR[0] : lock

module top_one_seg (
    input  logic       MAX10_CLK1_50,   // unused, kept so the pin assignment can stay
    input  logic [1:0] KEY,
    input  logic [9:0] SW,
    output logic [7:0] HEX0,
    output logic [7:0] HEX1,
    output logic [7:0] HEX2,
    output logic [7:0] HEX3,
    output logic [7:0] HEX4,
    output logic [7:0] HEX5,
    output logic [9:0] LEDR
);

    logic clk, rst, in;
    logic lock;

    assign clk = ~KEY[0];   // keys are active low -> rising edge on press
    assign rst = ~KEY[1];
    assign in  = SW[0];

    // alarm_on and unlock are intentionally left unconnected
    FSM_async u_fsm (
        .clk      (clk),
        .rst      (rst),
        .in       (in),
        .alarm_on (),
        .lock     (lock),
        .unlock   ()
    );

    // Active-low 7-seg decoder for a single bit (shows 0 or 1)
    // Segment order: {dp, g, f, e, d, c, b, a}
    function automatic logic [7:0] seg_bit(input logic b);
        return b ? 8'b1111_1001   // "1"
                 : 8'b1100_0000;  // "0"
    endfunction

    assign HEX0 = seg_bit(lock);

    // Blank the unused displays
    assign HEX1 = 8'hFF;
    assign HEX2 = 8'hFF;
    assign HEX3 = 8'hFF;
    assign HEX4 = 8'hFF;
    assign HEX5 = 8'hFF;

    assign LEDR = {9'b0, lock};

endmodule
